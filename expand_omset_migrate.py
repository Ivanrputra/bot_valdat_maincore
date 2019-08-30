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

EXPAND, SC_NUMBER, IN, STO, ODP, OLD_CAPACITY, NEW_CAPACITY, ODP_COORDINATE, QRCODE_PORT,\
PORT_EXPAND, OLD_PORT, NEW_PORT, OLD_ODP, NEW_ODP, NO_INTERNET, NO_TELP, OMSET, MIGRATE, CUSTOMER_NAME, CUSTOMER_ADDRESS, \
NO_HP, PORT, DC, SN_ONT, SN_STB, TECHNICIAN_NAME, MITRA, CUSTOMER_COORDINATE, IN_NUMBER, \
CONFIRM, CEK_STO, ODP_REAL, LOCATION, CEK_IN_OMSET, CEK_SC_MIGRATE, CEK_IN_OMSET, CEK_IN_MIGRATE, \
TAG_ODP_MIGRATE, DC_LENGTH, QR_CODE_MIGRATE, QRCODE_DROPCORE, NO_INET_MIGRATE, NO_TELP_MIGRATE, ODP_MIGRATE, CONFIRM_MIGRATE, CEK_STO_MIGRATE = range(46)

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

def start_omset(update, context):
	context.user_data.clear()
	update.message.reply_text(
		 'Hi!ヽ(^o^)丿 Aku adalah valdat bot. '
		 'Ketik /cancel untuk berhenti .\n\n',reply_markup=ReplyKeyboardRemove())	
	update.message.reply_text(
		'Masukkan nomor IN.\n\n',
		reply_markup=ReplyKeyboardRemove())
	return CEK_IN_OMSET

def start_migrate(update, context):
	context.user_data.clear()
	update.message.reply_text(
		'Hi!ヽ(^o^)丿 Aku adalah valdat bot. '
		'Ketik /cancel untuk berhenti .\n\n',reply_markup=ReplyKeyboardRemove())	
	update.message.reply_text(
		'Masukkan nomor SC.\n\n',
		reply_markup=ReplyKeyboardRemove())
	return CEK_SC_MIGRATE

#expand
def sc_number(update, context):
	# global data_json

	reply_keyboard = [['IYA', 'TIDAK']]
	context.user_data = {}
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


#omset

def cek_in_omset(update, context):

	user = update.message.from_user
	context.user_data['CEK_IN_OMSET'] = update.message.text
	update.message.reply_text("Masukkan data port awal : ", reply_markup=ReplyKeyboardRemove())

	return OLD_PORT

def old_port(update, context):
	
	user = update.message.from_user
	context.user_data['OLD_PORT'] = update.message.text
	update.message.reply_text("Masukkan data port baru : ", reply_markup=ReplyKeyboardRemove())

	return NEW_PORT

def new_port(update, context):
	
	user = update.message.from_user
	context.user_data['NEW_PORT'] = update.message.text
	update.message.reply_text("Masukkan data ODP awal :", reply_markup=ReplyKeyboardRemove())

	return OLD_ODP

def oldp_odp(update, context):

	user = update.message.from_user
	context.user_data['OLD_ODP'] = update.message.text
	update.message.reply_text("Masukkan data ODP baru :", reply_markup=ReplyKeyboardRemove())

	return NEW_ODP

def new_odp(update, context):

	user = update.message.from_user
	context.user_data['NEW_ODP'] = update.message.text
	update.message.reply_text("Masukkan nomor Internet :", reply_markup=ReplyKeyboardRemove())

	return NO_INTERNET

def no_internet(update, context):

	user = update.message.from_user
	context.user_data['NO_INTERNET'] = update.message.text
	update.message.reply_text("Masukkan nomor telepon :", reply_markup=ReplyKeyboardRemove())

	return NO_TELP

def no_telp(update, context):
	
	user = update.message.from_user
	context.user_data['NO_TELP'] = update.message.text
	update.message.reply_text("Masukkan QR CODE :", reply_markup=ReplyKeyboardRemove())

	return QRCODE_DROPCORE

