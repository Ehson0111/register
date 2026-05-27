# Развёртывание CRM (Docker)

Инструкция для локального и серверного запуска всего проекта через Docker Compose.

## Требования

- **Docker Desktop** (Windows/macOS) или Docker Engine + Compose (Linux)
- **Git** — клонирование репозитория
- Свободные порты: `3000`, `8000`, `8004`–`8012`, `8025`, `9100`, `9101`

Рекомендуется включить BuildKit (ускоряет сборку):

```powershell
$env:DOCKER_BUILDKIT = "1"
$env:COMPOSE_DOCKER_CLI_BUILD = "1"
```

Можно скопировать переменные из файла `.env.docker` в `.env` в корне проекта.

---

## 1. Клонирование и переход в каталог

```powershell
git clone <url-репозитория> crm
cd crm
```

---

## 2. Сборка образов

Сборка выполняется в два шага: сначала общий Python-образ с зависимостями, затем все сервисы.

**Windows (PowerShell):**

```powershell
.\scripts\docker-build.ps1
```

**Linux / macOS:**

```bash
chmod +x scripts/docker-build.sh
./scripts/docker-build.sh
```

**Вручную:**

```powershell
docker compose build django-base
docker compose build user-service contact-service calendar marketing documents applications chat-service payments api-gateway tgbots frontend
```

Повторная сборка после изменения только кода сервиса (без смены `docker/django-base/requirements.txt`):

```powershell
docker compose build contact-service
```

---

## 3. Запуск

```powershell
docker compose up
```

Фоновый режим:

```powershell
docker compose up -d
```

Остановка:

```powershell
docker compose down
```

---

## 4. Адреса после запуска

| Сервис | URL |
|--------|-----|
| **Веб-интерфейс (Vue)** | http://localhost:3000 |
| **API Gateway** | http://localhost:8000 |
| **MailHog (тестовая почта)** | http://localhost:8025 |
| **MinIO Console** | http://localhost:9101 (логин `minioadmin` / `minioadmin`) |

Вход в CRM — через фронтенд на порту **3000**. Запросы к API идут через gateway на **8000**.

---

## 5. Первый запуск

При старте контейнеры автоматически выполняют `migrate` для своих БД (SQLite в общей папке `databases/` на хосте).

Создайте пользователя-администратора (если ещё нет) через Django в user-service:

```powershell
docker compose exec user-service python manage.py createsuperuser
```

Либо зарегистрируйтесь через UI, если включена регистрация.

---

## 6. Переменные окружения (важно для продакшена)

В `docker-compose.yml` заданы значения по умолчанию для разработки. Перед выкладкой на сервер задайте секреты через `.env` рядом с `docker-compose.yml`, например:

```env
TELEGRAM_BOT_TOKEN=...
TELEGRAM_BRIDGE_SECRET=...
ONEC_BRIDGE_SECRET=...
YANDEX_EMAIL=...
YANDEX_PASSWORD=...
PUBLIC_PAYMENTS_BASE_URL=https://your-domain.com
```

В `docker-compose.yml` для чувствительных полей уже используется синтаксис `${VAR:-default}` — подставьте свои значения в `.env`.

**Не коммитьте** `.env` с паролями в Git.

---

## 7. Полезные команды

Просмотр логов всех сервисов:

```powershell
docker compose logs -f
```

Логи одного сервиса:

```powershell
docker compose logs -f api-gateway
docker compose logs -f payments
```

Пересобрать и перезапустить один сервис:

```powershell
docker compose up -d --build documents
```

Команда внутри контейнера:

```powershell
docker compose exec user-service python manage.py migrate
```

---

## 8. Продакшен (кратко)

Текущий `docker-compose.yml` ориентирован на **разработку** (`runserver`, Vite dev server). Для боевого сервера обычно:

1. Собирают production-образ фронтенда (`npm run build` + nginx).
2. Заменяют `runserver` на **gunicorn/uvicorn** в Django-сервисах.
3. Выносят SQLite на **PostgreSQL**, MinIO — на отдельный S3/MinIO-кластер.
4. Ставят **reverse proxy** (nginx/Caddy) с HTTPS перед gateway и фронтом.
5. Убирают MailHog, настраивают реальный SMTP.

Структура микросервисов и gateway при этом не меняется — меняется только способ запуска процессов и хранилища.

---

## 9. Устранение проблем

**Ошибка `crm-django-base:latest: pull access denied`** — сначала соберите базовый образ:

```powershell
docker compose build django-base
```

Затем снова `.\scripts\docker-build.ps1`.

**Порт занят** — измените маппинг в `docker-compose.yml`, например `"3001:3000"` для frontend.

**Пустая БД** — проверьте, что папка `databases/` смонтирована и миграции прошли без ошибок в логах.
