from django.urls import path
from . import views
app_name = 'market'

urlpatterns = [
    # 상품 목록 : /market/
    path('', views.item_list, name='item_list'),
    # 상품 상세 : /market/1/, /market/2/ ...
    path('<int:pk>/', views.item_detail, name='item_detail'),
    # 상품 등록: /market/create/
    path('create/', views.item_create, name='item_create'),
    # 상품 수정
    path('<int:pk>/edit/', views.item_edit, name='item_edit'),
    # 상품 삭제
    path('<int:pk>/delete/', views.item_delete, name='item_delete'),
    # 상태 변경
    path('<int:pk>/status/<str:status>/', views.item_change_status, name='item_change_status'),
    # 내 상품
    path('mine/', views.my_items, name='my_items'),
    # 내 동네 상품만 보기
    path('region/', views.item_list_my_region, name='item_list_my_region'),
    # 리뷰 작성
    path('<int:pk>/review/', views.review_create, name='review_create'),
    # 채팅 시작
    path('<int:pk>/chat/', views.chat_start, name='chat_start'),
    # 채팅 방
    path('chat/<int:room_id>/', views.chat_room, name='chat_room' ),
    # 채팅 보내기
    path('chat/<int:room_id>/send/', views.chat_send, name='chat_send'),

    

]