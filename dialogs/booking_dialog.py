# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from io import BytesIO
from urllib import request

from botbuilder.core import MessageFactory
from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, PromptOptions
from botbuilder.schema import Attachment, MediaUrl
from botbuilder.schema import InputHints
from datatypes_date_time.timex import Timex

from Utility.BookChecker import is_valid_isbn
from Utility.GoogleBooksAPI import GoogleBooksAPI
from .cancel_and_help_dialog import CancelAndHelpDialog
from .date_resolver_dialog import DateResolverDialog


class BookingDialog(CancelAndHelpDialog):
    def __init__(self, dialog_id: str = None):
        super(BookingDialog, self).__init__(dialog_id or BookingDialog.__name__)

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(DateResolverDialog(DateResolverDialog.__name__))
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.destination_step,
                    self.origin_step,
                    self.travel_date_step,
                    self.confirm_step,
                    self.final_step,
                ],
            )
        )
        self.api = GoogleBooksAPI()
        self.initial_dialog_id = WaterfallDialog.__name__

    async def destination_step(
            self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """
        If a destination city has not been provided, prompt for one.
        :param step_context:
        :return DialogTurnResult:
        """
        booking_details = step_context.options

        if booking_details.destination is None:
            message_text = "Certo! Dimmi il nome o l'isbn del libro da cercare?"
            prompt_message = MessageFactory.text(
                message_text, message_text, InputHints.expecting_input
            )
            return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )
        return await step_context.next(booking_details.destination)

    async def origin_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        If an origin city has not been provided, prompt for one.
        :param step_context:
        :return DialogTurnResult:
        """
        booking_details = step_context.options
        result = None
        results = None

        # Capture the response to the previous step's prompt
        booking_details.destination = step_context.result
        if booking_details.origin is None:

            if is_valid_isbn(booking_details.destination):
                result = self.api.search_by_isbn(booking_details.destination)
            else:
                results = self.api.search_by_title(booking_details.destination)

            if results is not None:
                message = "Ho trovato i seguenti libri: \n\n"
                i = 1
                for result in results:
                    message += str(i) + "- " + result["title"] + " (" + result["isbn"] + ")" + "\n\n"
                    i += 1
                message += "\n Indicami scrivendomi il numero, quale libro stavi cercando"
                prompt_message = MessageFactory.text(
                    message, message, InputHints.expecting_input
                )
                return await step_context.prompt(
                    TextPrompt.__name__, PromptOptions(prompt=prompt_message)
                )
                return await step_context.next(booking_details.origin)

            if result is not None:
                print(result)
                await self._printBook(result, step_context)

        return await step_context.next(booking_details.origin)

    async def travel_date_step(
            self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        input = step_context.result
        book = self.api.getBookFinded(input)
        await self._printBook(book, step_context)

        booking_details = step_context.options

        # Capture the results of the previous step
        booking_details.origin = step_context.result
        if not booking_details.travel_date or self.is_ambiguous(
                booking_details.travel_date
        ):
            return await step_context.begin_dialog(
                DateResolverDialog.__name__, booking_details.travel_date
            )
        return await step_context.next(booking_details.travel_date)

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

    async def confirm_step(
            self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """
        Confirm the information the user has provided.
        :param step_context:
        :return DialogTurnResult:
        """
        booking_details = step_context.options

        # Capture the results of the previous step
        booking_details.travel_date = step_context.result
        message_text = (
            f"Please confirm, I have you traveling to: {booking_details.destination} from: "
            f"{booking_details.origin} on: {booking_details.travel_date}."
        )
        prompt_message = MessageFactory.text(
            message_text, message_text, InputHints.expecting_input
        )

        # Offer a YES/NO prompt.
        return await step_context.prompt(
            ConfirmPrompt.__name__, PromptOptions(prompt=prompt_message)
        )

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        Complete the interaction and end the dialog.
        :param step_context:
        :return DialogTurnResult:
        """
        if step_context.result:
            booking_details = step_context.options

            return await step_context.end_dialog(booking_details)
        return await step_context.end_dialog()

    def is_ambiguous(self, timex: str) -> bool:
        timex_property = Timex(timex)
        return "definite" not in timex_property.types
