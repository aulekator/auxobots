from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.http import urlencode
from .models import (BotConfig, DemoBotConfig, ExtraConfig, DemoTrade, LiveTrade, DemoBotLog, LiveBotLog)

@admin.register(DemoBotLog)
class DemoBotLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'colored_level', 'user_link', 'short_message')
    list_filter = ('level', 'user', 'timestamp')
    search_fields = ('user__username', 'user__email', 'message')
    readonly_fields = ('user', 'timestamp', 'level', 'message')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)
    list_per_page = 1000

    def has_add_permission(self, request):
        return False 

    def has_change_permission(self, request, obj=None):
        return False  # Immutable logs

    def colored_level(self, obj):
        color_map = {
            'INFO': '#28a745',    
            'WARN': '#ffc107',     
            'WARNING': '#ffc107',
            'ERROR': '#dc3545',    
        }
        bg_color = color_map.get(obj.level, '#6c757d')
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 0.85em;">{}</span>',
            bg_color, obj.level
        )
    colored_level.short_description = "Level"

    def user_link(self, obj):
        url = reverse("admin:auth_user_change", args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = "User"
    user_link.admin_order_field = 'user__username'

    def short_message(self, obj):
        msg = obj.message.strip()
        if len(msg) > 80:
            return msg[:80] + '...'
        return msg
    short_message.short_description = "Message"


@admin.register(DemoBotConfig)
class DemoBotConfigAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user_link', 'instrument', 'risk_level', 'is_active', 'total_pnl', 'win_rate', 'total_trades', 'updated_at')
    list_filter = ('is_active', 'risk_level', 'instrument', 'exchange')
    search_fields = ('user__username', 'user__email', 'instrument')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('User & Status', {'fields': ('user', 'is_active', 'exchange')}),
        ('Trading Settings', {'fields': ('instrument', 'risk_level', 'custom_quantity')}),
        ('API Keys (Demo)', {'fields': ('demo_api_key', 'demo_api_secret'), 'classes': ('collapse',)}),
        ('Performance', {'fields': ('total_pnl', 'realized_pnl', 'unrealized_pnl', 'win_rate', 'total_trades')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    def user_link(self, obj):
        url = reverse("admin:auth_user_change", args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = "User"
    user_link.admin_order_field = 'user__username'


@admin.register(BotConfig)
class BotConfigAdmin(admin.ModelAdmin):
    list_display = ('pk','user_link', 'exchange', 'instrument', 'risk_level', 'is_active', 'total_pnl', 'total_trades')
    list_filter = ('is_active', 'exchange', 'risk_level', 'instrument')
    search_fields = ('user__username', 'user__email', 'instrument')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('User & Status', {'fields': ('user', 'exchange', 'is_active')}),
        ('Trading Pair', {'fields': ('instrument', 'risk_level', 'custom_quantity')}),
        ('Live API Keys', {'fields': ('api_key', 'api_secret'), 'classes': ('collapse',)}),
        ('Performance', {'fields': ('total_pnl', 'realized_pnl', 'unrealized_pnl', 'win_rate', 'total_trades')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    def user_link(self, obj):
        url = reverse("admin:auth_user_change", args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = "User"


@admin.register(ExtraConfig)
class ExtraConfigAdmin(admin.ModelAdmin):
    list_display = ('user_link', 'price_sol', 'price_eth', 'price_btc', 'updated_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('updated_at',)

    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Approximate Mid Prices (Used for Grid Centering)', {
            'fields': (
                'price_sol', 'price_doge', 'price_eth', 'price_btc',
                'price_bnb', 'price_ada', 'price_xrp', 'price_pepe', 'price_shib',
            )
        }),
        ('Last Updated', {'fields': ('updated_at',)}),
    )

    def user_link(self, obj):
        url = reverse("admin:auth_user_change", args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = "User"


@admin.register(DemoTrade)
class DemoTradeAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user_link', 'instrument', 'colored_side', 'price', 'quantity')
    list_filter = ('instrument', 'side', 'user')
    search_fields = ('user__username', 'instrument')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)
    list_per_page = 50

    def colored_side(self, obj):
        color = '#28a745' if obj.side == 'BUY' else '#dc3545'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.side
        )
    colored_side.short_description = "Side"

    def user_link(self, obj):
        url = reverse("admin:auth_user_change", args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = "User"


@admin.register(LiveTrade)
class LiveTradeAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user_link', 'instrument', 'colored_side', 'price', 'quantity')
    list_filter = ('instrument', 'side', 'user')
    search_fields = ('user__username', 'instrument')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)
    list_per_page = 50

    def colored_side(self, obj):
        color = '#28a745' if obj.side == 'BUY' else '#dc3545'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.side
        )
    colored_side.short_description = "Side"

    def user_link(self, obj):
        url = reverse("admin:auth_user_change", args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = "User"


@admin.register(LiveBotLog)
class LiveBotLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'colored_level', 'user_link', 'short_message')
    list_filter = ('level', 'user', 'timestamp')
    search_fields = ('user__username', 'user__email', 'message')
    readonly_fields = ('user', 'timestamp', 'level', 'message')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)
    list_per_page = 1000

    def has_add_permission(self, request):
        return False 

    def has_change_permission(self, request, obj=None):
        return False  # Immutable logs

    def colored_level(self, obj):
        color_map = {
            'INFO': '#28a745',    
            'WARN': '#ffc107',     
            'WARNING': '#ffc107',
            'ERROR': '#dc3545',    
        }
        bg_color = color_map.get(obj.level, '#6c757d')
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 0.85em;">{}</span>',
            bg_color, obj.level
        )
    colored_level.short_description = "Level"

    def user_link(self, obj):
        url = reverse("admin:auth_user_change", args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = "User"
    user_link.admin_order_field = 'user__username'

    def short_message(self, obj):
        msg = obj.message.strip()
        if len(msg) > 80:
            return msg[:80] + '...'
        return msg
    short_message.short_description = "Message"
