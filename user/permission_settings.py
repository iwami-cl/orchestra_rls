# Modelパーミッションの設定を定義するファイル
PERMISSION_SETTINGS = {
    # logentry
    'add_logentry': { 'display_name': 'ログエントリーの追加', 'private': True, 'description': 'ログエントリーを新規作成する権限' },
    'change_logentry': { 'display_name': 'ログエントリーの変更', 'private': True, 'description': 'ログエントリーの情報を変更する権限' },
    'delete_logentry': { 'display_name': 'ログエントリーの削除', 'private': True, 'description': 'ログエントリーを削除する権限' },
    'view_logentry': { 'display_name': 'ログエントリーの閲覧', 'private': True, 'description': 'ログエントリーの情報を閲覧する権限' },
    # group
    'add_group': { 'display_name': 'グループの追加', 'private': True, 'description': 'グループを新規作成する権限' },
    'change_group': { 'display_name': 'グループの変更', 'private': True, 'description': 'グループの情報を変更する権限' },
    'delete_group': { 'display_name': 'グループの削除', 'private': True, 'description': 'グループを削除する権限' },
    'view_group': { 'display_name': 'グループの閲覧', 'private': True, 'description': 'グループの情報を閲覧する権限' },
    # permission
    'add_permission': { 'display_name': 'パーミッションの追加', 'private': True, 'description': 'パーミッションを新規作成する権限' },
    'change_permission': { 'display_name': 'パーミッションの変更', 'private': True, 'description': 'パーミッションの情報を変更する権限' },
    'delete_permission': { 'display_name': 'パーミッションの削除', 'private': True, 'description': 'パーミッションを削除する権限' },
    'view_permission': { 'display_name': 'パーミッションの閲覧', 'private': True, 'description': 'パーミッションの情報を閲覧する権限' },
    # contenttype
    'add_contenttype': { 'display_name': 'コンテントタイプの追加', 'private': True, 'description': 'コンテントタイプを新規作成する権限' },
    'change_contenttype': { 'display_name': 'コンテントタイプの変更', 'private': True, 'description': 'コンテントタイプの情報を変更する権限' },
    'delete_contenttype': { 'display_name': 'コンテントタイプの削除', 'private': True, 'description': 'コンテントタイプを削除する権限' },
    'view_contenttype': { 'display_name': 'コンテントタイプの閲覧', 'private': True, 'description': 'コンテントタイプの情報を閲覧する権限' },
    # instrument
    'add_instrument': { 'display_name': '楽器の追加', 'private': True, 'description': '楽器を新規作成する権限' },
    'change_instrument': { 'display_name': '楽器の変更', 'private': True, 'description': '楽器の情報を変更する権限' },
    'delete_instrument': { 'display_name': '楽器の削除', 'private': True, 'description': '楽器を削除する権限' },
    'view_instrument': { 'display_name': '楽器の閲覧', 'private': True, 'description': '楽器の情報を閲覧する権限' },
    # instrumentpart
    'add_instrumentpart': { 'display_name': '楽器パートの追加', 'private': True, 'description': '楽器パートを新規作成する権限' },
    'change_instrumentpart': { 'display_name': '楽器パートの変更', 'private': True, 'description': '楽器パートの情報を変更する権限' },
    'delete_instrumentpart': { 'display_name': '楽器パートの削除', 'private': True, 'description': '楽器パートを削除する権限' },
    'view_instrumentpart': { 'display_name': '楽器パートの閲覧', 'private': True, 'description': '楽器パートの情報を閲覧する権限' },
    # formation
    'add_formation': { 'display_name': '編成の追加', 'private': False, 'description': '編成を新規作成する権限' },
    'change_formation': { 'display_name': '編成の変更', 'private': False, 'description': '編成の情報を変更する権限' },
    'delete_formation': { 'display_name': '編成の削除', 'private': False, 'description': '編成を削除する権限' },
    'view_formation': { 'display_name': '編成の閲覧', 'private': False, 'description': '編成の情報を閲覧する権限' },
    # music
    'add_music': { 'display_name': '楽曲の追加', 'private': False, 'description': '楽曲を新規作成する権限' },
    'change_music': { 'display_name': '楽曲の変更', 'private': False, 'description': '楽曲の情報を変更する権限' },
    'delete_music': { 'display_name': '楽曲の削除', 'private': False, 'description': '楽曲を削除する権限' },
    'view_music': { 'display_name': '楽曲の閲覧', 'private': False, 'description': '楽曲の情報を閲覧する権限' },
    # attendance
    'add_attendance': { 'display_name': '出欠の追加', 'private': False, 'description': '出欠を新規作成する権限' },
    'change_attendance': { 'display_name': '出欠の変更', 'private': False, 'description': '出欠の情報を変更する権限' },
    'delete_attendance': { 'display_name': '出欠の削除', 'private': False, 'description': '出欠を削除する権限' },
    'view_attendance': { 'display_name': '出欠の閲覧', 'private': False, 'description': '出欠の情報を閲覧する権限' },
    # schedule
    'add_schedule': { 'display_name': 'スケジュールの追加', 'private': False, 'description': 'スケジュールを新規作成する権限' },
    'change_schedule': { 'display_name': 'スケジュールの変更', 'private': False, 'description': 'スケジュールの情報を変更する権限' },
    'delete_schedule': { 'display_name': 'スケジュールの削除', 'private': False, 'description': 'スケジュールを削除する権限' },
    'view_schedule': { 'display_name': 'スケジュールの閲覧', 'private': False, 'description': 'スケジュールの情報を閲覧する権限' },
    # schedulelog
    'add_schedulelog': { 'display_name': '活動履歴の追加', 'private': False, 'description': '活動履歴を新規作成する権限' },
    'change_schedulelog': { 'display_name': '活動履歴の変更', 'private': False, 'description': '活動履歴の情報を変更する権限' },
    'delete_schedulelog': { 'display_name': '活動履歴の削除', 'private': False, 'description': '活動履歴を削除する権限' },
    'view_schedulelog': { 'display_name': '活動履歴の閲覧', 'private': False, 'description': '活動履歴の情報を閲覧する権限' },
    # session
    'add_session': { 'display_name': 'セッションの追加', 'private': True, 'description': 'セッションを新規作成する権限' },
    'change_session': { 'display_name': 'セッションの変更', 'private': True, 'description': 'セッションの情報を変更する権限' },
    'delete_session': { 'display_name': 'セッションの削除', 'private': True, 'description': 'セッションを削除する権限' },
    'view_session': { 'display_name': 'セッションの閲覧', 'private': True, 'description': 'セッションの情報を閲覧する権限' },
    # custompermission
    'add_custompermission': { 'display_name': 'カスタムパーミッションの追加', 'private': True, 'description': 'カスタムパーミッションを新規作成する権限' },
    'change_custompermission': { 'display_name': 'カスタムパーミッションの変更', 'private': True, 'description': 'カスタムパーミッションの情報を変更する権限' },
    'delete_custompermission': { 'display_name': 'カスタムパーミッションの削除', 'private': True, 'description': 'カスタムパーミッションを削除する権限' },
    'view_custompermission': { 'display_name': 'カスタムパーミッションの閲覧', 'private': True, 'description': 'カスタムパーミッションの情報を閲覧する権限' },
    # leaveapplication
    'add_leaveapplication': { 'display_name': '休団申請の追加', 'private': False, 'description': '休団申請を新規作成する権限' },
    'change_leaveapplication': { 'display_name': '休団申請の変更', 'private': False, 'description': '休団申請の情報を変更する権限' },
    'delete_leaveapplication': { 'display_name': '休団申請の削除', 'private': False, 'description': '休団申請を削除する権限' },
    'view_leaveapplication': { 'display_name': '休団申請の閲覧', 'private': False, 'description': '休団申請の情報を閲覧する権限' },
    # permissionpreset
    'add_permissionpreset': { 'display_name': 'パーミッションプリセットの追加', 'private': True, 'description': 'パーミッションプリセットを新規作成する権限' },
    'change_permissionpreset': { 'display_name': 'パーミッションプリセットの変更', 'private': True, 'description': 'パーミッションプリセットの情報を変更する権限' },
    'delete_permissionpreset': { 'display_name': 'パーミッションプリセットの削除', 'private': True, 'description': 'パーミッションプリセットを削除する権限' },
    'view_permissionpreset': { 'display_name': 'パーミッションプリセットの閲覧', 'private': True, 'description': 'パーミッションプリセットの情報を閲覧する権限' },
    # tenant
    'add_tenant': { 'display_name': '団体の追加', 'private': True, 'description': '団体を新規作成する権限' },
    'change_tenant': { 'display_name': '団体の変更', 'private': False, 'description': '団体の情報を変更する権限' },
    'delete_tenant': { 'display_name': '団体の削除', 'private': False, 'description': '団体を削除する権限' },
    'view_tenant': { 'display_name': '団体の閲覧', 'private': False, 'description': '団体の情報を閲覧する権限' },
    # tenantuser
    'add_tenantuser': { 'display_name': 'ユーザーの追加', 'private': False, 'description': 'ユーザーを新規作成する権限' },
    'change_tenantuser': { 'display_name': 'ユーザーの変更', 'private': False, 'description': 'ユーザーの情報を変更する権限' },
    'delete_tenantuser': { 'display_name': 'ユーザーの削除', 'private': False, 'description': 'ユーザーを削除する権限' },
    'view_tenantuser': { 'display_name': 'ユーザーの閲覧', 'private': False, 'description': 'ユーザーの情報を閲覧する権限' },
    # useractivatetokens
    'add_useractivatetokens': { 'display_name': 'ユーザーアクティベートトークンの追加', 'private': True, 'description': 'ユーザーアクティベートトークンを新規作成する権限' },
    'change_useractivatetokens': { 'display_name': 'ユーザーアクティベートトークンの変更', 'private': True, 'description': 'ユーザーアクティベートトークンの情報を変更する権限' },
    'delete_useractivatetokens': { 'display_name': 'ユーザーアクティベートトークンの削除', 'private': True, 'description': 'ユーザーアクティベートトークンを削除する権限' },
    'view_useractivatetokens': { 'display_name': 'ユーザーアクティベートトークンの閲覧', 'private': True, 'description': 'ユーザーアクティベートトークンの情報を閲覧する権限' },
}

