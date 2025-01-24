from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse
from django.views import generic, View
from django.template import loader
from django.db.models import F
from django.shortcuts import render, get_object_or_404
from django.core.handlers.wsgi import WSGIRequest

from .models import Question, Choice


class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "question_list"

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by(
            "-pub_date"
        )[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/details.html"

    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now())


# TODO: filter out the future questions
# TODO: create tests
class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"


class VoteView(View):
    def post(self, request, question_id):
        question = get_object_or_404(Question, pk=question_id)
        try:
            choice = question.choice_set.get(pk=request.POST["choice"])
        except (KeyError, Choice.DoesNotExist):
            return render(
                request,
                "polls/details.html",
                context={
                    "question": question,
                    "error_message": "Please select one of the options below.",
                },
            )
        else:
            choice.votes = (
                F("votes") + 1
            )  # Performs the update directly on the database
            choice.save()

            return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))


class CreateQuestionView(View):
    def get(self, request):
        return render(request, "polls/create.html")

    def post(self, request: WSGIRequest):
        # TODO: add date field
        try:
            # get question
            question_text = request.POST["question"]

            # get choices and remove empty choices
            request.POST["choices"]  # check if the 'choices' key is present
            choices = [choice for choice in request.POST.getlist("choices") if choice]

            # validate data
            if not question_text:
                return HttpResponseBadRequest("The 'question' key can not be empty")
            if not (2 <= len(choices) <= 8):
                return HttpResponseBadRequest(
                    "The number of choices must be between 2 and 8 inclusive (empty choices do not count)"
                )

            # create poll
            question = Question.objects.create(question_text=question_text)
            for choice in choices:
                question.choice_set.create(choice_text=choice)

        except KeyError:
            return HttpResponseBadRequest(
                "The request body must contain the keys 'question' and 'choices'"
            )

        return HttpResponseRedirect(reverse("polls:index"))
