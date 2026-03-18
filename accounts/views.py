from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from .models import Department
from .decorators import management_or_superuser_required
from .forms import StaffUserForm, DepartmentForm, SetPasswordForm

User = get_user_model()

@login_required
@management_or_superuser_required
def settings_dashboard(request):
    """ Main Settings Tab """
    staff_users = User.objects.filter(role='Staff')
    departments = Department.objects.all()
    context = {
        'staff_users': staff_users,
        'departments': departments,
    }
    return render(request, 'accounts/settings_dashboard.html', context)

# --- Staff Management Views ---

@login_required
@management_or_superuser_required
def add_staff(request):
    if request.method == 'POST':
        form = StaffUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'Staff'
            user.set_password('Tradecore123!') # Default password
            user.save()
            messages.success(request, f"Staff user {user.username} created successfully.")
            return redirect('accounts:settings_dashboard')
    else:
        form = StaffUserForm()

    return render(request, 'accounts/staff_form.html', {'form': form})

@login_required
@management_or_superuser_required
def edit_staff(request, user_id):
    staff_user = get_object_or_404(User, id=user_id, role='Staff')
    if request.method == 'POST':
        form = StaffUserForm(request.POST, instance=staff_user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Staff user {staff_user.username} updated.")
            return redirect('accounts:settings_dashboard')
    else:
        form = StaffUserForm(instance=staff_user)

    return render(request, 'accounts/staff_form.html', {'form': form, 'staff_user': staff_user})

@login_required
@management_or_superuser_required
def remove_staff(request, user_id):
    staff_user = get_object_or_404(User, id=user_id, role='Staff')
    if request.method == 'POST':
        staff_user.delete()
        messages.success(request, f"Staff user deleted.")
        return redirect('accounts:settings_dashboard')
    return render(request, 'accounts/confirm_delete.html', {'object': staff_user})

@login_required
@management_or_superuser_required
def reset_staff_password(request, user_id):
    staff_user = get_object_or_404(User, id=user_id, role='Staff')
    if request.method == 'POST':
        form = SetPasswordForm(user=staff_user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Password reset for {staff_user.username}.")
            return redirect('accounts:settings_dashboard')
    else:
        form = SetPasswordForm(user=staff_user)

    return render(request, 'accounts/reset_password.html', {'form': form, 'staff_user': staff_user})

# --- Department Management Views ---

@login_required
@management_or_superuser_required
def add_department(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Department {form.cleaned_data['name']} created.")
            return redirect('accounts:settings_dashboard')
    else:
        form = DepartmentForm()
    return render(request, 'accounts/department_form.html', {'form': form})

@login_required
@management_or_superuser_required
def edit_department(request, dept_id):
    department = get_object_or_404(Department, id=dept_id)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, f"Department {department.name} updated.")
            return redirect('accounts:settings_dashboard')
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'accounts/department_form.html', {'form': form, 'department': department})

@login_required
@management_or_superuser_required
def remove_department(request, dept_id):
    department = get_object_or_404(Department, id=dept_id)
    if request.method == 'POST':
        department.delete()
        messages.success(request, "Department deleted.")
        return redirect('accounts:settings_dashboard')
    return render(request, 'accounts/confirm_delete.html', {'object': department})
