from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import DepartmentAdmin, CustomUser

class DepartmentAdminInline(admin.StackedInline):
    model = DepartmentAdmin
    can_delete = True
    verbose_name_plural = 'Department Admin'
    extra = 0

class CustomUserAdmin(UserAdmin):
    inlines = (DepartmentAdminInline, )
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'role', 'get_department')
    
    def get_department(self, obj):
        return obj.department.name if obj.department else '-'
    get_department.short_description = 'Department'

    def get_queryset(self, request):
        return CustomUser.objects.all()

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(DepartmentAdmin)
class DepartmentAdminAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'is_active', 'created_at')
    list_filter = ('department', 'is_active')
    search_fields = ('user__email', 'department__name')
    date_hierarchy = 'created_at'
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return ('user', 'department')
        return ()
