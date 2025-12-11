from django.db import models
from django.contrib.auth.models import User

class Item(models.Model):
    STATUS_CHOICES = [
        ('sale', '판매중'),
        ('reserved', '예약중'),
        ('sold', '판매완료'),
    ]
    seller = models.ForeignKey(User, on_delete=models.CASCADE,related_name='items')
    buyer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchased_items')
    title = models.CharField(max_length=100,help_text="상품 제목을 100자 이내로 입력하세요.")
    description = models.TextField(
        help_text="상품 상태, 사용 기간 등을 자세히 적어주세요."
    )
    price = models.IntegerField(
        help_text="가격을 숫자로만 입력하세요. (예: 30000)"
    )

    # 상품 사진 (선택)
    # 실제 파일은 MEDIA_ROOT/items/ 폴더에 저장됩니다.
    image = models.ImageField(upload_to='items/', blank=True, null=True)

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='sale',
    )
    created_at = models.DateField(auto_now_add=True)

    def average_rating(self):
        """
        이 상품에 달린 리뷰들의 평균 평점 반환.
        리뷰가 없으면 None 반환.
        """
        if self.reviews.exists():
            return round(self.reviews.aggregate(models.Avg('rating'))['rating_avg'], 1)
        return None

    def __str__(self):
        return f"{self.title} - {self.price}원"
    
class Review (models.Model):  
    """
    거래 완료 후 남기는 리뷰/평점 모델
    - 어떤 상품(Item)에 대한 리뷰인지
    - 누가(reviewer) 남겼는지
    - 평점(rating)
    - 한 줄/여러 줄 코멘틑(comment)
    """

    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='reviews' # item.reviews 로 해당 상품 리뷰들을 가져올 수 있음

    )

    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews' # user.reviews 로 유저가 쓴 리뷰들
    )

    #1~5점 평점(별점 같은 느낌)
    rating = models.PositiveSmallIntegerField() # 1~5제한은 뷰에서 체크

    # 리뷰 코멘트
    comment = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        
        # 같은 사람이 같은 상품에 중복 리뷰 남기지 못하게 막기
        
        unique_together = ('item', 'reviewer')
    
    def __str__(self):
        return f"{self.item.title} - {self.rating}점 by {self.reviewer.username}"

class ChatRoom(models.Model):
    """
    구매자와 판매자가 특정 Item 기준으로 사용하는 1:1 채팅방
    """
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='chatrooms')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buy_chatrooms')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sell_chatrooms')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ChatRoom for {self.item.title} ({self.buyer.username} ↔ {self.seller.username})"
    
class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.message[:20]}"