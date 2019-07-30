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


import pymysql.cursors
import logging

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

BIO,VALDAT_MAINCORE,ODP_LOCATION,ODC_LOCATION = range(4)

def connection():
    conn = pymysql.connect('10.112.82.94','ikrom','akuadmindb','valdat_test')
    cursor = conn.cursor()
    return cursor

def start(update, context):
    user = update.message.from_user
    
    update.message.reply_text('''
ODP-BLB-FBM/12
DS 3 KAP 12 CORE 6&7
FBM/D03/13.01
5 SPL-C KAP 8
QRCODE ODP : T3P0DXI5KKFM
QRCODE PORT : T3P0MUTW56R8 & T3P0FLL5638K
ALAMAT : PERUMAHAN PLAOSAN PERMAI BLOK  D-69
KELURAHAN : PANDANWANGI
KECAMATAN : BELIMBING
TO
ODC-BLB-FBM KAP 144
IN
OTB 1 PORT 5 CORE 5
TO
SPL-B 5 PORT 1&2
TO
OTB 9 PORT 6&7 CORE 6&7
KET : FEEDER LOSS
''')
    return VALDAT_MAINCORE


def valdat_maincore(update, context):
    # data = {}
    # context.user_data = {}
    context.user_data.clear()
    user = update.message.from_user
    split_message = update.message.text.splitlines()

    if len(split_message) != 18:
        update.message.reply_text('Input anda kurang atau berlebih silahkan ulangi lagi /start')
        return ConversationHandler.END        
    #
    distribusi                  = split_message[1].split()
    splitter                    = split_message[3].split()
    qrcode_port                 = split_message[5].split(':')
    odc                         = split_message[10].split()
    odc_in                      = split_message[12].split()
    #
    odc_split                   = split_message[14].split()
    #
    odc_out                     = split_message[16].split()
    

    d_core,odc_out_port,odc_out_core,odc_splt_out,odp_qr= {},{},{},{}

    if len(distribusi[5]) == 1 and len(odc_out[3]) == 1 and len(odc_out[5]) and len(odc_split[3]) == 1:
        d_core                  = distribusi[5]
        odc_out_port            = odc_out[3]
        odc_out_core            = odc_out[5]
        odc_splt_out            = odc_split[3]
        odp_qr                  = qrcode_port[1]

    elif len(distribusi[5]) >= 1:
        if len(distribusi[5].split('&')) != len(odc_out[3].split('&')) or len(distribusi[5].split('&')) != len(odc_out[5].split('&')) or len(distribusi[5].split('&')) != len(odc_split[3].split('&') or len(distribusi[5].split('&')) != len(qrcode_port[1].split('&')):
            update.message.reply_text('Jumlah core pada odp distribusi dan odc output tidak sama, silahkan ulang lagi /start')
            return ConversationHandler.END
        d_core                  = distribusi[5].split('&')
        odc_out_port            = odc_out[3].split('&')
        odc_out_core            = odc_out[5].split('&')
        odc_splt_out            = odc_split[3].split('&')
        odp_qr                  = qrcode_port[1].split('&')
    
    for x in range(len(d_core)):
        detail = {}
        #1
        detail['odp_name']            = split_message[0]
        #2
        detail['distribusi_ke']       = distribusi[1]
        detail['distribusi_kap']      = distribusi[3]
        detail['distribusi_core']     = d_core[x]
        #3
        detail['odp_index']           = split_message[2] 
        #4
        detail['splitter_no']         = splitter[0]
        detail['splitter_name']       = splitter[1]+'.1-01'
        detail['splitter_kap']        = splitter[3]
        #5-9
        detail['odp_qrcode']          = #split_message[4].split(':')[1]
        detail['odp_port']            = split_message[5].split(':')[1]
        detail['odp_address']         = split_message[6].split(':')[1]
        detail['odp_kelurahan']       = split_message[7].split(':')[1]
        detail['odp_kecamatan']       = split_message[8].split(':')[1]
        #11
        detail['odc_name']            = odc[0]
        detail['odc_kap']             = odc[2]
        #13
        detail['in_tray']             = odc_in[1]
        detail['in_port']             = odc_in[3]
        detail['in_core']             = '-'#odc_in[5]
        #15
        if len(odc_split[1]) > 1:
            detail['splt_name']       = odc_split[0]+'.1-'+odc_split[1]
        else:
            detail['splt_name']       = odc_split[0]+'.1-0'+odc_split[1]
        detail['splt_out']            = odc_splt_out[x]
        #17
        detail['out_tray']            = odc_out[1]
        detail['out_port']            = odc_out_port[x]
        detail['out_core']            = odc_out_core[x]
        #18
        detail['description']         = split_message[17].split(':')[1]
        # kapasitas in and out panel
        if detail['odc_kap'] == '144':
            detail['in_kap']          = 12
            detail['out_kap']         = 12
        elif detail['odc_kap'] == '288':
            detail['in_kap']          = 24
            detail['out_kap']         = 24
        # data[x] = detail
        context.user_data[x] = detail
    logger.info(context.user_data)
    update.message.reply_text('Masukkan koordinat ODC')

    return ODC_LOCATION

def odc_location(update, context):
    user = update.message.from_user
    user_location = update.message.location
    location = {}
    location['odc_lat']             = user_location.latitude
    location['odc_long']            = user_location.longitude
    for x in range(len(context.user_data)):
        context.user_data[x].update(location)
    
    logger.info("Location of %s: %f / %f", user.first_name, user_location.latitude,
                user_location.longitude)

    update.message.reply_text('Masukkan koordinat ODP')

    return ODP_LOCATION

def odp_location(update, context):
    cursor = connection()
    # cursor.execute("insert into `odc` ")
    # res = cursor.fetchone()

    
    user = update.message.from_user
    user_location = update.message.location

    location = {}
    location['odp_lat']             = user_location.latitude
    location['odp_long']            = user_location.longitude
    for x in range(len(context.user_data)):
        context.user_data[x].update(location)

    data = context.user_data
    logger.info("Location of %s: %f / %f", user.first_name, user_location.latitude,
                user_location.longitude)
    data = context.user_data 
    for x in range(len(data)):
        update.message.reply_text(data[x])
        # update.message.reply_text(data[x]['odp_name']+"\n"+
        # "DS "+data[x]['distribusi_ke']+" KAP "+data[x]['distribusi_kap']+" CORE "+data[x]['distribusi_core']+"\n")
    # print(update.data)        
# 5 SPL-C KAP 8
# QRCODE ODP
# QRCODE PORT
# ALAMAT
# KELURAHAN
# KECAMATAN
# TO
# ODC-BLB-FBM KAP 144
# IN
# OTB 1 PORT 5 CORE 5
# TO
# SPL-B 5 PORT 1&2
# TO
# OTB 9 PORT 6&7 CORE 6&7
# KET : FEEDER LOSS
# )
    update.message.reply_text('Terima Kasih Anda telah berhasil input Validasi Maincore, klik /start untuk validasi lagi')
    cursor.close()
    return ConversationHandler.END

def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the validation.", user.first_name)
    update.message.reply_text('Anda Telah Membatalkan Validasi, ulangi /start',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def format(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('''
ODP-BLB-FBM/12
DS 3 KAP 12 CORE 6&7
FBM/D03/13.01
5 SPL-C KAP 8
QRCODE ODP
QRCODE PORT
ALAMAT
KELURAHAN
KECAMATAN
TO
ODC-BLB-FBM KAP 144
IN
OTB 1 PORT 5 CORE 5
TO
SPL-B 5 PORT 1&2
TO
OTB 9 PORT 6&7 CORE 6&7
KET : FEEDER LOSS
''')

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
            VALDAT_MAINCORE: [MessageHandler(Filters.text, valdat_maincore)],

            ODC_LOCATION: [MessageHandler(Filters.location, odc_location)],
            ODP_LOCATION: [MessageHandler(Filters.location, odp_location)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler("format", format))

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

