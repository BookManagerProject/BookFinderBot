from botbuilder.core import MessageFactory, UserState
from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions
from botbuilder.schema import InputHints

from Utility.DatabaseUtility import DatabaseUtility
from dialogs import CancelAndHelpDialog
from servicesResources.DatabaseInterface import DatabaseInterface
from user_info import UserInfo


class LoginDialog(CancelAndHelpDialog):
    def __init__(self, user_state: UserState, dialog_id: str = None):
        super(LoginDialog, self).__init__(dialog_id or LoginDialog.__name__)

        self.user_profile_accessor = user_state.create_property("UserInfo")

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.email_step,
                    self.password_step,
                    self.result_step,
                    self.final_step
                ],
            )
        )

        self.initial_dialog_id = WaterfallDialog.__name__

    async def email_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        account_info = step_context.options

        if account_info.email is None:
            message_text = 'Inserisci la tua email'
            prompt_message = MessageFactory.text(
                message_text, message_text, InputHints.expecting_input
            )
            return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )
        return await step_context.next(account_info.email)

    async def password_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        account_info = step_context.options

        # Capture the response to the previous step's prompt
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

    async def result_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        account_info = step_context._options

        # Capture the response to the previous step's prompt
        account_info.password = step_context.result

        pwd = DatabaseInterface.get_pwd(account_info.email)
        if pwd == False:
            message = f'Non ti sei registrato, per farlo basta dire "Vorrei registrarmi" o "registrazione"'
            prompt_message = MessageFactory.text(
                message, message, InputHints.expecting_input
            )
            # returning the results at the users
            await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )
            return await step_context.end_dialog(account_info)

        result = DatabaseUtility.check_pwd(account_info.password, pwd.encode('utf-8'))
        if result == True:
            account_info = DatabaseInterface.login(account_info.email)
            session_account = await self.user_profile_accessor.get(step_context.context, UserInfo)
            session_account.email = account_info.email
            session_account.firstName = account_info.firstName
            session_account.lastName = account_info.lastName
            session_account.starredBook = account_info.starredBook
            message = f'Benvenuto {session_account.firstName} {session_account.lastName}'
            prompt_message = MessageFactory.text(
                message, message, InputHints.expecting_input
            )
            # returning the results at the users
            await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )
        else:
            message = f'Email o password errata. Se vuoi riprovare chiedimi di rifare il login'
            prompt_message = MessageFactory.text(
                message, message, InputHints.expecting_input
            )
            # returning the results at the users
            await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )

        return await step_context.end_dialog(account_info)

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:

        if step_context.result:
            account_info = step_context.options

            return await step_context.end_dialog(account_info)
        return await step_context.end_dialog()
