from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.translation import gettext as _
from django.db.models import Count, Q, Prefetch
from .models import Building, Room, Bed
from accounts.models import User
from accounts.views import is_admin


@login_required
def my_room(request):
    bed = getattr(request.user, 'bed', None)
    if not bed:
        messages.info(request, _('You are not assigned to any room yet.'))
        return render(request, 'dormitory/my_room.html', {'bed': None})

    roommates = Bed.objects.filter(
        room=bed.room, is_occupied=True
    ).select_related('student').order_by('bed_number')

    return render(request, 'dormitory/my_room.html', {
        'bed': bed,
        'room': bed.room,
        'building': bed.room.building,
        'roommates': roommates,
    })


@login_required
@user_passes_test(is_admin)
def building_list(request):
    section = request.GET.get('section', '')
    buildings = Building.objects.annotate(
        room_count=Count('rooms'),
        bed_count=Count('rooms__beds'),
        occupied=Count('rooms__beds', filter=Q(rooms__beds__is_occupied=True))
    )
    if section in ['brothers', 'sisters']:
        buildings = buildings.filter(section=section)
    return render(request, 'dormitory/building_list.html', {
        'buildings': buildings,
        'current_section': section,
    })


@login_required
@user_passes_test(is_admin)
def room_detail(request, room_id):
    room = get_object_or_404(
        Room.objects.select_related('building').prefetch_related(
            Prefetch('beds', queryset=Bed.objects.select_related('student').order_by('bed_number'))
        ),
        pk=room_id
    )
    return render(request, 'dormitory/room_detail.html', {'room': room})


@login_required
@user_passes_test(is_admin)
def assign_bed(request, bed_id):
    bed = get_object_or_404(Bed.objects.select_related('room', 'room__building'), pk=bed_id)
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        action = request.POST.get('action')

        if action == 'release':
            if bed.is_occupied:
                bed.release()
                messages.success(request, _('Bed released successfully.'))
            return redirect('dormitory:room_detail', room_id=bed.room_id)

        if student_id:
            try:
                student = User.objects.get(pk=student_id, role=User.Role.STUDENT)
                # Check gender match with section
                section = bed.room.building.section
                expected_gender = 'male' if section == 'brothers' else 'female'
                if student.gender != expected_gender:
                    messages.error(request, _('Student gender does not match building section.'))
                    return redirect('dormitory:room_detail', room_id=bed.room_id)

                # Release previous bed if any
                if hasattr(student, 'bed') and student.bed:
                    student.bed.release()

                if bed.is_occupied:
                    messages.error(request, _('This bed is already occupied.'))
                else:
                    bed.assign_student(student)
                    messages.success(request, _('Student assigned successfully.'))
            except User.DoesNotExist:
                messages.error(request, _('Student not found.'))
        return redirect('dormitory:room_detail', room_id=bed.room_id)

    # Available students of matching gender without bed
    section = bed.room.building.section
    gender = 'male' if section == 'brothers' else 'female'
    available_students = User.objects.filter(
        role=User.Role.STUDENT,
        gender=gender,
        is_active_student=True,
        bed__isnull=True
    ).order_by('last_name', 'first_name')

    return render(request, 'dormitory/assign_bed.html', {
        'bed': bed,
        'available_students': available_students,
    })


@login_required
@user_passes_test(is_admin)
def section_overview(request, section):
    if section not in ['brothers', 'sisters']:
        messages.error(request, _('Invalid section.'))
        return redirect('dormitory:building_list')

    buildings = Building.objects.filter(section=section).prefetch_related(
        Prefetch('rooms', queryset=Room.objects.prefetch_related(
            Prefetch('beds', queryset=Bed.objects.select_related('student'))
        ))
    )
    return render(request, 'dormitory/section_overview.html', {
        'buildings': buildings,
        'section': section,
        'section_display': _('Brothers Section') if section == 'brothers' else _('Sisters Section'),
    })
