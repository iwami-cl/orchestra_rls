# myapp/templatetags/breadcrumbs.py
from django import template
from django.urls import resolve, reverse

register = template.Library()

HOME = {'name': '<i class="fa-solid fa-house"></i>', 'url': 'index'}
MUSIC_LIST = {'name': '曲一覧', 'url': 'music:music_list'}
MUSIC_DETAIL = {'name': '曲詳細', 'url': 'music:music_detail', 'kwargs': ['pk']}
MUSIC_CREATE = {'name': '曲登録', 'url': 'music:music_create'}
MUSIC_UPDATE = {'name': '曲編集', 'url': 'music:music_update', 'kwargs': ['pk']}
MUSIC_DELETE = {'name': '曲削除', 'url': 'music:music_delete', 'kwargs': ['pk']}
FORMATION_CREATE = {'name': '編成登録', 'url': 'music:formation_create', 'kwargs': ['pk']}
FORMATION_UPDATE = {'name': '編成編集', 'url': 'music:formation_update', 'kwargs': ['pk', 'formation_id']}
FORMATION_DELETE = {'name': '編成削除', 'url': 'music:formation_delete', 'kwargs': ['pk', 'formation_id']}
USER_LIST = {'name': '団員一覧', 'url': 'user:user_list'}
USER_DETAIL = {'name': '団員詳細', 'url': 'user:user_detail', 'kwargs': ['pk']}
INSTRUMENT_PART_LIST = {'name': 'パート一覧', 'url': 'instrument:instrument_part_list'}
INSTRUMENT_PART_DETAIL = {'name': 'パート詳細', 'url': 'instrument:instrument_part_detail', 'kwargs': ['pk']}
LEAVE_APPLICATION_LIST = {'name': '休団申請一覧', 'url': 'user:leave_application_list'}
LEAVE_APPLICATION_DETAIL = {'name': '休団申請詳細', 'url': 'user:leave_application_detail', 'kwargs': ['pk']}
LEAVE_APPLICATION_CREATE = {'name': '休団申請作成', 'url': 'user:leave_application_create'}
LEAVE_APPLICATION_UPDATE = {'name': '休団申請更新', 'url': 'user:leave_application_update', 'kwargs': ['pk']}
LEAVE_APPLICATION_DELETE = {'name': '休団申請削除', 'url': 'user:leave_application_delete', 'kwargs': ['pk']}
SCHEDULE_LIST = {'name': 'スケジュール一覧', 'url': 'schedule:schedule_list'}
SCHEDULE_DETAIL = {'name': 'スケジュール詳細', 'url': 'schedule:schedule_detail', 'kwargs': ['pk']}
SCHEDULE_CREATE = {'name': 'スケジュール作成', 'url': 'schedule:schedule_create'}
SCHEDULE_UPDATE = {'name': 'スケジュール編集', 'url': 'schedule:schedule_update', 'kwargs': ['pk']}
SCHEDULE_DELETE = {'name': 'スケジュール削除', 'url': 'schedule:schedule_delete', 'kwargs': ['pk']}
SCHEDULE_LOG_LIST = {'name': '活動履歴一覧', 'url': 'schedule:schedule_log_list'}
SCHEDULE_LOG_DETAIL = {'name': '活動履歴詳細', 'url': 'schedule:schedule_log_detail', 'kwargs': ['pk']}
SCHEDULE_LOG_DELETE = {'name': '活動履歴削除', 'url': 'schedule:schedule_log_delete', 'kwargs': ['pk']}
ATTENDANCE_CHECK = {'name': '出欠確認', 'url': 'schedule:attendance_check', 'kwargs': ['pk']}

BREAD_DICT = {
    'index': [HOME],
    'music:music_list': [HOME, MUSIC_LIST],
    'music:music_detail': [HOME, MUSIC_LIST, MUSIC_DETAIL],
    'music:music_create': [HOME, MUSIC_LIST, MUSIC_CREATE],
    'music:music_update': [HOME, MUSIC_LIST, MUSIC_DETAIL, MUSIC_UPDATE],
    'music:music_delete': [HOME, MUSIC_LIST, MUSIC_DETAIL, MUSIC_DELETE],
    'music:formation_create': [HOME, MUSIC_LIST, MUSIC_DETAIL, FORMATION_CREATE],
    'music:formation_update': [HOME, MUSIC_LIST, MUSIC_DETAIL, FORMATION_UPDATE],
    'music:formation_delete': [HOME, MUSIC_LIST, MUSIC_DETAIL, FORMATION_UPDATE, FORMATION_DELETE],
    'user:user_list': [HOME, USER_LIST],
    'user:user_detail': [HOME, USER_LIST, USER_DETAIL],
    'instrument:instrument_part_list': [HOME, INSTRUMENT_PART_LIST],
    'instrument:instrument_part_detail': [HOME, INSTRUMENT_PART_LIST, INSTRUMENT_PART_DETAIL],
    'user:leave_application_list': [HOME, LEAVE_APPLICATION_LIST],
    'user:leave_application_detail': [HOME, LEAVE_APPLICATION_LIST, LEAVE_APPLICATION_DETAIL],
    'user:leave_application_create': [HOME, LEAVE_APPLICATION_LIST, LEAVE_APPLICATION_CREATE],
    'user:leave_application_update': [HOME, LEAVE_APPLICATION_LIST, LEAVE_APPLICATION_DETAIL, LEAVE_APPLICATION_UPDATE],
    'user:leave_application_delete': [HOME, LEAVE_APPLICATION_LIST, LEAVE_APPLICATION_DETAIL, LEAVE_APPLICATION_DELETE],
    'schedule:schedule_list': [HOME, SCHEDULE_LIST],
    'schedule:schedule_detail': [HOME, SCHEDULE_LIST, SCHEDULE_DETAIL],
    'schedule:schedule_create': [HOME, SCHEDULE_LIST, SCHEDULE_CREATE],
    'schedule:schedule_update': [HOME, SCHEDULE_LIST, SCHEDULE_DETAIL, SCHEDULE_UPDATE],
    'schedule:schedule_delete': [HOME, SCHEDULE_LIST, SCHEDULE_DETAIL, SCHEDULE_DELETE],
    'schedule:schedule_log_list': [HOME, SCHEDULE_LOG_LIST],
    'schedule:schedule_log_detail': [HOME, SCHEDULE_LOG_LIST, SCHEDULE_LOG_DETAIL],
    'schedule:schedule_log_delete': [HOME, SCHEDULE_LOG_LIST, SCHEDULE_LOG_DETAIL, SCHEDULE_LOG_DELETE],
    'schedule:attendance_check': [HOME, SCHEDULE_LIST, SCHEDULE_DETAIL, ATTENDANCE_CHECK],
}

@register.simple_tag
def breadcrumbs(path):
    parts = resolve(path)
    breadcrumb_names = BREAD_DICT.get(parts.view_name, [HOME])
    breadcrumbs = []
    for b in breadcrumb_names:
        url = reverse(b['url'], kwargs={k: parts.kwargs[k] for k in b.get('kwargs', [])} if 'kwargs' in b else {})
        breadcrumbs.append({'name': b['name'], 'url': url})
    return breadcrumbs

register.filter("breadcrumbs", breadcrumbs)