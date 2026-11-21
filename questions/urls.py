from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('hot/', views.hot, name='hot'),
    path('tag/<str:tag_name>/', views.question_by_tag, name='tag'),
    path('question/<int:question_id>/', views.question_detail, name='question'),
    path('ask/', views.ask, name='ask'),

    path('api/question/vote/', views.vote_question, name='vote_question'),
    path('api/answer/vote/', views.vote_answer, name='vote_answer'),
    path('api/answer/correct/', views.mark_correct_answer, name='mark_correct_answer'),
]