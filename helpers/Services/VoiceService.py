import os

import azure.cognitiveservices.speech as speechsdk
import requests

from config import DefaultConfig


class SpeechToTextConverter:
    SERVICE_REGION = "eastus"
    FILENAME = "tmp.mp4"
    LANGUAGE = "it-IT"

    def recognize_from_url(self, url):
        speech_config = speechsdk.SpeechConfig(subscription=DefaultConfig.VOICE_SERVICE_KEY, region=self.SERVICE_REGION)
        r = requests.get(url).content
        with open(self.FILENAME, 'wb') as f:
            f.write(r)
        audio_config = speechsdk.audio.AudioConfig(filename=self.FILENAME)
        # Creates a speech recognizer using a file as audio input, also specify the speech language
        speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config, language=self.LANGUAGE, audio_config=audio_config)

        result = speech_recognizer.recognize_once()

        # Check the result
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print("Recognized: {}".format(result.text))
        elif result.reason == speechsdk.ResultReason.NoMatch:
            print("No speech could be recognized: {}".format(result.no_match_details))
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print("Speech Recognition canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))

        speech_config = speechsdk.SpeechConfig(subscription=DefaultConfig.VOICE_SERVICE_KEY, region=self.SERVICE_REGION)
        speech_config.speech_recognition_language = "it-IT"
        r = requests.get(url).content
        with open('tmp.mp4', 'wb') as f:
            f.write(r)

        audio_config = speechsdk.audio.AudioConfig(filename="tmp.mp4")
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        print("Recognizing speech from {}".format(url))
        speech_recognition_result = speech_recognizer.recognize_once_async().get()

        if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print("Recognized: {}".format(speech_recognition_result.text))
        elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
            print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
        elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_recognition_result.cancellation_details
            print("Speech Recognition canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")
        os.remove('tmp.mp4')
