from django import forms
from .models import Question, Answer, Tag, QuestionLike, AnswerLike


class AskForm(forms.ModelForm):
    tags = forms.CharField(
        label='Теги',
        required=True,
        help_text='Введите до 3 тегов через запятую или пробел',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'python, django, web'}),
    )

    class Meta:
        model = Question
        fields = ('title', 'text')
        labels = {
            'title': 'Заголовок',
            'text': 'Текст вопроса',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }

    def clean_tags(self):
        raw_tags = self.cleaned_data['tags']
        tag_names = [t.strip().lower() for t in raw_tags.replace(',', ' ').split() if t.strip()]
        unique_tags = list(dict.fromkeys(tag_names))
        if not unique_tags:
            raise forms.ValidationError('Укажите хотя бы один тег.')
        if len(unique_tags) > 3:
            raise forms.ValidationError('Можно указать не более 3 тегов.')
        for name in unique_tags:
            if len(name) > 50:
                raise forms.ValidationError(f'Тег «{name}» слишком длинный (макс. 50 символов).')
        return unique_tags

    def save(self, author, commit=True):
        question = super().save(commit=False)
        question.author = author
        if commit:
            question.save()
            tag_objs = [Tag.objects.get_or_create(name=name)[0] for name in self.cleaned_data['tags']]
            question.tags.set(tag_objs)
        return question


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('text',)
        labels = {'text': 'Ваш ответ'}
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Напишите ответ...'}),
        }

    def save(self, author, question, commit=True):
        answer = super().save(commit=False)
        answer.author = author
        answer.question = question
        if commit:
            answer.save()
        return answer


class QuestionVoteForm(forms.Form):
    question_id = forms.IntegerField(min_value=1)
    vote_type = forms.ChoiceField(choices=[('like', 'Like'), ('dislike', 'Dislike')])

    def clean_question_id(self):
        question_id = self.cleaned_data['question_id']
        try:
            self.question = Question.objects.get(pk=question_id)
        except Question.DoesNotExist:
            raise forms.ValidationError('Вопрос не найден.')
        return question_id

    def save(self, user):
        value = 1 if self.cleaned_data['vote_type'] == 'like' else -1
        like_obj, created = QuestionLike.objects.get_or_create(
            user=user,
            question=self.question,
            defaults={'value': value}
        )
        if not created:
            if like_obj.value == value:
                raise forms.ValidationError('Вы уже поставили эту оценку.')
            like_obj.value = value
            like_obj.save()

        self.question.rating = sum(self.question.likes.values_list('value', flat=True))
        self.question.save(update_fields=['rating'])
        return self.question.rating


class AnswerVoteForm(forms.Form):
    answer_id = forms.IntegerField(min_value=1)
    vote_type = forms.ChoiceField(choices=[('like', 'Like'), ('dislike', 'Dislike')])

    def clean_answer_id(self):
        answer_id = self.cleaned_data['answer_id']
        try:
            self.answer = Answer.objects.get(pk=answer_id)
        except Answer.DoesNotExist:
            raise forms.ValidationError('Ответ не найден.')
        return answer_id

    def save(self, user):
        value = 1 if self.cleaned_data['vote_type'] == 'like' else -1
        like_obj, created = AnswerLike.objects.get_or_create(
            user=user,
            answer=self.answer,
            defaults={'value': value}
        )
        if not created:
            if like_obj.value == value:
                raise forms.ValidationError('Вы уже поставили эту оценку.')
            like_obj.value = value
            like_obj.save()

        self.answer.rating = sum(self.answer.likes.values_list('value', flat=True))
        self.answer.save(update_fields=['rating'])
        return self.answer.rating


class CorrectAnswerForm(forms.Form):
    question_id = forms.IntegerField(min_value=1)
    answer_id = forms.IntegerField(min_value=1)

    def clean(self):
        cleaned_data = super().clean()
        q_id = cleaned_data.get('question_id')
        a_id = cleaned_data.get('answer_id')
        if q_id and a_id:
            try:
                self.question = Question.objects.get(pk=q_id)
            except Question.DoesNotExist:
                raise forms.ValidationError('Вопрос не найден.')
            try:
                self.answer = Answer.objects.get(pk=a_id, question=self.question)
            except Answer.DoesNotExist:
                raise forms.ValidationError('Ответ не принадлежит этому вопросу.')
        return cleaned_data

    def save(self):
        self.answer.is_correct = not self.answer.is_correct
        self.answer.save(update_fields=['is_correct'])
        return self.answer.is_correct