def qrcode_dropcore(update, context):

	user = update.message.from_user
	context.user_data['QRCODE_DROPCORE'] = update.message.text
	sql = " insert into valdat_omset values (NULL,NULL,NULL,'"+context.user_data['CEK_IN_OMSET']+"','"+context.user_data['OLD_PORT']+"','"+context.user_data['NEW_PORT']+"','"+context.user_data['OLD_ODP']+"','"+context.user_data['NEW_ODP']+"','"+context.user_data['NO_TELP']+"','"+context.user_data['NO_INTERNET']+"','"+context.user_data['QRCODE_DROPCORE']+"',1,NULL,NULL,NULL)"
	print (sql)
	cursor = db_conn.query(sql)
	db_conn.comit()

	context.user_data['CEK_IN_OMSET'] = "✔"
	context.user_data['OLD_PORT'] = "✔"
	context.user_data['NEW_PORT'] = "✔"
	context.user_data['OLD_ODP'] = "✔"
	context.user_data['NEW_ODP'] = "✔"
	context.user_data['NO_INTERNET'] = "✔"
	context.user_data['NO_TELP'] = "✔" 
	context.user_data['QRCODE_DROPCORE'] = "✔"

	update.message.reply_text("Data \n" "{}".format(list_data(context.user_data)))
	update.message.reply_text("Terimakasih Data Telah Tersimpan", reply_markup=ReplyKeyboardRemove())

	
	return ConversationHandler.END 


# migrate conversation
def cek_sc_migrate(update, context):
	
	# global data_json
	
	reply_keyboard = [['IYA', 'TIDAK']]
	context.user_data = {}
	text = update.message.text

	data_ = str(get_sc_migrate(text).text)
	json_ = json.loads(data_)


	if len(json_['data']) == 0:
		update.message.reply_text('Nomor SC tidak ditemukan, Masukkan nomor SC lagi :', reply_markup=ReplyKeyboardRemove())
		return CEK_SC_MIGRATE

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

	return CONFIRM_MIGRATE

def get_sc_migrate(sc):
	url = "https://starclick.telkom.co.id/backend/public/api/tracking?_dc=1533002388191&ScNoss=true&Field=ORDER_ID&SearchText=" + sc
	return requests.get(url)

def confirm_migrate(update, context):
	
	reply_keyboard = [['INPUT_DATA']]
	user = update.message.from_user
	text = str(update.message.text)
	print(update.message.text)
	if "IYA" == text:

		update.message.reply_text("Masukkan nomor IN : \nJika tidak ada diisi '-' ", reply_markup=ReplyKeyboardRemove())
		return CEK_IN_MIGRATE

	else :
		update.message.reply_text(
			'Masukkan nomor SC.\n\n',
			reply_markup=ReplyKeyboardRemove())
		return CEK_SC_MIGRATE

def cek_in_migrate(update, context):

	user = update.message.from_user
	context.user_data['CEK_IN_MIGRATE'] = update.message.text

	update.message.reply_text("Masukkan nomor internet :", reply_markup=ReplyKeyboardRemove())

	return NO_INET_MIGRATE

def no_inet_migrate(update, context):
	
	user = update.message.from_user
	context.user_data['NO_INET_MIGRATE'] = update.message.text

	update.message.reply_text("Masukkan nomor telepon :", reply_markup=ReplyKeyboardRemove())

	return NO_TELP_MIGRATE

def no_telp_migrate(update, context):

	user = update.message.from_user
	context.user_data['NO_TELP_MIGRATE'] = update.message.text

	update.message.reply_text("Masukkan nama pelanggan :", reply_markup=ReplyKeyboardRemove())

	return CUSTOMER_NAME

def customer_name(update, context):
	
	user = update.message.from_user
	context.user_data['CUSTOMER_NAME'] = update.message.text

	update.message.reply_text("Masukkan alamat pelanggan :", reply_markup=ReplyKeyboardRemove())

	return CUSTOMER_ADDRESS

def customer_address(update, context):
	
	user = update.message.from_user
	context.user_data['CUSTOMER_ADDRESS'] = update.message.text

	update.message.reply_text("Masukkan nomor HP pelanggan :", reply_markup=ReplyKeyboardRemove())

	return NO_HP

def no_hp(update, context):
	
	user = update.message.from_user
	context.user_data['NO_HP'] = update.message.text

	update.message.reply_text("Masukkan data STO :\nFormat STO 3 huruf",reply_markup=ReplyKeyboardRemove())

	return CEK_STO_MIGRATE

