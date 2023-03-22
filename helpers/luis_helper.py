# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from enum import Enum
from typing import Dict

from botbuilder.ai.luis import LuisRecognizer
from botbuilder.core import IntentScore, TopIntent, TurnContext

from book_search_detail import BookSearchDetail
from user_info import UserInfo


class Intent(Enum):
    CERCA_LIBRO = "CercaLibro"
    CANCEL = "Annulla"
    LOGIN = "Login"
    NONE_INTENT = "NoneIntent"
    PREFERITI = "Preferiti"
    REGISTRAZIONE = "Registrazione"
    LOGOUT = "Logout"
    CLASSIFICA = "LibriPiuCercati"
    ELIMINAPREFERITI = "RimuoviPreferiti"
    WELCOME = 'Welcome'


def top_intent(intents: Dict[Intent, dict]) -> TopIntent:
    max_intent = Intent.NONE_INTENT
    max_value = 0.0

    for intent, value in intents:
        intent_score = IntentScore(value)
        if intent_score.score > max_value:
            max_intent, max_value = intent, intent_score.score

    return TopIntent(max_intent, max_value)


class LuisHelper:
    @staticmethod
    async def execute_luis_query(
            luis_recognizer: LuisRecognizer, turn_context: TurnContext
    ) -> (Intent, object):
        """
        Returns an object with preformatted LUIS results for the bot's dialogs to consume.
        """
        result = None
        intent = None

        try:
            recognizer_result = await luis_recognizer.recognize(turn_context)

            intent = (
                sorted(
                    recognizer_result.intents,
                    key=recognizer_result.intents.get,
                    reverse=True,
                )[:1][0]
                if recognizer_result.intents
                else None
            )

            if intent == Intent.CERCA_LIBRO.value or intent == Intent.PREFERITI.value or intent == Intent.ELIMINAPREFERITI.value:
                result = BookSearchDetail()
            elif intent == Intent.LOGIN.value:
                result = UserInfo()
            elif intent == Intent.REGISTRAZIONE.value:
                result = UserInfo()

        except Exception as exception:
            print(exception)

        return intent, result
