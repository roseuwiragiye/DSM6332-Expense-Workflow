# 💼 ExpenseFlow - Company Expense & Approval Workflow

**DSM6332 Cloud Computing and Web Programming - Individual Assignment #19**

## 📋 Project Overview

ExpenseFlow is a full-stack Django web application designed to streamline company expense management with an intelligent role-based approval workflow system. The application enables employees to submit expenses, managers to review and approve/reject them, and administrators to manage the entire system.

### Key Objectives

✅ Implement a secure, multi-user expense management system  
✅ Enforce role-based access control (Employee, Manager, Admin)  
✅ Create an intuitive approval workflow  
✅ Provide role-specific user interfaces  
✅ Ensure data integrity and security  
✅ Deliver a scalable, maintainable codebase  

---

## ✨ Features

### 👤 User Management
- **Role-based Registration:** Users choose their role (Employee or Manager) during signup
- **User Authentication:** Secure login with Django's authentication system
- **Profile Management:** Users can view and edit their profiles
- **Profile Pictures:** Upload and manage profile photos
- **Role-Specific Dashboards:** Different interfaces for each role

### 📄 Expense Management
- **Submit Expenses:** Employees submit expenses with title, amount, category, date, and receipt
- **Edit Pending Expenses:** Employees can edit their own pending expenses
- **View Expenses:** 
  - Employees see only their own expenses
  - Managers see all expenses (for approval)
  - Admins see all expenses (with management options)
- **Delete Expenses:** Only admins can delete expenses
- **Search & Filter:** Filter by employee name, date range, and status

### ✅ Approval Workflow
- **Review Expenses:** Managers review pending expenses
- **Approve/Reject:** Make decisions with optional comments
- **Status Tracking:** Real-time expense status updates
- **Approval History:** View all approval decisions with timestamps
- **Automatic Sync:** Expense status automatically updates when approval is made

### 🔐 Security Features
- **Role-Based Access Control (RBAC):** View-level permission checks
- **Permission Enforcement:** Users can only access appropriate data
- **Secure File Uploads:** Validated receipt uploads with size limits
- **CSRF Protection:** All forms protected with CSRF tokens
- **SQL Injection Prevention:** Django ORM prevents SQL injection
- **Password Hashing:** Django's PBKDF2 password hashing

