from django.contrib import admin
from account.models import Role, Department, OrgType, Profile, Team, PasswordResetOTP, Invitation

admin.site.register(OrgType)
admin.site.register(Invitation)
admin.site.register(PasswordResetOTP)

# Register your models here.
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['role_name', 'group']  # Assuming 'name' is a field in the Role model

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('department_name', 'created_by')

@admin.register(Profile)
class PeoplesAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'profile_image', 'department', 'address', 'country']

@admin.register(Team)
class MembersAdmin(admin.ModelAdmin):
    fields = ('user_id', 'name', 'role_id')
    list_display = ('name', 'role_id', 'get_user_id')

    def get_user_id(self, obj):
        return ", ".join([d.username for d in obj.user_id.all()])

    get_user_id.short_description = 'User ID'
    get_user_id.admin_order_field = 'user_id'
