from django import forms

from user.models import TenantUser
from .models import InstrumentPart, Instrument
from django_select2.forms import Select2MultipleWidget


class InstrumentCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    option_template_name = 'widgets/instrument_option.html'

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        option['label_instance'] = value.instance.id
        return option
    
    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        # attrs['class'] = 'instrument-checkbox-select-multiple'
        return attrs
    

class InstrumentMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.name} ({obj.jp_name})"


class InstrumentPartForm(forms.ModelForm):
    instrument = InstrumentMultipleChoiceField(
        queryset=Instrument.objects.all(),
        widget=Select2MultipleWidget,
        label='楽器選択',
    )
    
    # ownerはドロップダウンリストにする
    owner = forms.ModelChoiceField(
        queryset=TenantUser.objects.all(),
        label='担当者',
        required=True,
    )

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.tenant = instance.owner.tenant  # ユーザー関連情報を保存
        if commit:
            instance.save()
            self.save_m2m()
        return instance

    class Meta:
        model = InstrumentPart
        fields = ['instrument', 'part_name', 'owner']
        widgets = {
            'part_name': forms.TextInput(attrs={'class': 'form-control'}),
        }