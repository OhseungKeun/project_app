from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from .models import UserPoint
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

@login_required
def user_info(request):
    user = request.user
    point = UserPoint.objects.get(user=user)

    return render(request, "HTML/user_info.html", {
        "user": user,
        "balance": point.balance
    })

# 메인 페이지
def main(request):

    user = request.user
    balance = None
    username = None

    if user.is_authenticated:
        username = user.username
        try:
            point = UserPoint.objects.get(user=user)
            balance = point.balance
        except UserPoint.DoesNotExist:
            balance = 0

    return render(request, "HTML/main.html", {
        "username": username,
        "balance": balance,
    })

# 퀴즈 사이트
def quiz(request):
    return render(request, "HTML/quiz.html")

# 환급
def point(request):
    return render(request, "HTML/point.html")

# 회원 정보
def user_info(request):
    return render(request, "HTML/user_info.html")

# 로그인
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("main")
        else:
            return render(request, "HTML/login.html", {"error": "로그인 실패"})

    return render(request, "HTML/login.html")

# 회원 가입
def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # ID 중복 확인
        if User.objects.filter(username=username).exists():
            return render(request, "HTML/signup.html", {"error": "이미 존재하는 ID 입니다"})

        user = User.objects.create(
            username=username,
            password=make_password(password)
        )

        UserPoint.objects.create(user=user, balance=0)

        return redirect("login")

    return render(request, "HTML/signup.html")