from django.test import TestCase
from django.urls import reverse

from .models import *


def create_question(question_text, days, choice_texts=None):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    question = Question.objects.create(question_text=question_text, pub_date=time)
    if choice_texts:
        choices = []
        for c in choice_texts:
            choices.append(Choice(question=question, choice_text=c))
        question.choice_set.bulk_create(choices)
        question.refresh_from_db()
    return question


class QuestionDetailViewTestCase(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_query = create_question('Future query', days=3)
        response = self.client.get(reverse('polls:detail', args=(future_query.id,)))
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_query = create_question('Past query', days=-3)
        response = self.client.get(reverse('polls:detail', args=(past_query.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, past_query.question_text)


class QuestionResultsViewTestCase(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_query = create_question('Future query', days=3)
        response = self.client.get(reverse('polls:results', args=(future_query.id,)))
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_query = create_question('Past query', days=-3)
        response = self.client.get(reverse('polls:results', args=(past_query.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, past_query.question_text)


class QuestionIndexViewTestCase(TestCase):
    def test_no_question(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available!')
        self.assertQuerysetEqual(response.context['latest_questions'], [])

    def test_past_question_without_choices(self):
        """
        Questions without a choice and with a pub_date in the past are not displayed on the
        index page.
        """
        create_question("Past query", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_questions'],
            [],
        )

    def test_past_question_with_choices(self):
        """
        Questions with choice(s) and a pub_date in the past are displayed on the
        index page.
        """
        create_question("Past query", days=-30, choice_texts=[
            'PQC 1',
            'PQC 2',
            'PQC 3',
        ])
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_questions'],
            ['<Question: Past query>'],
        )

    def test_future_question_without_choices(self):
        """
        Questions without choices and with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question("Future query", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available!")
        self.assertQuerysetEqual(
            response.context['latest_questions'],
            [],
        )

    def test_future_question_with_choices(self):
        """
        Questions with a pub_date in the future aren't displayed on the index page
        even if they have choices.
        """
        create_question("Future query", days=30, choice_texts=[
            'FQC 1',
            'FQC 2',
            'FQC 3',
        ])
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available!")
        self.assertQuerysetEqual(
            response.context['latest_questions'],
            [],
        )

    def test_future_and_past_questions_without_choices(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        create_question("Past query", days=-30)
        create_question("Future query", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_questions'],
            [],
        )

    def test_future_and_past_questions_with_choices(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        create_question("Past query", days=-30, choice_texts=[
            'PQC 1',
            'PQC 2',
            'PQC 3',
        ])
        create_question("Future query", days=30, choice_texts=[
            'FQC 1',
            'FQC 2',
            'FQC 3',
        ])
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_questions'],
            ['<Question: Past query>'],
        )

    def test_past_three_questions_with_and_without_choices(self):
        """
        The questions index page may display multiple questions.
        """
        create_question('Past query 1', days=-30, choice_texts=[
            'PQ1C 1',
            'PQ1C 2',
            'PQ1C 3',
        ])
        create_question('Past query 2', days=-30)
        create_question('Past query 3', days=-5, choice_texts=[
            'PQ3C 1',
            'PQ3C 2',
            'PQ3C 3',
        ])
        response = self.client.get(reverse('polls:index'))
        # tests the order also
        self.assertQuerysetEqual(
            response.context['latest_questions'],
            ['<Question: Past query 3>', '<Question: Past query 1>'],
        )


class QuestionTestCase(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        future_date = timezone.now() + datetime.timedelta(days=30)
        question = Question(pub_date=future_date)
        self.assertIs(question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is passed.
        """
        past_date = timezone.now() - datetime.timedelta(days=1, seconds=1)
        question = Question(pub_date=past_date)
        self.assertIs(question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last 24hrs.
        """
        past_date = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        question = Question(pub_date=past_date)
        self.assertIs(question.was_published_recently(), True)

    def test_was_published_recently_with_question_published_in_a_day(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is 24hrs.
        """
        past_date = timezone.now() - datetime.timedelta(hours=24)
        question = Question(pub_date=past_date)
        self.assertIs(question.was_published_recently(), False)
