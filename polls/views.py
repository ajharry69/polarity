from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from .models import *


def index(request):
    latest_questions = Question.objects.order_by('-pub_date')[:5]
    # dictionary mapping template variable names to Python objects
    context = {
        'latest_questions': latest_questions
    }
    return render(request, 'polls/index.html', context)


def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/details.html', {'question': question})


def results(request, question_id):
    return HttpResponse(f'You are looking at the results of question {question_id}')


def vote(request, question_id):
    return HttpResponse(f'You are voting on question {question_id}')
