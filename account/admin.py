from django.contrib import admin

from account.models import CustomUser
from django.contrib.auth.admin import UserAdmin



# Register your models here.
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['id','first_name','last_name','username','email','role','is_active','is_staff','is_superuser','date_joined']
    fieldsets = UserAdmin.fieldsets + (
            (None, {'fields': ('role','gender','branch','mobile','batch_year','image')}),
    )
    add_fieldsets =  (
            (None, {'fields': ('role','first_name','email','gender','branch','mobile','image','password1','password2'   )}),
    )

admin.site.register(CustomUser,CustomUserAdmin)
