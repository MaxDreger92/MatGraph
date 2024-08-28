import json

from django.contrib import admin
from django.utils.safestring import mark_safe
from django import forms
from sdl.models import ExperimentModel

class PrettyJSONWidget(forms.Textarea):
    def format_value(self, value):
        try:
            # Convert the JSON string to a pretty-printed format
            value = json.dumps(json.loads(value), indent=4, sort_keys=True)
        except (TypeError, ValueError):
            pass  # If value is not valid JSON, just return it as-is
        return value

    def render(self, name, value, attrs=None, renderer=None):
        # Call the parent render method to display the JSON data
        formatted_value = self.format_value(value)
        return mark_safe(super().render(name, formatted_value, attrs, renderer))


@admin.register(ExperimentModel)
class ExperimentModelAdmin(admin.ModelAdmin):

    list_display = ['id', 'date_created', 'date_updated', "status"]
    list_filter = ('id', 'date_created', 'date_updated', 'status')
    fields = (('id', 'date_created', "status"), 'description', 'remarks', 'results', 'opentrons', 'labware', 'chemicals', 'biologic', 'arduino', 'arduino_relays', 'workflow')
    readonly_fields = ('id', 'date_created', 'date_updated', 'remarks', "description", 'results')

    # Override formfield_for_dbfield to apply the custom widget
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in ['opentrons', 'labware', 'chemicals', 'biologic', 'arduino', 'workflow', 'results']:
            kwargs['widget'] = PrettyJSONWidget(attrs={'rows': 10, 'cols': 80})
        return super().formfield_for_dbfield(db_field, **kwargs)

    class Media:
        css = {
            'all': ('matching/css/admin_overrides.css',)
        }