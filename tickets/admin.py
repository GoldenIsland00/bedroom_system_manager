from django.contrib import admin
from .models import Ticket, TicketReply


class TicketReplyInline(admin.TabularInline):
    model = TicketReply
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'student', 'category', 'priority', 'status', 'created_at')
    list_filter = ('status', 'priority', 'category', 'created_at')
    search_fields = ('title', 'student__username', 'student__student_id')
    raw_id_fields = ('student', 'room', 'assigned_to')
    inlines = [TicketReplyInline]


@admin.register(TicketReply)
class TicketReplyAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'user', 'is_internal', 'created_at')
    list_filter = ('is_internal', 'created_at')
