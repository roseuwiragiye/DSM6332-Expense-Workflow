from django.contrib import admin
from .models import Employee, Category, Expense, Approval, Manager

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'created_at']
    search_fields = ['name', 'department']

@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    list_display = ['name', 'department']
    search_fields = ['name']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['title', 'employee', 'category', 'amount', 'date', 'status']
    list_filter = ['status', 'category']
    search_fields = ['title', 'employee__name']

@admin.register(Approval)
class ApprovalAdmin(admin.ModelAdmin):
    list_display = ['expense', 'manager', 'decision', 'decided_at']
    list_filter = ['decision']
    search_fields = ['expense__title', 'manager__name']
