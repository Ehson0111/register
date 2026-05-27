# CRM Project: функции и функциональность системы

## Карта проекта

- `api-gateway` — единая точка входа API (`/api/*`), проксирует запросы в микросервисы.
- `services/user-service` — пользователи, роли, JWT-аутентификация, регистрация/верификация, профиль, управление командой.
- `services/contact_service` — контакты, услуги, сделки, стадии сделок, клиентский кабинет, аналитика, аудит.
- `services/calendar` — календарь и задачи менеджера.
- `services/marketing` — шаблоны, кампании, рассылки, история и статистика коммуникаций.
- `services/documents` — документы клиентов (загрузка, хранение, скачивание через MinIO/S3).
- `services/applications` — заявки из почты, аудит обработки, API для почтового модуля.
- `services/chatService` — чаты менеджеров, AI-чат, Telegram bridge.
- `services/payments` — счета/инвойсы, платежи YooKassa, синхронизация с 1С.
- `services/tgbots` — Telegram бот-поллер для интеграции с chat-service.
- `frontend/vue-project` — Vue 3 SPA для менеджера и клиента.
- `docker-compose.yml` — оркестрация всех сервисов и инфраструктуры.

## Бизнес-функциональность по модулям

### 1) Пользователи и доступ

- Регистрация клиента с OTP/email-верификацией.
- Логин и refresh JWT.
- Сброс пароля через OTP.
- Просмотр и обновление профиля.
- Управление пользователями команды (список, создание, смена ролей, активация/деактивация) с ограничениями по роли.

### 2) CRM-ядро: контакты, услуги, сделки

- Полный CRUD контактов.
- Поиск и фильтрация контактов, упрощенные селекты для UI.
- Обогащение карточки компании по ИНН через внешний источник (`egrul.org`).
- CRUD услуг, мягкое удаление/деактивация.
- CRUD сделок, смена статусов и стадий.
- Статистика по сделкам контактов и состоянию воронки.
- Клиентский кабинет: профиль, просмотр своих сделок/услуг, создание заявки.
- Аудит действий по основным сущностям CRM.

### 3) Аналитика CRM

- Сводные показатели по контактам, сделкам, услугам и выручке.
- Конверсия, тренды по времени, top-контакты и top-услуги.
- Отчеты по диапазонам вероятностей и периодам.

### 4) Календарь и задачи

- CRUD задач менеджера.
- Выборки: на сегодня, предстоящие, просроченные.
- Представления по диапазону дат и по месяцу.
- Дневной и месячный режимы.
- Статистика задач по статусам/приоритетам.

### 5) Маркетинг и коммуникации

- CRUD шаблонов сообщений (email/sms).
- Дублирование шаблонов.
- Создание и ведение кампаний.
- Массовые, индивидуальные и быстрые рассылки.
- История отправок и статистика.
- Персонализация данных сообщений из клиентских данных.

### 6) Документы

- Загрузка документов клиента.
- Просмотр списка документов по клиенту.
- Скачивание документов (streaming response).

### 7) Заявки и почтовый контур

- Импорт заявок из Яндекс.Почты (IMAP).
- CRUD заявок с поиском/фильтрами.
- Пометка и аудит обработки заявок (processed/approved/rejected).
- Почтовые операции: папки, синхронизация, просмотр писем, отправка.

### 8) Чаты и AI

- Комнаты, участники, сообщения.
- AI-комната менеджера.
- Сброс AI-контекста по комнате.
- Интеграция Telegram как канал входящих/исходящих сообщений.

### 9) Платежи и 1С

- Выставление счета по выигранной сделке.
- Генерация ссылки на оплату.
- Оплата через YooKassa и webhook-обработка статусов.
- Синхронизация счета и оплаты с 1С.
- Retry-механизм при ошибках внешней синхронизации.

### 10) Workflow-автоматизация

- Каталог/конструктор workflow.
- Узлы графа: `start`, `condition`, `action`.
- Триггеры: `manual`, `user_created`, `deal_status_changed`.
- Действия: `send_email`, `webhook`, `log`.
- Ручной запуск и запуск через event endpoint (с секретом).
- Хранение execution-логов и итогового статуса выполнения.

