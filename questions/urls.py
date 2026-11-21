from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('hot/', views.hot, name='hot'),
    path('tag/<str:tag_name>/', views.question_by_tag, name='tag'),
    path('question/<int:question_id>/', views.question_detail, name='question'),
]