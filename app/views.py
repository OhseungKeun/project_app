from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from .models import UserPoint, Quiz, QuizCategory, UserExamRecord
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse


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

# 퀴즈 카테고리
def quiz_category_list(request):
    selected = request.GET.get("cat", "전체")
    categories = QuizCategory.objects.all()

    return render(request, "HTML/quiz_category_list.html", {
        "categories": categories,
        "selected": selected,
    })

# 퀴즈 카테고리
@login_required
def quiz_view(request, category_id):
    category = QuizCategory.objects.get(id=category_id)
    questions = Quiz.objects.filter(category=category)
    return render(request, "HTML/quiz.html", {
        "category": category,
        "questions": questions,
    })

# 퀴즈 풀기 및 점수 체점
@login_required
def quiz_submit(request, category_id):
    if request.method != "POST":
        return redirect(f"/quiz/{category_id}/")

    user = request.user
    category = QuizCategory.objects.get(id=category_id)
    questions = Quiz.objects.filter(category=category)

    # 유저 시험 기록 조회 (없으면 생성)
    user_exam, created = UserExamRecord.objects.get_or_create(
        user=user,
        category=category
    )

    # ----- 채점 시작 -----
    correct_count = 0                 # ✔ 맞춘 문제 개수
    question_count = questions.count()  # 총 문제 수

    for quiz in questions:
        selected = request.POST.get(str(quiz.id))
        if selected and int(selected) == quiz.answer:
            correct_count += 1

    # ✔ 합격 기준 = 맞춘 개수 / 전체 문제 70%
    passed = correct_count >= (question_count * 0.7)

    # ✔ 합격 시 1000원 지급
    reward = 1000 if passed else 0

    # 🔥 이미 합격하여 보상 받은 기록이 있는지 확인
    already_rewarded = user_exam.rewarded

    # 이미 보상받았다면 이번 reward 를 0으로 설정
    if already_rewarded:
        reward = 0

    # ----- 결과 저장 -----
    user_exam.score = correct_count  # score = 맞춘 문제 수
    user_exam.passed = passed

    if passed and not user_exam.rewarded:
        user_exam.rewarded = True
        user_point, _ = UserPoint.objects.get_or_create(user=user)
        user_point.balance += reward
        user_point.save()
    else:
        reward = 0  # 이미 보상받은 경우 보상 제거

    user_exam.save()

    return render(request, "HTML/exam_result.html", {
        "category": category,
        "score": correct_count,       # 맞춘 개수
        "question_count": question_count,
        "passed": passed,
        "reward": reward,
        "already_rewarded": already_rewarded,   
        "balance": UserPoint.objects.get(user=user).balance,
    })

# 환급
def point(request):
    return render(request, "HTML/point.html")

# 회원 정보
@login_required
def user_info(request):
    user = request.user
    try:
        point = UserPoint.objects.get(user=user)
        balance = point.balance
    except UserPoint.DoesNotExist:
        balance = 0

    return render(request, "HTML/user_info.html", {
        "username": user.username,
        "balance": balance,
    })

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

# 회원 가입 시 중복 체크
def check_username(request):
    username = request.GET.get("username")
    exists = User.objects.filter(username=username).exists()
    return JsonResponse({"exists": exists})

# 로그아웃
def logout_view(request):
    logout(request)
    return redirect("main")

# 회원 가입
def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # ID 중복 확인
        if User.objects.filter(username=username).exists():
            return render(request, "HTML/signup.html", {"error": "이미 존재하는 ID 입니다."})

        user = User.objects.create(
            username=username,
            password=make_password(password)
        )

        UserPoint.objects.create(user=user, balance=0)

        return redirect("login")

    return render(request, "HTML/signup.html")
