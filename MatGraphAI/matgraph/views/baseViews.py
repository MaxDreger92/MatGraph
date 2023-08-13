from dal import autocomplete
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
class MyProtectedView(LoginRequiredMixin, TemplateView):
    template_name = 'my_protected_view.html'
class AutocompleteView(autocomplete.Select2QuerySetView):
    model = None

    label_property = 'name'
    value_property = 'uid'

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return self.model.nodes.none()
        return self.model.nodes.filter(**{self.label_property + '__icontains': self.q})

    def get_result_value(self, result):
        return str(getattr(result, self.value_property))

    def get_result_label(self, result):
        return str(getattr(result, self.label_property))



@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def upload(request):
    return render(request, 'upload.html')

@login_required
def download(request):
    return render(request, 'download.html')

@login_required
def analyze(request):
    return render(request, 'analyze.html')

@login_required
def select_data(request):
    data_type = request.GET.get('data_type', None)
    if data_type == 'measurement':
        return redirect('measurement_query')
    elif data_type == 'materials':
        # Redirect to materials data page
        pass
    elif data_type == 'simulation':
        # Redirect to simulation data page
        pass
    elif data_type == 'fabrication':
        # Redirect to fabrication data page
        pass
    else:
        # Redirect to an error page or show a message if the selection is not valid
        pass


