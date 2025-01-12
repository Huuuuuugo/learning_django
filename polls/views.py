from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404
from django.urls import reverse
from django.template import loader
from django.db.models import F
from django.shortcuts import render, get_object_or_404

from .models import Question, Choice


def index(request):
    latest_questions = Question.objects.order_by("-pub_date")[:5]
    context = {"question_list": latest_questions}
    return render(request, "polls/index.html", context)


def details(request, question_id):
    try:
        question = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        raise Http404("This question doesn't exist or is no longer avaliable")
    context = {"question": question}
    return render(request, "polls/details.html", context)


def results(request, question_id):
    return HttpResponse(f"You're looking at the results from question {question_id}")


def vote(request, question_id):
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
        choice.votes = F("votes") + 1  # Performs the update directly on the database
        choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))
