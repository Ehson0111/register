/*
================================================================================
  CRM — создание микросервисных баз данных (Microsoft SQL Server / SSMS)
  Эквивалент текущих SQLite: user.db, contact.db, calendar.db, ...
  Проект в Docker по-прежнему использует SQLite — этот скрипт только для демо/отчёта.
================================================================================
  Выполнить целиком в SQL Server Management Studio (F5).
  Требуются права: CREATE DATABASE.
================================================================================
*/

SET NOCOUNT ON;
GO

/* ============================================================================
   1. USER-SERVICE  (SQLite: databases/user.db)
   ============================================================================ */
IF DB_ID(N'crm_user') IS NOT NULL
BEGIN
    ALTER DATABASE crm_user SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE crm_user;
END
GO
CREATE DATABASE crm_user
    COLLATE Cyrillic_General_CI_AS;
GO
USE crm_user;
GO

CREATE TABLE users_user (
    id              BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    password        NVARCHAR(128)        NOT NULL,
    last_login      DATETIME2            NULL,
    is_superuser    BIT                  NOT NULL CONSTRAINT DF_users_user_super DEFAULT 0,
    username        NVARCHAR(150)        NOT NULL,
    first_name      NVARCHAR(150)        NOT NULL,
    last_name       NVARCHAR(150)        NOT NULL,
    email           NVARCHAR(254)        NOT NULL,
    is_staff        BIT                  NOT NULL CONSTRAINT DF_users_user_staff DEFAULT 0,
    is_active       BIT                  NOT NULL CONSTRAINT DF_users_user_active DEFAULT 1,
    date_joined     DATETIME2            NOT NULL CONSTRAINT DF_users_user_joined DEFAULT SYSUTCDATETIME(),
    role            NVARCHAR(20)         NOT NULL CONSTRAINT DF_users_user_role DEFAULT N'client',
    CONSTRAINT UQ_users_user_username UNIQUE (username),
    CONSTRAINT UQ_users_user_email UNIQUE (email)
);

CREATE TABLE users_userprofile (
    id              BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    user_id         BIGINT               NOT NULL UNIQUE,
    phone           NVARCHAR(20)         NOT NULL DEFAULT N'',
    address         NVARCHAR(MAX)        NOT NULL DEFAULT N'',
    date_of_birth   DATE                 NULL,
    created_at      DATETIME2            NOT NULL CONSTRAINT DF_users_profile_ca DEFAULT SYSUTCDATETIME(),
    updated_at      DATETIME2            NOT NULL CONSTRAINT DF_users_profile_ua DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_users_profile_user FOREIGN KEY (user_id) REFERENCES users_user(id) ON DELETE CASCADE
);

CREATE TABLE authentication_emailotp (
    id              BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    email           NVARCHAR(254)        NOT NULL,
    purpose         NVARCHAR(20)         NOT NULL,
    code            NVARCHAR(6)          NOT NULL,
    created_at      DATETIME2            NOT NULL CONSTRAINT DF_auth_otp_ca DEFAULT SYSUTCDATETIME(),
    expires_at      DATETIME2            NOT NULL,
    used            BIT                  NOT NULL CONSTRAINT DF_auth_otp_used DEFAULT 0,
    attempts        INT                  NOT NULL CONSTRAINT DF_auth_otp_attempts DEFAULT 0
);
CREATE INDEX IX_auth_otp_email_purpose ON authentication_emailotp (email, purpose, used);
CREATE INDEX IX_auth_otp_expires ON authentication_emailotp (expires_at);
GO

/* ============================================================================
   2. CONTACT-SERVICE  (SQLite: databases/contact.db)
   ============================================================================ */
IF DB_ID(N'crm_contact') IS NOT NULL
BEGIN
    ALTER DATABASE crm_contact SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE crm_contact;
END
GO
CREATE DATABASE crm_contact COLLATE Cyrillic_General_CI_AS;
GO
USE crm_contact;
GO