def cek_sto_migrate(update, context):
	
	user = update.message.from_user
	context.user_data['CEK_STO_MIGRATE'] = update.message.text

	update.message.reply_text("Masukkan data ODP :",reply_markup=ReplyKeyboardRemove())

	return ODP_MIGRATE

def odp_migrate(update, context):
	
	user = update.message.from_user
	context.user_data['ODP_MIGRATE'] = update.message.text

	matches = re.search(regex_odp, update.message.text, re.IGNORECASE)
	if matches:
		update.message.reply_text("Masukkan data PORT :", reply_markup=ReplyKeyboardRemove())
		return PORT
	else: 
		update.message.reply_text("Format ODP salah silahkan masukkan lagi \nFormat ODP yang benar (ODP-TUR-FA/01) \nJika No Label ditutup ditulis NO LABEL "
								"\n Jika tanpa tutup ditulis TANPA TUTUP", reply_markup=ReplyKeyboardRemove())
		return ODP_MIGRATE

def port(update, context):

	user = update.message.from_user
	context.user_data['PORT'] = update.message.text

	matches = re.findall(regex_port, update.message.text, re.IGNORECASE)
	if matches:
		update.message.reply_text("Masukkan data DC :", reply_markup=ReplyKeyboardRemove())
		return DC_LENGTH
	else:
		update.message.reply_text("Format PORT salah silahkan masukkan lagi :",reply_markup=ReplyKeyboardRemove())
		return PORT

def dc_length(update, context):

	user = update.message.from_user
	context.user_data['DC_LENGTH'] = update.message.text

	matches = re.search(regex_dc, update.message.text, re.IGNORECASE)
	if matches:
		update.message.reply_text("Masukaan QR CODE :", reply_markup=ReplyKeyboardRemove())
		return QR_CODE_MIGRATE
	else:
		update.message.reply_text("Format DC salah silahkan masukkan lagi :", reply_markup=ReplyKeyboardRemove())
		return DC_LENGTH

def qr_code_migrate(update, context):

	user = update.message.from_user
	context.user_data['QR_CODE_MIGRATE'] = update.message.text
	update.message.reply_text("Masukkan data SN ONT :", reply_markup=ReplyKeyboardRemove())
	return SN_ONT

def sn_ont(update, context):

	user = update.message.from_user
	context.user_data['SN_ONT'] = update.message.text
	update.message.reply_text("Masukkan data SN STB :", reply_markup=ReplyKeyboardRemove())
	return SN_STB	

def sn_stb(update, context):

	user = update.message.from_user
	context.user_data['SN_STB'] = update.message.text
	update.message.reply_text("Masukkan nama teknisi :", reply_markup=ReplyKeyboardRemove())
	return TECHNICIAN_NAME
	
def technician_name(update, context):

	user = update.message.from_user
	context.user_data['TECHNICIAN_NAME'] = update.message.text
	update.message.reply_text("Masukkan nama mitra :", reply_markup=ReplyKeyboardRemove())
	return MITRA

def mitra(update, context):

	user = update.message.from_user
	context.user_data['MITRA']= update.message.text
	update.message.reply_text("Masukkan data tag ODP :", reply_markup=ReplyKeyboardRemove())

	return TAG_ODP_MIGRATE

def tag_odp_migrate(update, context):

	user = update.message.from_user
	user_location = update.message.location
	location = str(user_location.latitude) + ", " + str(user_location.longitude)
	context.user_data['TAG_ODP_MIGRATE'] = location

	update.message.reply_text("Masukkan tag pelanggan :", reply_markup=ReplyKeyboardRemove())

	return CUSTOMER_COORDINATE

