- ミドルウェア一覧
| ミドルウェア | バージョン |
| --- | --- |
| Django | 5.2.7 |
| psycopg2 | 2.9.7 |
| pyenv | 2.3.0 |
| postgreSQL | 15.7 |



- DBの作成とRLSの設定
- 以下のロールを作っておく
dspf -> DBの所有者
CREATE ROLE "dspf";
tenantuser -> RLS用のユーザー
CREATE ROLE "tenantuser";

- dspfのロール
- dspfには、tenantuserのADMIN OPTIONをつけておく
GRANT tenantuser TO dspf WITH ADMIN OPTION;
ALTER ROLE "dspf" CREATEROLE;

- 本番環境の場合のロール


- DB削除
```
DROP DATABASE "ORCHESTRA_DB_RLS";
```

- ROLE 削除(dspf, postgres, tenantuser以外)
DROP ROLE "1";
- DB作成
```
CREATE DATABASE "ORCHESTRA_DB_RLS" WITH OWNER = 'dspf' ENCODING = 'UTF-8' LC_COLLATE = 'C' LC_CTYPE = 'C' TABLESPACE = pg_default TEMPLATE = template0;
```

- マイグレーション

- DBに入って、以下を実行
psql -U dspf ORCHESTRA_DB_RLS

- アプリからデータアクセスを許可する（django_admin_log, django_sessionは必須）
```
GRANT select, insert, delete ON django_session TO tenantuser;
GRANT select, insert, delete ON django_admin_log TO tenantuser;
GRANT select, insert ON django_content_type TO tenantuser;
GRANT select, insert ON auth_group TO tenantuser;
GRANT select, insert ON auth_permission TO tenantuser;
GRANT select, insert ON auth_group_permissions TO tenantuser;
GRANT select, delete ON user_activate_tokens TO tenantuser;
GRANT select ON stripe_product TO tenantuser;
GRANT select ON stripe_price TO tenantuser;
```
- アプリからデータアクセスを許可する（tenant_usersは必須）
```
GRANT select, update, insert ON tenants TO tenantuser;
GRANT select, update, insert, delete ON tenant_users TO tenantuser;
GRANT select, update, insert, delete ON tenant_users_groups TO tenantuser;
GRANT select, update, insert, delete ON tenant_users_user_permissions TO tenantuser;
GRANT select, update, insert, delete ON tenant_formation TO tenantuser;
GRANT select, update, insert, delete ON tenant_formation_users TO tenantuser;
GRANT select, update, insert, delete ON tenant_music TO tenantuser;
GRANT select, update, insert, delete ON tenant_instrument TO tenantuser;
GRANT select, update, insert, delete ON tenant_instrument_part TO tenantuser;
GRANT select, update, insert, delete ON tenant_instrument_part_instrument TO tenantuser;
GRANT select ON custom_permissions TO tenantuser;
GRANT select, update, insert, delete ON permission_presets TO tenantuser;
GRANT select, update, insert, delete ON permission_presets_permissions TO tenantuser;

GRANT select, update, insert, delete ON tenant_schedule TO tenantuser;
GRANT select, update, insert, delete ON tenant_schedule_music TO tenantuser;
GRANT select, update, insert, delete ON tenant_attendance TO tenantuser;
GRANT select, update, insert, delete ON tenant_schedule_log TO tenantuser;

GRANT select, update, insert, delete ON tenant_attendance TO tenantuser;
GRANT select, update, insert, delete ON leave_applications TO tenantuser;

```

