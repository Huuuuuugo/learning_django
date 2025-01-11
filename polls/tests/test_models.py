import datetime

from django.test import TestCase
from django.utils import timezone

from polls.models import Question, Choice


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_questions(self):
        """
        Tests if the `was_published_recently()` method from `Question` model
        returns `False` for questions with a `pub_date` set in the future.
        """

        pub_date = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=pub_date)

        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_questions(self):
        """
        Tests if the `was_published_recently()` method from `Question` model
        returns `False` for questions older than one day.
        """
        pub_date = timezone.now() + datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=pub_date)

        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_new_questions(self):
        """
        Tests if the `was_published_recently()` method from `Question` model
        returns `True` for questions made within one day.
        """
        pub_date = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        new_question = Question(pub_date=pub_date)

        self.assertIs(new_question.was_published_recently(), True)
