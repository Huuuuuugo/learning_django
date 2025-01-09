from django.http import HttpResponse
from django.http import Http404
from django.template import loader
from django.shortcuts import render

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
    return HttpResponse(f"You're voting on question {question_id}")
