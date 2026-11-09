from django.urls import path

from . import role_views, user_views, views

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("password/change/", views.PasswordChangeView.as_view(), name="password_change"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("roles/", role_views.RoleListView.as_view(), name="role_list"),
    path("roles/new/", role_views.RoleCreateView.as_view(), name="role_create"),
    path("roles/<int:pk>/edit/", role_views.RoleUpdateView.as_view(), name="role_update"),
    path("roles/<int:pk>/delete/", role_views.RoleDeleteView.as_view(), name="role_delete"),
    path("users/", user_views.UserListView.as_view(), name="user_list"),
    path("users/new/", user_views.UserCreateView.as_view(), name="user_create"),
    path("users/<int:pk>/edit/", user_views.UserUpdateView.as_view(), name="user_update"),
    path(
        "users/<int:pk>/password/",
        user_views.UserPasswordResetView.as_view(),
        name="user_password_reset",
    ),
]
