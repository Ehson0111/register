# Как отправляются запросы в CRM

Документ описывает, как фронтенд и внешние клиенты обращаются к API проекта.  
Цель — понять цепочку «кто куда стучится» без чтения всего кода.

---

## 1. Общая схема

```
Браузер (Vue, localhost:3000)
        │
        ├─► /api/... ──────────────► API Gateway (localhost:8000)
        │                                    │
        │                                    ├─► user-service      :8004
        │                                    ├─► contact-service   :8005
        │                                    ├─► marketing         :8007
        │                                    ├─► documents         :8008
        │                                    ├─► chat-service
        │                                    ├─► payments
        │                                    └─► calendar/tasks
        │
        └─► localhost:8009/api/applications/... ──► applications-service (напрямую)
```

**Важно:**

- Большинство CRM-запросов идут через **шлюз** `http://localhost:8000/api/...`.
- Сервис **заявок** (`applications`) фронт вызывает **напрямую** на порт `8009` — он не проксируется через gateway.
- В dev-режиме Vite проксирует `/api` на gateway (`vite.config.ts` → `VITE_PROXY_TARGET`).

---

## 2. Авторизация (JWT)

### Вход

```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "manager",
  "password": "пароль"
}
```

**Ответ:**

```json
{
  "access": "eyJ...",
  "refresh": "eyJ..."
}
```

### Обновление токена

```http
POST /api/auth/refresh/
Content-Type: application/json

{
  "refresh": "eyJ..."
}
```

### Как фронт подставляет токен

Файл `frontend/vue-project/src/services/api.js`:

1. При каждом запросе в заголовок добавляется `Authorization: Bearer <access_token>` (из Pinia store).
2. При ответе `401/403` фронт пробует `POST /api/auth/refresh/`, затем повторяет исходный запрос.
3. Если refresh не удался — пользователь разлогинивается и перенаправляется на `/login`.

Сервис заявок (`applications.ts`) читает токен из `localStorage.getItem("access_token")` и тоже кладёт его в `Authorization`.

---

## 3. Contact Service (контакты, услуги, сделки, аналитика)

Базовый путь через шлюз: `http://localhost:8000/api/`

Все эндпоинты ниже требуют роль менеджера и заголовок `Authorization: Bearer <token>`.

### Контакты

| Действие | Метод | URL | Тело (JSON) |
|----------|-------|-----|-------------|
| Список | GET | `/contacts/` | — |
| Поиск | GET | `/contacts/?search=иванов` | — |
| Детали | GET | `/contacts/{id}/` | — |
| Создать | POST | `/contacts/add/` | см. ниже |
| Изменить | PUT | `/contacts/{id}/` | поля контакта |
| Удалить | DELETE | `/contacts/remove/{id}/` | — |
| Для выпадающего списка | GET | `/contacts/select/` | — |
| Загрузить реквизиты по ИНН | POST | `/contacts/{id}/load-company-data/` | `{"inn": "7707083893"}` |

**Создание контакта** (в т.ч. при одобрении заявки):

```http
POST /api/contacts/add/
Authorization: Bearer <token>
Content-Type: application/json

{
  "first_name": "Петр",
  "last_name": "Лушников",
  "email": "petr@example.ru",
  "phone": "+7 999 123-45-67",
  "inn": "7707083893",
  "company": "ООО ТехноЛидер",
  "position": "Руководитель отдела продаж",
  "address": "г. Москва, ул. Тверская, 12",
  "status": "lead",
  "notes": "Создано из заявки"
}
```

**Ответ (201):**

```json
{
  "message": "Контакт успешно создан",
  "contact": {
    "id": 42,
    "first_name": "Петр",
    "last_name": "Лушников",
    "inn": "7707083893",
    ...
  }
}
```

### Услуги

| Действие | Метод | URL |
|----------|-------|-----|
| Список | GET | `/services/` |
| Создать | POST | `/services/add/` |
| Для select | GET | `/services/select/` |

