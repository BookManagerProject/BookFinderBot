import datetime
from io import BytesIO
from urllib import request

from botbuilder.core import MessageFactory, UserState
from botbuilder.dialogs import (
    Choice, ChoicePrompt
)
from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions
from botbuilder.schema import Attachment, InputHints

from Utility.GoogleBooksAPI import GoogleBooksAPI
from dialogs import CancelAndHelpDialog
from user_info import UserInfo


class StarredBookDialog(CancelAndHelpDialog):
    def __init__(self, user_state: UserState, dialog_id: str = None):
        super(StarredBookDialog, self).__init__(
            dialog_id or StarredBookDialog.__name__
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
                "Ecco la lista dei libri preferiti, selezionane uno se vuoi vedere ulteriori dettagli o altrimenti scrivi annulla per uscire"
            )
            return await step_context.prompt(
                ChoicePrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text(message_text),
                    choices=choices,
                    retry_prompt=MessageFactory.text(
                        "Valore non valido riprova! Seleziona un libro se vuoi vedere ulteriori dettagli o altrimenti scrivi annulla per uscire"
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

    async def _printBook(self, book, step_context):
        if book is not False:
            pd = str(book.publishedDate).replace("(datetime.date(", "").replace("),)", "").replace("',)", "").replace(
                "(", "").replace("'", "")
            try:
                datesplit = pd.split(",")
                date = datetime.date(int(datesplit[0]), int(datesplit[1]), int(datesplit[2]))
            except:
                date = datetime.date(int(pd), 1, 1)
            datestring = str(date.day) + "/" + str(date.month) + "/" + str(date.year)
            message = "Ecco le info del libro\n\nTitolo: " + book.title
            descrizione = str(book.description).replace("('", "").replace("',)", "")
            if descrizione != "" and descrizione != "None":
                message += "\n\nDescrizione: " + descrizione
            message += "\n\nData di pubblicazione: " + datestring
            if book.autori != "" and book.autori != "None":
                message += "\n\nAutore/i: " + book.autori
            image_url = str(book.image).replace("('", "").replace("',)", "")
            image_content = request.urlopen(image_url).read()
            image_data = BytesIO(image_content)
            attachment = Attachment(
                name=message,
                content_type="image/jpeg",
                content_url=image_url,
                content=image_data,
                thumbnail_url=image_url
            )
            message_with_image = MessageFactory.attachment(attachment, text=message)
            await step_context.context.send_activity(message_with_image)

    async def second(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if step_context.result is not None:
            index = step_context.result.index
            book_detail = step_context.options
            await self._printBook(book_detail.books[index], step_context)
            return await step_context.next(book_detail.books)
        return await step_context.next(None)
