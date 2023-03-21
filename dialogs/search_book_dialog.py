from io import BytesIO
from urllib import request

from botbuilder.core import MessageFactory, UserState
from botbuilder.dialogs import (
    Choice, PromptValidatorContext, NumberPrompt, AttachmentPrompt
)
from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, PromptOptions
from botbuilder.schema import InputHints, Attachment, MediaUrl

from Utility.BookParser import BookParser
from Utility.GoogleBooksAPI import GoogleBooksAPI
from dialogs import CancelAndHelpDialog
from servicesResources.CognitiveService import ComputerVision
from servicesResources.VoiceService import SpeechToTextConverter
from user_info import UserInfo
from book_detail import BookDetail
from servicesResources.DatabaseInterface import DatabaseInterface


class BookDialog(CancelAndHelpDialog):
    def __init__(self, user_state: UserState, dialog_id: str = None):
        super(BookDialog, self).__init__(
            dialog_id or BookDialog.__name__
        )

        self.user_profile_accessor = user_state.create_property("UserInfo")

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.first,
                    self.second,
                    self.three,
                    self.four,
                    self.six
                ],
            )
        )
        self.add_dialog(
            NumberPrompt(NumberPrompt.__name__, self.book_index_validator)
        )
        self.add_dialog(
            AttachmentPrompt(
                AttachmentPrompt.__name__
            )
        )
        self.api = GoogleBooksAPI()
        self.initial_dialog_id = WaterfallDialog.__name__
        self.index = 1

    async def book_index_validator(self, prompt_context: PromptValidatorContext) -> bool:
        # This condition is our validation rule. You can also change the value at this point.
        return (
                prompt_context.recognized.succeeded
                and 0 < prompt_context.recognized.value < int(self.index)
        )

    async def first(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        book_detail = step_context.options
        book_detail.titleorisbn = step_context.result
        if book_detail.titleorisbn is None:
            message_text = "Certo! Dimmi il nome o l'isbn del libro da cercare oppure scatta una foto"
            prompt_message = PromptOptions(
                prompt=MessageFactory.text(
                    message_text, InputHints.expecting_input
                )
            )
            return await step_context.prompt(
                TextPrompt.__name__, prompt_message
            )
        return await step_context.next(book_detail.titleorisbn)

    async def second(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        book_detail = step_context.options
        result = None
        results = None
        if type(step_context.result) == list:
            result = step_context.result
            if len(result) > 0:
                if "image" in result[0].content_type:
                    cerca = ComputerVision()
                    results = cerca.get_text_from_img(result[0].content_url)
                elif "audio" in result[0].content_type:
                    cerca = SpeechToTextConverter()
                    text = cerca.recognize_from_url(result[0].content_url)
        else:
            book_detail.titleorisbn = step_context.result
            if BookParser.is_valid_isbn(book_detail.titleorisbn):
                result = self.api.search_by_isbn(book_detail.titleorisbn)
            else:
                results = self.api.search_by_title(book_detail.titleorisbn)
        if book_detail.index is None:
            if results is not None:
                message = "Ho trovato i seguenti libri: \n\n"
                i = 1
                for result in results:
                    message += str(i) + "- " + result["title"] + " (" + result["isbn"] + ")" + "\n\n"
                    i += 1
                message += "\n Indicami scrivendomi il numero, quale libro stavi cercando"
                self.index = len(results) + 1
                book_detail.books = results
                return await step_context.prompt(
                    NumberPrompt.__name__,
                    PromptOptions(
                        prompt=MessageFactory.text(message),
                        retry_prompt=MessageFactory.text(
                            "Valore non valido riprova!"
                        ),
                    ),
                )
            elif result is not None:
                book_detail.books = [result]
                book_detail.index = 0
                return await step_context.next(book_detail.index)
            else:
                book_detail.books = None
                message_text = "Nessun risultato trovato. Riprova"
                prompt_message = MessageFactory.text(message_text, message_text, InputHints.expecting_input)
                await step_context.context.send_activity(prompt_message)
                return await step_context.next(book_detail.index)

    async def _printBook(self, book, step_context):
        if book is not False:
            message = "Ecco le info del libro\n\n" + book["title"] + "\n\n" + book["description"] + "\n\n" + book[
                "publishedDate"]
            image_url = book["previewLink"]
            image_content = request.urlopen(image_url).read()
            image_data = BytesIO(image_content)
            media_url = MediaUrl(url=image_url)
            attachment = Attachment(
                name=message,
                content_type="image/jpeg",
                content_url=image_url,
                content=image_data,
                thumbnail_url=image_url,
                thumbnail_media_url=media_url,
            )
            message_with_image = MessageFactory.attachment(attachment, text=message)
            await step_context.context.send_activity(message_with_image)

    async def three(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        book_detail = step_context.options
        book_detail.index = step_context.result
        if book_detail.books is not None:
            books = book_detail.books
            if book_detail.index is None:
                await self._printBook(books[0], step_context)
            else:
                index = int(book_detail.index) - 1
                if len(books) > index:
                    book = books[index]
                    book_detail.book = book
                    await self._printBook(book, step_context)
                    return await step_context.next(book_detail.books)
        return await step_context.next(book_detail.books)

    async def four(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        session_account = await self.user_profile_accessor.get(step_context.context, UserInfo)
        book_detail = step_context.options
        book = BookDetail(book_detail.book["isbn"], book_detail.book["title"], book_detail.book["publishedDate"],
                          book_detail.book["description"], book_detail.book["previewLink"])
        DatabaseInterface.addSearchedBook(book)
        if session_account.email is not None:
            book_detail.book = book
            message_text = (
                "Vuoi aggiungerlo ai preferiti?"
            )
            return await step_context.prompt(
                ConfirmPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text(message_text),
                    choices=[Choice("Si"), Choice("No")],
                ),
            )
        elif session_account.email is None and book_detail.books is not None and book_detail.index is not None:
            message_text = "Dato che non sei loggato non puoi aggiungere il libro ai preferiti poichè non sei loggato"
            prompt_message = MessageFactory.text(message_text, message_text, InputHints.expecting_input)
            await step_context.context.send_activity(prompt_message)
        return await step_context.next(step_context.options)

    async def six(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        book_detail = step_context.options
        session_account = await self.user_profile_accessor.get(step_context.context, UserInfo)
        if book_detail.books is not None and book_detail.index is not None and session_account.email is not None:
            result = step_context.result
            if result:
                if session_account.checkIfBookIsStarred(book_detail.book):
                    message_text = (
                        "Il libro è già presente tra i tuoi preferiti!"
                    )
                elif DatabaseInterface.addStarredBook(session_account, book_detail.book):
                    session_account.starredBook.append(book_detail.book)
                    message_text = (
                        "Aggiunto!"
                    )
                else:
                    message_text = (
                        "Si è verificato un errore durante l'aggiunta. Riprova!"
                    )
            else:
                message_text = (
                    "Non aggiunto!"
                )
            prompt_message = MessageFactory.text(message_text, message_text, InputHints.expecting_input)
            await step_context.context.send_activity(prompt_message)
        return await step_context.next(book_detail.index)
