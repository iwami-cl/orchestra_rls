// 権限プリセットが変更されたときの処理
var permission_change_flag = false; // 権限変更フラグ
$('#id_permission_presets').on('change', function() {
    var presetId = $(this).val();
    if (presetId) {
        for (const [id, preset] of Object.entries(PERMISSION_PRESETS)) {
            if (id === presetId) {
                // チェックボックスをすべてオフにする
                $('#id_permissions input[type="checkbox"]').prop('checked', false);
                // プリセットに含まれる権限のチェックボックスをオンにする
                preset.permissions.forEach(function(permissionId) {
                    $('#id_permissions input[type="checkbox"][value="' + permissionId + '"]').prop('checked', true);
                });
            }
        }
    } else {
        // プリセットが選択されていない場合はすべてのチェックボックスをオフにする
        $('#id_permissions input[type="checkbox"]').prop('checked', false);
    }
    permission_change_flag = true; // 権限変更フラグを立てる
});

// チェックボックスが変更されたときの処理
$('#id_permissions input[type="checkbox"]').on('change', function() {
    permission_change_flag = true; // 権限変更フラグを立てる
});

// 保存操作時に権限変更フラグONなら確認ダイアログを表示
$('#save-button').on('click', function(event) {
    if (permission_change_flag) {
        var confirmMessage = '権限が変更されています。\n対応する権限の操作ができなくなる可能性があります。\n保存してもよろしいですか？';
        if (!confirm(confirmMessage)) {
            event.preventDefault(); // 保存処理をキャンセル
        }   else {
            permission_change_flag = false; // フラグをリセット
        }
    }
});