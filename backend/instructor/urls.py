from django.urls import path

from . import views

app_name = "instructor"

urlpatterns = [
    path(
        "dashboard/",
        views.DashboardAPIView.as_view(),
        name="dashboard",
    ),
    path(
        "wallet/balance/",
        views.WalletBalanceAPIView.as_view(),
        name="wallet-balance",
    ),
    path(
        "wallet/transactions/",
        views.WalletTransactionListAPIView.as_view(),
        name="wallet-transactions",
    ),
    path(
        "wallet/withdrawal-requests/",
        views.WithdrawalRequestListAPIView.as_view(),
        name="withdrawal-requests",
    ),
    path(
        "wallet/withdrawal-requests/create/",
        views.WithdrawalRequestCreateAPIView.as_view(),
        name="withdrawal-request-create",
    ),
]
