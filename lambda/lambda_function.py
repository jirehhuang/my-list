# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

## my packages
import re
import urllib.request
import datetime

## globals
mode = ""
# mode = "work"
if (mode == "work"):
    required_user_id = "amzn1.ask.account.AMAWCFJKYRPNZNAR7GKWSUR6HCSQTXVEW2AGGTL5VTQTKAWVKIW35326DOEK4OLPTBCIT2VU6BCAHDK3JKEATAYARHJUKVNL55MJRDKHNR2NOJTC53R2UK4LXJ4WRNGG7EG6B5ON5B35QL27IW3GIZ7724HDMNH2K3VLVWF73IG5MN274DWWOBPHQIRW4L54YWYHGVZDI2B2DD3NEAHAJYOKSGTSXNURCWG3YNKY4IDQ"
else:
    required_user_id = "amzn1.ask.account.AMAQHAVMJSFT4QRGIGTI2BEVDF2J6AHO73JCLYUJK33JUQLGRBHZXXY3VPLJ2LIRGNOSVQE66KT74EC7CP5754545BJQOAPFG2SW3JSUS6NIWRJBZYEUHYB56WWKX6UFPGCFOXZ7ZBGCSKIG4P7IQNEPE6AGKDJZLRQ2CAMK5PRT65ODDQIYZ6LGYNCC7ZCRSE56AKFYG4W5GHBDKDSOU2S6UV5J2CGYWPWQFX5HQGOA"


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        # speak_output = "Welcome, you can say Hello or Help. Which would you like to try?"
        speak_output = "How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


# class HelloWorldIntentHandler(AbstractRequestHandler):
#     """Handler for Hello World Intent."""
#     def can_handle(self, handler_input):
#         # type: (HandlerInput) -> bool
#         return ask_utils.is_intent_name("HelloWorldIntent")(handler_input)

#     def handle(self, handler_input):
#         # type: (HandlerInput) -> Response
#         speak_output = "Hello World!"

#         return (
#             handler_input.response_builder
#                 .speak(speak_output)
#                 # .ask("add a reprompt if you want to keep the session open for the user to respond")
#                 .response
#         )


