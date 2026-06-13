import datetime
from urllib.parse import urlparse
from django import forms

from .models import Schedule
from music.models import Music
from django_select2.forms import Select2MultipleWidget


class TimeInput15Min(forms.TimeInput):
    def __init__(self, attrs=None, format=None):
        super().__init__(attrs=attrs, format=format)
        if self.attrs is None:
            self.attrs = {}
        self.attrs['step'] = '900'


class ScheduleForm(forms.ModelForm):
    music = forms.ModelMultipleChoiceField(
        queryset=Music.objects.filter(is_show=True).order_by('title'),
        widget=Select2MultipleWidget,
        required=False,
        label="演奏曲")
    
    start = forms.TimeField(
        widget=TimeInput15Min(format='%H:%M', attrs={'type': 'time'}),
        input_formats=['%H:%M'],
        label="開始時間",
        help_text="24時間表記で入力してください（例: 14:30）"
    )
    end = forms.TimeField(
        widget=TimeInput15Min(format='%H:%M', attrs={'type': 'time'}),
        input_formats=['%H:%M'],
        label="終了時間",
        help_text="24時間表記で入力してください（例: 16:00）"
    )

    # カレンダーウィジェットを使用するためのフィールド定義(年は4桁、月と日は2桁で入力)
    date = forms.DateField(
        widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        input_formats=['%Y-%m-%d'],
        label="日付",
        help_text="日付を入力してください（例: 2024-06-30）",
    )

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:  # ユーザー情報を利用可能
            instance.tenant = self.user.tenant  # ユーザー関連情報を保存
        if commit:
            instance.save()
            self.save_m2m()
        return instance
    
    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start')
        end = cleaned_data.get('end')

        if start and end and start >= end:
            self.add_error("end", "終了時間は開始時間より後にしてください")

        return cleaned_data
    
    def clean_place_map_url(self):
        place_map_url = self.cleaned_data.get('place_map_url')
        if place_map_url:
            parsed_url = urlparse(place_map_url)
            if not all([parsed_url.scheme, parsed_url.netloc]):
                raise forms.ValidationError("有効なURLを入力してください。")
        return place_map_url

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # ユーザーを取得
        date = kwargs.pop('date', None)  # 日付を取得

        today = datetime.date.today()

        super().__init__(*args, **kwargs)
        music_queryset = Music.objects.filter(tenant=self.user.tenant, is_show=True) if self.user else None


        # 新規作成のときはdateパラメータを初期値として設定する
        if self.instance._state.adding:
        
            # dateの型変換（文字列の場合はdatetime.date型に変換）
            if isinstance(date, str):
                try:
                    date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
                except ValueError:
                    date = None

            self.fields['date'].initial = date if date else today
        else:
            self.fields['date'].initial = self.instance.date
            self.fields['start'].initial = self.instance.start
            self.fields['end'].initial = self.instance.end

            # 更新の時は既に選択されている楽曲を含めるため、インスタンスがある場合はその楽曲もクエリセットに含める
            selected_music = self.instance.music.all()
            music_queryset = (music_queryset | selected_music).distinct() if music_queryset else selected_music
        

        if music_queryset:
            self.fields['music'].queryset = music_queryset
        else:
            del self.fields['music']
    
    class Meta:
        model = Schedule
        # fields = ('title', 'date', 'start', 'end', 'place', 'place_map_url', 'note', 'music')
        fields = ('title', 'date', 'start', 'end', 'place', 'note', 'music')

        help_texts = {
            'music': '演奏曲を選択してください。（複数選択可）',
            #'place_map_url': 'Google MapsのURLを入力してください。',
        }