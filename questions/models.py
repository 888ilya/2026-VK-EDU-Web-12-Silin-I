from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Название')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name

class QuestionManager(models.Manager):
    def get_new(self):
        return self.order_by('-created_at').select_related('author', 'author__profile').prefetch_related('tags')
        
    def get_hot(self):
        return self.order_by('-rating', '-created_at').select_related('author', 'author__profile').prefetch_related('tags')
        
    def get_by_tag(self, tag_name):
        return self.filter(tags__name=tag_name).select_related('author', 'author__profile').prefetch_related('tags')

class Question(models.Model):
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст вопроса')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions', verbose_name='Автор')
    tags = models.ManyToManyField(Tag, related_name='questions', verbose_name='Теги')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')

    objects = QuestionManager()

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('question', kwargs={'question_id': self.pk})

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', verbose_name='Вопрос')
    text = models.TextField(verbose_name='Текст ответа')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers', verbose_name='Автор')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    is_correct = models.BooleanField(default=False, verbose_name='Правильный ответ')
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'

    def __str__(self):
        return f'Ответ от {self.author} на {self.title}'

class QuestionLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='Вопрос')
    is_like = models.BooleanField(default=True, verbose_name='Лайк/Дизлайк')

    class Meta:
        unique_together = ('user', 'question')
        verbose_name = 'Оценка вопроса'
        verbose_name_plural = 'Оценки вопросов'

class AnswerLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, verbose_name='Ответ')
    is_like = models.BooleanField(default=True, verbose_name='Лайк/Дизлайк')

    class Meta:
        unique_together = ('user', 'answer')
        verbose_name = 'Оценка ответа'
        verbose_name_plural = 'Оценки ответов'