from django.urls import path
from . import views


urlpatterns=[
    path('api/user-read/', views.UserInfo.as_view()),
    path('api/user-delete/', views.UserDelete.as_view()),

    path('api/splitwise/', views.SplitwiseAuthUrl.as_view()),
    path('api/splitwise-friend/', views.SplitwiseFriend.as_view()),
    path('api/post-expense/', views.SplitwiseExpense.as_view()),

    path('api/gmail-receipt/', views.GmailReceipt.as_view()),
    path('api/get-receipt/', views.GetReceipt.as_view()),
    path('api/receipt-update/', views.ReceiptUpdate.as_view()),
    path('api/receipt-create/', views.ReceiptCreate.as_view()),

]
