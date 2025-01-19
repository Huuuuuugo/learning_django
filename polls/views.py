from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404
from django.urls import reverse
from django.views import generic, View
from django.template import loader
from django.db.models import F
from django.shortcuts import render, get_object_or_404

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
    def post(request, question_id):
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

    def post(self, request):
        return HttpResponseRedirect(reverse("polls:index"))
