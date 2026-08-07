from django.contrib import admin
from .models import MealType, WeeklyMenu, FoodOrder, Transaction


@admin.register(MealType)
class MealTypeAdmin(admin.ModelAdmin):
    list_display = ('name_fa', 'name_en', 'price', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name_fa', 'name_en')


@admin.register(WeeklyMenu)
class WeeklyMenuAdmin(admin.ModelAdmin):
    list_display = ('week_start', 'get_day_display', 'meal_time', 'meal_type', 'is_available')
    list_filter = ('week_start', 'day', 'meal_time', 'is_available')
    search_fields = ('meal_type__name_fa',)


@admin.register(FoodOrder)
class FoodOrderAdmin(admin.ModelAdmin):
    list_display = ('student', 'menu_item', 'status', 'price', 'ordered_at')
    list_filter = ('status', 'ordered_at')
    search_fields = ('student__username', 'student__student_id')
    raw_id_fields = ('student', 'menu_item')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'type', 'description', 'created_at')
    list_filter = ('type', 'created_at')
    search_fields = ('user__username', 'user__student_id')
    raw_id_fields = ('user', 'created_by')