CREATE TABLE contacts_contact (
    id              BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    first_name      NVARCHAR(100)        NOT NULL,
    last_name       NVARCHAR(100)        NOT NULL,
    email           NVARCHAR(254)        NOT NULL,
    phone           NVARCHAR(20)         NOT NULL DEFAULT N'',
    inn             NVARCHAR(12)         NOT NULL DEFAULT N'',
    created_at      DATETIME2            NOT NULL CONSTRAINT DF_contacts_ca DEFAULT SYSUTCDATETIME(),
    status          NVARCHAR(10)         NOT NULL CONSTRAINT DF_contacts_status DEFAULT N'lead',
    company         NVARCHAR(200)        NOT NULL DEFAULT N'',
    position        NVARCHAR(100)        NOT NULL DEFAULT N'',
    address         NVARCHAR(MAX)        NOT NULL DEFAULT N'',
    notes           NVARCHAR(MAX)        NOT NULL DEFAULT N'',
    CONSTRAINT UQ_contacts_email_phone UNIQUE (email, phone)
);

CREATE TABLE contacts_contactcompanydetails (
    id              BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    contact_id      BIGINT               NOT NULL UNIQUE,
    company_name    NVARCHAR(500)        NOT NULL DEFAULT N'Не найдено',
    inn             NVARCHAR(12)         NOT NULL DEFAULT N'Не найдено',
    kpp             NVARCHAR(20)         NOT NULL DEFAULT N'Не найдено',
    ogrn            NVARCHAR(20)         NOT NULL DEFAULT N'Не найдено',
    status_text     NVARCHAR(255)        NOT NULL DEFAULT N'Не найдено',
    address         NVARCHAR(MAX)        NOT NULL DEFAULT N'Не найдено',
    okved           NVARCHAR(500)        NOT NULL DEFAULT N'Не найдено',
    director        NVARCHAR(255)        NOT NULL DEFAULT N'Не найдено',
    raw_data        NVARCHAR(MAX)        NOT NULL CONSTRAINT DF_contact_co_json DEFAULT N'{}',
    updated_at      DATETIME2            NOT NULL CONSTRAINT DF_contact_co_ua DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_contact_co_contact FOREIGN KEY (contact_id) REFERENCES contacts_contact(id) ON DELETE CASCADE
);

CREATE TABLE contacts_service (
    id              BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    name            NVARCHAR(200)        NOT NULL,
    description     NVARCHAR(MAX)        NOT NULL DEFAULT N'',
    price           DECIMAL(10,2)        NOT NULL,
    duration_days   INT                  NOT NULL CONSTRAINT DF_service_duration DEFAULT 30,
    is_active       BIT                  NOT NULL CONSTRAINT DF_service_active DEFAULT 1,
    created_at      DATETIME2            NOT NULL CONSTRAINT DF_service_ca DEFAULT SYSUTCDATETIME()
);

CREATE TABLE contacts_dealstage (
    id              BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    name            NVARCHAR(100)        NOT NULL UNIQUE,
    [order]         INT                  NOT NULL CONSTRAINT DF_stage_order DEFAULT 0,
    color           NVARCHAR(20)         NOT NULL CONSTRAINT DF_stage_color DEFAULT N'#2563eb',
    is_default      BIT                  NOT NULL CONSTRAINT DF_stage_default DEFAULT 0
);

CREATE TABLE contacts_deal (
    id                      BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    contact_id              BIGINT               NOT NULL,
    service_id              BIGINT               NOT NULL,
    stage_id                BIGINT               NULL,
    title                   NVARCHAR(200)        NOT NULL,
    description             NVARCHAR(MAX)        NOT NULL DEFAULT N'',
    amount                  DECIMAL(10,2)        NOT NULL,
    probability             INT                  NOT NULL CONSTRAINT DF_deal_prob DEFAULT 0,
    status                  NVARCHAR(20)         NOT NULL CONSTRAINT DF_deal_status DEFAULT N'new',
    expected_close_date     DATE                 NULL,
    actual_close_date       DATE                 NULL,
    created_at              DATETIME2            NOT NULL CONSTRAINT DF_deal_ca DEFAULT SYSUTCDATETIME(),
    updated_at              DATETIME2            NOT NULL CONSTRAINT DF_deal_ua DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_deal_contact FOREIGN KEY (contact_id) REFERENCES contacts_contact(id) ON DELETE CASCADE,
    CONSTRAINT FK_deal_service FOREIGN KEY (service_id) REFERENCES contacts_service(id) ON DELETE CASCADE,
    CONSTRAINT FK_deal_stage FOREIGN KEY (stage_id) REFERENCES contacts_dealstage(id) ON DELETE SET NULL,
    CONSTRAINT CK_deal_probability CHECK (probability >= 0 AND probability <= 100)
);