- 所属テナントのデータのみを見せたい場合、各テーブルにRLSを設定
```
-- tenants
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenantuser_tenants ON tenants USING(tenant_id::text = current_user);

-- tenant_users
ALTER TABLE tenant_users ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenantuser_tenantusers ON tenant_users USING(tenant_id::text = current_user);

-- leave_applications
ALTER TABLE leave_applications ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenantuser_leaveapplications ON leave_applications USING(tenant_id::text = current_user);

-- permission_presets
ALTER TABLE permission_presets ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenantuser_permissionpresets ON permission_presets USING(tenant_id::text = current_user);

-- permission_presets_permissions
ALTER TABLE permission_presets_permissions ENABLE ROW LEVEL SECURITY;
CREATE POLICY permission_presets_permissions_policy ON permission_presets_permissions
USING (
EXISTS (
    SELECT 1
    FROM permission_presets
    WHERE permission_presets.id = permission_presets_permissions.permissionpreset_id
      AND permission_presets.tenant_id::text = current_user
  )
);

-- tenant_music
ALTER TABLE tenant_music ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenantuser_tenantmusic ON tenant_music USING(tenant_id::text = current_user);

-- tenant_formation
ALTER TABLE tenant_formation ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenantuser_tenantformation ON tenant_formation USING(tenant_id::text = current_user);

-- tenant_schedule
ALTER TABLE tenant_schedule ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenantuser_tenantschedule ON tenant_schedule USING(tenant_id::text = current_user);

-- tenant_schedule_music
ALTER TABLE tenant_schedule_music ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenantuser_schedule_policy ON tenant_schedule_music
USING (
EXISTS (
    SELECT 1
    FROM tenant_schedule
    WHERE tenant_schedule.id = tenant_schedule_music.schedule_id
      AND tenant_schedule.tenant_id::text = current_user
  )
);

-- tenant_schedule_log
ALTER TABLE tenant_schedule_log ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenantuser_tenantschedulelog ON tenant_schedule_log USING(tenant_id::text = current_user);

-- tenant_attendance
ALTER TABLE tenant_attendance ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenantuser_tenantattendance ON tenant_attendance USING(tenant_id::text = current_user);

-- tenant_instrument_part
ALTER TABLE tenant_instrument_part ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenantuser_tenantinstrumentpart ON tenant_instrument_part USING(tenant_id::text = current_user);

-- tenant_instrument
ALTER TABLE tenant_instrument ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenantuser_tenantinstrument ON tenant_instrument USING(tenant_id::text = current_user);

-- tenant_instrument_part_instrument
ALTER TABLE tenant_instrument_part_instrument ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenantuser_instrument_part_policy ON tenant_instrument_part_instrument
USING (
EXISTS (
    SELECT 1
    FROM tenant_instrument_part
    WHERE tenant_instrument_part.id = tenant_instrument_part_instrument.instrumentpart_id
      AND tenant_instrument_part.tenant_id::text = current_user
  )
);
```

- テストデータの投入
```
python manage.py insert_custome_permissions
python manage.py insert_tenant
python manage.py set_permission_preset
python manage.py insert_instrument
python manage.py set_instrument
python manage.py insert_music
python manage.py insert_schedule
python manage.py insert_attendance
```

- 環境構築
- ソースコードのクローン
```
mkdir /usr/local/dialog_pf/otonosu
cd /usr/local/dialog_pf/otonosu
git clone git@github.com:iwami-cl/orchestra_rls.git
cd orchestra_rls
```
-　最新のコードをpull
```
git pull origin main
```

- pyenvのインストール
```
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
```

- pyenvの設定
```
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo -e 'if command -v pyenv 1>/devnull 2>&1; then\n  eval "$(pyenv init --path)"\nfi' >> ~/.bashrc
source ~/.bashrc
```

- xzのインストール
```
sudo yum install -y xz xz-devel
```

- Python 3.13.7のインストール
```
pyenv install 3.13.7
```

- アプリケーションのルートディレクトリで、Python 3.13.7を使用するように設定
```
cd /usr/local/dialog_pf/otonosu/orchestra_rls
pyenv local 3.13.7
ls -a .python-version
```

- pyenv-virtualenvのインストール
```
git clone https://github.com/pyenv/pyenv-virtualenv.git ~/.pyenv/plugins/pyenv-virtualenv
```

- pyenv-virtualenvの最新コードをpull
```
cd ~/.pyenv/plugins/pyenv-virtualenv
git pull origin master
```

- pyenv-virtualenvの設定
```
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
source ~/.bashrc
```



- 仮想環境の構築(Python 3.13.7を使用)
```
cd /usr/local/dialog_pf/otonosu/orchestra_rls
pyenv virtualenv 3.13.7 otonosu-venv
```

- 仮想環境を作り直す
```
rm -rf otonosu-venv
python -m venv otonosu-venv
```

- 仮想環境の起動
```
pyenv activate otonosu-venv
(otonosu-venv) [root@vm-5dc5db51-92 orchestra_rls]#
```

- 仮想環境の終了
```
pyenv deactivate
``` 

- 依存関係のインストール
```
pip install -r requirements.txt
```

- 環境変数の設定
```
export DJANGO_SETTINGS_MODULE=orchestra_rls.settings
export DB_NAME=ORCHESTRA_DB_RLS
export DB_USER=dspf
export DB_PASSWORD=your_password
export DB_HOST=localhost
export DB_PORT=5432
```

- マイグレーションの実行(仮想環境を起動している状態で実行)
```
python manage.py migrate
```

- 静的ファイルの収集
```
python manage.py collectstatic
```

- 設定ファイルの読み込み
- デフォルトでは、otonosu_settings.pyが存在すればそれを読み込む。
```
mkdir /root/.otonosu
cp /usr/local/dialog_pf/otonosu/orchestra_rls/orchestra_rls/otonosu_settings.py /root/.otonosu/.
export OTONOSU_SETTINGS=/root/.otonosu/otonosu_settings.py
```