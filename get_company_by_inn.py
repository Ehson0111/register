import json
import socket
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


API_TEMPLATE = "https://egrul.org/{inn}.json"


def extract_field(data, *keys, default=None):
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def attrs(node):
    if isinstance(node, dict):
        return node.get("@attributes", {})
    return {}


def first_non_empty(*values):
    for value in values:
        if value not in (None, "", [], {}):
            return value
    return None


def build_address(sv_ul: dict) -> str | None:
    address_rf = extract_field(sv_ul, "СвАдресЮЛ", "АдресРФ", default={})
    if not isinstance(address_rf, dict):
        return None

    region = attrs(address_rf.get("Регион", {})).get("НаимРегион")
    district = attrs(address_rf.get("Район", {})).get("НаимРайон")
    city_info = attrs(address_rf.get("Город", {}))
    city = " ".join(
        part for part in [city_info.get("ТипГород"), city_info.get("НаимГород")] if part
    ).strip()
    locality_info = attrs(address_rf.get("НаселПункт", {}))
    locality = " ".join(
        part for part in [locality_info.get("ТипНаселПункт"), locality_info.get("НаимНаселПункт")] if part
    ).strip()
    street_info = attrs(address_rf.get("Улица", {}))
    street = " ".join(
        part for part in [street_info.get("ТипУлица"), street_info.get("НаимУлица")] if part
    ).strip()
    house = first_non_empty(
        attrs(address_rf).get("Дом"),
        attrs(address_rf).get("Здание"),
        attrs(address_rf).get("Корпус"),
    )
    index = attrs(address_rf).get("Индекс")

    parts = [index, region, district, city, locality, street, house]
    result = ", ".join(part for part in parts if part)
    return result or None


def build_director(sv_ul: dict) -> str | None:
    director_node = extract_field(sv_ul, "СведДолжнФЛ", default={})
    person_attrs = attrs(director_node.get("СвФЛ", {}))
    position_attrs = attrs(director_node.get("СвДолжн", {}))

    fio = " ".join(
        part for part in [person_attrs.get("Фамилия"), person_attrs.get("Имя"), person_attrs.get("Отчество")] if part
    ).strip()
    position = position_attrs.get("НаимДолжн")

    if fio and position:
        return f"{fio}, {position}"
    return fio or position


def normalize_inn(raw_inn: str) -> str:
    inn = "".join(ch for ch in raw_inn if ch.isdigit())
    if len(inn) not in (10, 12):
        raise ValueError("ИНН должен содержать 10 или 12 цифр.")
    return inn


def fetch_company_data(inn: str) -> dict:
    url = API_TEMPLATE.format(inn=urllib.parse.quote(inn))
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Python INN Lookup Script/1.0",
            "Accept": "application/json",
        },
    )

    last_error = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                charset = response.headers.get_content_charset() or "utf-8"
                raw = response.read().decode(charset, errors="replace")
                return json.loads(raw)
        except (urllib.error.URLError, TimeoutError, socket.timeout, ssl.SSLError) as exc:
            last_error = exc
            if attempt == 2:
                raise
            time.sleep(1.5 * (attempt + 1))

    if last_error:
        raise last_error
    raise RuntimeError("Не удалось получить данные.")


def print_company_info(data: dict) -> None:
    sv_ul = extract_field(data, "СвЮЛ", default={}) if "СвЮЛ" in data else data
    top_attrs = attrs(sv_ul)

    name = first_non_empty(
        attrs(extract_field(sv_ul, "СвНаимЮЛ", "СвНаимЮЛСокр", default={})).get("НаимСокр"),
        attrs(extract_field(sv_ul, "СвНаимЮЛ", default={})).get("НаимЮЛПолн"),
        data.get("name"),
    )
    inn = first_non_empty(top_attrs.get("ИНН"), data.get("ИНН"))
    kpp = first_non_empty(top_attrs.get("КПП"), data.get("КПП"))
    ogrn = first_non_empty(top_attrs.get("ОГРН"), data.get("ОГРН"))
    status = first_non_empty(
        attrs(extract_field(sv_ul, "СвСтатус", default={})).get("НаимСтатусЮЛ"),
        data.get("Статус"),
        "Действующее",
    )
    address = build_address(sv_ul)

    okved_main = first_non_empty(
        extract_field(sv_ul, "СвОКВЭДОтч", "СвОКВЭДОтчОсн", default=None),
        extract_field(sv_ul, "СвОКВЭД", "СвОКВЭДОсн", default=None),
        extract_field(sv_ul, "СвОКВЭД", "СвОКВЭДДоп", default=None),
    )
    okved_code = attrs(okved_main).get("КодОКВЭД") if okved_main else None
    okved_name = attrs(okved_main).get("НаимОКВЭД") if okved_main else None
    director = build_director(sv_ul)

    print("\nРезультат поиска по ИНН")
    print("-" * 40)
    print(f"Наименование: {name or 'Не найдено'}")
    print(f"ИНН:          {inn or 'Не найдено'}")
    print(f"КПП:          {kpp or 'Не найдено'}")
    print(f"ОГРН:         {ogrn or 'Не найдено'}")
    print(f"Статус:       {status or 'Не найдено'}")
    print(f"Адрес:        {address or 'Не найдено'}")

    if okved_code or okved_name:
        print(f"ОКВЭД:        {(okved_code or '').strip()} {(okved_name or '').strip()}".strip())
    else:
        print("ОКВЭД:        Не найдено")

    if director:
        print(f"Руководитель: {director}")


def main() -> int:
    try:
        if len(sys.argv) > 1:
            raw_inn = sys.argv[1]
        else:
            raw_inn = input("Введите ИНН: ").strip()

        inn = normalize_inn(raw_inn)
        data = fetch_company_data(inn)

        if not isinstance(data, dict) or not data:
            print("Данные по ИНН не найдены.")
            return 1

        print_company_info(data)
        return 0

    except ValueError as exc:
        print(f"Ошибка: {exc}")
        return 1
    except urllib.error.HTTPError as exc:
        print(f"HTTP ошибка: {exc.code} {exc.reason}")
        return 1
    except urllib.error.URLError as exc:
        print(f"Ошибка сети: {exc.reason}")
        return 1
    except json.JSONDecodeError:
        print("Не удалось разобрать ответ сервера.")
        return 1
    except Exception as exc:
        print(f"Неожиданная ошибка: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