CREATE TABLE contacts_audittrail (
    id              BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    actor           NVARCHAR(255)        NOT NULL DEFAULT N'',
    action          NVARCHAR(64)         NOT NULL,
    entity_type     NVARCHAR(64)         NOT NULL,
    entity_id       INT                  NULL,
    metadata        NVARCHAR(MAX)        NOT NULL CONSTRAINT DF_audit_meta DEFAULT N'{}',
    created_at      DATETIME2            NOT NULL CONSTRAINT DF_audit_ca DEFAULT SYSUTCDATETIME()
);
GO

/* ============================================================================
   3. CALENDAR-SERVICE  (SQLite: databases/calendar.db)
   ============================================================================ */
IF DB_ID(N'crm_calendar') IS NOT NULL
BEGIN
    ALTER DATABASE crm_calendar SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE crm_calendar;
END
GO
CREATE DATABASE crm_calendar COLLATE Cyrillic_General_CI_AS;
GO
USE crm_calendar;
GO

CREATE TABLE calendarUser_calendartask (
    id                  BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    title               NVARCHAR(200)        NOT NULL,
    description         NVARCHAR(MAX)        NOT NULL DEFAULT N'',
    task_type           NVARCHAR(20)         NOT NULL CONSTRAINT DF_cal_task_type DEFAULT N'task',
    [date]              DATE                 NOT NULL,
    [time]              TIME(0)              NULL,
    priority            NVARCHAR(10)         NOT NULL CONSTRAINT DF_cal_priority DEFAULT N'medium',
    completed           BIT                  NOT NULL CONSTRAINT DF_cal_completed DEFAULT 0,
    manager_id          INT                  NOT NULL,
    location            NVARCHAR(200)        NOT NULL DEFAULT N'',
    color               NVARCHAR(7)          NOT NULL CONSTRAINT DF_cal_color DEFAULT N'#4CAF50',
    is_recurring        BIT                  NOT NULL CONSTRAINT DF_cal_recurring DEFAULT 0,
    recurrence_rule     NVARCHAR(100)        NOT NULL DEFAULT N'',
    created_at          DATETIME2            NOT NULL CONSTRAINT DF_cal_ca DEFAULT SYSUTCDATETIME(),
    updated_at          DATETIME2            NOT NULL CONSTRAINT DF_cal_ua DEFAULT SYSUTCDATETIME()
);
CREATE INDEX IX_cal_manager_date ON calendarUser_calendartask (manager_id, [date]);
CREATE INDEX IX_cal_manager_done ON calendarUser_calendartask (manager_id, completed);
CREATE INDEX IX_cal_date_priority ON calendarUser_calendartask ([date], priority);
GO

/* ============================================================================
   4. MARKETING-SERVICE  (SQLite: databases/marketing.db)
   ============================================================================ */
IF DB_ID(N'crm_marketing') IS NOT NULL
BEGIN
    ALTER DATABASE crm_marketing SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE crm_marketing;
END
GO
CREATE DATABASE crm_marketing COLLATE Cyrillic_General_CI_AS;
GO
USE crm_marketing;
GO

CREATE TABLE marketing_template (
    id              BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    name            NVARCHAR(100)        NOT NULL,
    template_type   NVARCHAR(10)         NOT NULL CONSTRAINT DF_tpl_type DEFAULT N'email',
    subject         NVARCHAR(255)        NOT NULL DEFAULT N'',
    content         NVARCHAR(MAX)        NOT NULL,
    sms_content     NVARCHAR(500)        NOT NULL DEFAULT N'',
    variables       NVARCHAR(MAX)        NOT NULL CONSTRAINT DF_tpl_vars DEFAULT N'[]',
    description     NVARCHAR(MAX)        NOT NULL DEFAULT N'',
    manager_id      INT                  NOT NULL,
    is_active       BIT                  NOT NULL CONSTRAINT DF_tpl_active DEFAULT 1,
    created_at      DATETIME2            NOT NULL CONSTRAINT DF_tpl_ca DEFAULT SYSUTCDATETIME(),
    updated_at      DATETIME2            NOT NULL CONSTRAINT DF_tpl_ua DEFAULT SYSUTCDATETIME()
);
CREATE INDEX IX_tpl_manager_type ON marketing_template (manager_id, template_type);

