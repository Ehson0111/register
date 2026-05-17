"""Загрузка реквизитов компании по ИНН с egrul.org."""
import time
from typing import Any

import requests
from glom import Coalesce, glom
from stdnum.ru import inn as ru_inn

EGRUL_URL = "https://egrul.org/{inn}.json"
NOT_FOUND = "Не найдено"
DEFAULT_STATUS = "Действующее"

# NOT_FOUND.format()
#10-значный ИНН юрлица или 12-значный ИП

def normalize_inn(raw_inn: str) -> str:
    digits = ru_inn.compact(str(raw_inn or ""))
    if not digits:
        raise ValueError("ИНН должен содержать 10 или 12 цифр")
    try:
        ru_inn.validate(digits)
    except Exception as exc:
        raise ValueError("ИНН должен содержать 10 или 12 цифр") from exc
    return digits


def fetch_company_by_inn(inn: str) -> dict:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "CRM Contact INN Lookup/1.0",
            "Accept": "application/json",
        }
    )
    last_error = None
    for attempt in range(3):  #делаем 3 запроса 
        try:
            response = session.get(EGRUL_URL.format(inn=inn), timeout=30)
            response.raise_for_status() #Если статус 4xx или 5xx — выбросить исключение
            return response.json()
        except requests.RequestException as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(1.5 * (attempt + 1))
    raise last_error


def _join_text(*parts: Any) -> str:
    return " ".join(str(part).strip() for part in parts if part).strip()

# _join_text("г", "Москва", None, "", "  ул  ", "Тверская")
# # → "г Москва ул Тверская"
# glom(объект, путь, default=значение_по_умолчанию)
# data = {
#     "user": {
#         "name": "Алексей",
#         "contacts": {
#             "email": "alex@example.com"
#         }
#     }
# } Coalesce — это "попробуй несколько путей, верни первый, который существует".



# # Кортежем
# name = glom(data, ("user", "name"))  # "Алексей"

def _address_from_ul(sv_ul: dict) -> str:
    addr_rf = glom(sv_ul, ("СвАдресЮЛ", "АдресРФ"), default={})
    if not isinstance(addr_rf, dict):
        return NOT_FOUND

    house = glom(
        addr_rf,
        Coalesce(
            ("@attributes", "Дом"),
            ("@attributes", "Здание"),
            ("@attributes", "Корпус"),
            default=None,
        ),
    )
    parts = [
        glom(addr_rf, ("@attributes", "Индекс"), default=None),
        glom(addr_rf, ("Регион", "@attributes", "НаимРегион"), default=None),
        glom(addr_rf, ("Район", "@attributes", "НаимРайон"), default=None),
        _join_text(
            glom(addr_rf, ("Город", "@attributes", "ТипГород"), default=None),
            glom(addr_rf, ("Город", "@attributes", "НаимГород"), default=None),
        ),
        _join_text(
            glom(addr_rf, ("НаселПункт", "@attributes", "ТипНаселПункт"), default=None),
            glom(addr_rf, ("НаселПункт", "@attributes", "НаимНаселПункт"), default=None),
        ),
        _join_text(
            glom(addr_rf, ("Улица", "@attributes", "ТипУлица"), default=None),
            glom(addr_rf, ("Улица", "@attributes", "НаимУлица"), default=None),
        ),
        house,
    ]
    return ", ".join(part for part in parts if part) or NOT_FOUND


def _director_from_ul(sv_ul: dict) -> str:
    person = glom(sv_ul, ("СведДолжнФЛ", "СвФЛ", "@attributes"), default={})
    position = glom(sv_ul, ("СведДолжнФЛ", "СвДолжн", "@attributes", "НаимДолжн"), default=None)
    fio = _join_text(person.get("Фамилия"), person.get("Имя"), person.get("Отчество"))
    if fio and position:
        return f"{fio}, {position}"
    return fio or position or NOT_FOUND


def _okved_from_ul(sv_ul: dict) -> str:
    okved_node = glom(
        sv_ul,
        Coalesce(
            "СвОКВЭДОтч.СвОКВЭДОтчОсн",
            "СвОКВЭД.СвОКВЭДОсн",
            "СвОКВЭД.СвОКВЭДДоп",
            default={},
        ),
    )
    okved_attrs = glom(okved_node, "@attributes", default={}) if isinstance(okved_node, dict) else {}
    text = _join_text(okved_attrs.get("КодОКВЭД"), okved_attrs.get("НаимОКВЭД"))
    return text or NOT_FOUND


def map_company_data(raw_data: dict) -> dict:
    sv_ul = glom(raw_data, "СвЮЛ", default={})
    top_attrs = glom(sv_ul, "@attributes", default={})

    company_name = glom(
        sv_ul,
        Coalesce(
            ("СвНаимЮЛ", "СвНаимЮЛСокр", "@attributes", "НаимСокр"),
            ("СвНаимЮЛ", "@attributes", "НаимЮЛПолн"),
            default=NOT_FOUND,
        ),
    )

    return {
        "company_name": company_name,
        "inn": top_attrs.get("ИНН") or NOT_FOUND,
        "kpp": top_attrs.get("КПП") or NOT_FOUND,
        "ogrn": top_attrs.get("ОГРН") or NOT_FOUND,
        "status_text": glom(sv_ul, ("СвСтатус", "@attributes", "НаимСтатусЮЛ"), default=DEFAULT_STATUS),
        "address": _address_from_ul(sv_ul),
        "okved": _okved_from_ul(sv_ul),
        "director": _director_from_ul(sv_ul),
        "raw_data": raw_data if isinstance(raw_data, dict) else {},
    }
