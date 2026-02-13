Микросервисная CRM-система
Полноценная CRM с микросервисной архитектурой, контейнеризацией и S3-хранилищем. Всё поднимается одной командой.

🚀 БЫСТРЫЙ СТАРТ
1. Клонировать репозиторий
bash
git clone https://github.com/your-repo/crm-microservices.git
cd crm-microservices
2. Запустить одной командой
bash
docker-compose up --build
Готово! Через 2-3 минуты работают 8 сервисов:

Frontend: http://localhost:3000

API Gateway: http://localhost:8000

MinIO Console: http://localhost:9101

MailHog: http://localhost:8025

3. Остановить
bash
docker-compose down
🏗️ АРХИТЕКТУРА
text
Клиент (Vue 3) → API Gateway (порт 8000) → Микросервисы
                                          ├── User Service (8004)
                                          ├── Contact Service (8005)
                                          ├── Calendar Service (8006)
                                          ├── Marketing Service (8007)
                                          └── Documents Service (8008) → MinIO (9100)
Сервисы и порты (доступны с хоста)
Сервис	Порт	Описание
Frontend	3000	Vue 3 + TypeScript + Pinia
API Gateway	8000	Единая точка входа
User Service	8004	Аутентификация, JWT, профили
Contact Service	8005	Контакты, сделки, услуги, аналитика
Calendar Service	8006	Задачи, календарь, статистика
Marketing Service	8007	Шаблоны, рассылки, кампании
Documents Service	8008	MinIO S3, документы клиентов
MinIO Console	9101	S3-хранилище файлов
MailHog	8025	Тестовый SMTP-сервер
🔐 АВТОРИЗАЦИЯ
JWT-токен передаётся в заголовке:

text
Authorization: Bearer <access_token>
Получить токен:

bash
POST http://localhost:8000/api/auth/login/
{
  "email": "manager@crm.ru",
  "password": "password123"
}
📋 API ЭНДПОИНТЫ (через Gateway)
👥 User Service (/api/auth/*, /api/users/*)
POST /api/auth/login/ — вход

POST /api/auth/refresh/ — обновление токена

POST /api/users/register/ — регистрация + OTP

GET /api/users/profile/ — профиль

📞 Contact Service (/api/contacts/*)
GET /api/contacts/ — список контактов

POST /api/contacts/add/ — создание контакта

GET /api/contacts/analytics/overview/ — общая статистика

GET /api/contacts/analytics/timeline/ — динамика продаж

GET /api/contacts/analytics/top-contacts/ — топ клиентов

GET /api/contacts/analytics/top-services/ — топ услуг

💼 Deals & Services (/api/deals/*, /api/services/*)
GET /api/deals/ — сделки

POST /api/deals/add/ — создание сделки

POST /api/deals/{id}/change-status/ — смена статуса

GET /api/services/ — услуги

POST /api/services/add/ — создание услуги

📅 Calendar (/api/tasks/*)
GET /api/tasks/ — все задачи

GET /api/tasks/today/ — задачи на сегодня

GET /api/tasks/upcoming/ — ближайшие 7 дней

GET /api/tasks/stats/ — статистика

POST /api/tasks/ — создать задачу

POST /api/tasks/{id}/toggle_complete/ — выполнить/вернуть

📧 Marketing (/api/marketing/*)
Шаблоны:

GET /api/marketing/templates/ — список шаблонов

POST /api/marketing/templates/ — создать шаблон

Рассылки:

POST /api/marketing/send-individual/ — индивидуальная

POST /api/marketing/send-campaign/ — массовая

POST /api/marketing/send-quick-message/ — быстрое сообщение

Статистика:

GET /api/marketing/campaigns/ — история кампаний

GET /api/marketing/campaigns/stats/ — общая статистика

📄 Documents (/api/documents/*)
POST /api/documents/upload/ — загрузить файл

GET /api/documents/{client_id}/list/ — список документов клиента

GET /api/documents/download/{id}/ — скачать файл

📊 ПРИМЕРЫ ЗАПРОСОВ
📧 Маркетинг — массовая рассылка
bash
POST http://localhost:8000/api/marketing/send-campaign/
Authorization: Bearer <token>
Content-Type: application/json

{
  "template_id": 1,
  "recipient_ids": [10, 11, 12],
  "variables": {
    "offer": "СКИДКА20",
    "company": "ООО Промышленность"
  },
  "campaign_name": "Декабрьская акция"
}
📄 Документы — загрузка файла
bash
POST http://localhost:8000/api/documents/upload/
Authorization: Bearer <token>
Content-Type: multipart/form-data

--form 'client_id=10'
--form 'file=@/path/to/document.pdf'
📊 Аналитика — общая статистика
bash
GET http://localhost:8000/api/contacts/analytics/overview/
Authorization: Bearer <token>
🐳 DOCKER-КОМАНДЫ
Просмотр логов
bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f user-service
docker-compose logs -f api-gateway
Выполнить команду в контейнере
bash
docker-compose exec user-service bash
docker-compose exec api-gateway python manage.py migrate
Пересобрать конкретный сервис
bash
docker-compose up -d --build documents
Очистка (удалить всё)
bash
docker-compose down -v
🔧 ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ
Все настройки вынесены в docker-compose.yml.
Для продакшена замените значения в environment:

yaml
environment:
  MINIO_ACCESS_KEY: "minioadmin"  # сменить!
  MINIO_SECRET_KEY: "minioadmin"  # сменить!
  EMAIL_HOST_PASSWORD: "your-real-password"
🧪 ТЕСТОВЫЕ ДАННЫЕ
Менеджер:

text
Email: manager@crm.ru
Пароль: manager123
Клиент:

text
Email: client@crm.ru  
Пароль: client123
MinIO:

text
Login: minioadmin
Password: minioadmin
Console: http://localhost:9101
MailHog (все письма):

text
Web: http://localhost:8025
SMTP: localhost:1025
🛠️ СТЕК ТЕХНОЛОГИЙ
Бэкенд
Python 3.11 + Django 5.2

Django REST Framework

JWT (Simple JWT)

PostgreSQL/SQLite (в dev)

MinIO SDK

SMTP (Yandex/MailHog)

Фронтенд
Vue 3 + TypeScript

Pinia (стейт-менеджмент)

Vue Router

Axios (интерсепторы, авто-рефреш)

Tailwind CSS

Chart.js

Инфраструктура
Docker + Docker Compose

MinIO (S3-совместимое хранилище)

MailHog (тестовый SMTP)

📁 СТРУКТУРА ПРОЕКТА
text
crm-microservices/
├── api-gateway/               # Единая точка входа
│   ├── apps/gateway/         # ProxyView, rate limiting
│   └── config/
├── services/
│   ├── user-service/         # Аутентификация, JWT
│   ├── contact_service/      # Контакты, сделки, аналитика
│   ├── calendar/             # Задачи менеджеров
│   ├── marketing/            # Шаблоны, рассылки
│   └── documents/            # MinIO, документы
├── frontend/
│   └── vue-project/          # Vue 3 + TypeScript
├── databases/                # SQLite файлы (dev)
└── docker-compose.yml
