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
    APP_ID = os.environ.get("MicrosoftAppId", "9526ffd7-c70e-4687-86d6-f843e8fbba0d")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "lZH8Q~4o-TkLO-udeIRBoi1EzqIsdUPTmjoI6bVO")

    ##Luis
    LUIS_APP_ID = os.environ.get("LuisAppId", "179fc109-082e-4830-9e3b-ede129f8354f")
    LUIS_API_KEY = os.environ.get("LuisAPIKey", "a37771eb19e34aa78dd420ccf3f002e1")
    LUIS_API_HOST_NAME = os.environ.get("LuisAPIHostName",
                                        "bookfinderluisutility-authoring.cognitiveservices.azure.com/")
    ## Bing Search
    BING_SEARCH_API_KEY = os.environ.get("BingSubscriptionKey", "5b7a6da2bd204f65a081c887872510ec")
    ## Azure cognitive service
    COMPUTER_VISION_KEY = os.environ.get("ComputerVisonKey", "ca3f7e09c22142159d80180b75c0dec0")
    COMPUTER_VISION_ENDPOINT = os.environ.get("ComputerVisionEndpoint",
                                              "https://bookfindercognitiveservice.cognitiveservices.azure.com/")
    VOICE_SERVICE_ENDPOINT = os.environ.get("VoiceServiceEndpoint",
                                            "https://eastus.api.cognitive.microsoft.com/sts/v1.0/issuetoken")
    VOICE_SERVICE_KEY = os.environ.get("VoiceServiceKey",
                                       "b2622eb0797949bead840f7d08d5ac9c")
    # Azure SQL
    SERVER = 'boookfinder.database.windows.net'
    DATABASE = 'boookfinderdatabase'
    USERNAME = 'bookadmin'
    PASSWORD = '{vinciraia99!}'
