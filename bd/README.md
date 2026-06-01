# Скрипты баз данных CRM

## Файлы

| Файл | Назначение |
|------|------------|
| `crm_sqlserver_schema.sql` | Создание **9 баз** Microsoft SQL Server — по одной на микросервис (аналог текущих SQLite) |

> Проект **продолжает работать на SQLite** в Docker. Этот скрипт только для отчёта, демонстрации в **SQL Server Management Studio** или будущей миграции — **ничего в коде не меняется**.

## Как выполнить в SSMS

1. Откройте **SQL Server Management Studio**, подключитесь к экземпляру (LocalDB, Express или полный SQL Server).
2. **Файл → Открыть →** `crm_sqlserver_schema.sql`
3. **Выполнить** (F5). Нужны права на `CREATE DATABASE`.
4. В обозревате объектов появятся базы `crm_user`, `crm_contact`, `crm_payments` и т.д.

## Соответствие SQLite → SQL Server

| SQLite (Docker `./databases/`) | База SQL Server |
|-------------------------------|-----------------|
| `user.db` | `crm_user` |
| `contact.db` | `crm_contact` |
| `calendar.db` | `crm_calendar` |
| `marketing.db` | `crm_marketing` |
| `documetns.db` | `crm_documents` |
| `chat_service.db` | `crm_chat` |
| `applications.db` | `crm_applications` |
| `payments.db` | `crm_payments` |
| `gateway.db` | `crm_gateway` (только служебные таблицы Django) |

## Примечание про MySQL

Если нужен именно **MySQL** (не SSMS), синтаксис отличается (`AUTO_INCREMENT`, обратные кавычки). Текущий скрипт — **T-SQL для Microsoft SQL Server**.
