from django.urls import path
from django.contrib.auth import views as auth_views

from .forms import CustomPasswordResetForm, CustomSetPasswordForm
from .views import (
    CustomLoginView,
    CustomLogoutView,
    UsersListView,
    CreateUserView,
    UpdateUserView,
    GroupsListView,
    CreateGroupView,
    UpdateGroupView,
    VerifyAccountView,
    desactiveUser
)

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('users/', UsersListView.as_view(), name="users"),
    path('create-user/', CreateUserView.as_view(), name="create-user"),
    path('update-user/<int:pk>/', UpdateUserView.as_view(), name="edit-user"),
    path('change-status-user/<int:pk>/', desactiveUser, name="change-status-user"),
    path('groups/', GroupsListView.as_view(), name='groups'),
    path('create-group/', CreateGroupView.as_view(), name='create-group'),
    path('update-group/<int:pk>/', UpdateGroupView.as_view(), name='edit-group'),
    path('verification-user/<uuid:uuid>/', VerifyAccountView.as_view(), name='verify-account'),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            form_class=CustomPasswordResetForm,
            template_name="accounts/password_reset.html",
            email_template_name="accounts/password_reset_email.txt",
            subject_template_name="accounts/password_reset_subject.txt",
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html",
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html",
            form_class=CustomSetPasswordForm,
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
]
