# from django.db import models

# class Contact(models.Model):
#     first_name = models.CharField(max_length=100)
#     last_name = models.CharField(max_length=100)
#     email = models.EmailField("Email")
#     phone = models.CharField(max_length=20, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)  
    
#     STATUS_LEAD = 'lead'
#     STATUS_CLIENT = 'client'
#     STATUS_PARTNER = 'partner'
#     STATUS_CHOICES = [
#         (STATUS_LEAD, 'Lead'),
#         (STATUS_CLIENT, 'Client'),
#         (STATUS_PARTNER, 'Partner'),
#     ]
#     status = models.CharField(
#         "Status", 
#         max_length=10, 
#         choices=STATUS_CHOICES, 
#         default=STATUS_LEAD
#     )
#     company = models.CharField("Company", max_length=200, blank=True)
#     position = models.CharField("Position", max_length=100, blank=True)
#     address = models.TextField("Address", blank=True)
#     notes = models.TextField("Notes", blank=True)

#     class Meta:
#         ordering = ['-created_at']
#         unique_together = ['email', 'phone']

#     def __str__(self):
#         return f"{self.first_name}"
    
#     def get_full_name(self):
#         return f"{self.first_name} {self.last_name}"
    

 
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Contact(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField("Email")
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  
    
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
        return f"{self.first_name} {self.last_name}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class Service(models.Model):
    name = models.CharField("Service Name", max_length=200)
    description = models.TextField("Description", blank=True)
    price = models.DecimalField("Price", max_digits=10, decimal_places=2)
    duration_days = models.IntegerField("Duration (days)", default=30)
    is_active = models.BooleanField("Active", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - ${self.price}"


class Deal(models.Model):
    DEAL_NEW = 'new'
    DEAL_IN_PROGRESS = 'in_progress'
    DEAL_WON = 'won'
    DEAL_LOST = 'lost'
    DEAL_ON_HOLD = 'on_hold'
    
    DEAL_STATUS_CHOICES = [
        (DEAL_NEW, 'New'),
        (DEAL_IN_PROGRESS, 'In Progress'),
        (DEAL_WON, 'Won'),
        (DEAL_LOST, 'Lost'),
        (DEAL_ON_HOLD, 'On Hold'),
    ]

    contact = models.ForeignKey(
        Contact, 
        on_delete=models.CASCADE, 
        related_name='deals',
        verbose_name="Contact"
    )
    service = models.ForeignKey(
        Service, 
        on_delete=models.CASCADE, 
        related_name='deals',
        verbose_name="Service"
    )
    title = models.CharField("Deal Title", max_length=200)
    description = models.TextField("Description", blank=True)
    amount = models.DecimalField("Deal Amount", max_digits=10, decimal_places=2)
    probability = models.IntegerField(
        "Probability (%)", 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    status = models.CharField(
        "Status",
        max_length=20,
        choices=DEAL_STATUS_CHOICES,
        default=DEAL_NEW
    )
    expected_close_date = models.DateField("Expected Close Date", null=True, blank=True)
    actual_close_date = models.DateField("Actual Close Date", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Deal"
        verbose_name_plural = "Deals"

    def __str__(self):
        return f"{self.title} - {self.contact.get_full_name()} - ${self.amount}"

    def is_closed(self):
        return self.status in [self.DEAL_WON, self.DEAL_LOST]

    def get_status_color(self):
        status_colors = {
            self.DEAL_NEW: 'blue',
            self.DEAL_IN_PROGRESS: 'orange',
            self.DEAL_WON: 'green',
            self.DEAL_LOST: 'red',
            self.DEAL_ON_HOLD: 'gray',
        }
        return status_colors.get(self.status, 'blue')

