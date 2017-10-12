# coding=utf-8

# gst
# By Mahesh Jadhav <mahesh.jadhav@capgemini.com>
#
# Goods and Services Tax in India

import csv
import logging
import os
from datetime import datetime
from random import randint

from flask import Flask, render_template
from flask_ask import Ask, question, statement

__author__ = 'Mahesh Jadhav'
__email__ = 'mahesh.jadhav@capgemini.com'

app = Flask(__name__)
ask = Ask(app, '/')
logging.getLogger("flask_ask").setLevel(logging.DEBUG)

# Read GST Rates from gst-rates.csv file for all items
gst_rates_dict = {}
with open('gst-rates.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        gst_rates_dict[row['item']] = row['rate']


# Session starter
#
# This intent is fired automatically at the point of launch (= when the session starts).
# Use it to register a state machine for things you want to keep track of, such as what the last intent was, so as to be
# able to give contextual help.

@ask.on_session_started
def start_session():
    """
    Fired at the start of the session, this is a great place to initialise state variables and the like.
    """
    logging.debug("Session started at {}".format(datetime.now().isoformat()))


# Launch intent
#
# This intent is fired automatically at the point of launch.
# Use it as a way to introduce your Skill and say hello to the user. If you envisage your Skill to work using the
# one-shot paradigm (i.e. the invocation statement contains all the parameters that are required for returning the
# result

@ask.launch
def handle_launch():
    """
    (QUESTION) Responds to the launch of the Skill with a welcome statement and a card.

    Templates:
    * Initial statement: 'welcome'
    * Reprompt statement: 'welcome_re'
    * Card title: 'gst'
    * Card body: 'welcome_card'
    """

    welcome_text = render_template('welcome')
    welcome_re_text = render_template('welcome_re')
    welcome_card_text = render_template('welcome_card')

    return question(welcome_text).reprompt(welcome_re_text).standard_card(title="gst",
                                                                          text=welcome_card_text)


# Custom intents
#
# These intents are custom intents. We need to define utterances for custom intents.

@ask.intent('AboutIntent')
def handle_about():
    """
    (STATEMENT) Handles the 'about' custom intention.
    """
    about_text = render_template('about')
    card_title = render_template('card_title')
    return statement(about_text).simple_card(card_title, about_text)


@ask.intent('FactIntent')
def handle_fact():
    """
    (STATEMENT) Handles the 'fact' custom intention.
    """
    num_facts = 10  # increment this when adding a new fact template
    fact_index = randint(0, num_facts - 1)
    fact_text = render_template('gst_fact_{}'.format(fact_index))
    card_title = render_template('card_title')
    return statement(fact_text).simple_card(card_title, fact_text)


@ask.intent('RateIntent', mapping={'item': 'Item'})
def handle_rate(item):
    """
    (STATEMENT) Handles the 'rate' or 'slab' or 'tax' custom intention.
    """
    card_title = render_template('card_title')
    try:
        rate = gst_rates_dict[item]
    except Exception as e:
        logging.error('Failed getting rate for item {}'.format(item))
        return unknown_item_reprompt()

    if rate is not None:
        rate_text = render_template('gst_rate', item=item, rate=rate)
        return statement(rate_text).simple_card(card_title, rate_text)
    else:
        return unknown_item_reprompt()


def unknown_item_reprompt():
    """
    (Question) handles the unknown gst item reprompt 
    :return: response unknown item prompt
    """
    card_title = render_template('card_title')
    question_text = render_template('unknown_item_reprompt')
    return question(question_text).reprompt(question_text).simple_card(card_title, question_text)


# Built-in intents
#
# These intents are built-in intents. Conveniently, built-in intents do not need you to define utterances, so you can
# use them straight out of the box. Depending on whether you wish to implement these in your application, you may keep
#  or delete them/comment them out.
#
# More about built-in intents: http://d.pr/KKyx

@ask.intent('AMAZON.StopIntent')
def handle_stop():
    """
    (STATEMENT) Handles the 'stop' built-in intention.
    """
    farewell_text = render_template('stop_bye')
    return statement(farewell_text)


@ask.intent('AMAZON.CancelIntent')
def handle_cancel():
    """
    (STATEMENT) Handles the 'cancel' built-in intention.
    """
    farewell_text = render_template('cancel_bye')
    return statement(farewell_text)


@ask.intent('AMAZON.HelpIntent')
def handle_help():
    """
    (QUESTION) Handles the 'help' built-in intention.

    You can provide context-specific help here by rendering templates conditional on the help referrer.
    """

    help_text = render_template('help_text')
    return question(help_text)


@ask.intent('AMAZON.NoIntent')
def handle_no():
    """
    (?) Handles the 'no' built-in intention.
    """
    pass


@ask.intent('AMAZON.YesIntent')
def handle_yes():
    """
    (?) Handles the 'yes'  built-in intention.
    """
    pass


@ask.intent('AMAZON.PreviousIntent')
def handle_back():
    """
    (?) Handles the 'go back!'  built-in intention.
    """
    pass


@ask.intent('AMAZON.StartOverIntent')
def start_over():
    """
    (QUESTION) Handles the 'start over!'  built-in intention.
    """
    pass


# Ending session
#
# This intention ends the session.

@ask.session_ended
def session_ended():
    """
    Returns an empty for `session_ended`.

    .. warning::

    The status of this is somewhat controversial. The `official documentation`_ states that you cannot return a response
    to ``SessionEndedRequest``. However, if it only returns a ``200/OK``, the quit utterance (which is a default test
    utterance!) will return an error and the skill will not validate.

    """
    return statement("")


if __name__ == '__main__':
    if 'ASK_VERIFY_REQUESTS' in os.environ:
        verify = str(os.environ.get('ASK_VERIFY_REQUESTS', '')).lower()
        if verify == 'false':
            app.config['ASK_VERIFY_REQUESTS'] = False
    app.run(debug=True)