CREATE TABLE marketing_campaign (
    id                  BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    name                NVARCHAR(200)        NOT NULL,
    campaign_type       NVARCHAR(20)         NOT NULL CONSTRAINT DF_camp_type DEFAULT N'individual',
    status              NVARCHAR(20)         NOT NULL CONSTRAINT DF_camp_status DEFAULT N'draft',
    template_id         BIGINT               NULL,
    subject             NVARCHAR(255)        NOT NULL DEFAULT N'',
    content             NVARCHAR(MAX)        NOT NULL,
    recipients          NVARCHAR(MAX)        NOT NULL CONSTRAINT DF_camp_recip DEFAULT N'[]',
    recipient_count     INT                  NOT NULL CONSTRAINT DF_camp_rc DEFAULT 0,
    sent_at             DATETIME2            NULL,
    success_count       INT                  NOT NULL CONSTRAINT DF_camp_ok DEFAULT 0,
    failed_count        INT                  NOT NULL CONSTRAINT DF_camp_fail DEFAULT 0,
    manager_id          INT                  NOT NULL,
    created_at          DATETIME2            NOT NULL CONSTRAINT DF_camp_ca DEFAULT SYSUTCDATETIME(),
    updated_at          DATETIME2            NOT NULL CONSTRAINT DF_camp_ua DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_camp_template FOREIGN KEY (template_id) REFERENCES marketing_template(id) ON DELETE SET NULL
);
CREATE INDEX IX_camp_manager_status ON marketing_campaign (manager_id, status);

CREATE TABLE marketing_campaignrecipient (
    id                  BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    campaign_id         BIGINT               NOT NULL,
    recipient_id        INT                  NOT NULL,
    recipient_email     NVARCHAR(254)        NOT NULL DEFAULT N'',
    recipient_phone     NVARCHAR(20)         NOT NULL DEFAULT N'',
    status              NVARCHAR(20)         NOT NULL CONSTRAINT DF_crecip_st DEFAULT N'pending',
    sent_at             DATETIME2            NULL,
    delivered_at        DATETIME2            NULL,
    opened_at           DATETIME2            NULL,
    error_message       NVARCHAR(MAX)        NOT NULL DEFAULT N'',
    created_at          DATETIME2            NOT NULL CONSTRAINT DF_crecip_ca DEFAULT SYSUTCDATETIME(),
    updated_at          DATETIME2            NOT NULL CONSTRAINT DF_crecip_ua DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_crecip_campaign FOREIGN KEY (campaign_id) REFERENCES marketing_campaign(id) ON DELETE CASCADE,
    CONSTRAINT UQ_crecip_campaign_recipient UNIQUE (campaign_id, recipient_id)
);
GO

/* ============================================================================
   5. DOCUMENTS-SERVICE  (SQLite: databases/documetns.db)
   ============================================================================ */
IF DB_ID(N'crm_documents') IS NOT NULL
BEGIN
    ALTER DATABASE crm_documents SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE crm_documents;
END
GO
CREATE DATABASE crm_documents COLLATE Cyrillic_General_CI_AS;
GO
USE crm_documents;
GO

CREATE TABLE documents_clientdocument (
    id                  BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    client_id           INT                  NOT NULL,
    original_filename   NVARCHAR(255)        NOT NULL,
    object_name         NVARCHAR(512)        NOT NULL,
    content_type        NVARCHAR(100)        NOT NULL DEFAULT N'',
    file_size           BIGINT               NULL,
    uploaded_by         INT                  NOT NULL,
    uploaded_at         DATETIME2            NOT NULL CONSTRAINT DF_doc_up DEFAULT SYSUTCDATETIME(),
    CONSTRAINT UQ_documents_object_name UNIQUE (object_name)
);
CREATE INDEX IX_doc_client ON documents_clientdocument (client_id);
CREATE INDEX IX_doc_uploaded ON documents_clientdocument (uploaded_at);
GO

