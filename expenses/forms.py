# expenses/forms.py
# COMPLETE VERSION - All required forms

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Employee, Category, Expense, Approval, Manager


# ─────────────────────────────────────────────
# REGISTRATION FORM
# ─────────────────────────────────────────────

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    name  = forms.CharField(max_length=100, label="Full Name")
    department = forms.CharField(
        max_length=100, 
        label="Department",
        widget=forms.TextInput(attrs={'placeholder': 'e.g., Finance, IT, HR, Data Science'})
    )
    
    ROLE_CHOICES = [
        ('employee', '👤 Employee - Submit Expenses'),
        ('manager', '👔 Manager - Approve Expenses'),
    ]
    role = forms.ChoiceField(
        choices=ROLE_CHOICES, 
        label="Select Your Role",
        widget=forms.RadioSelect()
    )

    class Meta:
        model  = User
        fields = ['username', 'email', 'name', 'department', 'role', 'password1', 'password2']


# ─────────────────────────────────────────────
# EMPLOYEE FORM
# ─────────────────────────────────────────────

class EmployeeForm(forms.ModelForm):
    class Meta:
        model  = Employee
        fields = ['name', 'department', 'profile_photo']
        widgets = {
            'name':       forms.TextInput(attrs={'placeholder': 'Full Name'}),
            'department': forms.TextInput(attrs={'placeholder': 'e.g. Finance, IT, HR'}),
        }


# ─────────────────────────────────────────────
# MANAGER FORM
# ─────────────────────────────────────────────

class ManagerForm(forms.ModelForm):
    class Meta:
        model  = Manager
        fields = ['name', 'department']
        widgets = {
            'name':       forms.TextInput(attrs={'placeholder': 'Full Name'}),
            'department': forms.TextInput(attrs={'placeholder': 'e.g. Finance, IT, HR'}),
        }


# ─────────────────────────────────────────────
# CATEGORY FORM
# ─────────────────────────────────────────────

class CategoryForm(forms.ModelForm):
    class Meta:
        model  = Category
        fields = ['name', 'description']
        widgets = {
            'name':        forms.TextInput(attrs={'placeholder': 'e.g. Travel, Food, IT Equipment'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Optional description'}),
        }


# ─────────────────────────────────────────────
# EXPENSE FORM
# ─────────────────────────────────────────────

class ExpenseForm(forms.ModelForm):
    class Meta:
        model  = Expense
        fields = ['employee', 'category', 'title', 'amount', 'date', 'receipt']
        widgets = {
            'date':   forms.DateInput(attrs={'type': 'date'}),
            'title':  forms.TextInput(attrs={'placeholder': 'Brief description of expense'}),
            'amount': forms.NumberInput(attrs={'placeholder': '0.00', 'step': '0.01'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= 0:
            raise forms.ValidationError('Amount must be greater than 0.')
        return amount


# ─────────────────────────────────────────────
# APPROVAL FORM
# ─────────────────────────────────────────────

class ApprovalForm(forms.ModelForm):
    class Meta:
        model  = Approval
        fields = ['manager', 'decision', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Add a note for the employee...'}),
        }


# ─────────────────────────────────────────────
# EXPENSE SEARCH FORM
# ─────────────────────────────────────────────

class ExpenseSearchForm(forms.Form):
    employee_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Employee name…'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Statuses'), ('Pending', 'Pending'),
                 ('Approved', 'Approved'), ('Rejected', 'Rejected')]
    )


# ─────────────────────────────────────────────
# PROFILE FORM - NEW!
# ─────────────────────────────────────────────

class ProfileForm(forms.Form):
    """
    Form for users to edit their profile
    (both Employee and Manager use this)
    """
    name = forms.CharField(
        max_length=100,
        label="Full Name",
        widget=forms.TextInput(attrs={'placeholder': 'Your full name'})
    )
    
    department = forms.CharField(
        max_length=100,
        label="Department",
        widget=forms.TextInput(attrs={'placeholder': 'e.g., Finance, IT, HR'})
    )
    
    profile_photo = forms.ImageField(
        label="Profile Picture",
        required=False,
        widget=forms.FileInput(attrs={
            'accept': 'image/*',
            'help_text': 'JPG, PNG, or GIF (max 5MB)'
        })
    )
    
    def clean_profile_photo(self):
        """Validate image file"""
        photo = self.cleaned_data.get('profile_photo')
        if photo:
            # Check file size (5MB max)
            if photo.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Image must be less than 5MB')
            
            # Check file extension
            valid_extensions = ['jpg', 'jpeg', 'png', 'gif']
            ext = photo.name.split('.')[-1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError('Only JPG, PNG, or GIF files allowed')
        
        return photo