from botbuilder.core import MessageFactory, UserState
from botbuilder.dialogs import (
    Choice, ChoicePrompt
)
from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions
from botbuilder.schema import InputHints

from Utility.GoogleBooksAPI import GoogleBooksAPI
from dialogs import CancelAndHelpDialog
from servicesResources.DatabaseInterface import DatabaseInterface
from user_info import UserInfo


class RemoveStarredBookDialog(CancelAndHelpDialog):
    def __init__(self, user_state: UserState, dialog_id: str = None):
        super(RemoveStarredBookDialog, self).__init__(
            dialog_id or RemoveStarredBookDialog.__name__
        )

        self.user_profile_accessor = user_state.create_property("UserInfo")

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.first,
                    self.second
                ],
            )
        )
        self.api = GoogleBooksAPI()
        self.initial_dialog_id = WaterfallDialog.__name__
        self.index = 1

    async def first(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        session_account = await self.user_profile_accessor.get(step_context.context, UserInfo)
        book_detail = step_context.options
        books = session_account.starredBook
        if books is not None and len(books) > 0:
            book_detail.books = books
            choices = []
            for book in books:
                choices.append(Choice(book.title + " - " + book.isbn))
            message_text = (
                "Ecco la lista dei libri preferiti, selezionane uno per eliminarlo o altrimenti scrivi annulla per uscire"
            )
            return await step_context.prompt(
                ChoicePrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text(message_text),
                    choices=choices,
                    retry_prompt=MessageFactory.text(
                        "Valore non valido riprova! Seleziona un libro per eliminarlo o altrimenti scrivi annulla per uscire"
                    )
                ),
            )
        else:
            message_text = (
                "Non hai libri preferiti, cercane qualcuno e aggiungili ai prferiti"
            )
            message = MessageFactory.text(
                message_text, message_text, InputHints.ignoring_input
            )
            await step_context.context.send_activity(message)
        return await step_context.next(None)

    async def second(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if step_context.result is not None:
            session_account = await self.user_profile_accessor.get(step_context.context, UserInfo)
            index = step_context.result.index
            book_detail = step_context.options
            if DatabaseInterface.removeStarredBook(session_account, book_detail.books[index]):
                session_account.starredBook.pop(index)
                message_text = (
                    "Libro rimosso con successo!"
                )
                message = MessageFactory.text(
                    message_text, message_text, InputHints.ignoring_input
                )
                await step_context.context.send_activity(message)
            else:
                message_text = (
                    "Errore durante l'eliminazione, riprova"
                )
                message = MessageFactory.text(
                    message_text, message_text, InputHints.ignoring_input
                )
                await step_context.context.send_activity(message)
            return await step_context.next(book_detail.books)
        return await step_context.next(None)
