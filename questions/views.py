from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

QUESTIONS = []
for i in range(1, 30):
    QUESTIONS.append({
        'title': f'title {i}',
        'id': i,
        'text': f'text {i}'
    })

def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page', 1)
    
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
        
    return page

def index(request):
    page = paginate(QUESTIONS, request)
    return render(request, 'core/index.html', {'questions': page})

def hot(request):
    page = paginate(QUESTIONS, request)
    return render(request, 'core/hot.html', {'questions': page})

def tag(request, tag_name):
    page = paginate(QUESTIONS, request)
    return render(request, 'core/tag.html', {'questions': page, 'tag': tag_name})

def question(request, question_id):
    question_item = next((q for q in QUESTIONS if q['id'] == question_id), None)
    return render(request, 'core/question.html', {'question': question_item})

def ask(request):
    return render(request, 'core/ask.html')