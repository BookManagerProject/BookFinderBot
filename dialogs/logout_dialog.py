from botbuilder.core import MessageFactory, UserState
from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult, Choice, ChoicePrompt, \
    ComponentDialog
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions
from botbuilder.schema import InputHints

from user_info import UserInfo


class LogoutDialog(ComponentDialog):
    def __init__(self, user_state: UserState, dialog_id: str = None):
        super(LogoutDialog, self).__init__(dialog_id or LogoutDialog.__name__)

        self.user_profile_accessor = user_state.create_property("UserInfo")

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.logout_step,
                    self.logout_final
                ],
            )
        )
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))

        self.initial_dialog_id = WaterfallDialog.__name__

    async def logout_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        message_text = (
            "Sei sicuro di fare il logout?"
        )
        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text(message_text),
                choices=[Choice("Si"), Choice("Annulla")],
            ),
        )
        return await step_context.next(step_context.options)

    async def logout_final(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        choice = step_context.result
        if choice.index == 0:
            session_account = await self.user_profile_accessor.get(step_context.context, UserInfo)
            session_account.email = None
            session_account.firstName = None
            session_account.lastName = None
            session_account.starredBook = None
            message_text = (
                "Logout effettuato!"
            )
            message = MessageFactory.text(
                message_text, message_text, InputHints.ignoring_input
            )
            await step_context.context.send_activity(message)
        elif choice.index == 1:
            message_text = (
                "Logout annullato!"
            )
            message = MessageFactory.text(
                message_text, message_text, InputHints.ignoring_input
            )
            await step_context.context.send_activity(message)
        return await step_context.next(None)