/* ============================================================================
   6. CHAT-SERVICE  (SQLite: databases/chat_service.db)
   ============================================================================ */
IF DB_ID(N'crm_chat') IS NOT NULL
BEGIN
    ALTER DATABASE crm_chat SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE crm_chat;
END
GO
CREATE DATABASE crm_chat COLLATE Cyrillic_General_CI_AS;
GO
USE crm_chat;
GO

CREATE TABLE chatService_chatroom (
    id                  BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    title               NVARCHAR(255)        NOT NULL DEFAULT N'',
    created_by_id       INT                  NOT NULL,
    created_by_email    NVARCHAR(254)        NOT NULL DEFAULT N'',
    created_by_name     NVARCHAR(255)        NOT NULL DEFAULT N'',
    is_ai               BIT                  NOT NULL CONSTRAINT DF_room_ai DEFAULT 0,
    is_active           BIT                  NOT NULL CONSTRAINT DF_room_active DEFAULT 1,
    created_at          DATETIME2            NOT NULL CONSTRAINT DF_room_ca DEFAULT SYSUTCDATETIME(),
    updated_at          DATETIME2            NOT NULL CONSTRAINT DF_room_ua DEFAULT SYSUTCDATETIME()
);

CREATE TABLE chatService_chatparticipant (
    id                  BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    room_id             BIGINT               NOT NULL,
    user_id             INT                  NOT NULL,
    email               NVARCHAR(254)        NOT NULL DEFAULT N'',
    first_name          NVARCHAR(150)        NOT NULL DEFAULT N'',
    last_name           NVARCHAR(150)        NOT NULL DEFAULT N'',
    role                NVARCHAR(20)         NOT NULL,
    joined_at           DATETIME2            NOT NULL CONSTRAINT DF_part_joined DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_part_room FOREIGN KEY (room_id) REFERENCES chatService_chatroom(id) ON DELETE CASCADE,
    CONSTRAINT UQ_part_room_user UNIQUE (room_id, user_id)
);

CREATE TABLE chatService_chatmessage (
    id                  BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    room_id             BIGINT               NOT NULL,
    sender_id           INT                  NOT NULL,
    sender_email        NVARCHAR(254)        NOT NULL DEFAULT N'',
    sender_first_name   NVARCHAR(150)        NOT NULL DEFAULT N'',
    sender_last_name    NVARCHAR(150)        NOT NULL DEFAULT N'',
    sender_role         NVARCHAR(20)         NOT NULL,
    text                NVARCHAR(MAX)        NOT NULL,
    created_at          DATETIME2            NOT NULL CONSTRAINT DF_msg_ca DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_msg_room FOREIGN KEY (room_id) REFERENCES chatService_chatroom(id) ON DELETE CASCADE
);

CREATE TABLE chatService_telegramroombinding (
    id                          BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    room_id                     BIGINT               NOT NULL UNIQUE,
    telegram_chat_id            BIGINT               NOT NULL UNIQUE,
    telegram_username           NVARCHAR(255)        NOT NULL DEFAULT N'',
    telegram_first_name         NVARCHAR(255)        NOT NULL DEFAULT N'',
    telegram_last_name          NVARCHAR(255)        NOT NULL DEFAULT N'',
    last_forwarded_message_id   BIGINT               NOT NULL CONSTRAINT DF_tg_msg DEFAULT 0,
    created_at                  DATETIME2            NOT NULL CONSTRAINT DF_tg_ca DEFAULT SYSUTCDATETIME(),
    updated_at                  DATETIME2            NOT NULL CONSTRAINT DF_tg_ua DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_tg_room FOREIGN KEY (room_id) REFERENCES chatService_chatroom(id) ON DELETE CASCADE
);
GO

/* ============================================================================
   7. APPLICATIONS-SERVICE  (SQLite: databases/applications.db)
   ============================================================================ */
IF DB_ID(N'crm_applications') IS NOT NULL
BEGIN
    ALTER DATABASE crm_applications SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE crm_applications;
END
GO
CREATE DATABASE crm_applications COLLATE Cyrillic_General_CI_AS;
GO
USE crm_applications;
GO

