import smtplib
from email.mime.text import MIMEText

def quick_send_yandex():
    msg = MIMEText("Текст 1", 'plain', 'utf-8')
    msg['Subject'] = 'тестирование     '
    msg['From'] = 'ehsonboboev7@yandex.ru'
    msg['To'] = 'ehsonboboev7@gmail.com'
    
    server = smtplib.SMTP_SSL('smtp.yandex.ru', 465)
    server.login('ehsonboboev7@yandex.ru', 'token')
    server.send_message(msg)
    server.quit()
    print("Письмо отправлено!")

quick_send_yandex()
