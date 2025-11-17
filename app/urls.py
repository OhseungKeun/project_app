from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('', views.main, name="main"),

    # 회원가입/로그인
    path('signup/', views.signup, name="signup"),
    path('login/', views.login_view, name="login"),
    path('check-username/', views.check_username, name='check_username'),  
    path('logout/', views.logout_view, name='logout'), 

    # 카테고리 (대분류 → 소분류 → 퀴즈)
    # ----- 수정 전 -----
    # path("quiz/", views.quiz_category_list, name="quiz_category_list"),
    # path("quiz/<int:category_id>/", views.quiz_view, name="quiz_view"),
    # path("quiz/<int:category_id>/submit/", views.quiz_submit, name="quiz_submit"),

    # ----- 수정 후 -----
    path('quiz/', views.main_category_list, name="main_category_list"),                      # 대분류 목록
    path('quiz/<int:main_id>/', views.sub_category_list, name="sub_category_list"),         # 소분류 목록
    path('quiz/sub/<int:sub_id>/', views.quiz_view, name="quiz_view"),                      # 퀴즈
    path('quiz/sub/<int:sub_id>/submit/', views.quiz_submit, name="quiz_submit"),           # 퀴즈 제출

    # 포인트 / 유저 정보
    path("point/", views.point, name="point"),
    path("user/", views.user_info, name="user_info"),

    # 공지
    path("notice/", views.notice_list, name="notice_list"),
    path("notice/create/", views.notice_create, name="notice_create"),
    path("notice/<int:pk>/", views.notice_detail, name="notice_detail"),  # ← 상세 페이지
    path("notice/delete/<int:notice_id>/", views.notice_delete, name="notice_delete"),
]
