# market/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # /ws/chat/4/ 같은 주소를 ChatConsumer 에 연결
    re_path(r"ws/chat/(?P<room_id>\d+)/$", consumers.ChatConsumer.as_asgi()),
]