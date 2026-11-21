from django.contrib import admin
from .models import Question, Answer, Tag, QuestionLike, AnswerLike

class AnswerInline(admin.StackedInline):
    model = Answer
    extra = 0
    raw_id_fields = ('author',) # Защита от N+1

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'rating', 'created_at')
    search_fields = ('title', 'text')
    list_filter = ('created_at',)
    raw_id_fields = ('author',) # Защита от N+1
    inlines = [AnswerInline]

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'author', 'is_correct', 'rating', 'created_at')
    search_fields = ('text',)
    list_filter = ('is_correct', 'created_at')
    raw_id_fields = ('author', 'question') # Защита от N+1

admin.site.register(Tag)
admin.site.register(QuestionLike)
admin.site.register(AnswerLike)