CREATE TABLE applications_applications (
    id              BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    subject         NVARCHAR(500)        NOT NULL,
    [date]          DATETIME2            NOT NULL CONSTRAINT DF_app_date DEFAULT SYSUTCDATETIME(),
    text            NVARCHAR(MAX)        NOT NULL,
    sender_email    NVARCHAR(255)        NOT NULL DEFAULT N'',
    message_id      NVARCHAR(255)        NULL,
    is_processed    BIT                  NOT NULL CONSTRAINT DF_app_proc DEFAULT 0,
    created_at      DATETIME2            NOT NULL CONSTRAINT DF_app_ca DEFAULT SYSUTCDATETIME(),
    updated_at      DATETIME2            NOT NULL CONSTRAINT DF_app_ua DEFAULT SYSUTCDATETIME(),
    CONSTRAINT UQ_applications_message_id UNIQUE (message_id)
);

CREATE TABLE applications_applicationaudit (
    id              BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    application_id  BIGINT               NULL,
    actor           NVARCHAR(255)        NOT NULL DEFAULT N'',
    action          NVARCHAR(32)         NOT NULL,
    metadata        NVARCHAR(MAX)        NOT NULL CONSTRAINT DF_appaudit_meta DEFAULT N'{}',
    created_at      DATETIME2            NOT NULL CONSTRAINT DF_appaudit_ca DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_appaudit_app FOREIGN KEY (application_id) REFERENCES applications_applications(id) ON DELETE CASCADE
);

CREATE TABLE applications_mailboxemail (
    id              BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    external_id     NVARCHAR(255)        NOT NULL,
    message_id      NVARCHAR(255)        NOT NULL DEFAULT N'',
    subject         NVARCHAR(500)        NOT NULL DEFAULT N'',
    sender_name     NVARCHAR(255)        NOT NULL DEFAULT N'',
    sender_email    NVARCHAR(255)        NOT NULL DEFAULT N'',
    recipients      NVARCHAR(MAX)        NOT NULL DEFAULT N'',
    cc              NVARCHAR(MAX)        NOT NULL DEFAULT N'',
    [date]          DATETIME2            NOT NULL CONSTRAINT DF_mail_date DEFAULT SYSUTCDATETIME(),
    body_text       NVARCHAR(MAX)        NOT NULL DEFAULT N'',
    body_html       NVARCHAR(MAX)        NOT NULL DEFAULT N'',
    preview         NVARCHAR(MAX)        NOT NULL DEFAULT N'',
    is_read         BIT                  NOT NULL CONSTRAINT DF_mail_read DEFAULT 0,
    is_important    BIT                  NOT NULL CONSTRAINT DF_mail_imp DEFAULT 0,
    in_inbox        BIT                  NOT NULL CONSTRAINT DF_mail_inbox DEFAULT 0,
    in_sent         BIT                  NOT NULL CONSTRAINT DF_mail_sent DEFAULT 0,
    in_trash        BIT                  NOT NULL CONSTRAINT DF_mail_trash DEFAULT 0,
    primary_folder  NVARCHAR(32)         NOT NULL CONSTRAINT DF_mail_folder DEFAULT N'inbox',
    raw_flags       NVARCHAR(MAX)        NOT NULL CONSTRAINT DF_mail_flags DEFAULT N'[]',
    created_at      DATETIME2            NOT NULL CONSTRAINT DF_mail_ca DEFAULT SYSUTCDATETIME(),
    updated_at      DATETIME2            NOT NULL CONSTRAINT DF_mail_ua DEFAULT SYSUTCDATETIME(),
    CONSTRAINT UQ_mailbox_external_id UNIQUE (external_id)
);
CREATE INDEX IX_mailbox_date ON applications_mailboxemail ([date]);
GO

/* ============================================================================
   8. PAYMENTS-SERVICE  (SQLite: databases/payments.db)
   ============================================================================ */
IF DB_ID(N'crm_payments') IS NOT NULL
BEGIN
    ALTER DATABASE crm_payments SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE crm_payments;
END
GO
CREATE DATABASE crm_payments COLLATE Cyrillic_General_CI_AS;
GO
USE crm_payments;
GO

