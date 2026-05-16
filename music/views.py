from datetime import datetime

from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.views import generic as generic_view

from common.views import OrchestraDeleteMixin, OrchestraPermissionRequiredMixin

from .forms import MusicForm, FormationForm
from .models import Music, Formation
from django.db import models
import django_filters 
from django_filters.views import FilterView


class MusicTitleFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains', label='曲名', help_text='曲名で部分一致検索できます。')
    composer = django_filters.CharFilter(field_name='composer', lookup_expr='icontains', label='作曲者', help_text='作曲者で部分一致検索できます。')
    arranger = django_filters.CharFilter(field_name='arranger', lookup_expr='icontains', label='編曲者', help_text='編曲者で部分一致検索できます。')
    is_show = django_filters.ChoiceFilter(method='filter_is_show', label='非表示の曲も表示する', choices=[(True, '表示する'), (False, '非表示のみ表示')], empty_label='表示しない')

    def filter_is_show(self, queryset, name, value):
        if value == 'True':
            return queryset
        elif value == 'False':
            return queryset.filter(is_show=False)
        else:
            return queryset.filter(is_show=True)
    
    class Meta:
        model = Music
        fields = ['title', 'composer', 'arranger', 'is_show']


class MusicListView(OrchestraPermissionRequiredMixin, FilterView):
    template_name = 'music/music_list.html'
    model = Music
    paginate_by = 10  # 1ページあたりの表示件数
    filterset_class = MusicTitleFilter

    permission_required = "music.view_music"
    permission_redirect_url_name = "index"
    permission_denied_message = "曲の閲覧権限がありません。"

    detail_url_field = "title"
    list_display_fields = ['composer', 'arranger']

    def get_queryset(self):
        queryset = super().get_queryset()
        filterset = MusicTitleFilter(self.request.GET, queryset=queryset)
        return filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['show_past'] = self.request.GET.get('show_past', 'false')

        # データ総件数をコンテキストに追加
        context['total_count'] = self.get_queryset().count()
        context['model'] = self.model._meta.verbose_name
        context['add_url'] = reverse("music:music_create")
        context['list_display_fields'] = self.list_display_fields
        context['detail_url_field'] = self.detail_url_field
        return context


