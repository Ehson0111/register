## 2.1 Структура базы данных

В разработанной CRM-системе в качестве СУБД используется SQLite. Хранение данных организовано по микросервисному принципу: каждый сервис использует собственный файл базы данных. Такой подход уменьшает связанность модулей, упрощает сопровождение и локализует риски при изменениях.

Используемые базы данных:
- `user.db` - сервис пользователей и аутентификации;
- `contact.db` - сервис контактов и сделок;
- `calendar.db` - сервис календаря;
- `marketing.db` - сервис маркетинга и рассылок;
- `documetns.db` - сервис документов;
- `applications.db` - сервис заявок;
- `gateway.db` - API-шлюз.

### Что означает «структура хранения данных»

Под структурой хранения данных в проекте понимается:
1. набор таблиц (сущностей), в которых сохраняются данные;
2. состав атрибутов каждой таблицы (тип, обязательность, ограничения);
3. связи между таблицами (1:1, 1:M);
4. правила целостности (PK, FK, `unique`, `unique_together`, индексы);
5. способ межсервисной интеграции (часть связей хранится как `*_id` без FK между разными БД, с проверкой через API).

Иными словами, структура хранения данных описывает, **где именно лежат данные, в каком формате, и как они связаны между собой**.

Ниже приведены атрибуты прикладных таблиц проекта.

### Таблица 1 - Атрибуты `User` (`user.db`)

| Название атрибута | Тип | Null | Комментарий |
|---|---|---|---|
| id | BigAutoField | Нет | Первичный ключ |
| email | EmailField | Нет | Уникальный email пользователя |
| first_name | CharField(30) | Нет | Имя |
| last_name | CharField(150) | Нет | Фамилия |
| role | CharField(10) | Нет | Роль: manager/client |
| username | CharField | Нет | Логин Django |
| password | CharField | Нет | Хеш пароля |
| is_active | BooleanField | Нет | Активность учетной записи |
| is_staff | BooleanField | Нет | Признак сотрудника |
| is_superuser | BooleanField | Нет | Права администратора |
| date_joined | DateTimeField | Нет | Дата регистрации |
| last_login | DateTimeField | Да | Последний вход |

### Таблица 2 - Атрибуты `UserProfile` (`user.db`)

| Название атрибута | Тип | Null | Комментарий |
|---|---|---|---|
| id | BigAutoField | Нет | Первичный ключ |
| user_id | OneToOneField(User) | Нет | Профиль конкретного пользователя (1:1) |
| phone | CharField(20) | Да | Телефон |
| address | TextField | Да | Адрес |
| date_of_birth | DateField | Да | Дата рождения |
| created_at | DateTimeField | Нет | Дата создания |
| updated_at | DateTimeField | Нет | Дата изменения |

### Таблица 3 - Атрибуты `EmailOTP` (`user.db`)

| Название атрибута | Тип | Null | Комментарий |
|---|---|---|---|
| id | BigAutoField | Нет | Первичный ключ |
| email | EmailField | Нет | Email для подтверждения |
| purpose | CharField(20) | Нет | Назначение кода: register/reset |
| code | CharField(6) | Нет | OTP-код |
| created_at | DateTimeField | Нет | Дата создания |
| expires_at | DateTimeField | Нет | Время окончания действия |
| used | BooleanField | Нет | Признак использования кода |
| attempts | PositiveIntegerField | Нет | Количество попыток ввода |

### Таблица 4 - Атрибуты `Contact` (`contact.db`)

| Название атрибута | Тип | Null | Комментарий |
|---|---|---|---|
| id | BigAutoField | Нет | Первичный ключ |
| first_name | CharField(100) | Нет | Имя контакта |
| last_name | CharField(100) | Нет | Фамилия контакта |
| email | EmailField | Нет | Email контакта |
| phone | CharField(20) | Да | Телефон |
| created_at | DateTimeField | Нет | Дата создания |
| status | CharField(10) | Нет | Статус: lead/client/partner |
| company | CharField(200) | Да | Компания |
| position | CharField(100) | Да | Должность |
| address | TextField | Да | Адрес |
| notes | TextField | Да | Примечания |

Ограничение: `unique_together(email, phone)`.

### Таблица 5 - Атрибуты `Service` (`contact.db`)

