from nonrelated_inlines.admin import NonrelatedStackedInline
from django.forms import formset_factory

from matgraph.forms.formsProperties import PropertyForm, PropertyFormsetCls
from matgraph.models.properties import Property


class TabularPropertyInline(NonrelatedStackedInline):

    # display no empty rows by default
    extra = 0

    # force tabular inline template (library only has NonrelatedStackedInline)
    template = 'admin/edit_inline/tabular.html'
    class Media:
        css = {
            'all': ('css/wide_inputs.css',)
        }

    form = PropertyForm
    formset = formset_factory(PropertyForm, formset = PropertyFormsetCls)
    verbose_name = 'Property'
    verbose_name_plural = 'Properties'

    # some random model to keep admin checks happy
    model = Property
    def get_form_queryset(self, obj):
        return Property.objects.none()


    def get_formset(self, request, obj=None, **kwargs):
        return formset_factory(PropertyForm, formset=PropertyFormsetCls)
        pass