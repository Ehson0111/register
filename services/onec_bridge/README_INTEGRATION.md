# Интеграция CRM с 1С - Bridge Сервис v2.0

## Обзор

Новая версия bridge сервиса обеспечивает интеграцию CRM с 1С для финансовых операций:
- Создание счетов в 1С по сделкам CRM
- Регистрация оплат через YooKassa
- Автоматический перезапуск w3wp.exe процессов
- Retry-механизм для надежности

## Архитектура

```
CRM (Payments Service) -> Bridge Service -> 1C OData
```

### Новые Endpoints

1. **POST /invoice/create** - Создание счета в 1С
2. **POST /payment/register** - Регистрация оплаты
3. **POST /invoke** - Legacy совместимость

## Запуск и настройка

### 1. Настройка переменных окружения

```bash
# Bridge сервис
ONEC_BRIDGE_HOST=0.0.0.0
ONEC_BRIDGE_PORT=8013
ONEC_BRIDGE_SECRET=your_secret_key

# 1С подключение
ONEC_BASE_URL=http://127.0.0.1/1c/odata/standard.odata/
ONEC_USERNAME=your_username
ONEC_PASSWORD=your_password

# Перезапуск 1С
ONEC_RESTART_EACH_REQUEST=true
ONEC_PROCESS_NAME=w3wp
ONEC_APP_POOL_NAME=DefaultAppPool
ONEC_RESTART_COMMAND=

# Health check
ONEC_USE_HEALTHCHECK=true
ONEC_HEALTHCHECK_PATH=$metadata
ONEC_HEALTH_TIMEOUT_SECONDS=45
ONEC_HEALTHCHECK_TIMEOUT_SECONDS=10
ONEC_HEALTHCHECK_INTERVAL_SECONDS=2

# Retry механизм
ONEC_LIMIT_RETRY_ATTEMPTS=3
ONEC_LIMIT_RETRY_DELAY_SECONDS=1.5
```

### 2. Запуск Bridge сервиса

```bash
cd d:\django\crm\services\onec_bridge
python server.py
```

### 3. Настройка Payments сервиса

В `config/settings.py` убедитесь что:

```python
ONEC_TRANSPORT_MODE = "bridge"
ONEC_BRIDGE_URL = "http://127.0.0.1:8013/invoke"
ONEC_BRIDGE_SECRET = "your_secret_key"
```

## Тестирование с Postman

1. Импортируйте коллекцию `postman_tests.json`
2. Установите переменные:
   - `bridge_url`: http://127.0.0.1:8013
   - `bridge_secret`: ваш секретный ключ

### Тест создания счета

```json
POST /invoice/create
{
  "crm_invoice_id": "12345",
  "crm_deal_id": "67890", 
  "customer_name": "Иванов Иван Иванович",
  "customer_email": "ivanov@example.com",
  "service_name": "Консультационная услуга",
  "amount": "15000.00",
  "comment": "Тестовый счет"
}
```

### Тест регистрации оплаты

```json
POST /payment/register
{
  "crm_invoice_id": "12345",
  "onec_document_id": "00000000-0000-0000-0000-000000000001",
  "yookassa_payment_id": "yp_1234567890",
  "amount": "15000.00",
  "payment_date": "2026-04-22T23:30:00",
  "payment_method": "yookassa"
}
```

## Бизнес-процесс

1. **Создание счета**:
   - Менеджер в CRM закрывает сделку со статусом "won"
   - Нажимает "Выставить счет"
   - Payments сервис вызывает bridge `/invoice/create`
   - Bridge перезапускает w3wp.exe (если настроено)
   - Создает документ "СчетПокупателю" в 1С
   - Возвращает ID и номер документа

2. **Оплата**:
   - Клиент оплачивает счет через YooKassa
   - YooKassa отправляет webhook в payments сервис
   - Payments сервис вызывает bridge `/payment/register`
   - Bridge перезапускает w3wp.exe
   - Создает документ "ОплатаПоСчету" в 1С
   - Обновляет статус счета на "Оплачен"

## Структура данных в 1С

### Справочники:
- Организации
- Клиенты  
- Услуги

### Документы:
- СчетПокупателю
- ОплатаПоСчету

### Поля счета:
- Number (номер)
- Date (дата)
- CRM_Invoice_ID (ID счета из CRM)
- CRM_Deal_ID (ID сделки из CRM)
- Organization_Key (организация)
- Customer (клиент)
- Customer_Email (email клиента)
- Status (статус: НеОплачен/Оплачен)
- Amount (сумма)
- Comment (комментарий)
- Services (табличная часть с услугами)

### Поля оплаты:
- Счет_Key (ссылка на счет)
- CRM_Payment_ID (ID платежа из CRM)
- YooKassaPaymentID (ID платежа YooKassa)
- Amount (сумма оплаты)
- PaymentDate (дата оплаты)
- PaymentMethod (способ оплаты)
- Comment (комментарий)

## Логирование

Bridge сервис пишет детальные логи:
- Уровень логирования (INFO, DEBUG, ERROR, WARNING)
- Временные метки с миллисекундами
- Все шаги выполнения операций
- Ошибки с детальной информацией

## Обработка ошибок

- **Connection limit errors**: автоматический retry с экспоненциальным бэк-оффом
- **1С недоступна**: перезапуск и ожидание доступности
- **Ошибки валидации**: немедленный возврат ошибки
- **Network errors**: повторные попытки

## Мониторинг

- Health check endpoint для проверки доступности
- Детальные логи всех операций
- Метрики retry попыток
- Время выполнения операций

## Совместимость

- Поддержка legacy API через `/invoke`
- Обратная совместимость с существующими интеграциями
- Возможность постепенного перехода на новые endpoints
