from django.urls import path
from django.conf.urls import include
from . import views

app_name = 'user'
urlpatterns = [
    # path('signup/', views.SignupView.as_view(), name="signup"),
    # path('users/<uuid:activate_token>/activation/', views.activate_user, name='users-activation'),
    # path('users/<uuid:uuid>/detail/', views.AccountDetailView.as_view(), name='account_detail'),
    # path('users/list/', views.AccountListView.as_view(), name='account_list'),
    path('login/', views.LoginView.as_view(), name="login"),
    path('logout/', views.LogoutView.as_view(), name="logout"),
    path('create_tenant/', views.CreateTenantView.as_view(), name="create_tenant"),
    # path('success/', views.CreateAccountSuccessView.as_view(), name="create_success"),
    path('password_reset', views.PasswordResetView.as_view(), name="password_reset"),  # パスワードリセットのURL
    path('password_reset/success/', views.password_reset_success, name="password_reset_success"),  # パスワードリセット成功のURL
    path('password_reset/activate/', views.password_reset_avtivate, name="password_reset_avtivate"),  # パスワードリセットのアクティベートURL
    path('password_reset/authenticated/', views.PasswordResetForAuthenticatedUserView.as_view(), name="password_reset_authenticated"),  # ログインユーザー向けパスワードリセットのURL
    path('password_reset/authenticated/success/', views.password_reset_success_for_authenticated, name="password_reset_success_for_authenticated"),  # ログインユーザー向けパスワードリセット成功のURL
    path('user/list/', views.TenantUserListView.as_view(), name='user_list'),  # テナントユーザーのリストビュー
    path('user/<uuid:pk>/detail/', views.UserDetailView.as_view(), name='user_detail'),  # ユーザーの詳細ビュー
    path('user/create/', views.tenant_user_update_create_view, name='user_create'),  # ユーザーの作成ビュー
    path('user/<uuid:pk>/update/', views.tenant_user_update_create_view, name='user_update'),  # ユーザーの更新ビュー
    path('user/<uuid:pk>/delete/', views.TenantUserDeleteView.as_view(), name='user_delete'),  # ユーザーの削除ビュー
    path('terms_of_service/', views.terms_of_service, name='terms_of_service'),  # 利用規約のURL
    path('leave_application/create/', views.LeaveApplicationCreateView.as_view(), name='leave_application_create'),  # 休団申請
    path('leave_application/<uuid:pk>/update/', views.LeaveApplicationUpdateView.as_view(), name='leave_application_update'),  # 休団申請の更新
    path('leave_application/list/', views.LeaveApplicationListView.as_view(), name='leave_application_list'),  # 休団申請一覧
    path('leave_application/<uuid:pk>/detail/', views.LeaveApplicationDetailView.as_view(), name='leave_application_detail'),  # 休団申請の詳細
    path('leave_application/<uuid:pk>/delete/', views.LeaveApplicationDeleteView.as_view(), name='leave_application_delete'),  # 休団申請の削除
    path('manual/', views.manualView, name='manual'),  # マニュアルビュー
]
