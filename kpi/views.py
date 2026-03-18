from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.decorators import management_or_superuser_required
from .models import KPITask
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
@management_or_superuser_required
def management_dashboard(request):
    """
    Management Dashboard showing KPIs for Staff members.
    For this example, we generate dummy daily KPI data for a specific staff member
    to demonstrate the Chart.js integration separating weekends from weekdays.
    """
    staff_users = User.objects.filter(role='Staff')
    selected_staff_id = request.GET.get('staff_id')

    if selected_staff_id:
        selected_staff = User.objects.filter(id=selected_staff_id, role='Staff').first()
    else:
        selected_staff = staff_users.first()

    # Generate past 14 days of data
    today = timezone.now().date()
    labels = []
    data_points = []
    is_weekend = []

    # Example logic: Random KPI scores (or query actual KPITask objects)
    # We will simulate data for demonstration of the UI requirements
    import random

    for i in range(13, -1, -1):
        date = today - timedelta(days=i)
        # 0 = Monday, 6 = Sunday
        weekday = date.weekday()

        labels.append(date.strftime("%a, %b %d"))

        if weekday >= 5: # Saturday or Sunday
            is_weekend.append(True)
            # Weekends might have lower or 0 KPI if they don't work, let's say 20-50
            data_points.append(random.randint(20, 50))
        else:
            is_weekend.append(False)
            # Weekdays have normal KPI, let's say 70-100
            data_points.append(random.randint(70, 100))

    import json

    context = {
        'staff_users': staff_users,
        'selected_staff': selected_staff,
        'labels_json': json.dumps(labels),
        'data_points_json': json.dumps(data_points),
        'is_weekend_json': json.dumps(is_weekend),
    }

    return render(request, 'kpi/management_dashboard.html', context)
