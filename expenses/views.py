# expenses/views.py
# COMPLETE VERSION - Authentication + CRUD + Approvals + Profile Management

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.contrib import messages
from .models import Employee, Category, Expense, Approval, Manager
from .forms import (
    EmployeeForm, CategoryForm, ExpenseForm,
    ApprovalForm, ExpenseSearchForm, RegisterForm, ManagerForm, ProfileForm
)


# ─────────────────────────────────────────────
# AUTH VIEWS
# ─────────────────────────────────────────────

def register_view(request):
    """
    Updated registration view that allows users to choose
    if they want to be an Employee or Manager
    """
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Create Django User
            user = form.save()
            
            # Get form data
            role = form.cleaned_data['role']
            department = form.cleaned_data['department']
            name = form.cleaned_data['name']
            
            # Create Employee OR Manager based on role choice
            if role == 'employee':
                Employee.objects.create(
                    user=user,
                    name=name,
                    department=department
                )
                messages.success(request, '✅ Employee account created! You can now submit expenses.')
            
            elif role == 'manager':
                Manager.objects.create(
                    user=user,
                    name=name,
                    department=department
                )
                messages.success(request, '✅ Manager account created! You can now approve expenses.')
            
            # Log in the new user
            login(request, user)
            return redirect('dashboard')
        else:
            # Show form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RegisterForm()
    
    return render(request, 'expenses/login.html', {'form': form, 'mode': 'register'})