### Сделки

| Действие | Метод | URL |
|----------|-------|-----|
| Список | GET | `/deals/` |
| Создать | POST | `/deals/add/` |
| Сменить статус | POST | `/deals/{id}/change-status/` |
| Сменить этап | POST | `/deals/{id}/change-stage/` |

**Создание сделки** (при одобрении заявки):

```http
POST /api/deals/add/
Content-Type: application/json

{
  "title": "Внедрение CRM-системы",
  "description": "Требуется подключить API...",
  "contact": 42,
  "service": 1,
  "amount": 45000,
  "status": "new",
  "expected_close_date": "2026-06-19"
}
```

### Аналитика

Период задаётся query-параметрами:

| Вариант | Пример |
|---------|--------|
| Последние N дней | `?days=30` (0 = всё время) |
| Свой диапазон дат | `?date_from=2026-01-01&date_to=2026-06-01` |

Эндпоинты:

- `GET /contacts/analytics/overview/?days=90`
- `GET /contacts/analytics/top-contacts/?date_from=2026-01-01&date_to=2026-06-01`
- `GET /contacts/analytics/top-services/?days=365`
- `GET /contacts/analytics/deal-performance/?days=30`

### Аудит

- `GET /audit-trail/` — журнал действий менеджеров.

---

## 4. Applications Service (заявки с Яндекс.Форм)

Базовый URL: `http://localhost:8009/api/applications/`

В Docker переменная фронта: `VITE_APPLICATIONS_API_URL=http://localhost:8009/api/applications/`

| Действие | Метод | URL |
|----------|-------|-----|
| Список заявок | GET | `/` |
| Поиск | GET | `/?search=CRM` |
| Фильтр по статусу | GET | `/?is_processed=false` |
| Одна заявка | GET | `/{id}/` |
| Забрать из почты | POST | `/fetch_from_mail/` |
| Отметить обработанной | PATCH | `/{id}/` |
| Журнал одобрений | GET | `/audit_trail/` |

### Синхронизация из Яндекс.Почты

```http
POST http://localhost:8009/api/applications/fetch_from_mail/
Authorization: Bearer <token>
```

**Ответ:**

```json
{
  "total": 10,
  "new": 2,
  "duplicates": 8
}
```

При повторной синхронизации текст уже существующих заявок **обновляется**, если в письме более полный вариант (например, после доработки парсера HTML).

### Одобрение / отклонение заявки

```http
PATCH http://localhost:8009/api/applications/17/
Authorization: Bearer <token>
Content-Type: application/json

{
  "is_processed": true,
  "audit_actor": "Иван Менеджер",
  "audit_action": "approved"
}
```

`audit_action`: `approved` | `rejected` | `processed`

> Создание контакта и сделки при одобрении делает **фронт** двумя запросами в contact-service (см. раздел 5).

---

## 5. Сценарий: одобрение заявки (полная цепочка)

1. Менеджер нажимает «Забрать из почты»  
   → `POST :8009/api/applications/fetch_from_mail/`

2. Фронт загружает список  
   → `GET :8009/api/applications/`

3. Менеджер нажимает «Одобрить» на заявке #17  
   → `GET :8009/api/applications/17/` (полный текст письма)

4. Фронт парсит поля из текста (`applicationParser.ts`):

   | Поле в письме | Куда попадает |
   |---------------|---------------|
   | Фамилия, Имя | `first_name`, `last_name` контакта |
   | Компания | `company` |
   | **ИНН** | `inn` контакта |
   | Должность | `position` |
   | Адрес | `address` |
   | Почта | `email` |
   | Контакт | `phone` |
   | Услуга | поиск `service_id` по имени |
   | Сумма сделки | `amount` сделки |
   | Название сделки | `title` сделки |
   | Описание | `description` сделки |
   | Ожидаемая дата закрытия | `expected_close_date` |

