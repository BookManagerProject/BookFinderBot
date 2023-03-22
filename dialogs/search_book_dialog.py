import datetime
from io import BytesIO
from urllib import request

from botbuilder.core import MessageFactory, UserState
from botbuilder.dialogs import (
    Choice, PromptValidatorContext, NumberPrompt, AttachmentPrompt, ChoicePrompt
)
from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions
from botbuilder.schema import InputHints, Attachment

from Utility.BookParser import BookParser
from Utility.GoogleBooksAPI import GoogleBooksAPI
from book_detail import BookDetail
from dialogs import CancelAndHelpDialog
from servicesResources.CognitiveService import ComputerVision
from servicesResources.DatabaseInterface import DatabaseInterface
from servicesResources.VoiceService import SpeechToTextConverter
from user_info import UserInfo


class BookDialog(CancelAndHelpDialog):
    def __init__(self, user_state: UserState, dialog_id: str = None):
        super(BookDialog, self).__init__(
            dialog_id or BookDialog.__name__
        )

        self.user_profile_accessor = user_state.create_property("UserInfo")

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.zero,
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
                AttachmentPrompt.__name__, self.picture_prompt_validator
            )
        )
        self.api = GoogleBooksAPI()
        self.initial_dialog_id = WaterfallDialog.__name__
        self.index = 1

    @staticmethod
    async def picture_prompt_validator(prompt_context: PromptValidatorContext) -> bool:
        if not prompt_context.recognized.succeeded:
            return False

        attachments = prompt_context.recognized.value

        valid_images = [
            attachment
            for attachment in attachments
            if attachment.content_type in ["image/jpeg", "image/png"]
        ]

        prompt_context.recognized.value = valid_images

        # If none of the attachments are valid images, the retry prompt should be sent.
        return len(valid_images) > 0

    async def book_index_validator(self, prompt_context: PromptValidatorContext) -> bool:
        # This condition is our validation rule. You can also change the value at this point.
        return (
                prompt_context.recognized.succeeded
                and 0 < prompt_context.recognized.value < int(self.index)
        )

    async def zero(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        book_detail = step_context.options
        book_detail.titleorisbn = step_context.result
        if book_detail.titleorisbn is None:
            message_text = "Certo! Vuoi cercare il libro tramite foto o tramite ricerca testuale?"
            return await step_context.prompt(
                ChoicePrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text(message_text),
                    choices=[Choice("Foto"), Choice("Testo")],
                ),
            )
            return await step_context.prompt(
                TextPrompt.__name__, prompt_message
            )
        return await step_context.next(book_detail.titleorisbn)

    async def first(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        choice = step_context.result
        if choice.index == 1:
            message_text = "Certo! Dimmi il nome o l'isbn del libro da cercare"
            prompt_message = PromptOptions(
                prompt=MessageFactory.text(
                    message_text, InputHints.expecting_input
                )
            )
            return await step_context.prompt(
                TextPrompt.__name__, prompt_message
            )
        elif choice.index == 0:
            message_text = "Certo! Scatta pure la foto all'isbn del libro"
            prompt_message = PromptOptions(
                prompt=MessageFactory.text(
                    message_text, InputHints.expecting_input
                ),
                retry_prompt=MessageFactory.text(
                    "Immagine non valida, riprova"
                )
            )
            return await step_context.prompt(
                AttachmentPrompt.__name__, prompt_message
            )

    async def second(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        book_detail = step_context.options
        result = None
        results = None
        if type(step_context.result) == list:
            resultcontext = step_context.result
            if len(resultcontext) > 0:
                if "image" in resultcontext[0].content_type:
                    cerca = ComputerVision()
                    results = cerca.get_text_from_img(resultcontext[0].content_url)
                elif "audio" in resultcontext[0].content_type:
                    cerca = SpeechToTextConverter()
                    text = cerca.recognize_from_url(resultcontext[0].content_url)
        else:
            book_detail.titleorisbn = step_context.result
            if BookParser.is_valid_isbn(book_detail.titleorisbn):
                result = self.api.search_by_isbn(book_detail.titleorisbn)
            else:
                results = self.api.search_by_title(book_detail.titleorisbn)
        if book_detail.index is None:
            if results is not None and len(results) > 0:
                message = "Ho trovato i seguenti libri: \n\n"
                i = 1
                for result in results:
                    message += str(i) + "." + result["title"] + " (" + result["isbn"] + ")" + "\n\n"
                    i += 1
                message += "\n\n\nIndicami scrivendomi il numero, quale libro stavi cercando"
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
            pd = str(book["publishedDate"]).replace("('", "").replace("',)", "")
            try:
                datesplit = pd.split("T")[0].split("-")
                date = datetime.date(int(datesplit[0]), int(datesplit[1]), int(datesplit[2]))
            except:
                date = datetime.date(int(pd), 1, 1)
            datestring = str(date.day) + "/" + str(date.month) + "/" + str(date.year)
            message = "Ecco le info del libro\n\nTitolo: " + book["title"]
            if book["description"] != "":
                message += "\n\nDescrizione: " + book["description"]
            message += "\n\nData di pubblicazione: " + datestring
            message += "\n\nAutore/i: " + book["autori"]
            image_url = book["previewLink"]
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
        if book_detail.books is not None:
            book = BookDetail(book_detail.book["isbn"], book_detail.book["title"], book_detail.book["publishedDate"],
                              book_detail.book["description"], book_detail.book["previewLink"],
                              book_detail.book["autori"])
            DatabaseInterface.addSearchedBook(book)
            if session_account.email is not None:
                book_detail.book = book
                message_text = (
                    "Vuoi aggiungerlo ai preferiti?"
                )
                return await step_context.prompt(
                    ChoicePrompt.__name__,
                    PromptOptions(
                        prompt=MessageFactory.text(message_text),
                        choices=[Choice("Si"), Choice("No")],
                    ),
                )
            elif session_account.email is None and book_detail.books is not None and book_detail.index is not None:
                message_text = "Dato che **non sei loggato** non puoi aggiungere il libro ai preferiti"
                prompt_message = MessageFactory.text(message_text, message_text, InputHints.expecting_input)
                await step_context.context.send_activity(prompt_message)
        return await step_context.next(step_context.options)

    async def six(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        book_detail = step_context.options
        session_account = await self.user_profile_accessor.get(step_context.context, UserInfo)
        if book_detail.books is not None and book_detail.index is not None and session_account.email is not None:
            result = step_context.result
            if result.index == 0:
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
            elif result.index == 1:
                message_text = (
                    "Non aggiunto!"
                )
            prompt_message = MessageFactory.text(message_text, message_text, InputHints.expecting_input)
            await step_context.context.send_activity(prompt_message)
        return await step_context.next(book_detail.index)
