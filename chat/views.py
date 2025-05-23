from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message

User = get_user_model()

@login_required
def start_chat(request, other_user_id):
    other_user = get_object_or_404(User, id=other_user_id)
    current_user = request.user

    # Prevent chatting with yourself
    if other_user == current_user:
        return redirect('home')  # Optional: redirect to a message or dashboard

    # Check if a chat room already exists
    chat_room = ChatRoom.objects.filter(
        Q(buyer=current_user, seller=other_user) | Q(buyer=other_user, seller=current_user)
    ).first()

    if not chat_room:
        # Create a new chat room if none exists
        chat_room = ChatRoom.objects.create(buyer=current_user, seller=other_user)

    return redirect('chat_room', room_id=chat_room.id)


@login_required
def chat_room(request, room_id):
    chat_room = get_object_or_404(ChatRoom, id=room_id)
    
    # Check if the user is either the buyer or seller in this chat room
    if request.user not in [chat_room.buyer, chat_room.seller]:
        return HttpResponseForbidden()

    if request.method == 'POST':
        content = request.POST.get('message')
        if content:
            Message.objects.create(
                room=chat_room,
                sender=request.user,
                content=content
            )
        return redirect('chat_room', room_id=chat_room.id)

    messages = chat_room.messages.all().order_by('timestamp')
    return render(request, 'chat/chat_room.html', {
        'chat_room': chat_room,
        'messages': messages
    })


@login_required
def inbox(request):
    # Get all chat rooms where the user is either the buyer or seller
    chat_rooms = ChatRoom.objects.filter(Q(buyer=request.user) | Q(seller=request.user))

    return render(request, 'chat/inbox.html', {
        'chat_rooms': chat_rooms
    })


@login_required
def conversation_detail(request, room_id):
    chat_room = get_object_or_404(ChatRoom, id=room_id)

    # Ensure the user is either the buyer or seller in the chat room
    if request.user not in [chat_room.buyer, chat_room.seller]:
        return HttpResponseForbidden()

    messages = chat_room.messages.all()
    return render(request, 'chat/conversation_detail.html', {
        'chat_room': chat_room,
        'messages': messages
    })
