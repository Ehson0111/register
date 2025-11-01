from django.db import models

class Contact(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField("Email")
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # исправил кавычки!
    
    STATUS_LEAD = 'lead'
    STATUS_CLIENT = 'client'
    STATUS_PARTNER = 'partner'
    STATUS_CHOICES = [
        (STATUS_LEAD, 'Lead'),
        (STATUS_CLIENT, 'Client'),
        (STATUS_PARTNER, 'Partner'),
    ]
    status = models.CharField(
        "Status", 
        max_length=10, 
        choices=STATUS_CHOICES, 
        default=STATUS_LEAD
    )
    company = models.CharField("Company", max_length=200, blank=True)
    position = models.CharField("Position", max_length=100, blank=True)
    address = models.TextField("Address", blank=True)
    notes = models.TextField("Notes", blank=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['email', 'phone']

    def __str__(self):
        return f"{self.first_name}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"