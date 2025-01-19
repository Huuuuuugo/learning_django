from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from polls.models import Question


def create_offset_question(question_text: str, days: int):
    """Creates a question with the specified `quention_text` and
    an offset of `days` from `timezone.now()` and saves it to the database.

    Use a positive `days` value for questions in the future and a negative for
    questions in the past.
    """

    pub_date = timezone.now() + timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=pub_date)


class IndexViewTests(TestCase):
    def test_no_questions(self):
        """Test if the index page shows an appropriate message when there are no polls avaliable"""
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)

        self.assertQuerySetEqual(response.context["question_list"], [])
        self.assertContains(response, "No polls avaliable")

    def test_question_sorting(self):
        """Tests if the question on the polls index are sorted correctly"""
        question1 = create_offset_question("question 1", days=-3)
        question2 = create_offset_question("question 2", days=-2)
        question3 = create_offset_question("question 3", days=-1)

        response1 = self.client.get(reverse("polls:index"))
        self.assertEqual(response1.status_code, 200)

        self.assertQuerySetEqual(
            response1.context["question_list"], [question3, question2, question1]
        )

    def test_question_limit(self):
        """Tests if the question on the polls index are within the limit of only the latest 5"""
        question1 = create_offset_question("question 1", days=-6)
        question2 = create_offset_question("question 2", days=-5)
        question3 = create_offset_question("question 3", days=-4)
        question4 = create_offset_question("question 4", days=-3)
        question5 = create_offset_question("question 5", days=-2)
        question6 = create_offset_question("question 6", days=-1)

        response1 = self.client.get(reverse("polls:index"))
        self.assertEqual(response1.status_code, 200)

        self.assertQuerySetEqual(
            response1.context["question_list"],
            [question6, question5, question4, question3, question2],
        )

    def test_past_questions_only(self):
        """Tests if the index page behaves correctly with a single question made in the past"""
        question = create_offset_question("question 1", days=-3)
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)

        self.assertQuerySetEqual(response.context["question_list"], [question])

    def test_future_questions_only(self):
        """Tests if the index page behaves correctly with a single question made in the future"""
        question = create_offset_question("question 1", days=3)

        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)

        self.assertQuerySetEqual(response.context["question_list"], [])

    def test_past_and_future_questions(self):
        """Tests if the index page behaves correctly with a query set that mixes past and future questions"""
        past1 = create_offset_question("question 1", days=-3)
        past2 = create_offset_question("question 2", days=-4)
        future1 = create_offset_question("question 3", days=3)
        future2 = create_offset_question("question 4", days=5)

        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)

        self.assertQuerySetEqual(response.context["question_list"], [past1, past2])


class DetailViewTests(TestCase):
    def test_past_questions(self):
        """Tests if the detail page is rendered for questions in the past"""
        question = create_offset_question("test_past_questions", -2)
        response = self.client.get(reverse("polls:details", args=(question.pk,)))
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, question.question_text)

    def test_future_questions(self):
        """Tests if the detail view returns 404 for questions in the future"""
        question = create_offset_question("test_future_questions", 2)
        response = self.client.get(reverse("polls:details", args=(question.pk,)))

        self.assertEqual(response.status_code, 404)