def customer_coordinate(update, context):

	user = update.message.from_user
	user_location = update.message.location
	location = str(user_location.latitude) + ", " + str(user_location.longitude)
	context.user_data['CUSTOMER_COORDINATE'] = location
	sql = " insert into valdat_migrate values (NULL,'"+data_json['ORDER_ID']+"','"+context.user_data['CEK_IN_MIGRATE']+"','"+context.user_data['NO_TELP_MIGRATE']+"','"+context.user_data['NO_INET_MIGRATE']+"','"+context.user_data['CUSTOMER_NAME']+"','"+context.user_data['CUSTOMER_ADDRESS']+"','"+context.user_data['CEK_STO_MIGRATE']+"','"+context.user_data['ODP_MIGRATE']+"','"+context.user_data['PORT']+"','"+context.user_data['DC_LENGTH']+"','"+context.user_data['QR_CODE_MIGRATE']+"','"+context.user_data['SN_ONT']+"','"+context.user_data['SN_STB']+"','"+context.user_data['TECHNICIAN_NAME']+"','"+context.user_data['MITRA']+"','"+context.user_data['TAG_ODP_MIGRATE']+"','"+context.user_data['CUSTOMER_COORDINATE']+"',NULL,1,1,'"+context.user_data['NO_HP']+"') "
	print (sql)
	cursor = db_conn.query(sql)
	db_conn.comit()

	update.message.reply_text("Data \n" "{}".format(list_data(context.user_data)))
	update.message.reply_text("Terimakasih Data Telah Tersimpan", reply_markup=ReplyKeyboardRemove())
	return ConversationHandler.END 

def cancel(update, context):
	user = update.message.from_user
	logger.info("User %s canceled the conversation.", user.first_name)
	update.message.reply_text('ヽ(^o^)丿Bye! aku harap kita dapat berbicara dilain waktu. Terimakasih!(๑˃̵ᴗ˂̵)ﻭ.',reply_markup=ReplyKeyboardRemove())

	return ConversationHandler.END

def error(update, context):
	"""Log Errors caused by Updates."""
	logger.warning('Update "%s" caused error "%s"', update, context.error)

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

	omset_handler = ConversationHandler(
		entry_points=[CommandHandler('omset', start_omset)],

		states={
			#omset
			CEK_IN_OMSET:[MessageHandler(Filters.text, cek_in_omset)],
			OLD_PORT: [MessageHandler(Filters.text, old_port)],
			NEW_PORT: [MessageHandler(Filters.text, new_port)],
			OLD_ODP: [MessageHandler(Filters.text, oldp_odp)],
			NEW_ODP: [MessageHandler(Filters.text, new_odp)],
			NO_INTERNET: [MessageHandler(Filters.text, no_internet)],
			NO_TELP: [MessageHandler(Filters.text, no_telp)],
			QRCODE_DROPCORE: [MessageHandler(Filters.text, qrcode_dropcore)],
		},

		fallbacks=[CommandHandler('cancel', cancel)]
	)

	migrate_handler = ConversationHandler(
		entry_points=[CommandHandler('migrate', start_migrate)],

		states={
			#migrate
			CEK_SC_MIGRATE: [MessageHandler(Filters.text, cek_sc_migrate)],
			CEK_IN_MIGRATE: [MessageHandler(Filters.text, cek_in_migrate)],
			NO_INET_MIGRATE: [MessageHandler(Filters.text, no_inet_migrate)],
			NO_TELP_MIGRATE: [MessageHandler(Filters.text, no_telp_migrate)],
			CUSTOMER_NAME: [MessageHandler(Filters.text, customer_name)],
			CUSTOMER_ADDRESS: [MessageHandler(Filters.text, customer_address)],
			NO_HP: [MessageHandler(Filters.text, no_hp)],
			CEK_STO_MIGRATE: [MessageHandler(Filters.text, cek_sto_migrate)],
			ODP_MIGRATE: [MessageHandler(Filters.text, odp_migrate)],
			PORT: [MessageHandler(Filters.text, port)],
			DC_LENGTH: [MessageHandler(Filters.text, dc_length)],
			QR_CODE_MIGRATE: [MessageHandler(Filters.text, qr_code_migrate)],
			SN_ONT: [MessageHandler(Filters.text, sn_ont)],
			SN_STB: [MessageHandler(Filters.text, sn_stb)],
			TECHNICIAN_NAME: [MessageHandler(Filters.text, technician_name)],
			MITRA: [MessageHandler(Filters.text, mitra)],
			TAG_ODP_MIGRATE: [MessageHandler(Filters.location, tag_odp_migrate)],
			CUSTOMER_COORDINATE: [MessageHandler(Filters.location, customer_coordinate)],
			CONFIRM_MIGRATE: [RegexHandler('^(IYA|TIDAK)$', confirm_migrate)],

		},

		fallbacks=[CommandHandler('cancel', cancel)]
	)

	return expand_handler,omset_handler,migrate_handler
