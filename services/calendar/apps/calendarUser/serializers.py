from rest_framework import serializers
from .models import CalendarUser

class CalendarList(serializers.ModelSerializer):
    
    class Meta:
        model=CalendarUser
        fields=[
            'id',
            'title',
            'description',
            'date',
            'priority',
            'completed'
        ]



 

    #  title = models.CharField(max_length=50)
    # description= models.CharField(max_length=100)
    # date = models.DateField(null=True,blank=True)
    
    # priority_high='high'
    # priority_medium='medium'
    # priority_low='low'

    # priority_choisec= [
    #     (priority_high, 'Высокий'),
    #     (priority_medium, 'Средний'),
    #     (priority_low, 'Низкий'),
    # ]

    # priority =models.models.CharField( max_length=40, choices=priority_choisec,default=priority_low)

    # completed=models.BooleanField(required=False)

    # def __str__(self):
    #     return f'{self.title} {self.description}'


    