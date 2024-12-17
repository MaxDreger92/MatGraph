import os
import tempfile

from django.forms import modelformset_factory

from .csv_split import load_and_split_file  # Import your csv_split function here
from .forms import ExcelUploadForm
from .ingestionquery import ingest_data


def upload_file(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']

            # Create a temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = os.path.join(temp_dir, file.name)

                # Save the uploaded file to the temporary directory
                with open(temp_path, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)

                # Process the file with csv_split
                load_and_split_file(temp_path)
                ingest_data(temp_path)

                # Respond with success or list of generated files
                return HttpResponse("File processed and CSVs stored.")
    else:
        form = ExcelUploadForm()
    return render(request, 'schema_ingestion/upload.html', {'form': form})


# Views
from django.http import HttpResponse

from django.shortcuts import render, redirect
from django.views import View
from .forms import SynthesisStepForm, MaterialForm
from .models import Material

from django.views.generic import TemplateView

class CreateSynthesisStepView(View):
    template_name = "synthesis_step_tab.html"

    @staticmethod
    def get_formsets(data=None):
        precursor_formset = modelformset_factory(
            Material, form=MaterialForm, extra=1, can_delete=True
        )
        step_form = SynthesisStepForm(data=data)
        return step_form, precursor_formset

    def get(self, request, *args, **kwargs):
        step_form, precursor_formset = self.get_formsets()
        return render(request, self.template_name, {
            'step_form': step_form,
            'precursor_formset': precursor_formset,
        })

    def post(self, request, *args, **kwargs):
        step_form, precursor_formset = self.get_formsets(data=request.POST)

        if step_form.is_valid() and precursor_formset.is_valid():
            synthesis_step = step_form.save()

            # Save precursor materials
            for form in precursor_formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    material = form.save()
                    synthesis_step.precursor_materials.add(material)

            return redirect('success_url')  # Replace with your success URL

        # If not valid, re-render with errors
        return render(request, self.template_name, {
            'step_form': step_form,
            'precursor_formset': precursor_formset,
        })

class TabbedFormsView(TemplateView):
    template_name = "tabbed_forms.html"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # No data parameter, because this is GET
        step_form, precursor_formset = CreateSynthesisStepView.get_formsets()

        tabs = [
            {
                'id': 'tab1',
                'name': 'Synthesis Step',
                'step_form': step_form,
                'precursor_formset': precursor_formset,
                'partial_template': 'synthesis_step_tab.html'
            },
        ]

        context['tabs'] = tabs
        return context

    def post(self, request, *args, **kwargs):
        active_tab = request.POST.get('active_tab', 'tab1')

        if active_tab == 'tab1':
            step_form, precursor_formset = CreateSynthesisStepView.get_formsets(data=request.POST)

            # Validate forms
            if (step_form.is_valid() and precursor_formset.is_valid()):

                # Perform save logic
                synthesis_step = step_form.save()
                # Save related objects from formsets...

                return redirect('success_url')

            # If not valid, re-render tabs
            tabs = [
                {
                    'id': 'tab1',
                    'name': 'Synthesis Step',
                    'step_form': step_form,
                    'precursor_formset': precursor_formset,
                    'partial_template': 'synthesis_step_tab.html'
                },
            ]
            return render(request, self.template_name, {'tabs': tabs, 'active_tab': 'tab1'})

        return super().post(request, *args, **kwargs)