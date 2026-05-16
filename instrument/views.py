from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from common.views import OrchestraDeleteMixin, OrchestraPermissionRequiredMixin
from .models import Instrument, InstrumentPart
from user.models import TenantUser
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import InstrumentPartForm

# Create your views here.
class InstrumentPartListView(OrchestraPermissionRequiredMixin, ListView):
    model = InstrumentPart
    template_name = 'instrument/instrument_part_list.html'
    context_object_name = 'instrument_parts'
    paginate_by = 10  # Display 10 instruments per page
    permission_required = "instrument.view_instrumentpart"
    permission_redirect_url = reverse_lazy('instrument:instrument_part_list')
    permission_denied_message = "楽器パートの閲覧権限がありません。"


class InstrumentPartCreateView(OrchestraPermissionRequiredMixin, CreateView):
    model = InstrumentPart
    template_name = 'instrument/instrument_part_form.html'
    success_url = reverse_lazy('instrument:instrument_part_list')
    form_class = InstrumentPartForm

    permission_required = "instrument.add_instrumentpart"
    permission_redirect_url = reverse_lazy('instrument:instrument_part_list')
    permission_denied_message = "楽器パートの作成権限がありません。"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create'] = True
        return context


class InstrumentPartUpdateView(OrchestraPermissionRequiredMixin, UpdateView):
    model = InstrumentPart
    template_name = 'instrument/instrument_part_form.html'

    form_class = InstrumentPartForm
    permission_required = "instrument.change_instrumentpart"
    permission_redirect_url = reverse_lazy('instrument:instrument_part_list')
    permission_denied_message = "楽器パートの編集権限がありません。"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        # ownerでない場合は、一覧にリダイレクト
        if not request.user == self.object.owner:
            return redirect('instrument:instrument_part_list')

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create'] = False
        return context
    
    def get_success_url(self):
        success_url = reverse_lazy('instrument:instrument_part_detail', kwargs={'pk': self.object.pk})
        return success_url


class InstrumentPartDeleteView(OrchestraPermissionRequiredMixin, OrchestraDeleteMixin, DeleteView):
    model = InstrumentPart
    template_name = 'instrument/instrument_part_delete.html'
    success_url = reverse_lazy('instrument:instrument_part_list')

    permission_required = "instrument.delete_instrumentpart"
    permission_redirect_url = reverse_lazy('instrument:instrument_part_list')
    permission_denied_message = "楽器パートの削除権限がありません。"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        # ownerでない場合は、一覧にリダイレクト
        if not request.user == self.object.owner:
            return redirect('instrument:instrument_part_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse_lazy('instrument:instrument_part_detail', kwargs={'pk': self.object.pk})
        return context


class InstrumentPartDetailView(OrchestraPermissionRequiredMixin, DetailView):
    model = InstrumentPart
    template_name = 'instrument/instrument_part_detail.html'
    context_object_name = 'instrument_part'

    permission_required = "instrument.view_instrumentpart"
    permission_redirect_url = reverse_lazy('instrument:instrument_part_list')
    permission_denied_message = "楽器パートの閲覧権限がありません。"

    def get_member(self):
        members_queryset = TenantUser.objects.filter(
            tenant=self.object.tenant, 
            is_active=True,
            instrument__in=self.object.instrument.all()
            )
        
        return members_queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['members'] = self.get_member()
        return context