## Технические функции системы

- Микросервисная архитектура на Django/DRF.
- API Gateway как единая внешняя точка.
- JWT и role-based authorization.
- Vue 3 SPA (Pinia, Router, Axios interceptors, авто-refresh токена).
- Хранилище документов через MinIO (S3-compatible).
- Интеграции с SMTP/IMAP, Telegram, YooKassa, 1С, AI endpoint.
- Фоновые задачи (management commands, worker-контейнеры, loop-процессы).
- Docker Compose для локального/интеграционного запуска контуров.

## Роли и доступы

- `admin`:
  - полный staff-доступ;
  - управление пользователями команды;
  - доступ к manager-функционалу.
- `manager`:
  - доступ к manager-порталу;
  - операции по CRM, календарю, маркетингу, чатам, документам, аналитике.
- `client`:
  - доступ к client-порталу;
  - собственный профиль, сделки, услуги, клиентская заявка.
- Доп. технические роли в чат-домене:
  - `telegram_client`;
  - `ai_assistant`.

## Основные маршруты frontend

- Публичные: `/login`, `/register`, `/forgot-password`.
- Менеджер: `/manager/dashboard`, `/manager/contacts`, `/manager/contacts/:id`, `/manager/deals`, `/manager/deals-kanban`, `/manager/deals/new`, `/manager/deals/:id`, `/manager/services`, `/manager/calendar`, `/manager/analytics`, `/manager/marketing`, `/manager/documents`, `/manager/chats`, `/manager/emails`, `/manager/meetings`, `/manager/applications`, `/manager/profile`, `/manager/users`.
- Клиент: `/client/dashboard`, `/client/deals`, `/client/services`, `/client/profile`.

## Основные маршруты backend (через gateway и сервисы)

- Auth/users: `/api/auth/*`, `/api/users/*`.
- Contacts/services/deals/client: `/api/contacts/*`, `/api/services/*`, `/api/deals/*`, `/api/deal-stages/*`, `/api/client/*`, `/api/contacts/analytics/*`, `/api/audit-trail/*`.
- Calendar: `/api/tasks/*`, `/api/tasks/today`, `/api/tasks/upcoming`, `/api/tasks/overdue`, `/api/tasks/stats`, `/api/tasks/by_date_range`, `/api/tasks/by_month`, `/api/daily`, `/api/monthly`.
- Marketing: `/api/marketing/templates/*`, `/api/marketing/campaigns/*`, `/api/marketing/campaigns/stats`, `/api/marketing/send-campaign`, `/api/marketing/send-quick-message`.
- Documents: `/api/documents/upload`, `/api/documents/<client_id>/list`, `/api/documents/download/<id>`.
- Chat: `/api/chat/rooms/*`, `/api/chat/rooms/ai`, `/api/chat/rooms/<room_id>/ai/reset`, `/api/chat/rooms/<room_id>/messages`, `/api/chat/telegram/inbound`, `/api/chat/telegram/outbound`.
- Payments: `/api/payment/deals/<deal_id>/invoice`, `/api/payment/invoices/<invoice_id>/retry-sync`, `/api/payment/webhook`, плюс web-страницы оплаты `/payment/pay/<invoice_id>`, `/payment/result/<invoice_id>`.
- Applications/mail: `/api/applications/*`, `/api/applications/fetch_from_mail`, `/api/mail/*`.

## Интеграции и фоновые процессы

- Внешние интеграции:
  - YooKassa;
  - 1С (sync/retry);
  - MinIO/S3;
  - Yandex IMAP/SMTP;
  - Telegram Bot API;
  - AI inference endpoint;
  - `egrul.org` для данных по ИНН.
- Фоновые задачи:
  - retry-воркер платежей (`process_invoice_retries --loop`);
  - импорт почты в заявки (`fetch_mail`);
  - thread-based отправки рассылок;
  - Telegram polling bot.

## Ограничения обзора

- Это статический обзор по коду и маршрутам без запуска end-to-end сценариев.
- Часть логики может быть незавершенной или зависеть от окружения/секретов.
- Для 100% подтверждения функционала нужен прогон интеграционных сценариев и smoke-тестов по сервисам.