### 🎨 User Interface
- **Responsive Design:** Works on desktop, tablet, and mobile
- **Role-Specific Themes:**
  - 🔵 **Employee:** Blue theme (#2563eb) - Friendly, action-focused
  - 🟣 **Manager:** Purple theme (#7c3aed) - Authority, oversight
  - 🔴 **Admin:** Red theme (#dc2626) - Control, full power
- **Intuitive Navigation:** Context-aware menus based on role
- **Clean, Modern Design:** Bootstrap-based styling
- **Visual Status Indicators:** Color-coded expense status (Pending, Approved, Rejected)

### 📊 REST API
- **List Expenses:** GET `/api/expenses/`
- **Create Expense:** POST `/api/expenses/`
- **Get Details:** GET `/api/expenses/<id>/`
- **Role-Based Filtering:** Only see appropriate data
- **JSON Responses:** Standardized API format

---

## 🛠 Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Django 3.2+, Python 3.12 |
| **Database** | MySQL 8.0 |
| **Frontend** | HTML5, CSS3, JavaScript |
| **Styling** | Bootstrap 5 |
| **API** | Django REST Framework |
| **Authentication** | Django Built-in Auth |
| **Server** | Ubuntu 24.04 LTS |
| **IDE** | VS Code with SSH |

---

## 📁 Project Structure

```
expense_project/
├── expenses/                          # Main application
│   ├── models.py                      # Database models (Employee, Manager, Expense, Approval, Category)
│   ├── views.py                       # Business logic & view handlers
│   ├── forms.py                       # Form definitions (RegisterForm, ExpenseForm, etc.)
│   ├── urls.py                        # URL routing
│   ├── admin.py                       # Django admin configuration
│   ├── serializers.py                 # REST API serializers
│   ├── migrations/                    # Database migrations
│   └── templates/expenses/            # HTML templates
│       ├── base.html                  # Main layout template (role-based)
│       ├── dashboard.html             # Dashboard view
│       ├── expense_list_employee.html # Employee expense list
│       ├── expense_list_manager.html  # Manager expense list
│       ├── expense_add.html           # Submit expense form
│       ├── profile.html               # User profile
│       ├── profile_edit.html          # Edit profile
│       ├── employee_list.html         # Manage employees
│       ├── category_list.html         # Manage categories
│       └── ...other templates
├── expense_project/                   # Project configuration
│   ├── settings.py                    # Django settings (DB, apps, middleware)
│   ├── urls.py                        # Main URL configuration
│   └── wsgi.py                        # WSGI application
├── manage.py                          # Django management utility
├── requirements.txt                   # Python dependencies
├── .gitignore                         # Git ignore file
└── README.md                          # This file
```

---

## 📊 Database Schema

### Models

**User** (Django Built-in)
```
id, username, email, password, first_name, last_name
```

**Employee**
```
id, user (OneToOne), name, department, profile_photo, created_at
Relations:
  - Has many Expenses (ForeignKey)
```

**Manager**
```
id, user (OneToOne), name, department, profile_photo
Relations:
  - Has many Approvals (ForeignKey)
```

**Category**
```
id, name, description
Relations:
  - Has many Expenses (ForeignKey)
```

**Expense**
```
id, employee (FK), category (FK), title, amount, date, receipt, status, created_at
Status: Pending, Approved, Rejected
Relations:
  - Belongs to Employee
  - Belongs to Category
  - Has one Approval (OneToOne)
```

**Approval**
```
id, expense (OneToOne), manager (FK), decision, comment, decided_at
Decision: Approved, Rejected
Relations:
  - Belongs to Expense
  - Belongs to Manager
  - Syncs status to Expense via signal
```

### Database Diagram
```
┌─────────────┐
│    User     │
└──────┬──────┘
       │
       ├─────────────────┬──────────────────┐
       │                 │                  │
    ┌──▼─────────┐  ┌───▼──────────┐  ┌───▼──────┐
    │ Employee   │  │   Manager    │  │ (Django) │
    └──┬─────────┘  └───┬──────────┘  └──────────┘
       │                │
       │    ┌───────────┘
       │    │
    ┌──▼────▼──────┐
    │   Expense    │◄──────┐
    └──┬──────┬────┘       │
       │      │           │
       │   ┌──▼──────────┐ │
       │   │ Category   │ │
       │   └─────────────┘ │
       │                   │
       └───────────┬───────┘
                   │
              ┌────▼──────┐
              │ Approval  │
              └───────────┘
```

---

## 🚀 Installation & Setup

### Prerequisites
- **Python:** 3.12+
- **MySQL:** 8.0+
- **Git:** 2.0+
- **pip:** Latest version

### Step 1: Clone Repository
```bash
git clone https://github.com/roseuwiragiye/DSM6332-Expense-Workflow.git
cd DSM6332-Expense-Workflow
```

### Step 2: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Database
Edit `expense_project/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'expense_db',
        'USER': 'expense_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

Create MySQL database:
```bash
mysql -u root -p
CREATE DATABASE expense_db;
CREATE USER 'expense_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON expense_db.* TO 'expense_user'@'localhost';
FLUSH PRIVILEGES;
```

### Step 5: Run Migrations
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

### Step 6: Create Superuser
```bash
python3 manage.py createsuperuser
# Username: admin
# Email: admin@example.com
# Password: (choose a strong password)
```

### Step 7: Load Sample Data (Optional)
```bash
python3 manage.py shell
>>> from expenses.models import Category, Employee, Manager
>>> Category.objects.create(name='Travel', description='Travel expenses')
>>> Category.objects.create(name='Food', description='Meal expenses')
>>> # ... create more categories
>>> exit()
```

### Step 8: Run Development Server
```bash
python3 manage.py runserver 0.0.0.0:8000
```

### Step 9: Access Application
- **Application:** http://localhost:8000
- **Admin Panel:** http://localhost:8000/admin/
- **REST API:** http://localhost:8000/api/expenses/

---

## 👥 User Roles & Permissions

### Employee (👤)
| Action | Allowed |
|--------|---------|
| Submit expenses | ✅ |
| View own expenses | ✅ |
| Edit own pending expenses | ✅ |
| Delete own expenses | ❌ |
| View all employees | ❌ |
| Approve expenses | ❌ |
| Access /admin/ | ❌ |

### Manager (👔)
| Action | Allowed |
|--------|---------|
| Submit expenses | ❌ |
| View all expenses | ✅ |
| Review pending expenses | ✅ |
| Approve/reject expenses | ✅ |
| View all employees | ✅ |
| Manage employees | ❌ |
| Access /admin/ | ❌ |

### Admin (⚙️)
| Action | Allowed |
|--------|---------|
| All actions | ✅ |
| Manage users | ✅ |
| Manage categories | ✅ |
| Access /admin/ | ✅ |
| Access REST API | ✅ |

---

## 🔌 REST API Endpoints

### Expenses
```
GET    /api/expenses/              List all expenses (paginated)
POST   /api/expenses/              Create new expense
GET    /api/expenses/<id>/         Get expense details
PUT    /api/expenses/<id>/         Update expense (not implemented)
DELETE /api/expenses/<id>/         Delete expense (not implemented)
```

### Example Request
```bash
# Get all expenses
curl -H "Authorization: Token YOUR_TOKEN" http://localhost:8000/api/expenses/

# Create expense
curl -X POST http://localhost:8000/api/expenses/ \
  -H "Content-Type: application/json" \
  -d '{"employee": 1, "category": 1, "title": "Hotel", "amount": 100, "date": "2024-06-20"}'
```

### Response Format
```json
{
  "id": 1,
  "employee": {
    "id": 1,
    "name": "Rose Uwiragiye",
    "department": "Data Science"
  },
  "category": {
    "id": 1,
    "name": "Travel"
  },
  "title": "Hotel accommodation",
  "amount": "100.00",
  "date": "2024-06-20",
  "status": "Pending",
  "approval": null
}
```

---

## 🔐 Security Implementation

### View-Level Permission Checks
Every view has role-based checks:
```python
@login_required
def employee_list(request):
    # Block employees from viewing
    if is_employee(request.user) and not is_manager(request.user):
        messages.error(request, 'Employees cannot view other employees.')
        return redirect('dashboard')
    # ... rest of view
```

### Expense Filtering by Role
```python
if is_employee(request.user):
    # Employee sees only their expenses
    expenses = Expense.objects.filter(employee=employee)
else:
    # Manager/Admin sees all expenses
    expenses = Expense.objects.all()
```

### File Upload Validation
```python
def clean_profile_photo(self):
    photo = self.cleaned_data.get('profile_photo')
    if photo:
        if photo.size > 5 * 1024 * 1024:  # 5MB max
            raise forms.ValidationError('Image must be less than 5MB')
```

---

## 🧪 Testing

### Manual Testing Checklist
- [ ] Employee registration and login
- [ ] Manager registration and login
- [ ] Admin access to all features
- [ ] Submit expense as employee
- [ ] Edit pending expense
- [ ] View own expenses (employee)
- [ ] View all expenses (manager)
- [ ] Approve/reject expense (manager)
- [ ] Upload profile picture
- [ ] Search and filter expenses
- [ ] Role-specific navigation
- [ ] Different color themes display correctly
- [ ] File upload size validation
- [ ] Unauthorized access redirection

---

## 📈 Performance Optimizations

### Database Queries
```python
# Use select_related for ForeignKeys
expenses = Expense.objects.select_related('employee', 'category')

# Use filter for efficient filtering
expenses = expenses.filter(status='Pending')
```

### Pagination
```python
# Implemented in REST API
# Limits data transfer and improves response time
```

### Caching (Future Enhancement)
```python
# Could implement Django cache framework
# Cache dashboard data
# Cache frequently viewed expenses
```

---

## 📝 Sample Data

### Categories
- Travel
- Food
- IT Equipment
- Office Supply
- Training

### Test Users
**Employee:**
- Username: `rose`
- Password: `Rose123!`
- Department: Data Science

**Manager:**
- Username: `anna`
- Password: `Anna123!`
- Department: Finance

**Admin:**
- Username: `admin`
- Password: (set during creation)

---

## 🎓 Learning Outcomes

This project demonstrates:

1. **Django MTV Architecture:** Models, Templates, Views separation
2. **Role-Based Access Control:** Securing views based on user roles
3. **Database Design:** Relationships (ForeignKey, OneToOne), migrations
4. **Form Handling:** ModelForms, validation, file uploads
5. **REST API:** DRF serializers, authentication, permissions
6. **Django Signals:** Automatic status sync between Expense and Approval
7. **Template Inheritance:** Base templates with role-based navigation
8. **CSS Variables:** Dynamic theming based on user role
9. **MySQL Integration:** Database configuration and management
10. **Git & GitHub:** Version control and repository management

---

## 🐛 Known Issues & Future Improvements

### Known Issues
- None reported

### Future Enhancements
- [ ] Email notifications for approvals
- [ ] Expense analytics and reporting dashboard
- [ ] Expense budget tracking by category
- [ ] Approval comments notifications
- [ ] Export expenses to PDF/Excel
- [ ] Two-factor authentication
- [ ] API token authentication
- [ ] Expense history and audit logs
- [ ] Department-level approval workflows
- [ ] Mobile app version

---

## 📚 References

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Django Model Relationships](https://docs.djangoproject.com/en/4.2/topics/db/models/relations/)
- [Django Signals](https://docs.djangoproject.com/en/4.2/topics/signals/)
- [Bootstrap CSS](https://getbootstrap.com/)
- [MySQL Documentation](https://dev.mysql.com/doc/)

---

## 👨‍💻 Author

**Rose Uwiragiye**
- **Student ID:** DSM6332
- **Course:** Cloud Computing and Web Programming
- **University:** University of Rwanda (ACEDS)
- **GitHub:** [@roseuwiragiye](https://github.com/roseuwiragiye)
- **Email:** roseuwiragiye8@example.com

---

## 📄 License

This project is for educational purposes as part of the DSM6332 assignment requirement.

---

## 🙏 Acknowledgments

- **Django Community:** For excellent documentation and framework
- **Bootstrap:** For responsive CSS framework
- **MySQL:** For reliable database management
- **VS Code:** For excellent development environment
- **GitHub:** For repository hosting

---

## 📞 Support

For issues or questions:
1. Check [Issues](https://github.com/roseuwiragiye/DSM6332-Expense-Workflow/issues)
2. Review [Documentation](./README.md)
3. Contact the author

---

**Last Updated:** June 2026  
**Version:** 1.0.0  
**Status:** Complete & Deployed ✅