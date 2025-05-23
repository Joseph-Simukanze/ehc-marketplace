from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatRoom(models.Model):
    buyer = models.ForeignKey(User, related_name='buyer_rooms', on_delete=models.CASCADE)
    seller = models.ForeignKey(User, related_name='seller_rooms', on_delete=models.CASCADE)
    product = models.ForeignKey('marketplace.Product', related_name='chat_rooms', on_delete=models.SET_NULL, null=True, blank=True)  # Update 'marketplace' if needed
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('buyer', 'seller', 'product')  # Unique chat per buyer/seller/product combo
        ordering = ['-created_at']

    def __str__(self):
        return f"Chat between {self.buyer.username} and {self.seller.username} for {self.product.name if self.product else 'No Product'}"


class Message(models.Model):
    room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.content[:30]}"

class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation between: {', '.join([user.username for user in self.participants.all()])}"

