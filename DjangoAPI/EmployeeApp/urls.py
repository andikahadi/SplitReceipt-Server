from django.urls import path
from . import views
from .views import ReceiptCreate
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns=[
    path('api/user-read/', views.UserInfo.as_view()),
    path('api/splitwise/', views.SplitwiseAuthUrl.as_view()),
    path('api/splitwise-friend/', views.SplitwiseFriend.as_view()),
    path('api/post-expense/', views.SplitwiseExpense.as_view()),
    path('api/gmail-receipt/', views.GmailReceipt.as_view()),
    path('api/get-receipt/', views.GetReceipt.as_view()),
    path('api/receipt-update/', views.ReceiptUpdate.as_view()),
    path('api/receipt-create/', views.ReceiptCreate.as_view()),

    path('api/user-delete/', views.UserDelete.as_view()),
]

# urlpatterns = [
#     path('task-list/', views.TaskList.as_view(), name='task-list'),
#     path('task-details/<str:pk>/', views.TaskDetails.as_view(), name='task-details'),
#     path('task-create/', views.TaskCreate.as_view(), name='task-create'),
#     path('task-update/<str:pk>', views.TaskUpdate.as_view(), name='task-update'),
#     path('task-delete/<str:pk>', views.TaskDelete.as_view(), name='task-delete'),
#     path('jwt-details/', views.JWTDetails.as_view(), name='jwt-details'),
# ]