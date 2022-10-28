from django.contrib import admin
from .models import User, VerificationCode
# Register your models here.


class UserAdmin(admin.ModelAdmin):
    list_display=['phonenumber', 'phonenumber_verified', 'is_active', 'is_superuser']
    list_filter=['phonenumber_verified', 'is_active', 'is_superuser'] 
admin.site.register(User, UserAdmin)







class VerificationCodeAdmin(admin.ModelAdmin):
    list_display=['code', 'user', 'active']
    list_filter=['active', 'date']

admin.site.register(VerificationCode)