# デフォルトで用意するパーミッションプリセットの定義
NON_PRIVATE_PERMISSIONS = {key for key, value in PERMISSION_SETTINGS.items() if not value["private"]}

DEFAULT_PERMISSION_PRESETS = [
    {"name": "管理者", "permissions": [
        p for p in [
            'change_tenant', 'delete_tenant',
            'view_tenant', 'add_tenantuser', 'change_tenantuser', 'delete_tenantuser', 'view_tenantuser',
            'add_music', 'change_music', 'delete_music', 'view_music',
            'add_formation', 'change_formation', 'delete_formation', 'view_formation',
            'add_instrument', 'change_instrument', 'delete_instrument', 'view_instrument',
            'add_instrumentpart', 'change_instrumentpart', 'delete_instrumentpart', 'view_instrumentpart',
            'add_attendance', 'change_attendance', 'delete_attendance', 'view_attendance',
            'add_schedule', 'change_schedule', 'delete_schedule', 'view_schedule',
            'add_schedulelog', 'change_schedulelog', 'delete_schedulelog', 'view_schedulelog',
            'add_leaveapplication', 'change_leaveapplication', 'delete_leaveapplication', 'view_leaveapplication'
        ] if p in NON_PRIVATE_PERMISSIONS
    ]},
    {"name": "一般ユーザー", "permissions": [
        p for p in [
            'view_tenant',
            'view_tenantuser',
            'view_music',
            'view_formation',
            'view_instrument',
            'view_instrumentpart',
            'add_attendance', 'change_attendance', 'delete_attendance', 'view_attendance',
            'view_schedule',
            'view_schedulelog',
            'view_leaveapplication'
        ] if p in NON_PRIVATE_PERMISSIONS
    ]},
    {"name": "ゲスト", "permissions": [
        p for p in [
            'add_attendance', 'change_attendance', 'delete_attendance', 'view_attendance',
            'view_schedule'
        ] if p in NON_PRIVATE_PERMISSIONS
    ]},
]