from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.translation import gettext as _
from .models import Ticket, TicketReply
from .forms import TicketCreateForm, TicketReplyForm, AdminTicketReplyForm, AdminTicketStatusForm
from accounts.views import is_admin


@login_required
def ticket_list(request):
    if request.user.is_admin_user:
        tickets = Ticket.objects.select_related('student', 'room', 'assigned_to').all()
        status = request.GET.get('status')
        if status:
            tickets = tickets.filter(status=status)
        return render(request, 'tickets/admin_ticket_list.html', {'tickets': tickets})
    else:
        tickets = Ticket.objects.filter(student=request.user).select_related('room')
        return render(request, 'tickets/ticket_list.html', {'tickets': tickets})


@login_required
def ticket_create(request):
    if request.method == 'POST':
        form = TicketCreateForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.student = request.user
            if hasattr(request.user, 'bed') and request.user.bed:
                ticket.room = request.user.bed.room
            ticket.save()
            messages.success(request, _('Ticket created successfully.'))
            return redirect('tickets:detail', ticket_id=ticket.pk)
    else:
        form = TicketCreateForm()
    return render(request, 'tickets/ticket_create.html', {'form': form})


@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(
        Ticket.objects.select_related('student', 'room', 'assigned_to'),
        pk=ticket_id
    )
    # Permission check
    if not request.user.is_admin_user and ticket.student != request.user:
        messages.error(request, _('You do not have permission to view this ticket.'))
        return redirect('tickets:list')

    replies = ticket.replies.select_related('user')
    if not request.user.is_admin_user:
        replies = replies.filter(is_internal=False)

    reply_form = None
    status_form = None

    if request.method == 'POST':
        if 'reply' in request.POST:
            if request.user.is_admin_user:
                form = AdminTicketReplyForm(request.POST)
            else:
                form = TicketReplyForm(request.POST)
            if form.is_valid():
                reply = form.save(commit=False)
                reply.ticket = ticket
                reply.user = request.user
                reply.save()
                if request.user.is_admin_user and ticket.status == 'open':
                    ticket.status = 'in_progress'
                    ticket.save()
                messages.success(request, _('Reply added.'))
                return redirect('tickets:detail', ticket_id=ticket.pk)
        elif 'update_status' in request.POST and request.user.is_admin_user:
            status_form = AdminTicketStatusForm(request.POST, instance=ticket)
            if status_form.is_valid():
                status_form.save()
                messages.success(request, _('Ticket updated.'))
                return redirect('tickets:detail', ticket_id=ticket.pk)

    if request.user.is_admin_user:
        reply_form = AdminTicketReplyForm()
        status_form = AdminTicketStatusForm(instance=ticket)
    else:
        reply_form = TicketReplyForm()

    return render(request, 'tickets/ticket_detail.html', {
        'ticket': ticket,
        'replies': replies,
        'reply_form': reply_form,
        'status_form': status_form,
    })
