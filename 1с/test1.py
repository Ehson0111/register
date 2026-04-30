resp = session.get(f"{BASE_URL}/$metadata")
print(resp.status_code)
# Можно сохранить или распарсить XML