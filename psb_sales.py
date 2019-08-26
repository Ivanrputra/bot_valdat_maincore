
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
# import goto
import logging
import requests
import json
import os
import db_conn

import sys
import PIL
import numpy as np
from PIL import Image
from datetime import date
import re
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode
from datetime import date


from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

ID_PSB,SC, INET,TELP,SID,PELGN,ALAMAT,STO,ODP_WO,ODP_REAL,PORT,DC,QR_CODE,ONT,\
STB,TAG_ODP,TAG_PELGN,HOBBY, PHOTO, LOCATION, BIO, INPUT, CEK_SC, CONFIRM, \
RUMAH_PELANGGAN, PETUGAS_PELANGGAN, PETUGAS_LAYANAN, HASIL_REDAMAN, PERANGKAT_ONTSTB, FOTO_ODP, CHECK_MYIR, \
CONFIRM_SALES, SALES_RUMAH_PELANGGAN, SALES_LOKASI_PELANGGAN = range(34)

db_conn.connect()


def start_psb(update, context):
    context.user_data.clear()
    context.user_data['regex_odp']  = r"^((ODP|OTB|GCL)-\D{3}-((\D{2,4}|\d{2,3}|\D\d{2,3})\/\d{1,3}|\d{2,3})|NO LABEL|TANPA TUTUP)"
    context.user_data['regex_port'] = r"^(\d{,2}.\d{,2}|\d{,2})"
    context.user_data['regex_dc']   = r"^(\d{1,4})"

    # global tanggal, pathmedia
    # today = date.today()
    context.user_data['tanggal'] = date.today().strftime("%Y-%m-%d")
    # global path
    context.user_data['pathmedia'] = "../valdat_web/media/evidence/"+context.user_data['tanggal']
    try:
        os.makedirs(context.user_data['pathmedia'])
    except OSError:
        print("directory sudah ada %s " % context.user_data['pathmedia'])
    else:
        print("Successfully created the directory %s" % context.user_data['pathmedia'])

    update.message.reply_text(
        'Hi!ヽ(^o^)丿 Aku adalah valdat bot. '
        'Ketik /cancel untuk berhenti .\n\n',
    reply_markup=ReplyKeyboardRemove())
    update.message.reply_text(
        'Masukkan nomor SC.\n\n',
        reply_markup=ReplyKeyboardRemove())
    return CEK_SC

def start_sales(update, context):
    context.user_data.clear()
    context.user_data['regex_odp']  = r"^((ODP|OTB|GCL)-\D{3}-((\D{2,4}|\d{2,3}|\D\d{2,3})\/\d{1,3}|\d{2,3})|NO LABEL|TANPA TUTUP)"
    context.user_data['regex_port'] = r"^(\d{,2}.\d{,2}|\d{,2})"
    context.user_data['regex_dc']   = r"^(\d{1,4})"

    # global tanggal, pathmedia
    # today = date.today()
    context.user_data['tanggal'] = date.today().strftime("%Y-%m-%d")
    # global path
    context.user_data['pathmedia'] = "../valdat_web/media/evidence/"+context.user_data['tanggal']
    try:
        os.makedirs(context.user_data['pathmedia'])
    except OSError:
        print("directory sudah ada %s " % context.user_data['pathmedia'])
    else:
        print("Successfully created the directory %s" % context.user_data['pathmedia'])

    update.message.reply_text(
        'Hi!ヽ(^o^)丿 Aku adalah valdat bot. '
        'Ketik /cancel untuk berhenti .\n\n',
        reply_markup=ReplyKeyboardRemove())
    update.message.reply_text(
        'Masukkan Nomor Myir\n\n',
        reply_markup=ReplyKeyboardRemove())
    return CHECK_MYIR

