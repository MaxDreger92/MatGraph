from django.utils.safestring import mark_safe

from matching.models import MatchingReport
from django.contrib import admin

@admin.register(MatchingReport)
class MatchingReportAdmin(admin.ModelAdmin):

    list_display = ['date', 'type']
    list_filter = ('type', 'date')
    fields = (('type','date'), 'get_report')
    readonly_fields = ('date', 'type', 'get_report')

    def get_report(self, obj):
        return mark_safe(obj.report)
    get_report.short_description = 'Report'

    class Media:
        css = {
            'all': ('matching/css/admin_overrides.css',)
        }
