from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic

from .models import *


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_questions'

    def get_queryset(self):
        return Question.objects.order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'
    context_object_name = 'question'


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'
    # context_object_name = 'question'  # unnecessary. django default(autogenerated from model) matches


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
