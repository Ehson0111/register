 Все сервисы запускаются..." - 
 API Gateway: http://localhost:8000"  
 User Service: http://localhost:8004"  
 Contact Service: http://localhost:8005"  
 Calendar: http://localhost:8006"  
 Frontend: http://localhost:3000"   
 



marketning сервис
Шаблоны:
text
GET    /api/templates/              # Список всех шаблонов
POST   /api/templates/              # Создать новый шаблон
GET    /api/templates/{id}/         # Получить шаблон
PUT    /api/templates/{id}/         # Обновить шаблон
DELETE /api/templates/{id}/         # Удалить шаблон
GET    /api/templates/by-type/?type=email  # Шаблоны по типу
POST   /api/templates/{id}/duplicate/      # Дублировать шаблон
История рассылок:
text
GET    /api/campaigns/              # Список всех рассылок
GET    /api/campaigns/{id}/         # Детали рассылки
GET    /api/campaigns/{id}/recipients/  # Получатели конкретной рассылки
GET    /api/campaigns/stats/        # Статистика по всем рассылкам
GET    /api/campaigns/recent/       # Последние 10 рассылок
GET    /api/history/?start_date=2024-01-01&page=1  # История с фильтрами
Отправка:
text
POST   /api/send-campaign/          # Отправить массовую рассылку
POST   /api/send-individual/        # Отправить индивидуально
📦 Примеры использования:


POST /api/templates/
{
  "name": "Приветственное письмо",
  "template_type": "email",
  "subject": "Добро пожаловать, {name}!",
  "content": "Уважаемый {name}, рады приветствовать вас...",
  "variables": ["name", "company"],
  "description": "Шаблон для новых клиентов"
}
2. Отправить массовую рассылку:
json
POST /api/send-campaign/
{
  "template_id": 1,
  "subject": "Скидка 20% для вас",
  "content": "Специальное предложение только для вас!",
  "recipient_ids": [101, 102, 103, 104],
  "campaign_name": "Декабрьская акция"
}
3. Отправить индивидуально:
json
POST [/api/send-individual/](http://localhost:8007/api/send-individual/{client_id}/)
{
  "template_id": 2,
  "recipient_id": 105,
  "variables": {
    "name": "Иван Иванов",
    "offer": "СКИДКА20"
  }
}


4. Получить историю с фильтрами:
text
GET /api/history/?start_date=2024-12-01&type=bulk&page=1
