import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Profile
from questions.models import Question, Answer, Tag, QuestionLike, AnswerLike
from faker import Faker

class Command(BaseCommand):
    help = 'Заполняет БД тестовыми данными. Формат: python manage.py fill_db [ratio]'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Коэффициент заполнения')

    def handle(self, *args, **kwargs):
        ratio = kwargs['ratio']
        fake = Faker('ru_RU') # Используем русский язык для данных
        
        users_count = ratio
        questions_count = ratio * 10
        answers_count = ratio * 100
        tags_count = ratio
        likes_count = ratio * 200 # Общее количество лайков

        self.stdout.write(self.style.WARNING(f'Начинаем генерацию данных (ratio={ratio})...'))

        # 1. Пользователи и Профили
        self.stdout.write('Создаем пользователей...')
        users = [User(username=fake.unique.user_name(), email=fake.unique.email(), password='password') for _ in range(users_count)]
        User.objects.bulk_create(users, batch_size=5000, ignore_conflicts=True)
        
        saved_users = list(User.objects.all())
        profiles = [Profile(user=u) for u in saved_users if not hasattr(u, 'profile')]
        Profile.objects.bulk_create(profiles, batch_size=5000)

        # 2. Теги
        self.stdout.write('Создаем теги...')
        tags = [Tag(name=fake.unique.word()[:50]) for _ in range(tags_count)]
        Tag.objects.bulk_create(tags, batch_size=5000, ignore_conflicts=True)
        saved_tags = list(Tag.objects.all())

        # 3. Вопросы
        self.stdout.write('Создаем вопросы...')
        questions = [Question(
            title=fake.sentence()[:255],
            text=fake.text(),
            author=random.choice(saved_users),
            rating=random.randint(-100, 100)
        ) for _ in range(questions_count)]
        Question.objects.bulk_create(questions, batch_size=5000)
        saved_questions = list(Question.objects.all())

        # Привязка тегов к вопросам
        self.stdout.write('Привязываем теги к вопросам...')
        ThroughModel = Question.tags.through
        question_tags = []
        for q in saved_questions:
            # От 1 до 3 случайных тегов на вопрос
            q_tags = random.sample(saved_tags, k=random.randint(1, min(3, len(saved_tags))))
            for t in q_tags:
                question_tags.append(ThroughModel(question_id=q.id, tag_id=t.id))
        ThroughModel.objects.bulk_create(question_tags, batch_size=5000, ignore_conflicts=True)

        # 4. Ответы
        self.stdout.write('Создаем ответы...')
        answers = [Answer(
            question=random.choice(saved_questions),
            text=fake.text(),
            author=random.choice(saved_users),
            is_correct=random.choice([True, False, False]), # Правильных ответов меньше
            rating=random.randint(-50, 50)
        ) for _ in range(answers_count)]
        Answer.objects.bulk_create(answers, batch_size=5000)
        saved_answers = list(Answer.objects.all())

        # 5. Лайки
        self.stdout.write('Создаем лайки...')
        q_likes = [QuestionLike(
            user=random.choice(saved_users),
            question=random.choice(saved_questions),
            is_like=random.choice([True, False])
        ) for _ in range(likes_count // 2)]
        QuestionLike.objects.bulk_create(q_likes, batch_size=5000, ignore_conflicts=True)

        a_likes = [AnswerLike(
            user=random.choice(saved_users),
            answer=random.choice(saved_answers),
            is_like=random.choice([True, False])
        ) for _ in range(likes_count // 2)]
        AnswerLike.objects.bulk_create(a_likes, batch_size=5000, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS('Генерация успешно завершена!'))