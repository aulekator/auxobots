from django.contrib import admin
from .models import Meeting

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('selected_time', 'user_email', 'created_at', 'formatted_created_at')
    list_filter = ('created_at',)
    search_fields = ('selected_time', 'user_email')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)

    def formatted_created_at(self, obj):
        return obj.created_at.strftime('%d %b %Y %I:%M %p')
    formatted_created_at.short_description = 'Created At'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(None)