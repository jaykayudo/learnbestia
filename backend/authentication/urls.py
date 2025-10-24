from django.urls import path

from . import views

urlpatterns = [
    # register
    path(
        "register/google/",
        views.GoogleRegisterAPIView.as_view(),
        name="google-register",
    ),
    path(
        "register/email/",
        views.EmailRegisterAPIView.as_view(),
        name="email-register",
    ),
    path(
        "register/ethereum/",
        views.EthereumRegisterAPIView.as_view(),
        name="ethereum-register",
    ),
    path(
        "register/polkadot/",
        views.PolkadotRegisterAPIViw.as_view(),
        name="polkadot-register",
    ),
    # login
    path(
        "login/google/",
        views.GoogleLoginAPIView.as_view(),
        name="google-login",
    ),
    path("login/email/", views.EmailLoginAPIView.as_view(), name="email-login"),
    path(
        "login/ethereum/",
        views.EthereumLoginAPIView.as_view(),
        name="ethereum-login",
    ),
    path(
        "login/polkadot/",
        views.PolkadotLoginAPIViw.as_view(),
        name="polkadot-login",
    ),
    # password
    path(
        "password/change/",
        views.ChangePasswordAPIView.as_view(),
        name="change-password",
    ),
    path(
        "password/forgot/",
        views.ForgotPasswordAPIView.as_view(),
        name="forgot-password",
    ),
    path(
        "password/reset/",
        views.ResetPasswordAPIView.as_view(),
        name="reset-password",
    ),
]
