from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.translation import gettext as _
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import MealType, WeeklyMenu, FoodOrder, Transaction
from accounts.views import is_admin


def get_current_week_start():
    today = timezone.now().date()
    # Saturday as start of week (Persian calendar style)
    days_since_sat = (today.weekday() + 2) % 7
    return today - timedelta(days=days_since_sat)


@login_required
def weekly_menu(request):
    week_start = request.GET.get('week')
    if week_start:
        from datetime import datetime
        try:
            week_start = datetime.strptime(week_start, '%Y-%m-%d').date()
        except ValueError:
            week_start = get_current_week_start()
    else:
        week_start = get_current_week_start()

    menus = WeeklyMenu.objects.filter(
        week_start=week_start,
        is_available=True
    ).select_related('meal_type').order_by('day', 'meal_time')

    # Group by day
    days = {}
    for menu in menus:
        day_name = menu.get_day_display()
        if day_name not in days:
            days[day_name] = []
        days[day_name].append(menu)

    my_orders = []
    if request.user.is_authenticated:
        my_orders = FoodOrder.objects.filter(
            student=request.user,
            menu_item__week_start=week_start
        ).values_list('menu_item_id', flat=True)

    prev_week = week_start - timedelta(days=7)
    next_week = week_start + timedelta(days=7)

    return render(request, 'cafeteria/weekly_menu.html', {
        'days': days,
        'week_start': week_start,
        'prev_week': prev_week,
        'next_week': next_week,
        'my_orders': list(my_orders),
    })


@login_required
def place_order(request):
    if request.method != 'POST':
        return redirect('cafeteria:menu')

    menu_ids = request.POST.getlist('menu_items')
    if not menu_ids:
        messages.warning(request, _('No meals selected.'))
        return redirect('cafeteria:menu')

    menus = WeeklyMenu.objects.filter(pk__in=menu_ids, is_available=True).select_related('meal_type')
    total = sum(m.meal_type.price for m in menus)

    if request.user.balance < total:
        messages.error(request, _('Insufficient balance. Please charge your account.'))
        return redirect('cafeteria:menu')

    for menu in menus:
        # Prevent duplicate order for same meal
        if FoodOrder.objects.filter(student=request.user, menu_item=menu, status__in=['pending', 'confirmed']).exists():
            continue
        FoodOrder.objects.create(
            student=request.user,
            menu_item=menu,
            price=menu.meal_type.price,
            status='confirmed'
        )

    request.user.balance -= total
    request.user.save()
    Transaction.objects.create(
        user=request.user,
        amount=-total,
        type='withdraw',
        description=_('Food order for week starting %(date)s') % {'date': menus[0].week_start if menus else ''},
    )
    messages.success(request, _('Order placed successfully. Total: %(total)s Toman') % {'total': total})
    return redirect('cafeteria:my_orders')


@login_required
def my_orders(request):
    orders = FoodOrder.objects.filter(student=request.user).select_related(
        'menu_item', 'menu_item__meal_type'
    ).order_by('-ordered_at')
    return render(request, 'cafeteria/my_orders.html', {'orders': orders})


@login_required
def transactions(request):
    txs = Transaction.objects.filter(user=request.user)
    return render(request, 'cafeteria/transactions.html', {'transactions': txs})


@login_required
@user_passes_test(is_admin)
def admin_menu_manage(request):
    week_start = get_current_week_start()
    menus = WeeklyMenu.objects.filter(week_start=week_start).select_related('meal_type')
    meal_types = MealType.objects.filter(is_active=True)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            day = request.POST.get('day')
            meal_time = request.POST.get('meal_time')
            meal_type_id = request.POST.get('meal_type')
            try:
                meal_type = MealType.objects.get(pk=meal_type_id)
                WeeklyMenu.objects.update_or_create(
                    week_start=week_start,
                    day=int(day),
                    meal_time=meal_time,
                    defaults={'meal_type': meal_type, 'is_available': True}
                )
                messages.success(request, _('Menu item added.'))
            except Exception as e:
                messages.error(request, str(e))
        return redirect('cafeteria:admin_menu')

    return render(request, 'cafeteria/admin_menu.html', {
        'menus': menus,
        'meal_types': meal_types,
        'week_start': week_start,
        'days': WeeklyMenu.DayOfWeek.choices,
        'meal_times': WeeklyMenu.MealTime.choices,
    })


@login_required
@user_passes_test(is_admin)
def admin_orders(request):
    orders = FoodOrder.objects.select_related('student', 'menu_item', 'menu_item__meal_type').order_by('-ordered_at')[:100]
    return render(request, 'cafeteria/admin_orders.html', {'orders': orders})
