from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views

urlpatterns = [
    path("chat/", views.lobby, name="chat"),
    path("chat/<str:room_name>/", views.room, name="room"),
    path('api/login/', views.LoginAPIView.as_view(), name='login'),
    path('logout/', views.LogoutAPIView.as_view()),
    path('gp/create/', views.GPCreateAPIView.as_view()),
    path('gp/list/', views.GPListAPIView.as_view(), name="gp_list"),
    path('gp/delete/', views.GPDestroyAPIView.as_view()),
    path('send_message/<str:gp>/', views.SendMessageCreateAPIView.as_view()),
]