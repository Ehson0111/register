


 Все сервисы запускаются..." - 
 API Gateway: http://localhost:8000"  api
 User Service: http://localhost:8004"   для авторизации  
 Contact Service: http://localhost:8005"  контакты, услуги, сделки 
 Calendar: http://localhost:8006"  календарь 
 Frontend: http://localhost:3000"   фронтенд
 



marketning сервис
Шаблон: 
http://localhost:8007/api/send-individual/

Authorization
Content-Type
{
  "name": "Приветственное письмо",
  "template_type": "email",
  "subject": "Добро пожаловать, {name}!",
  "content": "Уважаемый {name}, рады приветствовать вас...",
  "variables": ["name", "company"],
  "description": "Шаблон для новых клиентов"
} 
Индивидульная отправка 
http://localhost:8000/api/marketing/send-individual/
пример 1
  {
    "template_id": 4,
    "recipient_id": 11
  }
пример 2 
  {
    "template_id": 4,
    "recipient_id": 11,
    "variables": {
      "offer": "СКИДКА20",
      "company": "ООО 'Промышленность'",
      "new_email": "newemail@example.com",
      "personal_message": "Это сообщение специально для вас!"
    }
  }

масовая отправка  
http://localhost:8000/api/marketing/send-campaign/

{
  "template_id": 1,
  "subject": "Скидка 20% для вас",
  "content": "Специальное предложение только для вас!",
  "variables": {
    "offer": "СКИДКА20",
    "company": "ООО 'Промышленность'"
  },
  "recipient_ids": [10, 11],
  "campaign_name": "Декабрьская акция"
}

GET
http://localhost:8000/api/marketing/templates/
пример ответа 
[
    {
        "id": 4,
        "name": "Спасибо за вашу лояльность",
        "template_type": "email",
        "template_type_display": "Email",
        "subject": "",
        "content": "Дорогой(ая) {name}, команда {company} искренне благодарит вас за доверие и сотрудничество. Мы ценим ваш выбор и стремимся становиться лучше для вас каждый день.",
        "sms_content": "",
        "variables": [
            "name",
            "company"
        ],
        "description": "Шаблон для выражения общей благодарности клиенту.",
        "manager_id": 7,
        "is_active": true,
        "created_at": "2026-02-02T09:42:49.375892-06:00",
        "updated_at": "2026-02-02T09:42:49.375892-06:00"
    },
      
    {
        "id": 1,
        "name": "Приветственное письмо",
        "template_type": "email",
        "template_type_display": "Email",
        "subject": "Добро пожаловать, {name}!",
        "content": "Уважаемый {name}, рады приветствовать вас в нашей компании {company}.",
        "sms_content": "",
        "variables": [
            "name",
            "company"
        ],
        "description": "Шаблон для новых клиентов",
        "manager_id": 7,
        "is_active": true,
        "created_at": "2025-12-25T09:47:29.808631-06:00",
        "updated_at": "2025-12-25T09:47:29.808631-06:00"
    }
]

post 
http://localhost:8000/api/marketing/send-quick-message/

// {
//   "message": "Добрый день! Напоминаем о вашей записи на завтра в 14:00.",
//   "recipient_ids": [10, 11]
// }

{
  "message": "Уважаемый клиент! Наш офис будет закрыт с 1 по 8 марта. Приносим извинения за неудобства.",
  "subject": "Уведомление о графике работы",
  "recipient_ids": [10, 11, 12, 13],
  "campaign_name": "Уведомление о выходных"
}

GET http://localhost:8000/api/marketing/campaigns/stats/
пример ответа
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

get 
http://localhost:8000/api/marketing/campaigns/
[
    {
        "id": 106,
        "name": "Уведомление о выходных",
        "campaign_type": "bulk",
        "campaign_type_display": "Массовая",
        "status": "sent",
        "status_display": "Отправлено",
        "template": 6,
        "template_name": "Быстрый шаблон - 12:57:43",
        "subject": "Уведомление о графике работы",
        "content": "Уважаемый клиент! Наш офис будет закрыт с 1 по 8 марта. Приносим извинения за неудобства.",
        "recipients": [
            10,
            11,
            12,
            13
        ],
        "recipient_count": 4,
        "success_count": 4,
        "failed_count": 0,
        "sent_at": "2026-02-05T06:57:54.228578-06:00",
        "delivery_rate": 100.0,
        "recipients_detail": [
            {
                "id": 104,
                "recipient_id": 10,
                "recipient_email": "ehsonboboev2@gmail.com",
                "recipient_phone": "9963816063",
                "status": "sent",
                "status_display": "Отправлено",
                "sent_at": "2026-02-05T06:57:46.883605-06:00",
                "delivered_at": null,
                "opened_at": null,
                "error_message": "",
                "created_at": "2026-02-05T06:57:44.192776-06:00"
            },
            {
                "id": 105,
                "recipient_id": 11,
                "recipient_email": "ehsonboboev09@gmail.com",
                "recipient_phone": "9139849806",
                "status": "sent",
                "status_display": "Отправлено",
                "sent_at": "2026-02-05T06:57:49.242631-06:00",
                "delivered_at": null,
                "opened_at": null,
                "error_message": "",
                "created_at": "2026-02-05T06:57:46.918478-06:00"
            },
            {
                "id": 106,
                "recipient_id": 12,
                "recipient_email": "client12@example.com",
                "recipient_phone": "+79990000012",
                "status": "sent",
                "status_display": "Отправлено",
                "sent_at": "2026-02-05T06:57:51.715235-06:00",
                "delivered_at": null,
                "opened_at": null,
                "error_message": "",
                "created_at": "2026-02-05T06:57:49.277366-06:00"
            },
            {
                "id": 107,
                "recipient_id": 13,
                "recipient_email": "client13@example.com",
                "recipient_phone": "+79990000013",
                "status": "sent",
                "status_display": "Отправлено",
                "sent_at": "2026-02-05T06:57:54.215723-06:00",
                "delivered_at": null,
                "opened_at": null,
                "error_message": "",
                "created_at": "2026-02-05T06:57:51.760890-06:00"
            }
        ],
        "manager_id": 7,
        "created_at": "2026-02-05T06:57:43.764243-06:00",
        "updated_at": "2026-02-05T06:57:54.228578-06:00"
    },
    

запуск minio

docker run -d -p 9000:9000 -p 9001:9001 ^
  --name minio ^
  -e "MINIO_ROOT_USER=minioadmin" ^
  -e "MINIO_ROOT_PASSWORD=minioadmin" ^
  -v minio-data:/data ^
  quay.io/minio/minio server /data --console-address ":9001"


документы 
http://localhost:8000/api/documents/upload/

formdata 
client_id text id
file fike файл

список документов 
http://localhost:8000/api/documents/10/list/

загрузка документов 
http://localhost:8000/api/documents/download/1/
