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
import datetime
import os

############### CONFIGURE THIS ###################
# Open database connection
# db = pymysql.connect("localhost","root","","valdat_test")
db = pymysql.connect("10.112.82.94","ikrom","akuadmindb","valdat_test")

##################################################


cursor = db.cursor()



# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

GENDER, VALIDASIODP, DATAODP, PHOTO,PHOTO1,PHOTO2,PHOTO3,PHOTO4,PHOTO5, LOCATION, BIO = range(11)


def start(update, context):
    reply_keyboard = [['Validasiodp']]

    update.message.reply_text(
        'Halo dude. Selamat datang di Bot Valdat. Pilih Validasiodp untuk memasukkan Validasi Data ODP',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return VALIDASIODP

def validasiodp(update, context):
    context.user_data.clear()
    user = update.message.from_user
    logger.info("User %s Memilih %s", user.first_name, update.message.text)
    update.message.reply_text('odp :\n'
                "kap:\n"
                "Redaman:\n"
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
            # update.message.reply_text("JUMLAH KAPASITAS = "+kapasitas,reply_markup=ReplyKeyboardRemove())
        if not dataakhir[1].strip():
            print (dataakhir[0])
            if (dataakhir[0].find('.') != -1): 
                jumlahport = jumlahport+1
                # update.message.reply_text("Kosong",reply_markup=ReplyKeyboardRemove())
                stats=0
            else:
                try:
                    if int(dataakhir[0]) >= 0 and int(dataakhir[0]) <= 100:
                        jumlahport = jumlahport+1
                        # update.message.reply_text("Kosong",reply_markup=ReplyKeyboardRemove())
                        stats=0
                except ValueError:
                    # update.message.reply_text("ADA DATA TIDAK VALID. Periksa Kembali Kelengkapan Datamu",reply_markup=ReplyKeyboardRemove())
                    stats=1
                    break

        else:
            try:
               if int(dataakhir[0]) >= 0 and int(dataakhir[0]) <= 100:
                jumlahport = jumlahport+1
                try:
                    if dataakhir[1].strip() != "-" and dataakhir[1].lower().find('node') == -1:
                        cursor.execute("select `qrcode`, count(*) from `valdat_qrcode` where `qrcode` = '"+dataakhir[1].strip()+"'")
                        # update.message.reply_text(dataakhir[1],reply_markup=ReplyKeyboardRemove())

                        # gets the number of rows affected by the command executed
                        res = cursor.fetchone()
                        print (dataakhir[1].lower().find('node'))
                        print ("number of affected rows: {}".format(res))
                        
                        if res[0] is None:
                            print ("QR CODE Tidak valid")
                            stats=2
                            break
                except (db.Error, db.Warning) as e:
                    print(e)
                    return None
                    
            except ValueError:
                if (dataakhir[0].find('.') != -1 and dataakhir[1].lower().find('node') == -1): 
                    jumlahport = jumlahport+1
                    try:
                        cursor.execute("select `qrcode`, count(*) from `valdat_qrcode` where `qrcode` = '"+dataakhir[1].strip()+"'")
                        # update.message.reply_text(dataakhir[1],reply_markup=ReplyKeyboardRemove())
                        # gets the number of rows affected by the command executed
                        res = cursor.fetchone()
                        print (dataakhir[1].lower().find('node'))
                        print ("number of affected rows: {}".format(res))
                        if res[0] is None:
                            print ("QR CODE Tidak valid")
                            stats=2
                            break

                    except (db.Error, db.Warning) as e:
                        print(e)
                        return None
                elif (dataakhir[1].lower().find('node') != -1):
                    jumlahport = jumlahport+1

                else:
                    print(dataakhir[1])
                    # update.message.reply_text(dataakhir[1],reply_markup=ReplyKeyboardRemove())

    if stats==0:
        try:
            if int(kapasitas) == int(jumlahport):
                arays = []
                arays2 = []
                for datas in arraydata2:
                    dataakhir = datas.split(":")
                    arays.append(dataakhir[1])
                    arays2.append(dataakhir[0])
                a=0
                mengecek = 0
                araysimpan = []
                araysimpanno = []
                for x in range(int(kapasitas)):
                    if arays[a+5] in araysimpan:
                        if arays[a+5].strip() != "-" or dataakhir[1].lower().find('node') == -1:
                            print("ADA NOMER QR YANG SAMA. YOU CANT DO THAT. ULANGI 1" , araysimpan)
                            mengecek = 1
                            break
                    else:
                        if arays2[a+5] in araysimpanno:
                            print("ADA NOMER PORT YANG SAMA. YOU CANT DO THAT. ULANGI " , araysimpanno)
                            mengecek = 1
                            break
                        else:
                            araysimpanno.append(arays2[a+5])
                 
                    araysimpan.append(arays[a+5])
                    a+=1

                if mengecek == 0:
                    # cursor.execute("insert INTO valdat_odpmaster (name, qrcode_odp,  qrcode_port) VALUES ('"+arays[0]+"', '"+arays[3]+"', '"+arays[4]+"')")
                    # db.commit()
                    # cursor.execute("select id from `valdat_odpmaster` where `name` = '"+arays[0]+"' order by `id` desc limit 1")
                    # idodp = cursor.fetchone()
                    # print (idodp[0])
                    # a=0
                    # for x in range(int(kapasitas)):
                    #     cursor.execute("insert INTO valdat_validasi (reported_date, odp_port, qrcode_dropcore, odp_id) VALUES ('"+str(datetime.datetime.now())+"','"+str(arays2[a+5])+"', '"+arays[a+5]+"', '"+str(idodp[0])+"')")
                    #     db.commit()
                    #     a+=1
                        
                    update.message.reply_text("Data Berhasil Diinput.\nSilahkan Share Location ODP: ",reply_markup=ReplyKeyboardRemove())
                    context.user_data[0] = arraydata2
                    return LOCATION
                else:
                    update.message.reply_text("ADA DATA KEMBAR PADA QRCODE ATAU PORT. ULANGI ..")
                    return DATAODP


            else:
                update.message.reply_text("Data Kapasitas dan Jumlah Port Tidak Sama.\nKapasitas = "+str(kapasitas)+", Jumlah Port = "+str(jumlahport),reply_markup=ReplyKeyboardRemove())
                return DATAODP

        except ValueError:
            print(e)
            # if int(kapasitas) == int(jumlahport):
            #     arays = []
            #     arays2 = []
            #     for datas in arraydata2:
            #         dataakhir = datas.split(":")
            #         arays.append(dataakhir[1])
            #         arays2.append(dataakhir[0])

                
            #     a=0
            #     mengecek = 0
            #     araysimpan = []
            #     araysimpanno = []
            #     for x in range(int(kapasitas)):
            #         if arays[a+4] in araysimpan:
            #             if arays[a+4] != " " or  arays[a+4] != "":
            #                 print("ADA NOMER QR YANG SAMA. YOU CANT DO THAT. ULANGI 1" , araysimpan)
            #                 mengecek = 1
            #                 break
                        
            #         else:
            #             if arays2[a+4] in araysimpanno:
            #                 print("ADA NOMER PORT YANG SAMA. YOU CANT DO THAT. ULANGI " , araysimpanno)
            #                 mengecek = 1
            #                 break
            #             else:
            #                 araysimpanno.append(arays2[a+4])
            #             if arays[a+4].strip() != " " or  arays[a+4].strip() != "":
            #                 print("lewat2")
            #                 araysimpan.append(arays[a+4])
            #         a+=1


            #     if mengecek == 0:
            #         cursor.execute("insert INTO valdat_odpmaster (name, qrcode_port, qrcode_odp) VALUES ('"+arays[0]+"', '"+arays[2]+"', '"+arays[3]+"')")
            #         db.commit()
            #         cursor.execute("select id from `valdat_odpmaster` where `name` = '"+arays[0]+"' order by `id` desc limit 1")
            #         idodp = cursor.fetchone()
            #         print (idodp[0])
            #         a=0
            #         for x in range(int(kapasitas)):
            #             cursor.execute("insert INTO valdat_validasi (odp_port, qrcode_dropcore, odp_id) VALUES ('"+str(arays2[a+4])+"', '"+arays[a+4]+"', '"+str(idodp[0])+"')")
            #             db.commit()
            #             a+=1
                        
            #         update.message.reply_text("Berhasil Brother. Kapasitas = "+str(kapasitas)+", Jumlah Port = "+str(jumlahport)+".\nMasukkan LongLat : ",reply_markup=ReplyKeyboardRemove())
            #         context.user_data[0] = arraydata2
            #         return LOCATION
            #     else:
            #         update.message.reply_text("ADA DATA KEMBAR PADA QRCODE ATAU PORT. ULANGI ..")
            #         return DATAODP

            # else:
            #     update.message.reply_text("DATA KAPASITAS DAN JUMLAH PORT TIDAK COCOK. ULANGI LAGI. Kapasitas = "+str(kapasitas)+", Jumlah Port = "+str(jumlahport),reply_markup=ReplyKeyboardRemove())
            #     return DATAODP

            
    elif stats==1:
        update.message.reply_text("ADA DATA YANG TIDAK BOLEH KOSONG. ULANGI",reply_markup=ReplyKeyboardRemove())
        return DATAODP
    elif stats==2:
        update.message.reply_text("ADA QR CODE YANG TIDAK DITEMUKAN. ULANGI",reply_markup=ReplyKeyboardRemove())
        return DATAODP

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
    context.user_data['lat'] = user_location.latitude
    context.user_data['long'] = user_location.longitude
    logger.info("Location of %s: %f / %f", user.first_name, user_location.latitude,
                user_location.longitude)
    update.message.reply_text('Lokasi Berhasil Disimpan.\nSilahkan Upload Foto ODP Tampak Luar:')

    update.message.reply_text(context.user_data[0])

    return PHOTO1

def photo1(update, context):
    user = update.message.from_user
    dire = context.user_data[0][0].split(":")[1].strip().replace("/","-")
    context.user_data['path'] = '../media/valdat_odp/'+str(datetime.date.today())+'/'+dire
    photo_file = update.message.photo[-1].get_file()
    try:
        os.makedirs(context.user_data['path'])
        photo_file.download(context.user_data['path']+'/odp_luar.jpg')
    except:
        photo_file.download(context.user_data['path']+'/odp_luar.jpg')
    
    
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    update.message.reply_text('Foto ODP Tampak Luar Berhasil Disimpan.\nSilahkan Upload Foto ODP Tampak Dalam:')

    return PHOTO5

def photo2(update, context):
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download(context.user_data['path']+'/odp_dalam.jpg')
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    update.message.reply_text('Foto ODP Tampak Dalam Berhasil Disimpan.\nSilahkan Upload Foto Port ODP:')

    return PHOTO3

def photo3(update, context):
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download(context.user_data['path']+'/odp_port.jpg')
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    update.message.reply_text('Foto Port ODP Berhasil Disimpan.\nSilahkan Upload Foto QRCode ODP:')

    return PHOTO4

def photo4(update, context):
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download(context.user_data['path']+'/qrcode_odp.jpg')
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    update.message.reply_text('Foto QRCode ODP Berhasil Disimpan.\nSilahkan Upload Foto Redaman ODP:')

    return PHOTO5

def photo5(update, context):
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download(context.user_data['path']+'/odp_redaman.jpg')
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    update.message.reply_text('Foto Redaman ODP Berhasil Disimpan.\nSemua Laporan Telah Diterima.\nTerima kasih.')
    
    datasimpan = []
    dataket = []
    y=0
    for word in context.user_data[0]:
        datafinal = word.split(":")
        datasimpan.append(datafinal[1])
        dataket.append(datafinal[0])
        y+=1
        

    cursor.execute("insert INTO valdat_odpmaster (name, redaman, qrcode_odp, qrcode_port, lat, long, cap) VALUES ('"+str(datasimpan[0])+"','"+str(datasimpan[2])+"','"+str(datasimpan[3])+"','"+str(datasimpan[4])+"','"+str(context.user_data['lat'])+"','"+str(context.user_data['long'])+"','"+str(datasimpan[1])+"')")
    db.commit()
    cursor.execute("select id from `valdat_odpmaster` where `name` = '"+datasimpan[0]+"' order by `id` desc limit 1")
    idodp = cursor.fetchone()
    print (idodp[0])
    a=0
    for x in range(int(datasimpan[1])):
        cursor.execute("insert INTO valdat_validasi (odp_port, qrcode_dropcore, odp_id) VALUES ('"+str(datasimpan[a+5])+"', '"+datasimpan[a+5]+"', '"+str(idodp[0])+"')")
        db.commit()
        a+=1


    return ConversationHandler.END

def skip_location(update, context):
    user = update.message.from_user
    logger.info("User %s did not send a location.", user.first_name)
    update.message.reply_text('ZEEP')

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
    # updater = Updater("922566249:AAEkob4CL2Wh7SFtc399oyM5sKImiBOGugU", use_context=True)

    # Get the dispatcher to register handlers
    # dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('valdat_odp', start)],

        states={
            VALIDASIODP: [RegexHandler('^(Validasiodp)$', validasiodp)],

            DATAODP: [MessageHandler(Filters.text, dataodp)],

            GENDER: [RegexHandler('^(Boy|Girl|Other)$', gender)],

            PHOTO: [MessageHandler(Filters.photo, photo),
                    CommandHandler('skip', skip_photo)],

            LOCATION: [MessageHandler(Filters.location, location),
                       CommandHandler('skip', skip_location)],

            PHOTO1: [MessageHandler(Filters.photo, photo1),
                    CommandHandler('skip', skip_photo)],

            PHOTO2: [MessageHandler(Filters.photo, photo2),
                    CommandHandler('skip', skip_photo)],

            PHOTO3: [MessageHandler(Filters.photo, photo3),
                    CommandHandler('skip', skip_photo)],

            PHOTO4: [MessageHandler(Filters.photo, photo4),
                    CommandHandler('skip', skip_photo)],

            PHOTO5: [MessageHandler(Filters.photo, photo5),
                    CommandHandler('skip', skip_photo)],

            BIO: [MessageHandler(Filters.text, bio)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )
    return conv_handler
    # dp.add_handler(conv_handler)

    # log all errors
    # dp.add_error_handler(error)

    # Start the Bot
    # updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    # updater.idle()


# if __name__ == '__main__':
#     main()