class MusicCreateView(OrchestraPermissionRequiredMixin, generic_view.CreateView):
    model = Music
    form_class = MusicForm
    template_name = "music/music_create.html"
    # 成功した時のURL
    success_url = reverse_lazy('music:music_list')
    permission_required = "music.add_music"
    permission_redirect_url_name = "music:music_list"
    permission_denied_message = "曲の追加権限がありません。"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # ログインユーザーを渡す
        date_param = self.request.GET.get('date', None)
        if date_param:
            try:
                kwargs['date'] = datetime.strptime(date_param, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                kwargs['date'] = None
        return kwargs

    # 投稿に成功した時に実行される処理
    def get_success_url(self):
        messages.success(self.request, '曲の追加に成功ました。')
        return reverse_lazy('music:music_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model'] = self.model._meta.verbose_name
        context['cancel_url'] = reverse("music:music_list")
        return context


class MusicUpdateView(OrchestraPermissionRequiredMixin, generic_view.UpdateView):
    model = Music
    form_class = MusicForm
    template_name = "music/music_create.html"
    pk_url_kwarg = 'pk'
    # 成功した時のURL
    success_url = reverse_lazy('music:music_list')

    permission_required = "music.change_music"
    permission_denied_message = "曲の編集権限がありません。"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # ログインユーザーを渡す
        return kwargs

    # 投稿に成功した時に実行される処理
    def get_success_url(self):
        messages.success(self.request, '曲の編集に成功ました。')
        return reverse_lazy('music:music_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['update'] = True
        context['pk'] = self.get_form_kwargs()
        context['model'] = self.model._meta.verbose_name
        context['cancel_url'] = reverse("music:music_detail", kwargs={"pk": self.kwargs.get('pk')})
        return context
    
    def get_permission_redirect_url(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")
        return reverse_lazy("music:music_detail", kwargs={"pk": pk})


class MusicDeleteView(OrchestraPermissionRequiredMixin, OrchestraDeleteMixin, generic_view.DeleteView):
    model = Music
    template_name = "music/music_delete.html"
    # 成功した時のURL
    success_url = reverse_lazy('music:music_list')

    permission_required = "music.delete_music"
    permission_denied_message = "曲の削除権限がありません。"

    def get_success_url(self):
        messages.success(self.request, '曲の削除に成功ました。')
        return reverse_lazy('music:music_list')
    
    def get_permission_redirect_url(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        return reverse_lazy("music:music_detail", kwargs={"pk": pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse_lazy('music:music_detail', kwargs={'pk': self.object.pk})
        return context
    

class MusicDetailView(OrchestraPermissionRequiredMixin, generic_view.DetailView):
    model = Music
    template_name = "music/music_detail.html"
    context_object_name = 'item'
    permission_required = "music.view_music"
    permission_redirect_url_name = "music:music_list"
    permission_denied_message = "曲の閲覧権限がありません。"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pk = self.kwargs.get('pk')  # ← URLから取得
        formation = Formation.objects.filter(music__id=pk)
        context["formation"] = formation
        return context


class FormationCreateView(OrchestraPermissionRequiredMixin, generic_view.CreateView):
    model = Formation
    form_class = FormationForm
    template_name = "music/formation_create.html"

    permission_required = "music.add_formation"
    permission_redirect_url_name = "music:music_detail"
    permission_denied_message = "編成の追加権限がありません。"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # ログインユーザーを渡す

        music = Music.objects.get(id=self.kwargs["pk"])
        kwargs['music'] = music
        return kwargs

    # 投稿に成功した時に実行される処理
    def get_success_url(self):
        messages.success(self.request, '曲の追加に成功ました。')
        return reverse_lazy('music:music_detail', kwargs={'pk': self.kwargs.get('pk')})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['music_id'] = self.kwargs.get('pk')
        context['model'] = self.model._meta.verbose_name
        context['cancel_url'] = reverse("music:music_detail", kwargs={"pk": self.kwargs.get('pk')})
        return context


class FormationUpdateView(OrchestraPermissionRequiredMixin, generic_view.UpdateView):
    model = Formation
    form_class = FormationForm
    template_name = "music/formation_create.html"
    pk_url_kwarg = "formation_id"

    permission_required = "music.change_formation"
    permission_redirect_url_name = "music:music_detail"
    permission_denied_message = "編成の編集権限がありません。"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # ログインユーザーを渡す

        music = Music.objects.get(id=self.kwargs["pk"])
        kwargs['music'] = music
        return kwargs

    # 投稿に成功した時に実行される処理
    def get_success_url(self):
        messages.success(self.request, '曲の追加に成功ました。')
        return reverse_lazy('music:music_detail', kwargs={'pk': self.kwargs.get('pk')})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['update'] = True
        context['music_id'] = self.kwargs.get('pk')
        context['model'] = self.model._meta.verbose_name
        context['cancel_url'] = reverse("music:music_detail", kwargs={"pk": self.kwargs.get('pk')})
        return context


class FormationDeleteView(OrchestraPermissionRequiredMixin, OrchestraDeleteMixin, generic_view.DeleteView):
    model = Formation
    template_name = "music/formation_delete.html"
    pk_url_kwarg = "formation_id"

    permission_required = "music.delete_formation"
    permission_redirect_url_name = "music:music_detail"
    permission_denied_message = "編成の削除権限がありません。"

    def get_success_url(self):
        messages.success(self.request, '編成の削除に成功ました。')
        return reverse_lazy('music:music_detail', kwargs={'pk': self.kwargs.get('pk')})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['music_id'] = self.kwargs.get('pk')
        context['cancel_url'] = reverse_lazy('music:music_detail', kwargs={'pk': self.kwargs.get('pk')})
        return context
    
    def get_permission_redirect_url(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")
        return reverse_lazy("music:music_detail", kwargs={"pk": pk})