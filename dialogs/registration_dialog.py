import re

from botbuilder.core import MessageFactory, UserState
from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult, PromptValidatorContext
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions
from botbuilder.schema import InputHints

from Utility.DatabaseUtility import DatabaseUtility
from dialogs import CancelAndHelpDialog
from servicesResources.DatabaseInterface import DatabaseInterface
from user_info import UserInfo


class RegistrationDialog(CancelAndHelpDialog):
    def __init__(self, user_state: UserState, dialog_id: str = None):
        super(RegistrationDialog, self).__init__(dialog_id or RegistrationDialog.__name__)

        self.user_profile_accessor = user_state.create_property("UserInfo")

        self.add_dialog(TextPrompt(TextPrompt.__name__, self._is_valid_email))
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.email_step,
                    self.password_step,
                    self.first_name_step,
                    self.last_name_step,
                    self.confirmation_step,
                    self.final_step
                ],
            )
        )

        self.initial_dialog_id = WaterfallDialog.__name__
        self.flag = True

    async def _is_valid_email(self, prompt_context: PromptValidatorContext):
        if self.flag:
            email = prompt_context.recognized.value
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if re.match(pattern, email):
                self.flag = False
                return True
            else:
                return False
        else:
            return True

    async def email_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        account_info = step_context.options

        if account_info.email is None:
            message_text = 'Inserisci la tua email'
            prompt_message = MessageFactory.text(
                message_text, message_text, InputHints.expecting_input
            )
            return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message, retry_prompt=MessageFactory.text(
                    "Email non valida riprova"
                ))
            )
        return await step_context.next(account_info.email)

    async def password_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        account_info = step_context.options

        account_info.email = step_context.result

        if account_info.password is None:
            message_text = 'Inserisci la password'
            prompt_message = MessageFactory.text(
                message_text, message_text, InputHints.expecting_input
            )
            return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )
        return await step_context.next(account_info.password)

    async def first_name_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        account_info = step_context.options

        # Capture the response to the previous step's prompt
        account_info.password = step_context.result

        if account_info.firstName is None:
            message_text = 'Inserisci il tuo nome'
            prompt_message = MessageFactory.text(
                message_text, message_text, InputHints.expecting_input
            )
            return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )
        return await step_context.next(account_info.firstName)

    async def last_name_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        account_info = step_context.options

        # Capture the response to the previous step's prompt
        account_info.firstName = step_context.result

        if account_info.lastName is None:
            message_text = 'Inserisci il tuo cognome'
            prompt_message = MessageFactory.text(
                message_text, message_text, InputHints.expecting_input
            )
            return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )
        return await step_context.next(account_info.lastName)

    async def confirmation_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        account_info = step_context.options
        account_info.lastName = step_context.result

        message_text = "Hai inserito i seguenti dati \n\n Email: " + account_info.email + "\n\n Password:" + account_info.password + "\n\n Nome:" + account_info.firstName + "\n\n Cognome:" + account_info.lastName
        prompt_message = MessageFactory.text(
            message_text, message_text, InputHints.expecting_input
        )

        await step_context.prompt(
            TextPrompt.__name__, PromptOptions(prompt=prompt_message)
        )

        return await step_context.end_dialog(account_info)

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        account_info = step_context.options
        hashed_pwd = DatabaseUtility.get_hashed_pwd(account_info.password)
        result = DatabaseInterface.insert_user(account_info.email, account_info.firstName, account_info.lastName,
                                               hashed_pwd)
        if result == True:
            session_account = await self.user_profile_accessor.get(step_context.context, UserInfo)
            session_account.email = account_info.email
            message_text = 'Account creato con successo, ora puoi registrare i tuoi libri preferiti'
        else:
            message_text = "Errore nella creazione dell'account, riprova con un email diversa."
        prompt_message = MessageFactory.text(message_text, message_text, InputHints.expecting_input)
        # returning the results at the users
        await step_context.prompt(TextPrompt.__name__, PromptOptions(prompt=prompt_message))
        # call the final_step to end this convesation and call MainDialog.final_step. At this point the conversation is restarted
        return await step_context.end_dialog(account_info)
