# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.core import MessageFactory, UserState
from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions
from botbuilder.schema import InputHints

from conversation_recognizer import ConversationRecognizer
from helpers.luis_helper import LuisHelper, Intent
from user_info import UserInfo
from .login_dialog import LoginDialog
from .logout_dialog import LogoutDialog
from .registration_dialog import RegistrationDialog
from .remove_starred_book_dialog import RemoveStarredBookDialog
from .search_book_dialog import BookDialog
from .starred_book_dialog import StarredBookDialog


class MainDialog(ComponentDialog):
    def __init__(
            self, user_state: UserState, luis_recognizer: ConversationRecognizer, book_dialog: BookDialog,
            login_dialog: LoginDialog, registrazione_dialog: RegistrationDialog, starred_book_dialog: StarredBookDialog,
            logout_dialog: LogoutDialog, removed_starred_book_dialog: RemoveStarredBookDialog
    ):
        super(MainDialog, self).__init__(MainDialog.__name__)

        self._luis_recognizer = luis_recognizer
        self._book_dialog_id = book_dialog.id
        self._login_dialog_id = login_dialog.id
        self._registrazione_dialog_id = registrazione_dialog.id
        self._starred_book_dialog_id = starred_book_dialog.id
        self._remove_starred_book_dialog_id = removed_starred_book_dialog.id
        self._logout_dialog_id = logout_dialog.id
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(book_dialog)
        self.add_dialog(login_dialog)
        self.add_dialog(registrazione_dialog)
        self.add_dialog(starred_book_dialog)
        self.add_dialog(logout_dialog)
        self.add_dialog(removed_starred_book_dialog)
        self.add_dialog(
            WaterfallDialog(
                "WFDialog", [self.intro_step, self.act_step, self.final_step]
            )
        )
        self.user_profile_accessor = user_state.create_property("UserInfo")
        self.initial_dialog_id = "WFDialog"

    async def intro_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if not self._luis_recognizer.is_configured:
            await step_context.context.send_activity(
                MessageFactory.text(
                    "NOTE: LUIS is not configured. To enable all capabilities, add 'LuisAppId', 'LuisAPIKey' and "
                    "'LuisAPIHostName' to the appsettings.json file.",
                    input_hint=InputHints.ignoring_input,
                )
            )
            return await step_context.next(None)

        message_text = (
            str(step_context.options)
            if step_context.options
            else "Ciao, come posso aiutarti?"
        )
        prompt_message = MessageFactory.text(
            message_text, message_text, InputHints.expecting_input
        )

        return await step_context.prompt(
            TextPrompt.__name__, PromptOptions(prompt=prompt_message)
        )

    async def act_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        session_account = await self.user_profile_accessor.get(step_context.context, UserInfo)

        intent, luis_result = await LuisHelper.execute_luis_query(
            self._luis_recognizer, step_context.context
        )

        if intent == Intent.CERCA_LIBRO.value and luis_result:
            return await step_context.begin_dialog(self._book_dialog_id, luis_result)

        elif intent == Intent.LOGIN.value:
            if session_account.email is None:
                return await step_context.begin_dialog(self._login_dialog_id, luis_result)
            else:
                text = (
                    "Sei già loggato, non serve loggarti"
                )
                message = MessageFactory.text(
                    text, text, InputHints.ignoring_input
                )
                await step_context.context.send_activity(message)

        elif intent == Intent.REGISTRAZIONE.value:
            if session_account.email is None:
                return await step_context.begin_dialog(self._registrazione_dialog_id, luis_result)
            else:
                text = (
                    "Sei già loggato, non serve registrarti"
                )
                message = MessageFactory.text(
                    text, text, InputHints.ignoring_input
                )
                await step_context.context.send_activity(message)
        elif intent == Intent.PREFERITI.value:
            if session_account.email is not None:
                return await step_context.begin_dialog(self._starred_book_dialog_id, luis_result)
            else:
                text = (
                    "Per vedere i tuoi preferiti devi prima fare il login"
                )
                message = MessageFactory.text(
                    text, text, InputHints.ignoring_input
                )
                await step_context.context.send_activity(message)
        elif intent == Intent.LOGOUT.value:
            if session_account.email is not None:
                return await step_context.begin_dialog(self._logout_dialog_id, luis_result)
            else:
                text = (
                    "Devi essere loggato per fare il logout"
                )
                message = MessageFactory.text(
                    text, text, InputHints.ignoring_input
                )
                await step_context.context.send_activity(message)
        elif intent == Intent.CLASSIFICA.value:
            print("wip")
        elif intent == Intent.ELIMINAPREFERITI.value:
            if session_account.email is not None:
                return await step_context.begin_dialog(self._remove_starred_book_dialog_id, luis_result)
            else:
                text = (
                    "Devi essere loggato per eliminare un libro dai preferiti"
                )
                message = MessageFactory.text(
                    text, text, InputHints.ignoring_input
                )
                await step_context.context.send_activity(message)
        elif intent == Intent.WELCOME.value:
            return await step_context.replace_dialog(self.id, None)
        else:
            didnt_understand_text = (
                "Scusa ma non ho capito, perfavore ripova"
            )
            didnt_understand_message = MessageFactory.text(
                didnt_understand_text, didnt_understand_text, InputHints.ignoring_input
            )
            await step_context.context.send_activity(didnt_understand_message)

        return await step_context.next(None)

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        prompt_message = "C'è altro che posso fare per te?"
        return await step_context.replace_dialog(self.id, prompt_message)


