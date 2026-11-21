from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.urls import reverse
from .models import Question, Tag
from .forms import AskForm, AnswerForm
import json
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from .forms import AskForm, AnswerForm, QuestionVoteForm, AnswerVoteForm, CorrectAnswerForm

def paginate(objects_list, request, per_page=20):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    questions = Question.objects.get_new()
    return render(request, 'questions/index.html', {'page_obj': paginate(questions, request)})


def hot(request):
    questions = Question.objects.get_hot()
    return render(request, 'questions/hot.html', {'page_obj': paginate(questions, request)})


def question_by_tag(request, tag_name):
    tag_obj = get_object_or_404(Tag, name=tag_name)
    questions = Question.objects.get_by_tag(tag_name)
    return render(request, 'questions/tag.html', {'page_obj': paginate(questions, request), 'tag': tag_obj})


@login_required
def ask(request):
    if request.method == 'POST':
        form = AskForm(request.POST)
        if form.is_valid():
            question = form.save(author=request.user)
            return redirect('question', question_id=question.id)
    else:
        form = AskForm()
    return render(request, 'questions/ask.html', {'form': form})


def question_detail(request, question_id):
    question_obj = get_object_or_404(Question.objects.select_related('author', 'author__profile'), pk=question_id)
    answers_qs = question_obj.answers.select_related('author', 'author__profile').order_by('-rating', 'created_at')
    per_page = 20

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect(f"{reverse('login')}?next={request.path}")
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(author=request.user, question=question_obj)
            # Вычисляем страницу, на которую попал новый ответ
            answer_ids = list(answers_qs.values_list('id', flat=True))
            position = answer_ids.index(answer.id)
            page_num = position // per_page + 1
            url = reverse('question', kwargs={'question_id': question_obj.id})
            return redirect(f'{url}?page={page_num}#answer-{answer.id}')
    else:
        form = AnswerForm()

    return render(request, 'questions/question.html', {
        'question': question_obj,
        'page_obj': paginate(answers_qs, request, per_page=per_page),
        'form': form,
    })

def _parse_json_body(request):
    try:
        return json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return None


def vote_question(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Требуется авторизация', 'login_url': reverse('login')}, status=401)

    data = _parse_json_body(request)
    if data is None:
        return JsonResponse({'error': 'Некорректный JSON'}, status=400)

    form = QuestionVoteForm(data)
    if not form.is_valid():
        return JsonResponse({'error': 'Невалидные параметры', 'details': form.errors}, status=400)

    try:
        new_rating = form.save(user=request.user)
    except ValidationError as e:
        return JsonResponse({'error': e.message}, status=400)

    return JsonResponse({'rating': new_rating})


def vote_answer(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Требуется авторизация', 'login_url': reverse('login')}, status=401)

    data = _parse_json_body(request)
    if data is None:
        return JsonResponse({'error': 'Некорректный JSON'}, status=400)

    form = AnswerVoteForm(data)
    if not form.is_valid():
        return JsonResponse({'error': 'Невалидные параметры', 'details': form.errors}, status=400)

    try:
        new_rating = form.save(user=request.user)
    except ValidationError as e:
        return JsonResponse({'error': e.message}, status=400)

    return JsonResponse({'rating': new_rating})


def mark_correct_answer(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Требуется авторизация', 'login_url': reverse('login')}, status=401)

    data = _parse_json_body(request)
    if data is None:
        return JsonResponse({'error': 'Некорректный JSON'}, status=400)

    form = CorrectAnswerForm(data)
    if not form.is_valid():
        return JsonResponse({'error': 'Невалидные параметры', 'details': form.errors}, status=400)

    if form.question.author != request.user:
        return JsonResponse({'error': 'Только автор вопроса может отметить правильный ответ'}, status=403)

    is_correct = form.save()
    return JsonResponse({'is_correct': is_correct})