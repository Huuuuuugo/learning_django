from django.http import HttpResponse
from django.template import loader

from .models import Question, Choice


def index(request):
    latest_questions = Question.objects.order_by("-pub_date")[:5]
    template = loader.get_template("polls/index.html")
    return HttpResponse(template.render({"question_list": latest_questions}, request))


def details(request, question_id):
    return HttpResponse(f"You're looking at question {question_id}")


def results(request, question_id):
    return HttpResponse(f"You're looking at the results from question {question_id}")


def vote(request, question_id):
    return HttpResponse(f"You're voting on question {question_id}")
