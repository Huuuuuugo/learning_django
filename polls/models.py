import datetime

from django.db import models
from django.utils import timezone


class Question(models.Model):
    question_text = models.CharField("question", max_length=200)
    pub_date = models.DateTimeField("date published", default=timezone.now)

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

    def __str__(self):
        return f"{self.question_text}, {self.pub_date}"


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField("choice", max_length=200)
    votes = models.IntegerField("votes", default=0)

    def __str__(self):
        return f"{self.choice_text}, {self.votes}"
