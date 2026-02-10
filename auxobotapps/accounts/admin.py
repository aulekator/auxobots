from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'referral_code', 'refered_by', 'date_joined', 'is_active')
    search_fields = ('email', 'username', 'referral_code', 'refered_by')
    list_filter = ('is_active', 'date_joined')
    readonly_fields = ('referral_code', 'date_joined', 'refered_by', 'binance_api_key', 'binance_api_secret', 'password')
