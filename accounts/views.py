from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.translation import gettext as _
from django.db.models import Sum, Count, Q
from .forms import LoginForm, StudentRegistrationForm, ProfileUpdateForm
from .models import User
from dormitory.models import Bed, Room, Building
from tickets.models import Ticket
from cafeteria.models import FoodOrder, Transaction


def is_admin(user):
    return user.is_authenticated and user.is_admin_user


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, _('Welcome back!'))
            return redirect('accounts:dashboard')
        messages.error(request, _('Invalid username or password.'))
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, _('You have been logged out.'))
    return redirect('accounts:login')


@login_required
def dashboard(request):
    user = request.user
    context = {'user': user}

    if user.is_admin_user:
        context.update({
            'total_students': User.objects.filter(role=User.Role.STUDENT).count(),
            'total_rooms': Room.objects.count(),
            'occupied_beds': Bed.objects.filter(is_occupied=True).count(),
            'open_tickets': Ticket.objects.filter(status__in=['open', 'in_progress']).count(),
            'pending_orders': FoodOrder.objects.filter(status='pending').count(),
            'recent_tickets': Ticket.objects.select_related('student')[:5],
            'recent_orders': FoodOrder.objects.select_related('student', 'menu_item')[:5],
        })
        return render(request, 'accounts/admin_dashboard.html', context)

    # Student dashboard
    bed = getattr(user, 'bed', None)
    roommates = []
    if bed:
        roommates = Bed.objects.filter(
            room=bed.room, is_occupied=True
        ).exclude(student=user).select_related('student')

    context.update({
        'bed': bed,
        'roommates': roommates,
        'my_tickets': Ticket.objects.filter(student=user)[:5],
        'my_orders': FoodOrder.objects.filter(student=user).select_related('menu_item')[:5],
        'recent_transactions': Transaction.objects.filter(user=user)[:5],
    })
    return render(request, 'accounts/student_dashboard.html', context)


@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Profile updated successfully.'))
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def admin_students(request):
    students = User.objects.filter(role=User.Role.STUDENT).select_related('bed', 'bed__room', 'bed__room__building')
    section = request.GET.get('section')
    if section in ['brothers', 'sisters']:
        gender = 'male' if section == 'brothers' else 'female'
        students = students.filter(gender=gender)
    q = request.GET.get('q')
    if q:
        students = students.filter(
            Q(username__icontains=q) | Q(first_name__icontains=q) |
            Q(last_name__icontains=q) | Q(student_id__icontains=q)
        )
    return render(request, 'accounts/admin_students.html', {'students': students})


@login_required
@user_passes_test(is_admin)
def adjust_balance(request, user_id):
    student = get_object_or_404(User, pk=user_id, role=User.Role.STUDENT)
    if request.method == 'POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description', '')
        try:
            amount = int(amount)
            student.balance += amount
            student.save()
            Transaction.objects.create(
                user=student,
                amount=amount,
                type='deposit' if amount > 0 else 'adjustment',
                description=description or _('Admin balance adjustment'),
                created_by=request.user
            )
            messages.success(request, _('Balance updated successfully.'))
        except (ValueError, TypeError):
            messages.error(request, _('Invalid amount.'))
        return redirect('accounts:admin_students')
    return render(request, 'accounts/adjust_balance.html', {'student': student})


def set_language(request):
    from django.utils import translation
    lang = request.GET.get('lang', 'fa')
    if lang in ['fa', 'en']:
        translation.activate(lang)
        request.session['django_language'] = lang
    next_url = request.GET.get('next', '/')
    return redirect(next_url)


def set_theme(request):
    theme = request.GET.get('theme', 'light')
    if theme in ['light', 'dark']:
        request.session['theme'] = theme
    next_url = request.GET.get('next', '/')
    return redirect(next_url)
