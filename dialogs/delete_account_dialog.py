from botbuilder.core import MessageFactory, UserState
from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions
from botbuilder.schema import InputHints, SuggestedActions, CardAction, ActionTypes

from Utility.DatabaseUtility import DatabaseUtility
from dialogs import CancelAndHelpDialog
from servicesResources.DatabaseInterface import DatabaseInterface
from user_info import UserInfo


class DeleteAccountDialog(CancelAndHelpDialog):
    def __init__(self, user_state: UserState, dialog_id: str = None):
        super(DeleteAccountDialog, self).__init__(dialog_id or DeleteAccountDialog.__name__)

        self.user_profile_accessor = user_state.create_property("UserInfo")

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.password_step,
                    self.confirmation_step,
                    self.final_step,
                ],
            )
        )

        self.initial_dialog_id = WaterfallDialog.__name__

    async def password_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        account_info = step_context.options

        session_account = await self.user_profile_accessor.get(step_context.context, UserInfo)

        if session_account.email is not None:
            message = f"Inserisci la password per l'account **{session_account.email}** per procedere alla cancellazione."
            prompt_message = MessageFactory.text(
                message, message, InputHints.expecting_input
            )
            return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )
        return await step_context.next(account_info.name)

    async def confirmation_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        session_account = await self.user_profile_accessor.get(step_context.context, UserInfo)

        input_password = step_context.result
        pwd = DatabaseInterface.get_pwd(session_account.email)
        result = DatabaseUtility.check_pwd(input_password, pwd.encode('utf-8'))
        if result == True:
            message = MessageFactory.text(
                "Sei sicuro di voler cancellare l'account? (perderai anche tutte i libri registrati)")
            message.suggested_actions = SuggestedActions(
                actions=[
                    CardAction(
                        title="Sì",
                        type=ActionTypes.im_back,
                        value="Si",
                    ),
                    CardAction(
                        title="No",
                        type=ActionTypes.im_back,
                        value="No",
                    ),
                ]
            )
            return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=message)
            )
        else:
            message_text = 'Password errata'
            prompt_message = MessageFactory.text(
                message_text, message_text, InputHints.ignoring_input
            )
            await step_context.prompt(TextPrompt.__name__, PromptOptions(prompt=prompt_message))
            return await step_context.end_dialog()

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:

        answer = step_context.result

        session_account = await self.user_profile_accessor.get(step_context.context, UserInfo)
        if isinstance(answer, str):
            if answer == 'Si':
                result = DatabaseInterface.delete_account(session_account)
                if result == True:
                    session_account.email = None
                    session_account.firstName = None
                    session_account.lastName = None
                    session_account.starredBook = None
                    message_text = "**Cancellazione eseguita con successo.**"
                else:
                    message_text = "Errore nella cancellazione dell'account, riprova."

                prompt_message = MessageFactory.text(
                    message_text, message_text, InputHints.ignoring_input
                )
                await step_context.prompt(TextPrompt.__name__, PromptOptions(prompt=prompt_message))
            else:
                message_text = 'Operazione annullata'
                prompt_message = MessageFactory.text(
                    message_text, message_text, InputHints.ignoring_input
                )
                await step_context.prompt(TextPrompt.__name__, PromptOptions(prompt=prompt_message))
                return await step_context.end_dialog()

        return await step_context.end_dialog()