CREATE TABLE yookassa_integration_order (
    id              BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    amount          DECIMAL(10,2)        NOT NULL,
    payment_status  NVARCHAR(20)         NOT NULL CONSTRAINT DF_order_pst DEFAULT N'pending',
    payment_id      NVARCHAR(100)        NULL
);

CREATE TABLE yookassa_integration_invoice (
    id                          BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    deal_id                     INT                  NOT NULL,
    deal_title                  NVARCHAR(255)        NOT NULL DEFAULT N'',
    contact_id                  INT                  NULL,
    contact_name                NVARCHAR(255)        NOT NULL DEFAULT N'',
    contact_email               NVARCHAR(254)        NOT NULL DEFAULT N'',
    contact_phone               NVARCHAR(32)         NOT NULL DEFAULT N'',
    service_id                  INT                  NULL,
    service_name                NVARCHAR(255)        NOT NULL DEFAULT N'',
    comment                     NVARCHAR(MAX)        NOT NULL DEFAULT N'',
    invoice_number              NVARCHAR(50)         NOT NULL,
    onec_document_id            NVARCHAR(128)        NOT NULL DEFAULT N'',
    onec_invoice_number         NVARCHAR(128)        NOT NULL DEFAULT N'',
    onec_payment_document_id    NVARCHAR(128)        NOT NULL DEFAULT N'',
    amount                      DECIMAL(10,2)        NOT NULL,
    status                      NVARCHAR(20)         NOT NULL CONSTRAINT DF_inv_status DEFAULT N'draft',
    payment_id                  NVARCHAR(100)        NULL,
    payment_url                 NVARCHAR(200)        NOT NULL DEFAULT N'',
    onec_sync_status            NVARCHAR(20)         NOT NULL CONSTRAINT DF_inv_1c DEFAULT N'pending',
    crm_sync_status             NVARCHAR(20)         NOT NULL CONSTRAINT DF_inv_crm DEFAULT N'pending',
    onec_retry_count            INT                  NOT NULL CONSTRAINT DF_inv_1cr DEFAULT 0,
    crm_retry_count             INT                  NOT NULL CONSTRAINT DF_inv_crmr DEFAULT 0,
    last_onec_error             NVARCHAR(MAX)        NOT NULL DEFAULT N'',
    last_crm_error              NVARCHAR(MAX)        NOT NULL DEFAULT N'',
    created_at                  DATETIME2            NOT NULL CONSTRAINT DF_inv_ca DEFAULT SYSUTCDATETIME(),
    paid_at                     DATETIME2            NULL,
    sent_to_1c                  BIT                  NOT NULL CONSTRAINT DF_inv_sent DEFAULT 0,
    pay_link_sent_at            DATETIME2            NULL,
    next_retry_at               DATETIME2            NULL,
    CONSTRAINT UQ_invoice_number UNIQUE (invoice_number),
    CONSTRAINT UQ_invoice_deal_id UNIQUE (deal_id)
);
GO

/* ============================================================================
   9. API-GATEWAY  (SQLite: databases/gateway.db) — без доменных таблиц
   ============================================================================ */
IF DB_ID(N'crm_gateway') IS NOT NULL
BEGIN
    ALTER DATABASE crm_gateway SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE crm_gateway;
END
GO
CREATE DATABASE crm_gateway COLLATE Cyrillic_General_CI_AS;
GO
USE crm_gateway;
GO

-- Прокси без собственных бизнес-моделей; в SQLite только django_migrations / auth при migrate.
CREATE TABLE gateway_note (
    id          INT IDENTITY(1,1) PRIMARY KEY,
    note        NVARCHAR(500) NOT NULL DEFAULT N'API Gateway не хранит доменные данные — только маршрутизация к микросервисам.'
);
INSERT INTO gateway_note (note) VALUES (N'См. crm_contact, crm_user, crm_payments и др.');
GO

USE master;
GO
PRINT N'';
PRINT N'================================================================================';
PRINT N' Готово: созданы базы crm_user, crm_contact, crm_calendar, crm_marketing,';
PRINT N' crm_documents, crm_chat, crm_applications, crm_payments, crm_gateway';
PRINT N' (эквивалент SQLite-микросервисов CRM).';
PRINT N'================================================================================';
GO
