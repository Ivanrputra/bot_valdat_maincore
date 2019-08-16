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


import pymysql
import logging
#bot validasi hendra
import validasi
#bot validasi TELKOM UNIVERSITY
import psb_sales

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

MAINCORE_ODP,ODP_LOCATION,ODC_LOCATION,MAINCORE_ODC = range(4)

def connection():
    conn = pymysql.connect('10.112.82.94','ikrom','akuadmindb','valdat_test')
    # conn = pymysql.connect('localhost','root','','daman')
    return conn

def ValdatMaincoreOdc(update, context):
    user = update.message.from_user
    update.message.reply_text('''
ODC-BLB-FBM KAP 144
IN
OTB 1 PORT 5 CORE 5
TO
SPL-B 5 PORT 1&2
TO
OTB 9 PORT 6&7 CORE 6&7
DS 3 KAP 12 CORE 6&7
KET : FEEDER LOSS
STO BLB
KAP_DIS 12
''')
    return MAINCORE_ODC

def MaincoreOdc(update, context):
    context.user_data.clear()
    user = update.message.from_user
    split_message = update.message.text.splitlines()

    if len(split_message) != 11:
        update.message.reply_text('Input anda kurang atau berlebih silahkan ulangi lagi /start')
        return ConversationHandler.END        
    #
    odc                         = split_message[0].split()
    odc_in                      = split_message[2].split()
    odc_split                   = split_message[4].split()
    odc_out                     = split_message[6].split()
    distribusi                  = split_message[7].split()
    odc_out_port,odc_out_core,odc_splt_out,d_core = {},{},{},{}

    if len(odc_split[3].split('&')) == 1 and len(odc_out[3].split('&')) == 1 and len(odc_out[5].split('&')) == 1 and  len(distribusi[5].split('&')) == 1:
        odc_out_port = odc_out[3]
        odc_out_core = odc_out[5]
        odc_splt_out = odc_split[3]
        d_core       = distribusi[5]

    elif len(odc_split[3].split('&')) >= 1 and len(odc_out[3].split('&')) >= 1 and len(odc_out[5].split('&')) >= 1 and len(distribusi[5].split('&')) >= 1:
        if len(odc_split[3].split('&')) != len(odc_out[3].split('&')) or len(odc_split[3].split('&')) != len(odc_out[5].split('&')) or len(odc_split[3].split('&')) != len(distribusi[5].split('&')):
            update.message.reply_text('Jumlah port splitter dan dengan panel out(port / core) atau port distribusi tidak sama, silahkan ulang lagi /start')
            return ConversationHandler.END
        odc_out_port = odc_out[3].split('&')
        odc_out_core = odc_out[5].split('&')
        odc_splt_out = odc_split[3].split('&')
        d_core       = distribusi[5].split('&')
    
    for x in range(len(odc_out_port)):
        detail                        = {}
        #1
        detail['odc_name']            = odc[0]
        detail['odc_kap']             = odc[2]
        #3
        detail['in_tray']             = odc_in[1]
        detail['in_port']             = odc_in[3]
        detail['in_core']             = 0#odc_in[5]
        #5
        if len(odc_split[1]) > 1:
            detail['splt_name']       = odc_split[0]+'.1-'+odc_split[1]
        else:
            detail['splt_name']       = odc_split[0]+'.1-0'+odc_split[1]
        detail['splt_out']            = odc_splt_out[x]
        #7
        detail['out_tray']            = odc_out[1]
        detail['out_port']            = odc_out_port[x]
        detail['out_core']            = odc_out_core[x]
        #8
        detail['distribusi_ke']       = distribusi[1]
        detail['distribusi_kap']      = distribusi[3]
        detail['distribusi_core']     = d_core[x]
        #9
        detail['description']         = split_message[8].split(':')[1]
        #10
        detail['sto']                 = split_message[9].split()[1]
        #11
        detail['cap_dis']             = split_message[10].split()[1]
        # kapasitas in and out panel
        if detail['odc_kap'] == '144':
            detail['in_kap']          = 12
            detail['out_kap']         = 12
        elif detail['odc_kap'] == '288':
            detail['in_kap']          = 24
            detail['out_kap']         = 24

        
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

    data    = context.user_data 
    sql_odc     = ""
    sql_maincore = {}

    for x in range(len(data)):
        sql_odc = "(NULL,'{}','{}','{}',{},'{}',{},'{}')".format(str(data[x]['odc_name']),str(data[x]['odc_lat']),data[x]['odc_long'],int(data[x]['odc_kap']),str(data[x]['sto']),int(data[x]['cap_dis']),str(data[x]['description']))
        sql_maincore[x] = "(NULL,{},{},{},{},'{}',{},{},{},{},{},{},{},{},{},{})".format(
            int(data[x]['in_tray']),
            int(data[x]['in_port']),
            int(data[x]['in_core']),
            int(data[x]['in_kap']),
            str(data[x]['splt_name']),
            int(data[x]['splt_out']),
            int(data[x]['out_tray']),
            int(data[x]['out_port']),
            int(data[x]['out_core']),
            int(data[x]['out_kap']),
            int(data[x]['distribusi_ke']),
            int(data[x]['distribusi_kap']),
            int(data[x]['distribusi_core']),
            "id_to_odc",
            'NULL'
            )
        # update.message.reply_text(data[x])
    # sql_maincore = sql_maincore[1:]
    # update.message.reply_text(sql_maincore)
    conn    = connection()
    cursor  = conn.cursor()
    try:
        cursor.execute("insert into valdat_odc values"+sql_odc+"")
        update.message.reply_text('ODC baru telah terdaftar')
        conn.commit()
    except:
        update.message.reply_text('ODC terdaftar')
        conn.rollback()
        conn.close()
        # update.message.reply_text('ODC already exist')        
    try:
        cursor.execute("select id from valdat_odc where name = '"+str(data[0]['odc_name']+"'"))
        id_odc = int(cursor.fetchone()[0])
        for x in range(len(sql_maincore)):
            sql_maincore[x] = sql_maincore[x].replace("id_to_odc",str(id_odc))
            cursor.execute("select count(id) from valdat_maincore where distribution_to = "+data[x]['distribusi_ke']+" and distribution_cap = "+data[x]['distribusi_kap']+" and distribution_core = "+data[x]['distribusi_core']+" and odc_id = "+str(id_odc))
            exiss = int(cursor.fetchone()[0])
            if exiss<1:
                # update.message.reply_text(sql_maincore[x])
                cursor.execute("insert into valdat_maincore values"+sql_maincore[x]+"")
                conn.commit()
            else:
                update.message.reply_text("data maincore \nODC = "+data[0]['odc_name']+" \ndistribution_to = "+data[x]['distribusi_ke']+" and \ndistribution_cap = "+data[x]['distribusi_kap']+" and \ndistribution_core = "+data[x]['distribusi_core']+" sudah ada ")
                
    # conn.commit()
    except:
        update.message.reply_text("Gagal input data  odc , ulangi lagi /odc")
        conn.rollback()
        conn.close()

    conn.close()
    # update.message.reply_text('Terima Kasih Anda telah berhasil input Validasi Maincore, klik /start untuk validasi lagi')

    
    return ConversationHandler.END

