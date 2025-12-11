from accounts.models import Profile
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from .models import Item, Review, ChatRoom, ChatMessage

def item_list(request):
    # 최신 등록순으로 정렬 (-created_at : 내림차순)
    items = Item.objects.order_by('-created_at')

    # 템플릿에 items 리스트 전달
    return render(request, 'market/item_list.html', {'items': items})

def item_detail(request, pk):
     item = get_object_or_404(Item, pk=pk)

     return render(request, 'market/item_detail.html', {'item': item})
@login_required
def item_create(request):
     if request.method == 'POST':
          title = request.POST.get('title')
          description = request.POST.get('description')
          price = request.POST.get('price')
          image = request.FILES.get('image')
          # 가격 값이 비어 있으면 0 처리
          if not price:
               price = 0
          # int 형 변환 시도
          try :
               price = int(price)
          except ValueError:
               return render(request, 'market/item_create.html',{
                    'error': '가격은 숫자로 입력해야 합니다.'
                    })
          Item.objects.create(
               seller=request.user,
               title=title,
               description=description,
               price=price,
               image = image
          )

          return redirect('market:item_list')
     
     return render(request, 'market/item_create.html')

@login_required
def item_edit(request, pk):
     
     item = get_object_or_404(Item, pk=pk)

     if item.seller != request.user:
          return redirect('market:item_detail', pk=pk)
     
     if request.method == 'POST':
          item.title = request.POST.get('title')
          item.price = request.POST.get('price')
          item.description = request.POST.get('description')

          # 가격 형 변환
          if not item.price:
               item.price = 0
          try:
               item.price = int(item.price)
          except ValueError:
               return render(request, 'market/item_edit.html', {
                    'item': item,
                    'error': '가격은 숫자로 입력해야 합니다.'
               })
          # 이미지 새로 업로드한 경우에만 교체
          if 'image' in request.FILES:
               item.image = request.FILES['image']

          item.save()
          return redirect('market:item_detail', pk=pk)
     return render(request, 'market/item_edit.html', {'item':item})

@login_required
def item_delete(request, pk):
     item = get_object_or_404(Item, pk=pk)

     if item.seller != request.user:
          return redirect('market:item_detail', pk=pk)
     
     if request.method == 'POST':
          item.delete()
          return redirect('market:item_list')
     
     return render(request, 'market/item_delete.html', {'item': item})
@login_required
def item_change_status(request, pk, status):
     item = get_object_or_404(Item, pk=pk)

     if item.seller != request.user:
          return redirect('market:item_detail', pk=pk)
     
     allowed_status = ['sale', 'reserved', 'sold']
     if status not in allowed_status:
          return HttpResponseBadRequest("잘못된 상태 값입니다.")
     
     # 상태 변경 후 저장
     item.status = status
     item.save()

     return redirect('market:item_detail', pk=pk)

@login_required
def my_items(request):
     
     items = Item.objects.filter(seller=request.user).order_by('-created_at')
     return render(request, 'market/item_list.html', {
          'items' : items,
          'my_list' : True,
     })
@login_required
def item_list_my_region(request):
     
     # 현재 로그인한 유저의 프로필
     profile, _ = Profile.objects.get_or_create(
          user=request.user,
          defaults={'nickname' : request.user.username, 'region': '미설정'}
     )
     
     user_region = profile.region

     items = Item.objects.filter(seller__profile__region=user_region).order_by('-created_at')

     return render(request, 'market/item_list.html',{
          'items' : items,
          'my_list': True,
          'region_filter': user_region
     })

@login_required
def review_create(request, pk):
     """
     거래 완료된 상품에 대해 리뷰를 작성하는 뷰
     - GET : 리뷰 작성 폼
     - POST : 리뷰 저장
     """
     item = get_object_or_404(Item, pk=pk)

     # 1) 거래 완료된 상품만 리뷰 허용(status == 'sold')
     if item.status != 'sold':
          return HttpResponseBadRequest("판매 완료된 상품만 리뷰를 작성할 수 있습니다.")
     
     # 2) 판매자는 자기 상품에 리뷰 못 달게 예시로 막기 (원하면 제거 가능)
     if item.seller == request.user:
          return HttpResponseBadRequest("본인 상품에는 리뷰를 작성할 수 없습니다.")
     
     # 3) 이미 이 유저가 이 상품에 리뷰를 달았으면 또 못 달게 
     if Review.objects.filter(item=item, reviewer=request.user).exists():
          return HttpResponseBadRequest("이미 이 상품에 대한 리뷰를 작성하셨습니다.")
     
     if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        # 값 체크
        if not rating or not comment:
             return render(request, 'market/review_form.html', {
                  'item': item,
                  'error': '평점과 리뷰 내용을 모두 입력해 주세요.'
             })
        # 평점을 1~5 사이로 제한
        try:
             rating = int(rating)
        except ValueError:
             return render(request, 'market/review_from.html', {
                  'item': item,
                  'error': '평점은 숫자로 입력해야 합니다.',
             })
        if rating < 1 or rating > 5:
             return render(request, 'market/review_form.html', {
                  'item': item,
                  'error': '평점은 1~5 사이의 숫자여야 합니다.',
             })
        
        # 실제 리뷰 생성
        Review.objects.create(
             item=item,
             reviewer=request.user,
             rating=rating,
             comment=comment
        )

        return redirect('market:item_detail', pk=item.pk)
     
     return render(request, 'market/review_form.html', {'item': item})

@login_required
def chat_start(request, pk):
     """
     상품 상세에서 '채팅하기'눌렀을 때
     구매자-판매자 채팅방 생성 or 기존 방 열기
     """
     item = get_object_or_404(Item, pk=pk)

     # 판매자는 자기 물건에 채팅 못 건다
     if item.seller == request.user:
          return redirect('market:item_detail', pk=pk)

     room, created = ChatRoom.objects.get_or_create(
          item=item,
          buyer=request.user,
          seller=item.seller
     )  

     return redirect('market:chat_room', room_id=room.id)   

@login_required
def chat_room(request, room_id):
     room = get_object_or_404(ChatRoom, id=room_id)

     #권한 체크
     if request.user not in [room.buyer, room.seller]:
          return HttpResponseBadRequest("권한 없음")
     
     messages = room.messages.order_by('created_at')

     return render(request, 'market/chat_room.html', {
          'room':room,
          'messages':messages,
     })
@login_required
def chat_send(request, room_id):
     room = get_object_or_404(ChatRoom, id=room_id)

     if request.method == "POST":
          message = request.POST.get("message")
          if message:
               ChatMessage.objects.create(
                    room=room,
                    sender=request.user,
                    message=message
               )
     return redirect('market:chat_room', room_id=room_id)