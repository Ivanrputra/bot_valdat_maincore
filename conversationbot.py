#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.
#
# THIS EXAMPLE HAS BEEN UPDATED TO WORK WITH THE BETA VERSION 12 OF PYTHON-TELEGRAM-BOT.
# If you're still using version 11.1.0, please see the examples at
# https://github.com/python-telegram-bot/python-telegram-bot/tree/v11.1.0/examples

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""



import logging

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

BIO = range(4)


def start(update, context):
    user = update.message.from_user
    
    update.message.reply_text('''
        ODP-BLB-FBM/12 
        DS 3 KAP 12 CORE 6&7
        (odc/distribusi berapa/nomer odp.01) 
        FBM/D03/13.01
        5 SPL-C KAP 8
        QRCODE ODP
        QRCODE PORT
        ALAMAT
        KELURAHAN
        KECAMATAN
        KOORDINAT (lat,long)
        TO
        ODC-BLB-FBM KAP 144
        KOORDINAT (lat,long)
        IN
        OTB 1 PORT 5 CORE 5
        TO
        SPL-B 5 PORT 1&2
        TO
        OTB 9 PORT 6&7 CORE 6&7
        KET : FEEDER LOSS

        ODC KAP 144=12 PORT PANEL IN & OUT
        ODC KAP 48=24 PANEL IN & OUT

        baris 0 : nama odp
        baris 2 : nama odc
        baris 4 : nomer otb, port, core
        baris 6 : nomer spl, port (bisa 2 core, dipisah pake &)
        baris 8 : nomer otb, port, core (port dan core bisa 2 core, dipisah pake &)
        baris 9 : keterangan
        ''')
    return BIO


def bio(update, context):
    user = update.message.from_user
    logger.info("Bio of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('Thank you! I hope we can talk again some day.')

    return ConversationHandler.END


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("900688850:AAE4KtOWwlNlIRnf-JgtQPxfAyRLpceApxA", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            BIO: [MessageHandler(Filters.text, bio)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
