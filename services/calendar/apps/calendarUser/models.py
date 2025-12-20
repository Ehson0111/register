from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser

from django.contrib.auth.models import AbstractUser
from django.db import models

class CalendarUser(AbstractUser):
    title = models.CharField(max_length=50)
    description= models.CharField(max_length=100)
    date = models.DateField(null=True,blank=True)
    
    priority_high='high'
    priority_medium='medium'
    priority_low='low'

    priority_choisec= [
        (priority_high, 'Высокий'),
        (priority_medium, 'Средний'),
        (priority_low, 'Низкий'),
    ]

    priority =models.CharField( max_length=40, choices=priority_choisec,default=priority_low)

    completed=models.BooleanField()

    def __str__(self):
        return f'{self.title} {self.description}'
    
    class Meta: 
        ordering= ['-date']
        unique_together = ['title', 'description']
        

    




    #    id: 1,
    #   title: 'Встреча с клиентом',
    #   description: 'Обсуждение нового проекта',
    #   date: today,
    #   time: '10:00',
    #   priority: 'high'    ,
    #   completed: false
    # },