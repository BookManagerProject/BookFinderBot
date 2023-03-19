import os
import time

import requests
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials

from config import DefaultConfig


class ComputerVision:
    def __init__(self):
        self.subscription_key = DefaultConfig.COMPUTER_VISION_KEY
        self.endpoint = DefaultConfig.COMPUTER_VISION_ENDPOINT
        self.computer_vision_client = ComputerVisionClient(DefaultConfig.COMPUTER_VISION_ENDPOINT,
                                                           CognitiveServicesCredentials(
                                                               DefaultConfig.COMPUTER_VISION_KEY))

    '''
    OCR: Read File using the Read API, extract text - remote
    This API call can also extract handwriting style text (not shown).
    '''

    # TODO: implementare controllo tipo immagine e cercare di cancellare lettura e scrittura del file
    def get_text_from_img(self, img_url):
        r = requests.get(img_url).content
        with open('tmp.jpg', 'wb') as f:
            f.write(r)
        with open('tmp.jpg', 'rb') as img:
            read_response = self.computer_vision_client.read_in_stream(image=img, language='it', raw=True,
                                                                       mode='Printed')

        # Get the operation location (URL with an ID at the end) from the response
        read_operation_location = read_response.headers["Operation-Location"]
        # Grab the ID from the URL
        operation_id = read_operation_location.split("/")[-1]

        # Call the "GET" API and wait for it to retrieve the results
        while True:
            read_result = self.computer_vision_client.get_read_result(operation_id)
            if read_result.status not in ['notStarted', 'running']:
                break
            time.sleep(1)

        # Print the detected text, line by line
        text = ''
        if read_result.status == OperationStatusCodes.succeeded:
            for text_result in read_result.analyze_result.read_results:
                for line in text_result.lines:
                    text += ' ' + line.text
                    # print(line.bounding_box)
        text = text_result.lines[0].text + ' ' + text_result.lines[1].text

        os.remove('tmp.jpg')
        return text