| Название атрибута | Тип | Null | Комментарий |
|---|---|---|---|
| id | BigAutoField | Нет | Первичный ключ |
| name | CharField(200) | Нет | Название услуги |
| description | TextField | Да | Описание услуги |
| price | DecimalField(10,2) | Нет | Стоимость |
| duration_days | IntegerField | Нет | Длительность в днях |
| is_active | BooleanField | Нет | Доступность услуги |
| created_at | DateTimeField | Нет | Дата создания |

### Таблица 6 - Атрибуты `Deal` (`contact.db`)

| Название атрибута | Тип | Null | Комментарий |
|---|---|---|---|
| id | BigAutoField | Нет | Первичный ключ |
| contact_id | ForeignKey(Contact) | Нет | Связанный контакт |
| service_id | ForeignKey(Service) | Нет | Связанная услуга |
| title | CharField(200) | Нет | Название сделки |
| description | TextField | Да | Описание |
| amount | DecimalField(10,2) | Нет | Сумма сделки |
| probability | IntegerField | Нет | Вероятность закрытия (0..100) |
| status | CharField(20) | Нет | Статус: new/in_progress/won/lost/on_hold |
| expected_close_date | DateField | Да | Плановая дата закрытия |
| actual_close_date | DateField | Да | Фактическая дата закрытия |
| created_at | DateTimeField | Нет | Дата создания |
| updated_at | DateTimeField | Нет | Дата изменения |

### Таблица 7 - Атрибуты `AuditTrail` (`contact.db`)

| Название атрибута | Тип | Null | Комментарий |
|---|---|---|---|
| id | BigAutoField | Нет | Первичный ключ |
| actor | CharField(255) | Да | Инициатор действия |
| action | CharField(64) | Нет | Тип действия |
| entity_type | CharField(64) | Нет | Тип сущности |
| entity_id | IntegerField | Да | ID сущности |
| metadata | JSONField | Нет | Дополнительные данные |
| created_at | DateTimeField | Нет | Время события |

### Таблица 8 - Атрибуты `CalendarTask` (`calendar.db`)

| Название атрибута | Тип | Null | Комментарий |
|---|---|---|---|
| id | BigAutoField | Нет | Первичный ключ |
| title | CharField(200) | Нет | Название задачи |
| description | TextField | Да | Описание |
| task_type | CharField(20) | Нет | Тип: meeting/task/reminder/deadline |
| date | DateField | Нет | Дата задачи |
| time | TimeField | Да | Время задачи |
| priority | CharField(10) | Нет | Приоритет: high/medium/low |
| completed | BooleanField | Нет | Выполнена ли задача |
| manager_id | IntegerField | Нет | ID менеджера (межсервисная ссылка) |
| location | CharField(200) | Да | Место встречи/задачи |
| color | CharField(7) | Нет | Цвет в календаре (HEX) |
| is_recurring | BooleanField | Нет | Повторяемость |
| recurrence_rule | CharField(100) | Да | Правило повторения |
| created_at | DateTimeField | Нет | Дата создания |
| updated_at | DateTimeField | Нет | Дата изменения |

### Таблица 9 - Атрибуты `Template` (`marketing.db`)

| Название атрибута | Тип | Null | Комментарий |
|---|---|---|---|
| id | BigAutoField | Нет | Первичный ключ |
| name | CharField(100) | Нет | Название шаблона |
| template_type | CharField(10) | Нет | Тип шаблона: email/sms |
| subject | CharField(255) | Да | Тема email |
| content | TextField | Нет | Текст шаблона |
| sms_content | CharField(500) | Да | Текст SMS |
| variables | JSONField | Нет | Список переменных для подстановки |
| description | TextField | Да | Описание |
| manager_id | IntegerField | Нет | ID менеджера |
| is_active | BooleanField | Нет | Активность шаблона |
| created_at | DateTimeField | Нет | Дата создания |
| updated_at | DateTimeField | Нет | Дата изменения |

### Таблица 10 - Атрибуты `Campaign` (`marketing.db`)

