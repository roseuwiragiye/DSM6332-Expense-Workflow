# expenses/models.py

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.department})"


class Manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} – Manager ({self.department})"


class Expense(models.Model):
    STATUS_CHOICES = [
        ('Pending',  'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    employee   = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='expenses')
    category   = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='expenses')
    title      = models.CharField(max_length=200)
    amount     = models.DecimalField(max_digits=12, decimal_places=2)
    date       = models.DateField()
    receipt    = models.FileField(upload_to='receipts/', blank=True, null=True)
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} – {self.employee.name} – RWF {self.amount}"


class Approval(models.Model):
    DECISION_CHOICES = [
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    expense    = models.OneToOneField(Expense, on_delete=models.CASCADE, related_name='approval')
    manager    = models.ForeignKey(Manager, on_delete=models.SET_NULL, null=True, related_name='approvals')
    decision   = models.CharField(max_length=20, choices=DECISION_CHOICES)
    comment    = models.TextField(blank=True)
    decided_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.decision} – {self.expense.title}"


# Signal: sync Expense.status when an Approval is saved
@receiver(post_save, sender=Approval)
def sync_expense_status(sender, instance, **kwargs):
    expense = instance.expense
    expense.status = instance.decision
    expense.save(update_fields=['status'])