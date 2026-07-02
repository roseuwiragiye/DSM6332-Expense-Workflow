# expenses/urls.py - Updated with profile URLs

from django.urls import path
from . import views
from .serializers import ExpenseListCreateAPI, ExpenseDetailAPI

urlpatterns = [
    # Auth
    path('login/',    views.login_view,    name='login'),
    path('logout/',   views.logout_view,   name='logout'),
    path('register/', views.register_view, name='register'),
    
    # Profile
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/delete-photo/', views.profile_delete_photo, name='profile_delete_photo'),

    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Employees
    path('employees/',              views.employee_list,   name='employee_list'),
    path('employees/add/',          views.employee_add,    name='employee_add'),
    path('employees/<int:pk>/edit/',views.employee_edit,   name='employee_edit'),
    path('employees/<int:pk>/delete/', views.employee_delete, name='employee_delete'),

    # Managers
    path('managers/',               views.manager_list,    name='manager_list'),
    path('managers/add/',           views.manager_add,     name='manager_add'),
    path('managers/<int:pk>/edit/', views.manager_edit,    name='manager_edit'),
    path('managers/<int:pk>/delete/', views.manager_delete, name='manager_delete'),

    # Categories
    path('categories/',              views.category_list,   name='category_list'),
    path('categories/add/',          views.category_add,    name='category_add'),
    path('categories/<int:pk>/edit/',views.category_edit,   name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),

    # Expenses
    path('expenses/',               views.expense_list,    name='expense_list'),
    path('expenses/add/',           views.expense_add,     name='expense_add'),
    path('expenses/<int:pk>/',      views.expense_detail,  name='expense_detail'),
    path('expenses/<int:pk>/edit/', views.expense_edit,    name='expense_edit'),
    path('expenses/<int:pk>/delete/', views.expense_delete, name='expense_delete'),

    # Approvals
    path('expenses/<int:expense_pk>/approve/', views.approval_create, name='approval_create'),

    # REST API
    path('api/expenses/',        ExpenseListCreateAPI.as_view(), name='api_expense_list'),
    path('api/expenses/<int:pk>/', ExpenseDetailAPI.as_view(),   name='api_expense_detail'),
]


# ─────────────────────────────────────────────
# expense_project/urls.py  (main project urls)
# ─────────────────────────────────────────────

MAIN_URLS = """
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('expenses.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
"""