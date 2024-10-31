#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

TELEGRAM_TOKEN = "7401815042:AAF2OrPhPmpN-g-oCDaHUdmad90TqRe-YMo"
MONGO_URI = "mongodb+srv://pathclimbing:kG2sQYkAOhef6wlM@climbing-path.u52tc.mongodb.net/"

import pymongo

from telegram import Update
from telegram.ext import (
    Application,
)

from signin import SignIn
from log_ascent import logAscent


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

mongo_client = pymongo.MongoClient(MONGO_URI)["climbing-path"]

def main(event, context) -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    signin_bot = SignIn(mongo_client)
    log_ascent_bot = logAscent(mongo_client)

    application.add_handler(signin_bot.get_handler())
    application.add_handler(log_ascent_bot.get_handler())

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    