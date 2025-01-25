from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from polls.models import Question, Choice
from polls.views import CreateQuestionView, VoteView


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


class CreateQuestionViewTests(TestCase):
    url = reverse("polls:create")
    redirect = reverse("polls:index")

    def test_get_method_renders_create_page(self):
        """Test the GET request renders the 'create' template."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "polls/create.html")

    def test_post_method_empty_question(self):
        """Test posting with a missing 'question' field."""
        response = self.client.get(self.url)
        csrf_token = response.context["csrf_token"]

        data = {
            "csrfmiddlewaretoken": csrf_token,
            "question": "",
            "choices": ["Choice 1", "Choice 2"],
        }
        response = self.client.post(self.url, data)
        self.assertContains(
            response,
            CreateQuestionView.ErrorMessages.EMPTY_QUESTION.value,
            status_code=200,
        )

    def test_post_method_choices_too_few(self):
        """Test posting with less than 2 choices."""
        response = self.client.get(self.url)
        csrf_token = response.context["csrf_token"]

        data = {
            "csrfmiddlewaretoken": csrf_token,
            "question": "Test Question",
            "choices": ["Choice 1"],
        }
        post_response = self.client.post(self.url, data)
        self.assertContains(
            post_response,
            CreateQuestionView.ErrorMessages.INVALID_CHOICE_COUNT.value,
            status_code=200,
        )

    def test_post_method_choices_too_many(self):
        """Test posting with more than 8 choices."""
        response = self.client.get(self.url)
        csrf_token = response.context["csrf_token"]

        choices = ["Choice {}".format(i) for i in range(1, 10)]
        data = {
            "csrfmiddlewaretoken": csrf_token,
            "question": "Test Question",
            "choices": choices,
        }
        response = self.client.post(self.url, data)
        self.assertContains(
            response,
            CreateQuestionView.ErrorMessages.INVALID_CHOICE_COUNT.value,
            status_code=200,
        )

    def test_post_method_missing_choices(self):
        """Test posting without a 'choices' field."""
        response = self.client.get(self.url)
        csrf_token = response.context["csrf_token"]

        data = {"csrfmiddlewaretoken": csrf_token, "question": "Test Question"}
        response = self.client.post(self.url, data)
        self.assertContains(
            response,
            CreateQuestionView.ErrorMessages.MISSING_KEYS.value,
            status_code=200,
        )

    def test_post_method_missing_question(self):
        """Test posting without a 'choices' field."""
        response = self.client.get(self.url)
        csrf_token = response.context["csrf_token"]

        data = {"csrfmiddlewaretoken": csrf_token, "choices": ["Choice 1", "Choice 2"]}
        response = self.client.post(self.url, data)
        self.assertContains(
            response,
            CreateQuestionView.ErrorMessages.MISSING_KEYS.value,
            status_code=200,
        )

    def test_post_method_create_question_and_choices(self):
        """Test posting a valid question and choices."""
        response = self.client.get(self.url)
        csrf_token = response.context["csrf_token"]

        data = {
            "csrfmiddlewaretoken": csrf_token,
            "question": "Test Question",
            "choices": ["Choice 1", "Choice 2", "Choice 3"],
        }
        response = self.client.post(self.url, data)
        self.assertRedirects(response, self.redirect)

        # Ensure the Question and Choices were created in the database
        question = Question.objects.get(question_text="Test Question")
        choices = Choice.objects.filter(question=question)
        self.assertEqual(choices.count(), 3)
        self.assertTrue(
            all(
                choice.choice_text in ["Choice 1", "Choice 2", "Choice 3"]
                for choice in choices
            )
        )

    def test_post_method_empty_choices(self):
        """Test posting with a missing 'question' field."""
        response = self.client.get(self.url)
        csrf_token = response.context["csrf_token"]

        data = {
            "csrfmiddlewaretoken": csrf_token,
            "question": "Test Question",
            "choices": ["Choice 1", "", ""],
        }
        response = self.client.post(self.url, data)
        self.assertContains(
            response,
            CreateQuestionView.ErrorMessages.INVALID_CHOICE_COUNT.value,
            status_code=200,
        )


class VoteViewTests(TestCase):
    def setUp(self):
        """Create a question with choices for testing"""
        self.question = Question.objects.create(
            question_text="Test Question", pub_date=timezone.now()
        )
        self.choice1 = Choice.objects.create(
            choice_text="Choice 1", question=self.question
        )
        self.choice2 = Choice.objects.create(
            choice_text="Choice 2", question=self.question
        )

    def test_vote_valid_choice(self):
        """Test if a valid vote increases the vote count of the choice."""
        response = self.client.post(
            reverse("polls:vote", args=(self.question.id,)), {"choice": self.choice1.id}
        )
        self.assertRedirects(
            response, reverse("polls:results", args=(self.question.id,))
        )

        # Verify the choice's vote count was incremented
        self.choice1.refresh_from_db()
        self.assertEqual(self.choice1.votes, 1)

    def test_vote_invalid_choice(self):
        """Test if an invalid vote shows the correct error message."""
        invalid_choice_id = 999  # Simulate an invalid choice
        response = self.client.post(
            reverse("polls:vote", args=(self.question.id,)),
            {"choice": invalid_choice_id},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, VoteView.ErrorMessages.INVALID_CHOICE.name)

    def test_vote_no_choice_selected(self):
        """Test if no choice is selected, it returns the error message."""
        response = self.client.post(reverse("polls:vote", args=(self.question.id,)), {})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, VoteView.ErrorMessages.INVALID_CHOICE.name)

    def test_vote_on_non_existent_question(self):
        """Test if voting on a non-existent question returns a 404 error."""
        non_existent_question_id = 999  # Simulate a non-existent question
        response = self.client.post(
            reverse("polls:vote", args=(non_existent_question_id,)),
            {"choice": self.choice1.id},
        )
        self.assertEqual(response.status_code, 404)

    def test_multiple_votes_on_same_choice(self):
        """Test if multiple votes on the same choice increment the vote count correctly."""
        # First vote
        response = self.client.post(
            reverse("polls:vote", args=(self.question.id,)), {"choice": self.choice1.id}
        )
        self.choice1.refresh_from_db()
        self.assertEqual(self.choice1.votes, 1)

        # Second vote
        response = self.client.post(
            reverse("polls:vote", args=(self.question.id,)), {"choice": self.choice1.id}
        )
        self.choice1.refresh_from_db()
        self.assertEqual(self.choice1.votes, 2)

    def test_vote_redirects_to_results_page(self):
        """Test if voting redirects to the correct results page."""
        response = self.client.post(
            reverse("polls:vote", args=(self.question.id,)), {"choice": self.choice1.id}
        )
        self.assertRedirects(
            response, reverse("polls:results", args=(self.question.id,))
        )


class ResultsViewTests(TestCase):
    def setUp(self):
        """Create a question with choices for testing."""
        self.question = Question.objects.create(
            question_text="Test Question", pub_date=timezone.now()
        )
        self.choice1 = Choice.objects.create(
            choice_text="Choice 1", question=self.question, votes=5
        )
        self.choice2 = Choice.objects.create(
            choice_text="Choice 2", question=self.question, votes=3
        )

        self.question2 = Question.objects.create(
            question_text="Another Test Question", pub_date=timezone.now()
        )

    def test_results_view_with_choices(self):
        """Test if the results view displays the correct question and choices with vote counts."""
        response = self.client.get(reverse("polls:results", args=(self.question.id,)))
        self.assertEqual(response.status_code, 200)

        # Check if the correct question text is displayed
        self.assertContains(response, self.question.question_text)

        # Check if the choices are displayed with their vote counts
        self.assertContains(response, self.choice1.choice_text)
        self.assertContains(response, str(self.choice1.votes))
        self.assertContains(response, self.choice2.choice_text)
        self.assertContains(response, str(self.choice2.votes))

    def test_results_view_no_choices(self):
        """Test if the results view behaves correctly when there are no choices."""
        self.question.choice_set.all().delete()  # Remove choices for this question

        response = self.client.get(reverse("polls:results", args=(self.question.id,)))
        self.assertEqual(response.status_code, 200)

        # Check if the correct question text is displayed
        self.assertContains(response, self.question.question_text)

        # Check if no choices are displayed
        self.assertNotContains(response, "Choice")

    def test_results_view_question_not_found(self):
        """Test if the results view returns a 404 error when the question does not exist."""
        non_existent_question_id = 999  # Simulate a non-existent question
        response = self.client.get(
            reverse("polls:results", args=(non_existent_question_id,))
        )
        self.assertEqual(response.status_code, 404)

    def test_results_view_pluralize_votes(self):
        """Test if the pluralize filter works correctly for vote counts."""
        # Test a choice with 1 vote
        choice3 = Choice.objects.create(
            choice_text="Choice 3", question=self.question, votes=1
        )

        response = self.client.get(reverse("polls:results", args=(self.question.id,)))
        self.assertEqual(response.status_code, 200)

        # Check if the correct plural form of 'vote' is used
        self.assertContains(response, "Choice 1 -- 5 votes")
        self.assertContains(response, "Choice 2 -- 3 votes")
        self.assertContains(response, "Choice 3 -- 1 vote")

    def test_results_view_no_votes(self):
        """Test if the results view handles the case where no votes have been cast."""
        self.choice1.votes = 0
        self.choice2.votes = 0
        self.choice1.save()
        self.choice2.save()

        response = self.client.get(reverse("polls:results", args=(self.question.id,)))
        self.assertEqual(response.status_code, 200)

        # Check if the correct vote count (0 votes) is displayed
        self.assertContains(response, "Choice 1 -- 0 votes")
        self.assertContains(response, "Choice 2 -- 0 votes")
