import datetime

from django.db import models
from django.contrib import admin
from django.utils import timezone


class Question(models.Model):
    question_text = models.CharField("question", max_length=200)
    pub_date = models.DateTimeField("date published", default=timezone.now)

    # information used by the admin site
    @admin.display(
        boolean=True,  # makes the field be displayed as boolean
        ordering="pub_date",  # how to oreder entries by this function
        description="Was published recently?",  # name of the function on the admin page
    )
    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def __str__(self):
        return f"{self.question_text}, {self.pub_date}"


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField("choice", max_length=200)
    votes = models.IntegerField("votes", default=0)

    def __str__(self):
        return f"{self.choice_text}, {self.votes}"
