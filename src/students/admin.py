from django.contrib import admin
from .models import Department, Student

# Register your models here.

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'year_one_amount', 'other_years_amount')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'ref_number', 'department', 'unique_code', 'created_at')
    list_filter = ('department', 'created_at')
    search_fields = ('full_name', 'ref_number', 'unique_code', 'email')
    readonly_fields = ('unique_code', 'created_at', 'updated_at')
