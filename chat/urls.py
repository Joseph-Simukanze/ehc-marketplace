from django.urls import path
from . import views
app_name='chat'
urlpatterns = [
    path('chat/room/<int:room_id>/', views.chat_room, name='chat_room'),
    path('chat/start/<int:other_user_id>/', views.start_chat, name='start_chat'),  # Updated to start_chat
    path('chat/inbox/', views.inbox, name='inbox'),
    path('chat/conversation/<int:room_id>/', views.conversation_detail, name='conversation_detail'),
]