class AddToListIntentHandler(AbstractRequestHandler):
    """Handler for Add To List Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AddToListIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots
        
        ## check user
        user_id = ask_utils.request_util.get_user_id(handler_input)
        if (user_id not in ["", required_user_id]):
            return (
                handler_input.response_builder
                    # .speak("Invalid user")
                    .speak("Invalid user: " + user_id)
                    .response
            )
        
        ## initialize category: default blank
        category = ""
        
        ## get item
        item = ""
        for i in ["item_query", "task_food_est", "item_dessert", "item_drink", "item_food"]:
            ## can only take a single value
            if (i in ["item_query"] and slots[i].value):
                item = slots[i].value
            else:
                ## can take multiple values
                slotsi = ask_utils.get_simple_slot_values(ask_utils.get_slot_value_v2(handler_input, i))
                if (len(slotsi) > 0):
                    item = ", ".join([x.value for x in slotsi])
        
        # contact name task
        if (slots["name_slot"].value):
            item = slots["contact_slot"].value + " " + slots["name_slot"].value
        
        ## get purpose
        purpose = ""
        for i in ["purpose_dessert", "purpose_drink", "purpose_food", "purpose_recipe", "purpose_name", "purpose_church"]:
            if (slots[i].value):
                purpose = slots[i].value
        
        ## get suggested
        suggested = ""
        for i in ["suggested_corporation", "suggested_local"]:
            if (slots[i].value):
                suggested = slots[i].value

        # https://stackoverflow.com/a/6558571
        tzdelta = datetime.timedelta(-8/24)
        def next_weekday(weekday):
            d = datetime.datetime.now() + tzdelta
            weekday = weekday.lower()
            if (weekday == "monday"):
                weekday = 0
            elif (weekday == "tuesday"):
                weekday = 1
            elif (weekday == "wednesday"):
                weekday = 2
            elif (weekday == "thursday"):
                weekday = 3
            elif (weekday == "friday"):
                weekday = 4
            elif (weekday == "saturday"):
                weekday = 5
            elif (weekday == "sunday"):
                weekday = 6
            days_ahead = weekday - d.weekday()
            if days_ahead <= 0:  # target day already happened this week
                days_ahead += 7
            return (d + datetime.timedelta(days_ahead)).strftime("%Y-%m-%d");
        
        ## get due
        due = ""
        for i in ["due_date", "due_time", "due_day"]:
            if (slots[i].value):
                due = slots[i].value
                if (i == "due_date"):
                    due = due + " 11:59:59"
                elif (i == "due_time"):
                    now = datetime.datetime.strptime((datetime.datetime.now() + tzdelta).strftime("%H:%M:%S"), "%H:%M:%S")
                    due_time = datetime.datetime.strptime(due, "%H:%M")
                    due = (datetime.datetime.now() + tzdelta + datetime.timedelta(1 * (now > due_time))).strftime("%Y-%m-%d") + " " + due
                elif (i == "due_day"):
                    due = next_weekday(due) + " 11:59:59"
                if ("W" in due):
                    due = next_weekday("saturday") + " 11:59:59"
        
        ## determine category
        for i in ["add_grocery_slot", "item_dessert", "item_drink", "item_food"]:
            if (slots[i].value or 
                len(ask_utils.get_simple_slot_values(ask_utils.get_slot_value_v2(handler_input, i))) > 0):
                category = "Grocery"
                break
        for i in ["add_task_slot", "item_query", "task_food_est", "contact_slot"]:
            if (slots[i].value or 
                len(ask_utils.get_simple_slot_values(ask_utils.get_slot_value_v2(handler_input, i))) > 0):
                category = "Task"
                break
        for i in ["category_work"]:
            if (slots[i].value or 
                len(ask_utils.get_simple_slot_values(ask_utils.get_slot_value_v2(handler_input, i))) > 0):
                category = "Work"
                break
        
        # check inputs
        if (len(item) > 0):
            speak_output = "Added '" + item + "'"
            def capitalize(x):
                if (len(x) > 0):
                    x = x[:1].upper() + x[1:]
                return x
            item = capitalize(item)
            category = capitalize(category)
            purpose = purpose.title()
            suggested = capitalize(suggested)
            if (suggested == "H mart" or suggested == "Hmart"):
                suggested = "H Mart"
            if (suggested == "99 ranch" or suggested == "Ranch 99"):
                suggested = "99 Ranch"
            if (suggested == "Costco business center" or suggested == "Costco business"):
                suggested = "Costco Business"
                
            ## replace space with %20
            item = re.sub(" ", "%20", item)
            category = re.sub(" ", "%20", category)
            purpose = re.sub(" ", "%20", purpose)
            suggested = re.sub(" ", "%20", suggested)
            due = re.sub(" ", "%20", due)
            
            ## initialize author
            author = "Alexa%20via%20AddToListIntent"
            
            ## call webhook and return
            if (mode == "work"):
                category = "Work"
                purpose = ""
                author = author + "%20Work"
                speak_output = speak_output + " to work list"
            else:
                speak_output = speak_output + " to list"
                
            webhook = ("https://script.google.com/macros/s/AKfycbx9yHcP-bv2m8Czo7ah6GspkodwnsOk-uj1cg6snw4yXyKxCd-CZADw3XEHt8kOmKRnOA/exec?fn=add_item&item=" + 
                        item + "&category=" + category + "&purpose=" + purpose + "&suggested=" + suggested + "&due=" + due + "&author=" + author)
            contents = urllib.request.urlopen(webhook).read()
        else:
            speak_output = "No item was provided"
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("Anything else?")
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Would you like to add something to your list?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                # .speak(speak_output)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = "Hmm, I'm not sure. What would you like to do?"
        reprompt = "I didn't catch that. What can I help you with?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
# sb.add_request_handler(HelloWorldIntentHandler())
sb.add_request_handler(AddToListIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()