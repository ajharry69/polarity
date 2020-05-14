from django.http import HttpResponse
from django.template import loader

from .models import *


def index(request):
    latest_questions = Question.objects.order_by('-pub_date')[:5]
    template = loader.get_template('polls/index.html')
    # dictionary mapping template variable names to Python objects
    context = {
        'latest_questions': latest_questions
    }
    return HttpResponse(template.render(context, request))


def detail(request, question_id):
    return HttpResponse(f'You are looking at question {question_id}')


def results(request, question_id):
    return HttpResponse(f'You are looking at the results of question {question_id}')


def vote(request, question_id):
    return HttpResponse(f'You are voting on question {question_id}')
