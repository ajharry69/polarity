from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

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
    return render(request, 'polls/detail.html', {'question': question})


def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {'question': question})


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', context={
            'question': question,
            'error_message': 'You did not select a choice!'
        })
    else:
        # choice.votes += 1 # to avoid race conditions: lack of consistency during concurrent update
        choice.votes = F('votes') + 1
        choice.save()
        choice.refresh_from_db()
        # Always return an HttpResponseRedirect after successfully dealing with POST data.
        # This prevents data from being posted twice if a user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question_id,)))
