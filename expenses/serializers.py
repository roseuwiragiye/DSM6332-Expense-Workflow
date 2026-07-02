# expenses/serializers.py - WITH ROLE-BASED API RESTRICTIONS

from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Expense, Employee, Category, Approval, Manager


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Category
        fields = ['id', 'name', 'description']


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Employee
        fields = ['id', 'name', 'department']


class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Manager
        fields = ['id', 'name', 'department']


class ApprovalSerializer(serializers.ModelSerializer):
    manager_name = serializers.CharField(source='manager.name', read_only=True)

    class Meta:
        model  = Approval
        fields = ['id', 'decision', 'comment', 'manager_name', 'decided_at']


class ExpenseSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    approval = ApprovalSerializer(read_only=True)

    # For POST — accept IDs
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(), write_only=True, source='employee'
    )
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), write_only=True, source='category'
    )

    class Meta:
        model  = Expense
        fields = [
            'id', 'title', 'amount', 'date', 'status', 'created_at',
            'employee', 'employee_id',
            'category', 'category_id',
            'approval',
        ]
        read_only_fields = ['status', 'created_at']


# ─────────────────────────────────────────────
# API VIEWS WITH ROLE-BASED RESTRICTIONS
# ─────────────────────────────────────────────

def is_employee(user):
    """Check if user is an Employee"""
    try:
        return Employee.objects.filter(user=user).exists()
    except:
        return False


def is_manager(user):
    """Check if user is a Manager"""
    try:
        return Manager.objects.filter(user=user).exists()
    except:
        return False


def is_admin(user):
    """Check if user is an Admin"""
    return user.is_superuser


class ExpenseListCreateAPI(APIView):
    """
    GET  /api/expenses/         – list expenses (filtered by role)
    POST /api/expenses/         – create a new expense (employees only)
    
    ROLE-BASED ACCESS:
    - Employee: Can only see/create their own expenses
    - Manager: Can see all expenses
    - Admin: Can see and create all expenses
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """GET list of expenses based on user role"""
        user = request.user
        
        if is_employee(user):
            # Employee: Only their own expenses
            employee = Employee.objects.get(user=user)
            expenses = employee.expenses.select_related('employee', 'category').all()
            message = f"✅ Showing your expenses ({expenses.count()} total)"
        
        elif is_manager(user):
            # Manager: All expenses
            expenses = Expense.objects.select_related('employee', 'category').all()
            message = f"✅ Showing all expenses ({expenses.count()} total) - Manager access"
        
        else:
            # Admin: All expenses
            expenses = Expense.objects.select_related('employee', 'category').all()
            message = f"✅ Showing all expenses ({expenses.count()} total) - Admin access"
        
        serializer = ExpenseSerializer(expenses, many=True)
        
        return Response({
            'count': len(serializer.data),
            'message': message,
            'data': serializer.data
        })

    def post(self, request):
        """POST create expense (employees only)"""
        user = request.user
        
        # Only employees can create expenses
        if not is_employee(user):
            return Response(
                {
                    'error': '❌ Only employees can submit expenses.',
                    'your_role': 'Manager' if is_manager(user) else 'Admin'
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ExpenseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    'message': '✅ Expense created successfully!',
                    'data': serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            {
                'error': '❌ Validation failed',
                'details': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class ExpenseDetailAPI(APIView):
    """
    GET /api/expenses/<pk>/     – single expense detail (with permission check)
    
    ROLE-BASED ACCESS:
    - Employee: Can only view their own expenses
    - Manager: Can view all expenses
    - Admin: Can view all expenses
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """GET single expense detail"""
        user = request.user
        
        try:
            expense = Expense.objects.select_related('employee', 'category').get(pk=pk)
        except Expense.DoesNotExist:
            return Response(
                {'error': '❌ Expense not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Permission check
        if is_employee(user):
            employee = Employee.objects.get(user=user)
            if expense.employee != employee:
                return Response(
                    {
                        'error': '❌ You can only view your own expenses.',
                        'expense_owner': expense.employee.name
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = ExpenseSerializer(expense)
        return Response({
            'message': '✅ Expense retrieved successfully',
            'data': serializer.data
        })


class ExpenseApprovalAPI(APIView):
    """
    GET /api/expenses/<pk>/approvals/  – view approval status
    POST /api/expenses/<pk>/approve/   – create approval (managers only)
    
    ROLE-BASED ACCESS:
    - Employee: Cannot access
    - Manager: Can view and create approvals
    - Admin: Can view and create approvals
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """GET approval status"""
        user = request.user
        
        try:
            expense = Expense.objects.get(pk=pk)
        except Expense.DoesNotExist:
            return Response(
                {'error': '❌ Expense not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check permission
        if is_employee(user):
            employee = Employee.objects.get(user=user)
            if expense.employee != employee:
                return Response(
                    {'error': '❌ You can only view approval for your own expenses'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        if hasattr(expense, 'approval'):
            approval = expense.approval
            serializer = ApprovalSerializer(approval)
            return Response({
                'message': '✅ Approval found',
                'data': serializer.data
            })
        else:
            return Response({
                'message': '⏳ No approval yet (Pending)',
                'status': 'Pending'
            })

    def post(self, request, pk):
        """POST create approval (managers only)"""
        user = request.user
        
        # Only managers can approve
        if not is_manager(user):
            return Response(
                {
                    'error': '❌ Only managers can approve expenses.',
                    'your_role': 'Employee' if is_employee(user) else 'Admin'
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            expense = Expense.objects.get(pk=pk)
        except Expense.DoesNotExist:
            return Response(
                {'error': '❌ Expense not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if hasattr(expense, 'approval'):
            return Response(
                {'error': '❌ This expense already has an approval decision'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create approval
        manager = Manager.objects.get(user=user)
        decision = request.data.get('decision')  # 'Approved' or 'Rejected'
        comment = request.data.get('comment', '')
        
        if decision not in ['Approved', 'Rejected']:
            return Response(
                {'error': '❌ Decision must be "Approved" or "Rejected"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        approval = Approval.objects.create(
            expense=expense,
            manager=manager,
            decision=decision,
            comment=comment
        )
        
        serializer = ApprovalSerializer(approval)
        return Response({
            'message': f'✅ Expense {decision}!',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)


# ─────────────────────────────────────────────
# API ENDPOINTS TO ADD TO urls.py:
# ─────────────────────────────────────────────
"""
In expenses/urls.py, add these REST API paths:

    # REST API with role-based access
    path('api/expenses/', ExpenseListCreateAPI.as_view(), name='api_expense_list'),
    path('api/expenses/<int:pk>/', ExpenseDetailAPI.as_view(), name='api_expense_detail'),
    path('api/expenses/<int:pk>/approval/', ExpenseApprovalAPI.as_view(), name='api_expense_approval'),
"""