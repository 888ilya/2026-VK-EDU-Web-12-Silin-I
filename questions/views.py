from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Question, Tag

def paginate(objects_list, request, per_page=20):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)

def index(request):
    questions = Question.objects.get_new()
    return render(request, 'index.html', {'page_obj': paginate(questions, request)})

def hot(request):
    questions = Question.objects.get_hot()
    return render(request, 'hot.html', {'page_obj': paginate(questions, request)})

def question_by_tag(request, tag_name):
    tag_obj = get_object_or_404(Tag, name=tag_name)
    questions = Question.objects.get_by_tag(tag_name)
    return render(request, 'tag.html', {'page_obj': paginate(questions, request), 'tag': tag_obj})

def question_detail(request, question_id):
    # select_related здесь предотвращает N+1 при загрузке автора вопроса
    question_obj = get_object_or_404(Question.objects.select_related('author', 'author__profile'), pk=question_id)
    # select_related предотвращает N+1 при загрузке авторов ответов
    answers = question_obj.answers.select_related('author', 'author__profile').order_by('-rating', 'created_at')
    return render(request, 'question.html', {'question': question_obj, 'page_obj': paginate(answers, request)})