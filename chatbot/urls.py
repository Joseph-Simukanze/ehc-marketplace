from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.chatbot_ui, name='chat_ui'),
    path('respond/', views.bot_response, name='chabot_response'),
]