def login_view(request):
    """Standard login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Invalid username or password.')
    return render(request, 'expenses/login.html', {'mode': 'login'})


def logout_view(request):
    """Logout and redirect to login"""
    logout(request)
    return redirect('login')


# ─────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────

@login_required
def dashboard(request):
    total_expenses  = Expense.objects.count()
    pending_count   = Expense.objects.filter(status='Pending').count()
    approved_count  = Expense.objects.filter(status='Approved').count()
    rejected_count  = Expense.objects.filter(status='Rejected').count()
    total_amount    = Expense.objects.filter(status='Approved').aggregate(Sum('amount'))['amount__sum'] or 0
    recent_expenses = Expense.objects.select_related('employee', 'category')[:5]

    context = {
        'total_expenses':  total_expenses,
        'pending_count':   pending_count,
        'approved_count':  approved_count,
        'rejected_count':  rejected_count,
        'total_amount':    total_amount,
        'recent_expenses': recent_expenses,
    }
    return render(request, 'expenses/dashboard.html', context)


# ─────────────────────────────────────────────
# EMPLOYEE CRUD
# ─────────────────────────────────────────────

@login_required
def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'expenses/employee_list.html', {'employees': employees})


@login_required
def employee_add(request):
    form = EmployeeForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Employee added.')
        return redirect('employee_list')
    return render(request, 'expenses/form.html', {'form': form, 'title': 'Add Employee', 'back_url': 'employee_list'})


@login_required
def employee_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    form = EmployeeForm(request.POST or None, request.FILES or None, instance=employee)
    if form.is_valid():
        form.save()
        messages.success(request, 'Employee updated.')
        return redirect('employee_list')
    return render(request, 'expenses/form.html', {'form': form, 'title': 'Edit Employee', 'back_url': 'employee_list'})


@login_required
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.delete()
        messages.success(request, 'Employee deleted.')
        return redirect('employee_list')
    return render(request, 'expenses/confirm_delete.html', {'object': employee, 'back_url': 'employee_list'})


# ─────────────────────────────────────────────
# CATEGORY CRUD
# ─────────────────────────────────────────────

@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'expenses/category_list.html', {'categories': categories})


@login_required
def category_add(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Category added.')
        return redirect('category_list')
    return render(request, 'expenses/form.html', {'form': form, 'title': 'Add Category', 'back_url': 'category_list'})


@login_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=category)
    if form.is_valid():
        form.save()
        messages.success(request, 'Category updated.')
        return redirect('category_list')
    return render(request, 'expenses/form.html', {'form': form, 'title': 'Edit Category', 'back_url': 'category_list'})


@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        try:
            category.delete()
            messages.success(request, 'Category deleted.')
        except Exception:
            messages.error(request, 'Cannot delete: category has linked expenses.')
        return redirect('category_list')
    return render(request, 'expenses/confirm_delete.html', {'object': category, 'back_url': 'category_list'})


# ─────────────────────────────────────────────
# EXPENSE CRUD + SEARCH
# ─────────────────────────────────────────────

@login_required
def expense_list(request):
    form   = ExpenseSearchForm(request.GET or None)
    expenses = Expense.objects.select_related('employee', 'category')

    if form.is_valid():
        name       = form.cleaned_data.get('employee_name')
        date_from  = form.cleaned_data.get('date_from')
        date_to    = form.cleaned_data.get('date_to')
        status     = form.cleaned_data.get('status')

        if name:
            expenses = expenses.filter(Q(employee__name__icontains=name))
        if date_from:
            expenses = expenses.filter(date__gte=date_from)
        if date_to:
            expenses = expenses.filter(date__lte=date_to)
        if status:
            expenses = expenses.filter(status=status)

    return render(request, 'expenses/expense_list.html', {'expenses': expenses, 'search_form': form})


@login_required
def expense_add(request):
    form = ExpenseForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Expense submitted.')
        return redirect('expense_list')
    return render(request, 'expenses/form.html', {'form': form, 'title': 'Submit Expense', 'back_url': 'expense_list'})


@login_required
def expense_edit(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if expense.status != 'Pending':
        messages.error(request, 'Only pending expenses can be edited.')
        return redirect('expense_list')
    form = ExpenseForm(request.POST or None, request.FILES or None, instance=expense)
    if form.is_valid():
        form.save()
        messages.success(request, 'Expense updated.')
        return redirect('expense_list')
    return render(request, 'expenses/form.html', {'form': form, 'title': 'Edit Expense', 'back_url': 'expense_list'})


@login_required
def expense_detail(request, pk):
    expense = get_object_or_404(Expense.objects.select_related('employee', 'category'), pk=pk)
    approval = getattr(expense, 'approval', None)
    return render(request, 'expenses/expense_detail.html', {'expense': expense, 'approval': approval})


@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense deleted.')
        return redirect('expense_list')
    return render(request, 'expenses/confirm_delete.html', {'object': expense, 'back_url': 'expense_list'})


# ─────────────────────────────────────────────
# MANAGER CRUD
# ─────────────────────────────────────────────

@login_required
def manager_list(request):
    managers = Manager.objects.all()
    return render(request, 'expenses/manager_list.html', {'managers': managers})


@login_required
def manager_add(request):
    form = ManagerForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Manager added.')
        return redirect('manager_list')
    return render(request, 'expenses/form.html', {'form': form, 'title': 'Add Manager', 'back_url': 'manager_list'})


@login_required
def manager_edit(request, pk):
    manager = get_object_or_404(Manager, pk=pk)
    form = ManagerForm(request.POST or None, instance=manager)
    if form.is_valid():
        form.save()
        messages.success(request, 'Manager updated.')
        return redirect('manager_list')
    return render(request, 'expenses/form.html', {'form': form, 'title': 'Edit Manager', 'back_url': 'manager_list'})


@login_required
def manager_delete(request, pk):
    manager = get_object_or_404(Manager, pk=pk)
    if request.method == 'POST':
        manager.delete()
        messages.success(request, 'Manager deleted.')
        return redirect('manager_list')
    return render(request, 'expenses/confirm_delete.html', {'object': manager, 'back_url': 'manager_list'})


# ─────────────────────────────────────────────
# APPROVAL CRUD
# ─────────────────────────────────────────────

@login_required
def approval_create(request, expense_pk):
    expense = get_object_or_404(Expense, pk=expense_pk)
    if hasattr(expense, 'approval'):
        messages.warning(request, 'This expense already has an approval decision.')
        return redirect('expense_detail', pk=expense_pk)

    form = ApprovalForm(request.POST or None)
    if form.is_valid():
        approval = form.save(commit=False)
        approval.expense = expense
        approval.save()
        messages.success(request, f'Expense {approval.decision}.')
        return redirect('expense_detail', pk=expense_pk)
    return render(request, 'expenses/form.html', {
        'form': form,
        'title': f'Review Expense: {expense.title}',
        'back_url': 'expense_list'
    })


# ─────────────────────────────────────────────
# PROFILE VIEWS - NEW!
# ─────────────────────────────────────────────

@login_required
def profile_view(request):
    """
    Display current user's profile
    Works for both Employee and Manager
    """
    user = request.user
    profile_data = {
        'username': user.username,
        'email': user.email,
        'is_employee': False,
        'is_manager': False,
    }
    
    # Try to get Employee profile
    try:
        employee = Employee.objects.get(user=user)
        profile_data['is_employee'] = True
        profile_data['name'] = employee.name
        profile_data['department'] = employee.department
        profile_data['profile_photo'] = employee.profile_photo
        profile_data['role'] = 'Employee'
        profile_data['role_emoji'] = '👤'
    except Employee.DoesNotExist:
        pass
    
    # Try to get Manager profile
    try:
        manager = Manager.objects.get(user=user)
        profile_data['is_manager'] = True
        profile_data['name'] = manager.name
        profile_data['department'] = manager.department
        profile_data['profile_photo'] = manager.profile_photo
        profile_data['role'] = 'Manager'
        profile_data['role_emoji'] = '👔'
    except Manager.DoesNotExist:
        pass
    
    return render(request, 'expenses/profile.html', profile_data)


@login_required
def profile_edit(request):
    """
    Edit current user's profile
    Works for both Employee and Manager
    """
    user = request.user
    profile_obj = None
    is_employee = False
    is_manager = False
    
    # Get the user's profile object (Employee or Manager)
    try:
        profile_obj = Employee.objects.get(user=user)
        is_employee = True
    except Employee.DoesNotExist:
        try:
            profile_obj = Manager.objects.get(user=user)
            is_manager = True
        except Manager.DoesNotExist:
            messages.error(request, 'Profile not found.')
            return redirect('profile')
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            # Update profile fields
            profile_obj.name = form.cleaned_data['name']
            profile_obj.department = form.cleaned_data['department']
            
            # Update profile photo if provided
            if form.cleaned_data.get('profile_photo'):
                profile_obj.profile_photo = form.cleaned_data['profile_photo']
            
            profile_obj.save()
            
            messages.success(request, '✅ Profile updated successfully!')
            return redirect('profile')
    else:
        # Pre-populate form with current data
        initial_data = {
            'name': profile_obj.name,
            'department': profile_obj.department,
        }
        form = ProfileForm(initial=initial_data)
    
    context = {
        'form': form,
        'profile_obj': profile_obj,
        'is_employee': is_employee,
        'is_manager': is_manager,
    }
    return render(request, 'expenses/profile_edit.html', context)


@login_required
def profile_delete_photo(request):
    """
    Delete user's profile photo
    """
    user = request.user
    
    try:
        profile_obj = Employee.objects.get(user=user)
    except Employee.DoesNotExist:
        try:
            profile_obj = Manager.objects.get(user=user)
        except Manager.DoesNotExist:
            messages.error(request, 'Profile not found.')
            return redirect('profile')
    
    if profile_obj.profile_photo:
        profile_obj.profile_photo.delete()
        profile_obj.save()
        messages.success(request, '✅ Profile picture deleted.')
    else:
        messages.info(request, 'No profile picture to delete.')
    
    return redirect('profile')