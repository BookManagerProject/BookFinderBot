#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """

    PORT = 8000
    ##Azure Web App

    # Developing
    # APP_ID = os.environ.get("MicrosoftAppId", "")
    # APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")

    # Da usare su Azure
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")

    ##Luis
    LUIS_APP_ID = os.environ.get("LuisAppId", "")
    LUIS_API_KEY = os.environ.get("LuisAPIKey", "")
    LUIS_API_HOST_NAME = os.environ.get("LuisAPIHostName",
                                        "bookfinderluisutility-authoring.cognitiveservices.azure.com/")
    ## Bing Search
    BING_SEARCH_API_KEY = os.environ.get("BingSubscriptionKey", "")
    ## Azure cognitive service
    COMPUTER_VISION_KEY = os.environ.get("ComputerVisonKey", "")
    COMPUTER_VISION_ENDPOINT = os.environ.get("ComputerVisionEndpoint",
                                              "https://bookfindercognitiveservice.cognitiveservices.azure.com/")
    VOICE_SERVICE_ENDPOINT = os.environ.get("VoiceServiceEndpoint",
                                            "https://eastus.api.cognitive.microsoft.com/sts/v1.0/issuetoken")
    VOICE_SERVICE_KEY = os.environ.get("VoiceServiceKey",
                                       "")
    # Azure SQL
    SERVER = ''
    DATABASE = ''
    USERNAME = ''
    PASSWORD = '{}'
