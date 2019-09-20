#Updated by @spiegan
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


from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
						  ConversationHandler)
global regex_odp
global regex_port
global regex_dc

regex_odp = r"^((ODP|OTB|GCL)-\D{3}-((\D{2,4}|\d{2,3}|\D\d{2,3})\/\d{1,3}|\d{2,3})|NO LABEL|TANPA TUTUP)"
regex_port = r"^(\d{,2}.\d{,2}|\d{,2})"

regex_dc = r"^(\d{1,4})"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)

logger = logging.getLogger(__name__)

EXPAND, ODP_REAL, PORT_EXPAND, QRCODE_PORT, ODP_COORDINATE, NEW_CAPACITY, OLD_CAPACITY, SC_NUMBER, IN_NUMBER, CEK_STO, CONFIRM = range(11)

db_conn.connect()

def start_expand(update, context):
	context.user_data.clear()
	update.message.reply_text(
		 'Hi!ヽ(^o^)丿 Aku adalah valdat bot. '
		 'Ketik /cancel untuk berhenti .\n\n',reply_markup=ReplyKeyboardRemove())	
	update.message.reply_text(
		'Masukkan nomor SC.\n\n',
		reply_markup=ReplyKeyboardRemove())
	
	return SC_NUMBER

def sc_number(update, context):
	global data_json

	reply_keyboard = [['IYA', 'TIDAK']]
	context.user_data.clear()
	text = update.message.text

	data_ = str(get_sc(text).text)
	json_ = json.loads(data_)

	if len(json_['data']) == 0:
		update.message.reply_text('Nomor SC tidak ditemukan, Masukkan nomor SC lagi :', reply_markup=ReplyKeyboardRemove())
		return SC_NUMBER

	data_json = json_['data'][0]
	context.user_data['SC_NUMBER'] = data_json['ORDER_ID']
	context.user_data['No INET'] = "-" if data_json['SPEEDY'] is None else data_json['SPEEDY'].split('~')[1]
	context.user_data['No TELP'] = data_json['PHONE_NO']
	context.user_data['PELANGGAN'] = data_json['CUSTOMER_NAME']
	context.user_data['ALAMAT'] = data_json['CUSTOMER_ADDR']
	context.user_data['STO'] = data_json['XS2']
	context.user_data['ODP WO'] = data_json['LOC_ID']

	update.message.reply_text("Data \n" "{}".format(list_data(context.user_data)))
	update.message.reply_text("Apakah data ini yang dimaksud ?",reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

	return CONFIRM

def get_sc(sc):
	url = "https://starclick.telkom.co.id/backend/public/api/tracking?_dc=1533002388191&ScNoss=true&Field=ORDER_ID&SearchText=" + sc
	return requests.get(url)

def list_data(data):
	facts = list()
	for key, value in data.items():
		facts.append("{} : {}".format(key, value))

	return  "\n".join(facts).join(['\n', '\n'])

def confirm(update, context):
	
	reply_keyboard = [['INPUT_DATA']]
	user = update.message.from_user
	text = str(update.message.text)
	print(update.message.text)
	if "IYA" == text:

		update.message.reply_text("Masukkan nomor IN : \nJika tidak ada diisi '-' ", reply_markup=ReplyKeyboardRemove())
		return IN_NUMBER

	else :
		update.message.reply_text(
			'Masukkan nomor SC.\n\n',
			reply_markup=ReplyKeyboardRemove())
		return SC_NUMBER

def in_number(update, context):
	user = update.message.from_user
	context.user_data['IN_NUMBER'] = update.message.text
	
	update.message.reply_text("Masukkan data STO :", reply_markup=ReplyKeyboardRemove())
	

	return CEK_STO

def cek_sto(update, context):
	user = update.message.from_user
	context.user_data['CEK_STO'] = update.message.text
	
	update.message.reply_text("Masukkan data ODP  :", reply_markup=ReplyKeyboardRemove())

	return ODP_REAL

def odp_real(update, context):
	regex_odp
	user = update.message.from_user
	context.user_data['ODP_REAL'] =update.message.text

	matches = re.search(regex_odp, update.message.text, re.IGNORECASE)
	if matches:
		update.message.reply_text("Masukkan data kapasitas lama :", reply_markup=ReplyKeyboardRemove())
		return OLD_CAPACITY
	else:
		update.message.reply_text("Format ODP salah silahkan masukkan lagi \nFormat ODP yang benar (ODP-TUR-FA/01) \nJika No Label ditutup ditulis NO LABEL "
								"\n Jika tanpa tutup ditulis TANPA TUTUP", reply_markup=ReplyKeyboardRemove())
		return ODP_REAL

def old_capacity(update, context):
	user = update.message.from_user
	context.user_data['OLD_CAPACITY'] = update.message.text

	update.message.reply_text("Masukkan data kapasitas baru :", reply_markup=ReplyKeyboardRemove())

	return NEW_CAPACITY

def new_capacity(update, context):
	user = update.message.from_user
	context.user_data['NEW_CAPACITY'] = update.message.text

	update.message.reply_text("Masukkan data tag ODP :", reply_markup=ReplyKeyboardRemove())

	return ODP_COORDINATE

def odp_coordinate(update, context):
	user = update.message.from_user
	user_location = update.message.location
	location = str(user_location.latitude) + ", " + str(user_location.longitude)
	context.user_data['ODP_COORDINATE'] = location

	update.message.reply_text("Masukkan data QR CODE :", reply_markup=ReplyKeyboardRemove())

	return QRCODE_PORT

def qrcode_port(update, context):
	user = update.message.from_user
	context.user_data['QRCODE_PORT'] =update.message.text

	update.message.reply_text("Masukkan data jumlah PORT expand :", reply_markup=ReplyKeyboardRemove())

	return PORT_EXPAND

def port_expand(update, context):
	user = update.message.from_user
	context.user_data['PORT_EXPAND'] = update.message.text
	sql = " insert into valdat_expand values (NULL,NULL,NULL,'"+context.user_data['CEK_STO']+"','"+context.user_data['ODP_REAL']+"','"+data_json['ORDER_ID']+"','"+context.user_data['IN_NUMBER']+"','"+context.user_data['OLD_CAPACITY']+"','"+context.user_data['NEW_CAPACITY']+"','"+context.user_data['ODP_COORDINATE']+"',1,1,'"+context.user_data['QRCODE_PORT']+"',1,NULL,NULL,1,'"+context.user_data['PORT_EXPAND']+"')"
	print (sql)
	cursor = db_conn.query(sql)
	db_conn.comit()

	#context.user_data['SC_NUMBER'] = "✔"
	#context.user_data['IN_NUMBER'] = "✔"
	#context.user_data['CEK_STO'] = "✔"
	#context.user_data['ODP_REAL'] = "✔"
	#context.user_data['OLD_CAPACITY'] = "✔"
	#context.user_data['NEW_CAPACITY'] = "✔"
	#context.user_data['ODP_COORDINATE'] = "✔"
	#context.user_data['QRCODE_PORT'] = "✔"
	#context.user_data['PORT_EXPAND'] = "✔"

	update.message.reply_text("Data \n" "{}".format(list_data(context.user_data)))
	update.message.reply_text("Terimakasih Data Telah Tersimpan", reply_markup=ReplyKeyboardRemove())	

	return ConversationHandler.END

def cancel(update, context):
	user = update.message.from_user
	logger.info("User %s canceled the conversation.", user.first_name)
	update.message.reply_text('ヽ(^o^)丿Bye! aku harap kita dapat berbicara dilain waktu. Terimakasih!(๑˃̵ᴗ˂̵)ﻭ.',reply_markup=ReplyKeyboardRemove())

	return ConversationHandler.END

def main():
	expand_handler = ConversationHandler(
		entry_points=[CommandHandler('expand', start_expand)],

		states={
			#expand
			# INPUT_SC:[RegexHandler('^(EXPAND|OMSET|MIGRATE)$', input_sc)],
			ODP_REAL: [MessageHandler(Filters.text, odp_real)],
			PORT_EXPAND: [MessageHandler(Filters.text, port_expand)],
			QRCODE_PORT: [MessageHandler(Filters.text, qrcode_port)],
			ODP_COORDINATE: [MessageHandler(Filters.location, odp_coordinate)],
			NEW_CAPACITY: [MessageHandler(Filters.text, new_capacity)],
			OLD_CAPACITY: [MessageHandler(Filters.text, old_capacity)],
			SC_NUMBER: [MessageHandler(Filters.text, sc_number)],
			IN_NUMBER: [MessageHandler(Filters.text, in_number)],
			CEK_STO: [MessageHandler(Filters.text, cek_sto)],
			CONFIRM: [RegexHandler('^(IYA|TIDAK)$', confirm)],
		},

		fallbacks=[CommandHandler('cancel', cancel)]
	)

	return expand_handler