def ValdatMaincoreOdp(update, context):
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
KET : FEEDER LOSS
TO
ODC-BLB-FBM
''')
    return MAINCORE_ODP


def MaincoreOdp(update, context):
    context.user_data.clear()
    user = update.message.from_user
    split_message = update.message.text.splitlines()

    if len(split_message) != 12:
        update.message.reply_text('Input anda kurang atau berlebih silahkan ulangi lagi /start')
        return ConversationHandler.END        
    #
    distribusi                  = split_message[1].split()
    splitter                    = split_message[3].split()
    #
    qrcode_port                 = split_message[5].split(':')
    d_core,odp_qr= {},{}

    if len(distribusi[5].split('&')) == 1 and len(qrcode_port[1].split('&')) == 1:
        d_core                  = distribusi[5]
        odp_qr                  = qrcode_port[1]

    elif len(distribusi[5].split('&')) >= 1:
        if len(distribusi[5].split('&'))  != len(qrcode_port[1].split('&')):
            update.message.reply_text('Jumlah core pada odp distribusi dan qrcode port tidak sama, silahkan ulang lagi /start')
            return ConversationHandler.END
        d_core                  = distribusi[5].split('&')
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
        detail['odp_qrcode']          = split_message[4].split(':')[1]
        detail['odp_port_qrcore']     = odp_qr[x]#split_message[4].split(':')[1]
        detail['odp_address']         = split_message[6].split(':')[1]
        detail['odp_kelurahan']       = split_message[7].split(':')[1]
        detail['odp_kecamatan']       = split_message[8].split(':')[1]
        #10
        detail['description']         = split_message[9].split(':')[1]
        detail['odc_name']            = split_message[11]
        
        context.user_data[x] = detail
    logger.info(context.user_data)
    update.message.reply_text('Masukkan koordinat ODP')

    return ODP_LOCATION

def odp_location(update, context):
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
    sql_distribusi,sql_odp = "",""

    conn    = connection()
    cursor  = conn.cursor()

    try:
        cursor.execute("select id from valdat_odc where name = '"+str(data[0]['odc_name'])+"'")
        id_odc = int(cursor.fetchone()[0])
    except:
        update.message.reply_text('ODC tidak terdaftar, ulangi lagi, /odc /odp')
        conn.rollback()
        conn.close()
        return ConversationHandler.END

    try:
        cursor.execute("select id from valdat_odpmaster where name = '"+str(data[0]['odp_name'])+"'")
        odp_id=cursor.fetchone()
        if odp_id is None:
            sqllll = ("insert into valdat_odpmaster values "+
            "(NULL,'"+str(data[0]['odp_name'])+"',NULL,'"+str(data[0]['odp_index'])+"',"+data[0]['splitter_no']+",'"+str(data[0]['splitter_name'])+"',"+data[0]['splitter_kap']+",'"+str(data[0]['odp_qrcode'])+"','"+str(data[0]['odp_port_qrcore'])+"','"+str(data[0]['odp_address'])+"','"+str(data[0]['odp_kelurahan'])+"','"+str(data[0]['odp_kecamatan'])+"','"+str(data[0]['odp_lat'])+"','"+str(data[0]['odp_long'])+"','"+str(data[0]['description'])+"',NULL,'asd',"+str(id_odc)+")")
            cursor.execute(sqllll)
            conn.commit()
            odp_id = cursor.lastrowid
        else :        
            odp_id = int(odp_id[0])
    except:
        update.message.reply_text('Gagal input ODP ke database, /odc /odp')
        conn.rollback()
        conn.close()
        return ConversationHandler.END        
    
    try:
    #doesnt hancle if maincore doessnt exist
        for x in range(len(data)):
            sqllll = "update valdat_maincore as m inner join valdat_odc as o on m.odc_id = o.id "+"set m.odp_id = "+str(odp_id)+" where "+"o.name = '"+str(data[x]['odc_name'])+"' " +" and m.distribution_to   = "+str(data[x]['distribusi_ke'])+"" +" and m.distribution_cap  = "+str(data[x]['distribusi_kap'])+"" +" and m.distribution_core = "+str(data[x]['distribusi_core']+"")
            cursor.execute(sqllll)
        conn.commit()
        update.message.reply_text('Terima Kasih Anda telah berhasil input Validasi Maincore, klik /start untuk validasi lagi')
    except:
        update.message.reply_text('Gagal Update Maincore ulangi lagi, /odc /odp')
        conn.rollback()
        conn.close()
        return ConversationHandler.END        


    conn.close()
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

def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("900688850:AAE4KtOWwlNlIRnf-JgtQPxfAyRLpceApxA", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    valdat_maincore_odp = ConversationHandler(
        entry_points=[CommandHandler('odp', ValdatMaincoreOdp)],

        states={
            MAINCORE_ODP: [MessageHandler(Filters.text, MaincoreOdp)],
            ODP_LOCATION: [MessageHandler(Filters.location, odp_location)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    valdat_maincore_odc = ConversationHandler(
        entry_points=[CommandHandler('odc', ValdatMaincoreOdc)],

        states={
            MAINCORE_ODC: [MessageHandler(Filters.text, MaincoreOdc)],
            ODC_LOCATION: [MessageHandler(Filters.location, odc_location)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(valdat_maincore_odp)
    dp.add_handler(valdat_maincore_odc)
    dp.add_handler(validasi.main())
    dp.add_handler(psb_sales.main())
    
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