def cek_sc(update, context):
    # global data
    reply_keyboard = [['IYA', 'TIDAK']]
    context.user_data['data'] = {}
    text = update.message.text
    data_ = str(get_sc(text).text)
    json_ = json.loads(data_)
    # print(data_)
    if len(json_['data']) == 0:
        update.message.reply_text('Nomor SC tidak ditemukan, Masukkan Nomor SC lagi :',reply_markup=ReplyKeyboardRemove())
        return CEK_SC

    data_json = json_['data'][0]
    context.user_data['data']['No. SC']     = data_json['ORDER_ID']
    context.user_data['data']['No INET']    = "-" if data_json['SPEEDY'] is None else data_json['SPEEDY'].split('~')[1]
    context.user_data['data']['No TELP']    = data_json['PHONE_NO']
    context.user_data['data']['PELANGGAN']  = data_json['CUSTOMER_NAME']
    context.user_data['data']['ALAMAT']     = data_json['CUSTOMER_ADDR']
    context.user_data['data']['STO']        = data_json['XS2']
    context.user_data['data']['ODP WO']     = data_json['LOC_ID']

    update.message.reply_text("Data \n" "{}".format(list_data(context.user_data['data'])))
    update.message.reply_text("Apakah data ini benar ?",reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return CONFIRM

def get_sc(sc):
    url = "https://starclick.telkom.co.id/backend/public/api/tracking?_dc=1533002388191&ScNoss=true&Field=ORDER_ID&SearchText=" + sc
    return requests.get(url)

def list_data(data):
    facts = list()
    for key, value in data.items():
        facts.append("{} : {}".format(key, value))

    return  "\n".join(facts).join(['\n', '\n'])

def confirm(update,context):
    # global data
    reply_keyboard = [['INPUT_DATA']]
    user = update.message.from_user
    text = str(update.message.text)
    print(update.message.text)
    if "IYA" == text:
        update.message.reply_text("Masukkan data ODP REAL :", reply_markup=ReplyKeyboardRemove())
        return ODP_REAL
    else :
        update.message.reply_text(
            'Masukkan nomor SC.\n\n',
            reply_markup=ReplyKeyboardRemove())
        return CEK_SC

def odp_real(update, context):
    # global data, regex_odp
    user = update.message.from_user
    context.user_data['data']['ODP REAL'] = update.message.text



    matches = re.search(context.user_data['regex_odp'], update.message.text, re.IGNORECASE)
    if matches:
        update.message.reply_text("Masukkan data PORT :", reply_markup=ReplyKeyboardRemove())
        return PORT
    else:
        update.message.reply_text("Format odp salah silahkan masukkan lagi \nFormat ODP yang benar (ODP-TUR-FA/01) \nJika No label ditulis NO LABEL "
                                  "\nJika tanpa tutup ditulis TANPA TUTUP", reply_markup=ReplyKeyboardRemove())
        return ODP_REAL

def port(update, context):
    # global data, regex_port
    user = update.message.from_user
    context.user_data['data']['PORT'] = update.message.text
    matches = re.search(context.user_data['regex_port'], update.message.text, re.IGNORECASE)
    if matches:
        update.message.reply_text("Masukkan panjang DC :",reply_markup=ReplyKeyboardRemove())
        return DC
    else:
        update.message.reply_text("Format DC salah silahkan masukkan lagi. \nFormat Port yang benar berupa angka. \n ", reply_markup=ReplyKeyboardRemove())
        return PORT

def dc(update, context):
    # global data
    # global regex_dc
    user = update.message.from_user
    context.user_data['data']['panjang DC'] = update.message.text
    matches = re.search(context.user_data['regex_dc'], update.message.text, re.IGNORECASE)

    if matches:
        update.message.reply_text("Masukkan data QR Code :",reply_markup=ReplyKeyboardRemove())
        return QR_CODE
    else :
        update.message.reply_text("Format dc salah silahkan masukkan lagi. \nFormat dc yang benar berupa angka. \n ", reply_markup=ReplyKeyboardRemove())
        return DC

def qr_code(update, context):
    # global data
    user = update.message.from_user
    context.user_data['data']['QR CODE'] = update.message.text
    update.message.reply_text("Masukkan data SN ONT :",reply_markup=ReplyKeyboardRemove())
    return ONT

def sn_ont(update, context):
    # global data
    user = update.message.from_user
    context.user_data['data']['SN ONT'] = update.message.text
    update.message.reply_text("Masukkan data MAC STB :",reply_markup=ReplyKeyboardRemove())
    return STB

def sn_stb(update, context):
    # global data
    user = update.message.from_user
    context.user_data['data']['MAC STB'] = update.message.text
    update.message.reply_text("Masukkan data tag ODP :",reply_markup=ReplyKeyboardRemove())
    return TAG_ODP

def tag_odp(update, context):
    # global data
    user = update.message.from_user
    user_location = update.message.location
    location = str(user_location.latitude) + ", " + str(user_location.longitude)
    context.user_data['data']['TAG ODP'] = location

    update.message.reply_text("Masukkan data tag pelanggan :",reply_markup=ReplyKeyboardRemove())
    return TAG_PELGN

def tag_pelanggan(update, context):
    # global data
    user = update.message.from_user
    user_location = update.message.location
    location = str(user_location.latitude) + ", " + str(user_location.longitude)
    context.user_data['data']['TAG PELANGGAN'] = location
    update.message.reply_text("Masukkan foto rumah pelanggan :", reply_markup=ReplyKeyboardRemove())
    return RUMAH_PELANGGAN

def foto_rumah_pelanggan(update, context):
    # global data, pathmedia
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    path = context.user_data['pathmedia']+'/psb_{}_rumah_pelanggan.jpg'.format(context.user_data['data']['No. SC'])
    photo_file.download(path)
    context.user_data['data']['FOTO RUMAH PELANGGAN'] = path
    update.message.reply_text("Masukkan foto petugas dengan pelanggan :", reply_markup=ReplyKeyboardRemove())
    return PETUGAS_PELANGGAN

def foto_petugas_pelanggan(update, context):
    # global pathmedia
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    path = context.user_data['pathmedia']+'/psb_{}_petugas-dengan-pelanggan.jpg'.format(context.user_data['data']['No. SC'])
    photo_file.download(path)
    context.user_data['data']['FOTO PETUGAS & PELANGGAN'] = path
    update.message.reply_text("Masukkan foto petugas dengan layanan :", reply_markup=ReplyKeyboardRemove())
    return PETUGAS_LAYANAN

def foto_petugas_layanan(update, context):
    # global pathmedia
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    path = context.user_data['pathmedia']+'/psb_{}_petugas-dengan-layanan.jpg'.format(context.user_data['data']['No. SC'])
    photo_file.download(path)
    context.user_data['data']['FOTO PETUGAS & LAYANAN'] = path
    update.message.reply_text("Masukkan foto redaman :", reply_markup=ReplyKeyboardRemove())
    return HASIL_REDAMAN

def foto_redaman(update, context):
    # global pathmedia
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    path = context.user_data['pathmedia']+'/psb_{}_hasil-redaman.jpg'.format(context.user_data['data']['No. SC'])
    photo_file.download(path)
    context.user_data['data']['FOTO HASIL REDAMAN'] = path
    update.message.reply_text("Masukkan foto ont/stb :", reply_markup=ReplyKeyboardRemove())
    return PERANGKAT_ONTSTB

def foto_ontstb(update, context):
    # global pathmedia
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    path = context.user_data['pathmedia']+'/psb_{}_perangkat-ontstb.jpg'.format(context.user_data['data']['No. SC'])
    photo_file.download(path)
    context.user_data['data']['FOTO ONT & STB'] = path
    update.message.reply_text("Masukkan foto odp :", reply_markup=ReplyKeyboardRemove())
    return FOTO_ODP

def foto_odp(update, context):
    # global pathmedia
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    path = context.user_data['pathmedia']+'/psb_{}_foto-odp.jpg'.format(context.user_data['data']['No. SC'])
    photo_file.download(path)
    context.user_data['data']['FOTO ODP'] = path

    # insert to valdat_psb
    db_conn.connect()
    sql = ("insert into valdat_psb (ps_date,report_date,assigned_hd_date,sc,telegram_chat_id,telegram_username,no_voice,no_internet,sid,customer_name,customer_address,datel,sto,odp_wo,odp_real,odp_port,dc_length,qrcode_dropcore,sn_ont,sn_stb,odp_coordinate,customer_coordinate,status,status_dava,message_id)"+
        "values ('"+str(date.today())+"','"+str(date.today())+"','"+str(date.today())+"','"+
        context.user_data['data']['No. SC']+"',NULL,NULL,'"+
        context.user_data['data']['No TELP']+"','"+
        context.user_data['data']['No INET']+"',NULL,'"+
        context.user_data['data']['PELANGGAN']+"','"+
        context.user_data['data']['ALAMAT']+"',NULL,'"+
        context.user_data['data']['STO']+"','"+
        context.user_data['data']['ODP WO']+"','"+
        context.user_data['data']['ODP REAL']+"','"+
        context.user_data['data']['PORT']+"','"+
        context.user_data['data']['panjang DC']+"','"+
        context.user_data['data']['QR CODE']+"','"+
        context.user_data['data']['SN ONT']+"','"+
        context.user_data['data']['MAC STB']+"','"+
        context.user_data['data']['TAG ODP']+"','"+
        context.user_data['data']['TAG PELANGGAN']+"',NULL,NULL,NULL) ")    
    print (sql)
    cursor = db_conn.query(sql)
    db_conn.comit()
    # insert to valdat_psb

    media = []
    media.append(context.user_data['data']['FOTO RUMAH PELANGGAN'])
    media.append(context.user_data['data']['FOTO PETUGAS & PELANGGAN'])
    media.append(context.user_data['data']['FOTO PETUGAS & LAYANAN'])
    media.append(context.user_data['data']['FOTO HASIL REDAMAN'])
    media.append(context.user_data['data']['FOTO ONT & STB'])
    media.append(context.user_data['data']['FOTO ODP'])

    psb_id = cursor.lastrowid
    for x in media:
        sql = (" insert into valdat_evidence (url,category_id,psb_id) values ('"+
            str(x)+"',"+
            str(1)+","+
            str(psb_id)+") ")
        print(sql)
        cursor = db_conn.query(sql)
    db_conn.comit()

    context.user_data['data']['FOTO RUMAH PELANGGAN']= " ✔️ "
    context.user_data['data']['FOTO PETUGAS & PELANGGAN']= " ✔️ "
    context.user_data['data']['FOTO PETUGAS & LAYANAN']= " ✔️ "
    context.user_data['data']['FOTO HASIL REDAMAN']= " ✔️ "
    context.user_data['data']['FOTO ONT & STB']= " ✔️ "
    context.user_data['data']['FOTO ODP']= " ✔️ "

    update.message.reply_text("Data \n" "{}".format(list_data(context.user_data['data'])))
    update.message.reply_text("Terimakasih Data Telah Tersimpan", reply_markup=ReplyKeyboardRemove())

    #save kombinasi
    list_im1 = ([context.user_data['pathmedia']+'/psb_{}_rumah_pelanggan.jpg'.format(context.user_data['data']['No. SC']),context.user_data['pathmedia']+'/psb_{}_petugas-dengan-pelanggan.jpg'.format(context.user_data['data']['No. SC']), context.user_data['pathmedia']+'/psb_{}_petugas-dengan-layanan.jpg'.format(context.user_data['data']['No. SC'])])
    list_im2 = ([context.user_data['pathmedia']+'/psb_{}_rumah_pelanggan.jpg'.format(context.user_data['data']['No. SC']),context.user_data['pathmedia']+'/psb_{}_petugas-dengan-pelanggan.jpg'.format(context.user_data['data']['No. SC']), context.user_data['pathmedia']+'/psb_{}_petugas-dengan-layanan.jpg'.format(context.user_data['data']['No. SC'])])

    imgs1 = [Image.open(i) for i in list_im1]

    imgs2 = [Image.open(i) for i in list_im2]

    # pick the image which is the smallest, and resize the others to match it (can be arbitrary image shape here)
    min_shape = sorted([(np.sum(i.size), i.size) for i in imgs1])[0][1]

    imgs_comb1 = np.hstack((np.asarray(i.resize(min_shape)) for i in imgs1))
    imgs_comb2 = np.hstack((np.asarray(i.resize(min_shape)) for i in imgs2))


    imgs = ([imgs_comb1,imgs_comb2])
    # for a vertical stacking it is simple: use vstack
    imgs_comb = np.vstack((np.asarray(i) for i in imgs))
    imgs_comb = Image.fromarray(imgs_comb)
    imgs_comb.save(context.user_data['pathmedia']+'/psb_{}_kombinasi.jpg'.format(context.user_data['data']['No. SC']),'JPEG')
    return ConversationHandler.END

def get_myir(myir):
    url = 'http://api.indihome.co.id/api/track-view'
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Authorization": "Basic bXlpbmRpaG9tZTpwN2Qya0xYNGI0TkY1OFZNODR2Vw=="}
    payload = 'guid=myindihome#2017&code=&data={"trackId":"%s"}' % myir

    return requests.post(url, data=payload, headers=headers)

def check_myir(update, context):
    # global data
    reply_keyboard = [['IYA', 'TIDAK']]
    context.user_data['data'] = {}
    text = update.message.text
    data_ = str(get_myir(text).text)
    json_ = json.loads(data_)
    if json_['data'] == None:
        update.message.reply_text('MYIR tidak ditemukan, Masukkan Nomor MYIR lagi :',reply_markup=ReplyKeyboardRemove())
        return CHECK_MYIR

    print(data_)
    data_json = json_['data']
    context.user_data['data']['TRACK ID']           = data_json['track_id']
    context.user_data['data']['K-CONTACT']          = json_['data']['detail'][0]['x3']
    context.user_data['data']['NO SC']              = "-" if data_json['scid'] is None else data_json['scid']
    context.user_data['data']['TANGGAL ORDER']      = "-" if data_json['orderDate'] is None else data_json['scid']
    context.user_data['data']['STATUS MYIR']        = data_json['status_name']
    context.user_data['data']['NAMA CUSTOMER']      = data_json['user_name']
    context.user_data['data']['PAKET']              = data_json['name']
    context.user_data['data']['ALAMAT INSTALASI'] = json_['data']['address']['address']
    context.user_data['data']['STO'] = json_['data']['data1']['sto']

    update.message.reply_text("Data \n" "{}".format(list_data(context.user_data['data'])))
    update.message.reply_text("Apakah data ini benar ?",reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return CONFIRM_SALES

def confirm_sales(update, context):
    reply_keyboard = [['INPUT_DATA']]
    user = update.message.from_user
    text = str(update.message.text)
    print(update.message.text)
    if "IYA" == text:

        update.message.reply_text("Masukkan Foto Rumah Pelanggan :", reply_markup=ReplyKeyboardRemove())
        return SALES_RUMAH_PELANGGAN

    else :
        update.message.reply_text(
            'Masukkan Nomor MYIR.\n\n',
            reply_markup=ReplyKeyboardRemove())
        return CHECK_MYIR

def sales_rumah_pelanggan(update, context):
    # global pathmedia
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    path = context.user_data['pathmedia'] +'/sales_{}_rumah_pelanggan.jpg'.format(context.user_data['data']['TRACK ID'])
    photo_file.download(path)
    context.user_data['data']['FOTO RUMAH PELANGGAN'] = path
    update.message.reply_text("Masukkan Tag Lokasi Pelanggan :", reply_markup=ReplyKeyboardRemove())
    return SALES_LOKASI_PELANGGAN

def sales_lokasi_pelanggan(update, context):
    # global data, pathmedia
    user = update.message.from_user
    user_location = update.message.location
    location = str(user_location.latitude) + ", " + str(user_location.longitude)
    context.user_data['data']['TAG LOKASI PELANGGAN'] = location
    db_conn.connect()
    sql = (" insert into valdat_sales (track_id,k_contact,no_sc,tanggal_order,status,nama_customer,paket,alamat_instalasi,sto,foto_rumah_pelanggan,tag_lokasi_pelanggan) values ('"+
        context.user_data['data']['TRACK ID']+"','"+
        context.user_data['data']['K-CONTACT']+"','"+
        context.user_data['data']['NO SC']+"','"+
        context.user_data['data']['TANGGAL ORDER']+"','"+
        context.user_data['data']['STATUS MYIR']+"','"+
        context.user_data['data']['NAMA CUSTOMER']+"','"+
        context.user_data['data']['PAKET']+"','"+
        context.user_data['data']['ALAMAT INSTALASI']+"','"+
        context.user_data['data']['STO']+"','"+
        context.user_data['data']['FOTO RUMAH PELANGGAN']+"','"+
        context.user_data['data']['TAG LOKASI PELANGGAN']+"') ")
    print(sql)
    cursor = db_conn.query(sql)
    db_conn.comit()

    #pandaiman
    sales_id = cursor.lastrowid
    sql = (" insert into valdat_evidence (url,category_id,sales_id) values ('"+
        context.user_data['data']['FOTO RUMAH PELANGGAN']+"',"+
        str(1)+","+
        str(sales_id)+") ")
    print(sql)
    cursor = db_conn.query(sql)
    db_conn.comit()
    #pandaiman

    context.user_data['data']['FOTO RUMAH PELANGGAN'] = " ✔️ "
    update.message.reply_text("Data \n" "{}".format(list_data(context.user_data['data'])))
    update.message.reply_text("Terimakasih Data Telah Tersimpan", reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('ヽ(^o^)丿Bye! aku harap kita dapat berbicara dilain waktu. Terimakasih!(๑˃̵ᴗ˂̵)ﻭ.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    psb_handler = ConversationHandler(
        entry_points=[CommandHandler('PSB', start_psb)],

        states={
            # INPUT_SC:[RegexHandler('^(PSB|SALES)$', input_sc)],
            ODP_REAL: [MessageHandler(Filters.text, odp_real)],
            PORT: [MessageHandler(Filters.text, port)],
            DC: [MessageHandler(Filters.text, dc)],
            QR_CODE: [MessageHandler(Filters.text, qr_code)],
            ONT: [MessageHandler(Filters.text, sn_ont)],
            STB: [MessageHandler(Filters.text, sn_stb)],
            TAG_ODP: [MessageHandler(Filters.location, tag_odp)],
            TAG_PELGN: [MessageHandler(Filters.location, tag_pelanggan)],
            RUMAH_PELANGGAN: [MessageHandler(Filters.photo, foto_rumah_pelanggan)],
            PETUGAS_PELANGGAN: [MessageHandler(Filters.photo, foto_petugas_pelanggan)],
            PETUGAS_LAYANAN: [MessageHandler(Filters.photo, foto_petugas_layanan)],
            HASIL_REDAMAN: [MessageHandler(Filters.photo, foto_redaman)],
            PERANGKAT_ONTSTB: [MessageHandler(Filters.photo, foto_ontstb)],
            FOTO_ODP: [MessageHandler(Filters.photo, foto_odp)],
            INPUT: [RegexHandler('^(INPUT_DATA)$', input)],
            CEK_SC: [MessageHandler(Filters.text, cek_sc)],
            CONFIRM: [RegexHandler('^(IYA|TIDAK)$', confirm)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )
    sales_handler = ConversationHandler(
        entry_points=[CommandHandler('SALES', start_sales)],

        states={
            CHECK_MYIR : [MessageHandler(Filters.text, check_myir)],
            CONFIRM_SALES: [RegexHandler('^(IYA|TIDAK)$', confirm_sales)],
            SALES_RUMAH_PELANGGAN : [MessageHandler(Filters.photo, sales_rumah_pelanggan)],
            SALES_LOKASI_PELANGGAN : [MessageHandler(Filters.location, sales_lokasi_pelanggan)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )
    return psb_handler,sales_handler