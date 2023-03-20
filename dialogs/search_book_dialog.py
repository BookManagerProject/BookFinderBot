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
            message_text = "Certo! Dimmi il nome o l'isbn del libro da cercare?"
            prompt_message = PromptOptions(
                prompt=MessageFactory.text(
                    message_text
                )
            )
            return await step_context.prompt(
                AttachmentPrompt.__name__, prompt_message
            )
        return await step_context.next(book_detail.titleorisbn)

    async def second(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        book_detail = step_context.options
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
            if result is not None:
                return await step_context.next(book_detail.books)

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
        if book_detail.index is None:
            book = self.api.getBookFinded(0)
            book_detail.book = book
            await self._printBook(book, step_context)
            return await step_context.next(book_detail.book)
        else:
            books = book_detail.books
            index = int(book_detail.index) - 1
            if len(books) > index:
                book = books[index]
                book_detail.book = book
                await self._printBook(book, step_context)
                return await step_context.next(book_detail.book)

    async def four(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        book_detail = step_context.options
        book_detail.book = step_context.result
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

    async def six(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        book_detail = step_context.options
        if step_context.result is not None:
            result = step_context.result
            if result:
                message_text = (
                    "Aggiunto!"
                )
            else:
                message_text = (
                    "Non aggiunto!"
                )
            prompt_message = MessageFactory.text(message_text, message_text, InputHints.expecting_input)
            await step_context.context.send_activity(prompt_message)
            return await step_context.next(book_detail.index)

    @staticmethod
    async def picture_prompt_validator(prompt_context: PromptValidatorContext) -> bool:
        if not prompt_context.recognized.succeeded:
            await prompt_context.context.send_activity(
                "No attachments received. Proceeding without a profile picture..."
            )

            # We can return true from a validator function even if recognized.succeeded is false.
            return True

        attachments = prompt_context.recognized.value

        valid_images = [
            attachment
            for attachment in attachments
            if attachment.content_type in ["image/jpeg", "image/png"]
        ]

        prompt_context.recognized.value = valid_images

        # If none of the attachments are valid images, the retry prompt should be sent.
        return len(valid_images) > 0
