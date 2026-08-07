from django.contrib import admin
from .models import Building, Room, Bed


class BedInline(admin.TabularInline):
    model = Bed
    extra = 0
    fields = ('bed_number', 'is_occupied', 'student')


class RoomInline(admin.TabularInline):
    model = Room
    extra = 0
    fields = ('number', 'floor', 'capacity', 'is_active')


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ('name', 'section', 'floors', 'is_active')
    list_filter = ('section', 'is_active')
    search_fields = ('name',)
    inlines = [RoomInline]


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'floor', 'capacity', 'occupied_beds', 'is_active')
    list_filter = ('building__section', 'building', 'floor', 'is_active')
    search_fields = ('number', 'building__name')
    inlines = [BedInline]


@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_occupied', 'student')
    list_filter = ('is_occupied', 'room__building__section')
    search_fields = ('room__number', 'student__username', 'student__student_id')
    raw_id_fields = ('student',)
