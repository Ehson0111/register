дипломный проект 09.03.2026

CRM-проект на микросервисной архитектуре
========================================
🐳 Docker-команды
Просмотр логов






## 🛠️ Стек технологий

### Бэкенд
- **Django REST Framework**
- **JWT** 
- **SQLite**  
- **MinIO SDK** (S3)
- **SMTP** (Yandex / MailHog)

### Фронтенд
- **Vue 3** + **TypeScript**
- **Pinia** (стейт-менеджмент)
- **Vue Router**
- **Axios** (интерсепторы, авто-рефреш)
- **Tailwind CSS**

### cтруктура
- **Docker** + **Docker Compose**
- **MinIO** (S3-совместимое хранилище)
- **MailHog** (тестовый SMTP)


```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f user-service
docker-compose logs -f api-gateway
Выполнить команду в контейнере
bash
docker-compose exec user-service bash
docker-compose exec api-gateway python manage.py migrate
Пересобрать сервис
bash
docker-compose up -d --build documents
```
### Сервисы и порты

Все сервисы по умолчанию поднимаются на следующих адресах:

- **API Gateway**: `http://localhost:8000` — единая точка входа (`/api/...`)
- **User Service**: `http://localhost:8004` — аутентификация, пользователи, профили
- **Contact Service**: `http://localhost:8005` — контакты, услуги, сделки
- **Calendar Service**: `http://localhost:8006` — задачи и календарь менеджеров
- **Marketing Service**: `http://localhost:8007` — шаблоны и рассылки (email/SMS)
- **Frontend (Vue)**: `http://localhost:3000` — веб‑интерфейс CRM

---

### Маркетинговый сервис (marketing)

#### Создание шаблона (пример payload)

Эндпоинт сервиса маркетинга (внутренний):

- `POST http://localhost:8007/api/send-individual/`

Требуются заголовки:

- `Authorization: Bearer <token>`
- `Content-Type: application/json`

Пример тела запроса для создания шаблона:

```json
{
  "name": "Приветственное письмо",
  "template_type": "email",
  "subject": "Добро пожаловать, {name}!",
  "content": "Уважаемый {name}, рады приветствовать вас...",
  "variables": ["name", "company"],
  "description": "Шаблон для новых клиентов"
}
```

#### Индивидуальная отправка через API Gateway

- `POST http://localhost:8000/api/marketing/send-individual/`

Пример 1 (простая отправка по шаблону):

```json
{
  "template_id": 4,
  "recipient_id": 11
}
```

Пример 2 (с переопределением переменных шаблона):

```json
{
  "template_id": 4,
  "recipient_id": 11,
  "variables": {
    "offer": "СКИДКА20",
    "company": "ООО \"Промышленность\"",
    "new_email": "newemail@example.com",
    "personal_message": "Это сообщение специально для вас!"
  }
}
```

#### Массовая отправка

- `POST http://localhost:8000/api/marketing/send-campaign/`

```json
{
  "template_id": 1,
  "subject": "Скидка 20% для вас",
  "content": "Специальное предложение только для вас!",
  "variables": {
    "offer": "СКИДКА20",
    "company": "ООО \"Промышленность\""
  },
  "recipient_ids": [10, 11],
  "campaign_name": "Декабрьская акция"
}
```

#### Получение списка шаблонов

- `GET http://localhost:8000/api/marketing/templates/`

Ответ (сокращённый пример):

```json
[
  {
    "id": 4,
    "name": "Спасибо за вашу лояльность",
    "template_type": "email",
    "template_type_display": "Email",
    "subject": "",
    "content": "Дорогой(ая) {name}, команда {company} искренне благодарит вас за доверие и сотрудничество.",
    "variables": ["name", "company"],
    "description": "Шаблон для выражения общей благодарности клиенту.",
    "is_active": true
  },
  {
    "id": 1,
    "name": "Приветственное письмо",
    "template_type": "email",
    "template_type_display": "Email",
    "subject": "Добро пожаловать, {name}!",
    "content": "Уважаемый {name}, рады приветствовать вас в нашей компании {company}.",
    "variables": ["name", "company"],
    "description": "Шаблон для новых клиентов",
    "is_active": true
  }
]
```

#### Быстрое сообщение (quick message)

- `POST http://localhost:8000/api/marketing/send-quick-message/`

Пример:

```json
{
  "message": "Уважаемый клиент! Наш офис будет закрыт с 1 по 8 марта. Приносим извинения за неудобства.",
  "subject": "Уведомление о графике работы",
  "recipient_ids": [10, 11, 12, 13],
  "campaign_name": "Уведомление о выходных"
}
```

#### Статистика по кампаниям

- `GET http://localhost:8000/api/marketing/campaigns/stats/`

Пример ответа (сокращённо):

```json
{
  "total_campaigns": 106,
  "total_recipients": 127,
  "total_sent": 24,
  "recent_campaigns": 103,
  "recent_recipients": 124,
  "recent_sent": 21,
  "by_type": {
    "individual": 89,
    "bulk": 17
  },
  "by_status": {
    "draft": 0,
    "sent": 14,
    "sending": 87,
    "failed": 5
  }
}
```

#### История кампаний

- `GET http://localhost:8000/api/marketing/campaigns/`

Возвращает список кампаний с подробной информацией о получателях и статусах доставки.

---

### MinIO (хранилище документов)

Запуск MinIO в Docker:

```bash
docker run -d -p 9000:9000 -p 9001:9001 ^
  --name minio ^
  -e "MINIO_ROOT_USER=minioadmin" ^
  -e "MINIO_ROOT_PASSWORD=minioadmin" ^
  -v minio-data:/data ^
  quay.io/minio/minio server /data --console-address ":9001"
```

Консоль MinIO будет доступна по адресу `http://localhost:9001`.

---

### Документы (Documents Service через API Gateway)

#### Загрузка документа

- `POST http://localhost:8000/api/documents/upload/`

Формат `multipart/form-data`:

- `client_id`: идентификатор клиента (текст/число)
- `file`: прикрепляемый файл

#### Список документов клиента

- `GET http://localhost:8000/api/documents/<client_id>/list/`

Пример:

- `GET http://localhost:8000/api/documents/10/list/`

#### Скачивание документа

- `GET http://localhost:8000/api/documents/download/<id>/`

Пример:

- `GET http://localhost:8000/api/documents/download/1/`

 
