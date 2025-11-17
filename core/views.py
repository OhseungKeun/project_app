from django.http.response import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from .models import UserPoint, Quiz, MainCategory, SubCategory, UserExamRecord, Notice
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test


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

# ------------------------------------
# 대분류 목록
# ------------------------------------
def main_category_list(request):
    main_categories = MainCategory.objects.all()
    sub_categories = SubCategory.objects.all()

    return render(request, "HTML/main_category_list.html", {
        "main_categories": main_categories,
        "sub_categories": sub_categories
    })


# ------------------------------------
# 소분류 목록
# ------------------------------------
def sub_category_list(request, main_id):
    main = MainCategory.objects.get(id=main_id)
    sub_categories = SubCategory.objects.filter(main=main)

    return render(request, "HTML/sub_category_list.html", {
        "main": main,
        "sub_categories": sub_categories
    })

# ------------------------------------
# 퀴즈 페이지
# ------------------------------------
@login_required
def quiz_view(request, sub_id):
    subcategory = SubCategory.objects.get(id=sub_id)
    questions = Quiz.objects.filter(subcategory=subcategory)

    return render(request, "HTML/quiz.html", {
        "subcategory": subcategory,
        "questions": questions,
    })


# ------------------------------------
# 퀴즈 제출 & 채점
# ------------------------------------
@login_required
def quiz_submit(request, sub_id):
    if request.method != "POST":
        return redirect(f"/quiz/{sub_id}/")

    user = request.user
    subcategory = SubCategory.objects.get(id=sub_id)
    questions = Quiz.objects.filter(subcategory=subcategory)

    # 유저 시험 기록 조회 (없으면 생성)
    user_exam, created = UserExamRecord.objects.get_or_create(
        user=user,
        subcategory=subcategory
    )

    # ----- 채점 시작 -----
    correct_count = 0
    question_count = questions.count()

    for quiz in questions:
        selected = request.POST.get(str(quiz.id))
        if selected and int(selected) == quiz.answer:
            correct_count += 1

    # 합격 기준 = 70%
    passed = correct_count >= (question_count * 0.7)

    # 합격 보상
    reward = 1000 if passed else 0

    # 이미 보상 받았는지 확인
    already_rewarded = user_exam.rewarded
    if already_rewarded:
        reward = 0

    # 결과 저장
    user_exam.score = correct_count
    user_exam.passed = passed

    # 새로 합격 → 보상 지급
    if passed and not user_exam.rewarded:
        user_exam.rewarded = True
        user_point, _ = UserPoint.objects.get_or_create(user=user)
        user_point.balance += reward
        user_point.save()

    user_exam.save()

    return render(request, "HTML/exam_result.html", {
        "subcategory": subcategory,
        "score": correct_count,
        "question_count": question_count,
        "passed": passed,
        "reward": reward,
        "already_rewarded": already_rewarded,
        "balance": UserPoint.objects.get(user=user).balance,
    })


# ------------------------------------
# 환급 페이지
# ------------------------------------
def point(request):
    return render(request, "HTML/point.html")


# ------------------------------------
# 유저 정보
# ------------------------------------
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


# ------------------------------------
# 로그인
# ------------------------------------
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


# ------------------------------------
# 아이디 중복 체크
# ------------------------------------
def check_username(request):
    username = request.GET.get("username")
    exists = User.objects.filter(username=username).exists()
    return JsonResponse({"exists": exists})


# ------------------------------------
# 로그아웃
# ------------------------------------
def logout_view(request):
    logout(request)
    return redirect("main")


# ------------------------------------
# 회원가입
# ------------------------------------
def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # ID 중복 확인
        if User.objects.filter(username=username).exists():
            return render(request, "HTML/signup.html", {"error": "이미 존재하는 ID 입니다."})

        # 유저 생성
        user = User.objects.create(
            username=username,
            password=make_password(password)
        )

        # 포인트 계정 생성
        UserPoint.objects.create(user=user, balance=0)

        return redirect("login")

    return render(request, "HTML/signup.html")


# ------------------------------------
# 관리자만 접근
# ------------------------------------
def admin_only(user):
    return user.is_superuser or user.is_staff


# ------------------------------------
# 공지 목록 페이지
# ------------------------------------
def notice_list(request):
    notices = Notice.objects.order_by('-created_at')
    return render(request, "HTML/notice_list.html", {
        "notices": notices
    })

# ------------------------------------
# 공지 작성 페이지(관리자만 접근 가능)
# ------------------------------------
def admin_only(user):
    return user.is_superuser or user.is_staff

# ------------------------------------
# 공지 생성
# ------------------------------------
@user_passes_test(admin_only)
def notice_create(request):
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")

        Notice.objects.create(
            title=title,
            content=content,
            author=request.user
        )
        return redirect("notice_list")

    return render(request, "HTML/notice_create.html")

# ------------------------------------
# 공지 삭제
# ------------------------------------
@user_passes_test(admin_only)
def notice_delete(request, notice_id):
    try:
        notice = Notice.objects.get(id=notice_id)
    except Notice.DoesNotExist:
        return redirect("notice_list")

    if request.method == "POST":
        notice.delete()
        return redirect("notice_list")

    return render(request, "HTML/notice_delete_confirm.html", {
        "notice": notice,
    })

# ------------------------------------
# 공지 확인 페이지
# ------------------------------------
def notice_detail(request, pk):
    notice = get_object_or_404(Notice, id=pk)
    return render(request, "HTML/notice_detail.html", {"notice": notice})

