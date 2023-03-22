from botbuilder.core import MessageFactory, UserState
from botbuilder.dialogs import (
    PromptOptions
)
from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import TextPrompt
from botbuilder.schema import InputHints, HeroCard, CardAction, ActionTypes

from dialogs import CancelAndHelpDialog


class HelpDialog(CancelAndHelpDialog):
    def __init__(self, user_state: UserState, dialog_id: str = None):
        super(HelpDialog, self).__init__(dialog_id or HelpDialog.__name__)

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.help_step
                ],
            )
        )

        self.initial_dialog_id = WaterfallDialog.__name__

    async def help_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        message_text = 'Ecco le mie principali funzioni:\n\n'
        message_text += '  1. Cerca un libro.\n\n' \
                        '  2. Effetture il login per gestire i libri preferiti.\n\n' \
                        '  3. Effettuare la regitrazione.\n\n' \
                        '  4. Visulizza preferiti.\n\n' \
                        '  5. Elimina preferiti.\n\n'
        prompt_message = MessageFactory.text(
            message_text, message_text, InputHints.ignoring_input
        )
        await step_context.prompt(
            TextPrompt.__name__, PromptOptions(prompt=prompt_message)
        )

        card = HeroCard(title='Per comodità clicca la funzionalità che desideri', buttons=[
            CardAction(
                title='Cerca un libro',
                type=ActionTypes.im_back,
                value='cerca un libro',
            ),
            CardAction(
                title='Effettua il login',
                type=ActionTypes.im_back,
                value='login',
            ),
            CardAction(
                title='Effettua la registrazione',
                type=ActionTypes.im_back,
                value='registrati',
            ),
            CardAction(
                title="Visualizza i preferiti",
                type=ActionTypes.im_back,
                value='preferiti',
            ),
            CardAction(
                title='Elimina i preferiti',
                type=ActionTypes.im_back,
                value='elimina preferiti',
            ),
            CardAction(
                title='Libri più cercati',
                type=ActionTypes.im_back,
                value='libri più cercati',
            ),
            CardAction(
                title='Elimina il mio account',
                type=ActionTypes.im_back,
                value='elimina account',
            ),
        ],
                        )

        # message = MessageFactory.attachment(CardFactory.hero_card(card))
        # await step_context.context.send_activity(message)
        return await step_context.end_dialog(step_context.options)
