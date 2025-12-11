from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login
from.models import Profile


# Create your views here.
def signup(request):
    if request.method == 'POST':
        # Django 기본 제공 UserCreationForm 사용 (username + password 처리)
        form = UserCreationForm(request.POST)

        # 우리가 추가로 받는 값들
        nickname = request.POST.get('nickname')
        region = request.POST.get('region')

        # form 유효성 검사
        if form.is_valid():
            #UserCreationForm을 통해 기본 User 생성
            user = form.save()

            # User에 연결된 Profile 생성
            Profile.objects.create(
                user=user,
                nickname=nickname,
                region=region
            )
            # 회원가입 후 바로 자동 로그인 처리
            auth_login(request, user)

            # 로그인 후 프로필 페이지로 리다이렉트
            return redirect('accounts:profile')
    else:
            # GET 요청: 템플릿에서 보여줄 빈 폼 생성
            form = UserCreationForm()

        # signup.html 템플릿에 form 전달
    return render(request, 'accounts/signup.html', {'form': form})
    
@login_required
def profile(request):
        # 현재 로그인된 user의 Profile을 가져옴
        profile = Profile.objects.get(user=request.user)

        # profile.html 템플릿에 전달하여 렌더링
        return render(request, 'accounts/profile.html', {'profile': profile})