| Название атрибута | Тип | Null | Комментарий |
|---|---|---|---|
| id | BigAutoField | Нет | Первичный ключ |
| name | CharField(200) | Нет | Название кампании |
| campaign_type | CharField(20) | Нет | Тип: individual/bulk |
| status | CharField(20) | Нет | Статус: draft/sending/sent/failed |
| template_id | ForeignKey(Template) | Да | Связанный шаблон |
| subject | CharField(255) | Да | Тема рассылки |
| content | TextField | Нет | Контент кампании |
| recipients | JSONField | Нет | Список ID получателей |
| recipient_count | IntegerField | Нет | Количество получателей |
| sent_at | DateTimeField | Да | Время отправки |
| success_count | IntegerField | Нет | Успешно отправлено |
| failed_count | IntegerField | Нет | Ошибки отправки |
| manager_id | IntegerField | Нет | ID менеджера |
| created_at | DateTimeField | Нет | Дата создания |
| updated_at | DateTimeField | Нет | Дата изменения |

### Таблица 11 - Атрибуты `CampaignRecipient` (`marketing.db`)

| Название атрибута | Тип | Null | Комментарий |
|---|---|---|---|
| id | BigAutoField | Нет | Первичный ключ |
| campaign_id | ForeignKey(Campaign) | Нет | Кампания получателя |
| recipient_id | IntegerField | Нет | ID получателя |
| recipient_email | EmailField | Да | Email получателя |
| recipient_phone | CharField(20) | Да | Телефон получателя |
| status | CharField(20) | Нет | Статус отправки |
| sent_at | DateTimeField | Да | Время отправки |
| delivered_at | DateTimeField | Да | Время доставки |
| opened_at | DateTimeField | Да | Время открытия |
| error_message | TextField | Да | Ошибка отправки |
| created_at | DateTimeField | Нет | Дата создания |
| updated_at | DateTimeField | Нет | Дата изменения |

Ограничение: `unique_together(campaign, recipient_id)`.

### Таблица 12 - Атрибуты `ClientDocument` (`documetns.db`)

| Название атрибута | Тип | Null | Комментарий |
|---|---|---|---|
| id | BigAutoField | Нет | Первичный ключ |
| client_id | PositiveIntegerField | Нет | ID клиента |
| original_filename | CharField(255) | Нет | Исходное имя файла |
| object_name | CharField(512) | Нет | Уникальный путь/имя в MinIO |
| content_type | CharField(100) | Да | MIME-тип |
| file_size | PositiveBigIntegerField | Да | Размер файла в байтах |
| uploaded_by | PositiveIntegerField | Нет | ID менеджера, загрузившего файл |
| uploaded_at | DateTimeField | Нет | Дата загрузки |

### Таблица 13 - Атрибуты `Applications` (`applications.db`)

| Название атрибута | Тип | Null | Комментарий |
|---|---|---|---|
| id | BigAutoField | Нет | Первичный ключ |
| subject | CharField(500) | Нет | Тема обращения |
| date | DateTimeField | Нет | Дата получения |
| text | TextField | Нет | Текст обращения |
| sender_email | EmailField(255) | Да | Email отправителя |
| message_id | CharField(255) | Да | Уникальный ID входящего письма |
| is_processed | BooleanField | Нет | Признак обработки заявки |
| created_at | DateTimeField | Нет | Дата создания записи |
| updated_at | DateTimeField | Нет | Дата изменения записи |

### Таблица 14 - Атрибуты `ApplicationAudit` (`applications.db`)

| Название атрибута | Тип | Null | Комментарий |
|---|---|---|---|
| id | BigAutoField | Нет | Первичный ключ |
| application_id | ForeignKey(Applications) | Да | Связанная заявка |
| actor | CharField(255) | Да | Пользователь/сервис, выполнивший действие |
| action | CharField(32) | Нет | Тип действия: approved/rejected/processed |
| metadata | JSONField | Нет | Дополнительные данные |
| created_at | DateTimeField | Нет | Время события |

### Связи между таблицами (ER-модель)

Основные связи в системе:
- `User` 1:1 `UserProfile`;
- `Contact` 1:M `Deal`;
- `Service` 1:M `Deal`;
- `Template` 1:M `Campaign`;
- `Campaign` 1:M `CampaignRecipient`;
- `Applications` 1:M `ApplicationAudit`.

Также используются логические межсервисные связи по ID (без FK на уровне SQLite между разными файлами БД): `manager_id`, `client_id`, `recipient_id`, `uploaded_by`. Проверка таких связей выполняется на уровне API и бизнес-логики сервисов.