5. Менеджер подтверждает в модалке  
   → `POST :8000/api/contacts/add/` (с полем `inn`)  
   → `POST :8000/api/deals/add/`  
   → `PATCH :8009/api/applications/17/` (`is_processed: true`, `audit_action: approved`)

6. Опционально: на карточке контакта  
   → `POST :8000/api/contacts/{id}/load-company-data/` — подтянуть реквизиты с egrul.org по ИНН.

---

## 6. User Service (пользователи)

Через шлюз `http://localhost:8000/api/`:

| Действие | Метод | URL |
|----------|-------|-----|
| Вход | POST | `/auth/login/` |
| Refresh | POST | `/auth/refresh/` |
| Профиль | GET | `/users/profile/` |
| Обновить профиль | PUT | `/users/profile/update/` |
| Регистрация | POST | `/users/register/` |

---

## 7. Marketing, Documents, Payments

Эти сервисы тоже идут через gateway:

- Маркетинг: `/api/marketing/...` → marketing-service (:8007)
- Документы: `/api/documents/...` → documents-service
- Платежи: `/api/payment/...` → payments-service

Подробные примеры тел запросов — в `readme.md` (разделы Marketing, Documents).

---

## 8. Формат письма Яндекс.Формы

Типичное тело заявки:

```
Поступила новая заявка.

ID ответа:  2435063314
Фамилия:  Лушников
Имя: Петр
Должность:Руководитель отдела продаж
Адрес: г. Москва, ул. Тверская, д. 12
Компания:ООО «ТехноЛидер»
ИНН: 7707083893
Название сделки: Внедрение CRM-системы
Контакт:  +7 999 123-45-67
Услуга: Настройка и интеграция CRM
Сумма сделки: 45000
Почта: petr@example.ru
Ожидаемая дата закрытия: 2026-06-19

Описание:
Требуется подключить API...
```

Парсер учитывает:

- тему письма + тело;
- отсутствие пробела после двоеточия (`Должность:Директор`);
- таблицы из HTML (после конвертации в текст);
- игнорирование заглушек формы (`ИНН: ИНН`, `Фамилия: Фамилия`).

ИНН нормализуется до 10 или 12 цифр.

---

## 9. Примеры curl

### Логин

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"manager\",\"password\":\"pass\"}"
```

### Создать контакт с ИНН

```bash
curl -X POST http://localhost:8000/api/contacts/add/ \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"first_name\":\"Петр\",\"last_name\":\"Лушников\",\"email\":\"p@ex.ru\",\"phone\":\"+7999\",\"inn\":\"7707083893\",\"company\":\"ООО Тест\",\"status\":\"lead\",\"position\":\"\",\"address\":\"\",\"notes\":\"\"}"
```

### Забрать заявки из почты

```bash
curl -X POST http://localhost:8009/api/applications/fetch_from_mail/ \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

### Аналитика за период

```bash
curl "http://localhost:8000/api/contacts/analytics/overview/?days=90" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

```bash
curl "http://localhost:8000/api/contacts/analytics/overview/?date_from=2026-01-01&date_to=2026-06-01" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

---

## 10. Где смотреть код на фронте

| Модуль | Файл |
|--------|------|
| HTTP-клиент + JWT | `frontend/vue-project/src/services/api.js` |
| Контакты, сделки, аналитика | `frontend/vue-project/src/services/contactService.ts` |
| Заявки | `frontend/vue-project/src/services/applications.ts` |
| Парсер полей заявки | `frontend/vue-project/src/utils/applicationParser.ts` |
| UI одобрения | `frontend/vue-project/src/views/manager/Applications.vue` |
| Авторизация | `frontend/vue-project/src/services/auth.js` |

---

*Документ актуален для локального запуска через `docker-compose`. Порты могут отличаться, если вы меняли `docker-compose.yml`.*
