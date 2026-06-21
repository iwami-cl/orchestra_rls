import uuid
from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from .models import Music, Formation
from user.models import TenantUser
from django_select2.forms import Select2MultipleWidget


class MusicForm(forms.ModelForm):
    class Meta:
        model = Music
        fields = ('title', 'composer', 'arranger', 'note', 'is_show',)
        help_texts = {
            'title': '楽曲のタイトルを入力してください\n最大255文字まで',
            'composer': '作曲者の名前を入力してください\n最大255文字まで',
            'arranger': '編曲者の名前を入力してください\n最大255文字まで',
            'note': '備考や特記事項を入力してください\n複数行入力可能',
            'is_show': 'チェックを外すとシステムに表示されなくなります。\n演奏終了後など、今後の演奏予定がない場合にチェックを外してください。',
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:  # ユーザー情報を利用可能
            instance.tenant = self.user.tenant  # ユーザー関連情報を保存
        if commit:
            instance.save()
        return instance

    # フォームを綺麗にするための記載
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # ユーザーを取得
        super().__init__(*args, **kwargs)
        # for field in self.fields.values():
        #     field.widget.attrs['class'] = 'form-control'


class InstrumentCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    option_template_name = 'widgets/instrument_option.html'

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        option['label_instance'] = value.instance.instrument.id
        return option
    
    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        # attrs['class'] = 'instrument-checkbox-select-multiple'
        return attrs

class FormationUsersMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        if obj.instrument:
            return f"{obj}（パート: {obj.instrument.name}）"
        else:
            return str(obj)


class FormationForm(forms.ModelForm):
    users = FormationUsersMultipleChoiceField(
        queryset=TenantUser.objects.order_by('username'),
        widget=Select2MultipleWidget,
        label='メンバー選択',
    )

    class Meta:
        model = Formation
        fields = ('instrument', 'section', 'users')
        labels = {
            'instrument': '編成楽器',
            'section': 'セクション',
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.music:
            instance.music = self.music  # ユーザー関連情報を保存
        if self.user:  # ユーザー情報を利用可能
            instance.tenant = self.user.tenant  # ユーザー関連情報を保存
        if commit:
            instance.save()
            self.save_m2m()
        return instance

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # ユーザーを取得
        self.music = kwargs.pop('music', None)  # ユーザーを取得
        super().__init__(*args, **kwargs)