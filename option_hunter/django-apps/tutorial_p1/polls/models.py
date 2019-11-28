import datetime

from django.db import models
from django.utils import timezone


class Question(models.Model):
    # the Question model
    # each class variable represents a database field in the model
    # the variable name is referenced in python word & is used as the column name in database
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('data published')   # optional 1st arg to give a human-readable name

    def __str__(self):
        return self.question_text

class Choice(models.Model):
    # a relationship is defined w/ ForeignKey, i.e. each choice is related to a single Question
    # when the referenced object is deleted, also delete the objects that have references to it
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text
    def was_publiahsed_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)
