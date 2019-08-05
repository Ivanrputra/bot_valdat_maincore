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
from array import *

import pymysql.cursors
import pymysql

############### CONFIGURE THIS ###################
# Open database connection
# db = pymysql.connect("10.112.82.94","ikrom","akuadmindb","valdat_test")
db = pymysql.connect("localhost","root","","daman")
##################################################


cursor = db.cursor()



# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

GENDER, VALIDASIODP, DATAODP, PHOTO, LOCATION, BIO = range(6)


def start(update, context):
    reply_keyboard = [['Validasiodp']]

    update.message.reply_text(
        'Halo dude. Selamat datang di Bot Valdat. Pilih Validasiodp untuk memasukkan Validasi Data ODP',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return VALIDASIODP

def validasiodp(update, context):
    user = update.message.from_user
    logger.info("User %s Memilih %s", user.first_name, update.message.text)
    update.message.reply_text('odp :\n'
                "kap:\n"
                "tagging:\n"
                "qrcode odp :\n"
                "qrport port :\n"
                "1:\n"
                "2:\n"
                "3.1:\n"
                "3.2:\n"
                "dst(Sesuai Jumlah Port)",
                              reply_markup=ReplyKeyboardRemove())

    return DATAODP

def dataodp(update, context):
    user = update.message.from_user
    logger.info("Gender of %s: %s", user.first_name, update.message.text)

    datadariodp = update.message.text
    arraydata2 = datadariodp.split("\n")
    arraydata = datadariodp.split("\n")
    kapasitas = 0
    jumlahport = 0
    stats = 0
    for word in arraydata:
        dataakhir = word.split(":")

        if dataakhir[0].find('kap') != -1 :
            kapasitas=dataakhir[1]
            update.message.reply_text("JUMLAH KAPASITAS = "+kapasitas,reply_markup=ReplyKeyboardRemove())
        if not dataakhir[1].strip():
            if (dataakhir[0].find('.') != -1): 
            	jumlahport = jumlahport+1
            	update.message.reply_text("Kosong",reply_markup=ReplyKeyboardRemove())
            else:
            	try:
            		if int(dataakhir[0]) >= 0 and int(dataakhir[0]) <= 100:
            			jumlahport = jumlahport+1
            			update.message.reply_text("Kosong",reply_markup=ReplyKeyboardRemove())
            	except ValueError:
            		update.message.reply_text("ADA DATA TIDAK VALID. Periksa Kembali Kelengkapan Datamu",reply_markup=ReplyKeyboardRemove())
            		stats=1
            		break

        else:
            try:
               if int(dataakhir[0]) >= 0 and int(dataakhir[0]) <= 100:
                jumlahport = jumlahport+1
                try:
                	cursor.execute("select `qrcode`, count(*) from `valdat_qrcode` where `qrcode` = '"+dataakhir[1].strip()+"'")
	                update.message.reply_text(dataakhir[1],reply_markup=ReplyKeyboardRemove())

	                # gets the number of rows affected by the command executed
	                res = cursor.fetchone()

	                print ("number of affected rows: {}".format(res))
	                
	                if res[0] is None:
	                    print ("QR CODE Tidak valid")
	                    stats=2
	                    break
                except (db.Error, db.Warning) as e:
                	print(e)
                	return None
                    
            except ValueError:
                if (dataakhir[0].find('.') != -1): 
                    jumlahport = jumlahport+1
                    try:
                    	cursor.execute("select `qrcode`, count(*) from `valdat_qrcode` where `qrcode` = '"+dataakhir[1].strip()+"'")
                    	update.message.reply_text(dataakhir[1],reply_markup=ReplyKeyboardRemove())
                    	# gets the number of rows affected by the command executed
                    	res = cursor.fetchone()
                    	print ("number of affected rows: {}".format(res))
                    	if res[0] is None:
		                    print ("QR CODE Tidak valid")
		                    stats=2
		                    break

                    except (db.Error, db.Warning) as e:
                    	print(e)
                    	return None
                else:
                    update.message.reply_text(dataakhir[1],reply_markup=ReplyKeyboardRemove())

    if stats==0:
    	try:
    		if int(kapasitas) == int(jumlahport):
    			arays = []
    			arays2 = []
	    		for datas in arraydata2:
	    			dataakhir = datas.split(":")
	    			arays.append(dataakhir[1])
	    			arays2.append(dataakhir[0])

	    		cursor.execute("insert INTO valdat_odpmaster (name, tagging, qrcode_port, qrcode_odp) VALUES ('"+arays[0]+"', '"+arays[2]+"', '"+arays[4]+"', '"+arays[3]+"')")
	    		db.commit()
	    		cursor.execute("select id from `valdat_odpmaster` where `name` = '"+arays[0]+"' order by `id` desc limit 1")
	    		idodp = cursor.fetchone()
	    		print (idodp[0])
	    		a=0
	    		for x in range(int(kapasitas)):
	    			cursor.execute("insert INTO valdat_validasi (odp_port, qrcode_dropcore, odp_id) VALUES ('"+str(arays2[a+5])+"', '"+arays[a+5]+"', '"+str(idodp[0])+"')")
	    			db.commit()
	    			a+=1
					
	    		
	    		
	    	else:
	    		update.message.reply_text("DATA KAPASITAS DAN JUMLAH PORT TIDAK COCOK. ULANGI LAGI. Kapasitas = "+str(kapasitas)+", Jumlah Port = "+str(jumlahport),reply_markup=ReplyKeyboardRemove())
	        
    	except ValueError:
    		if int(kapasitas) == int(jumlahport):
	    		update.message.reply_text("JUMLAH PORT COCOK. Kapasitas = "+str(kapasitas)+", Jumlah Port = "+str(jumlahport),reply_markup=ReplyKeyboardRemove())
	    	else:
	    		update.message.reply_text("DATA KAPASITAS DAN JUMLAH PORT TIDAK COCOK. ULANGI LAGI. Kapasitas = "+str(kapasitas)+", Jumlah Port = "+str(jumlahport),reply_markup=ReplyKeyboardRemove())
	        
    elif stats==1:
    	update.message.reply_text("ADA DATA YANG TIDAK BOLEH KOSONG. ULANGI",reply_markup=ReplyKeyboardRemove())
    elif stats==2:
    	update.message.reply_text("ADA QR CODE YANG TIDAK DITEMUKAN. ULANGI",reply_markup=ReplyKeyboardRemove())


   
    # return PHOTO
    return ConversationHandler.END


def gender(update, context):
    user = update.message.from_user
    logger.info("Gender of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('I see! Please send me a photo of yourself, '
                              'so I know what you look like, or send /skip if you don\'t want to.',
                              reply_markup=ReplyKeyboardRemove())

    return PHOTO


def photo(update, context):
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('user_photo.jpg')
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    update.message.reply_text('Gorgeous! Now, send me your location please, '
                              'or send /skip if you don\'t want to.')

    return LOCATION


def skip_photo(update, context):
    user = update.message.from_user
    logger.info("User %s did not send a photo.", user.first_name)
    update.message.reply_text('I bet you look great! Now, send me your location please, '
                              'or send /skip.')

    return LOCATION


def location(update, context):
    user = update.message.from_user
    user_location = update.message.location
    logger.info("Location of %s: %f / %f", user.first_name, user_location.latitude,
                user_location.longitude)
    update.message.reply_text('Maybe I can visit you sometime! '
                              'At last, tell me something about yourself.')

    return BIO


def skip_location(update, context):
    user = update.message.from_user
    logger.info("User %s did not send a location.", user.first_name)
    update.message.reply_text('You seem a bit paranoid! '
                              'At last, tell me something about yourself.')

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
    updater = Updater("922566249:AAEkob4CL2Wh7SFtc399oyM5sKImiBOGugU", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            VALIDASIODP: [RegexHandler('^(Validasiodp)$', validasiodp)],

            DATAODP: [MessageHandler(Filters.text, dataodp)],

            GENDER: [RegexHandler('^(Boy|Girl|Other)$', gender)],

            PHOTO: [MessageHandler(Filters.photo, photo),
                    CommandHandler('skip', skip_photo)],

            LOCATION: [MessageHandler(Filters.location, location),
                       CommandHandler('skip', skip_location)],

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
