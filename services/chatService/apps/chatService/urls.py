from django.urls import path

from .views import (
    ChatAIRoomEnsureView,
    ChatAIRoomResetContextView,
    ChatMessageListCreateView,
    ChatRoomDetailView,
    ChatRoomListCreateView,
    TelegramInboundBridgeView,
    TelegramOutboundBridgeView,
)

urlpatterns = [
    path("chat/rooms/", ChatRoomListCreateView.as_view(), name="chat-room-list-create"),
    path("chat/rooms/ai/", ChatAIRoomEnsureView.as_view(), name="chat-room-ai-ensure"),
    path("chat/rooms/<int:room_id>/ai/reset/", ChatAIRoomResetContextView.as_view(), name="chat-room-ai-reset-context"),
    path("chat/rooms/<int:pk>/", ChatRoomDetailView.as_view(), name="chat-room-detail"),
    path("chat/rooms/<int:room_id>/messages/", ChatMessageListCreateView.as_view(), name="chat-message-list-create"),
    path("chat/telegram/inbound/", TelegramInboundBridgeView.as_view(), name="chat-telegram-inbound"),
    path("chat/telegram/outbound/", TelegramOutboundBridgeView.as_view(), name="chat-telegram-outbound"),
]
