import logging
import requests
import json
import os
import psb_sales_conn

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

global pathmedia

regex_odp = r"^((ODP|OTB|GCL)-\D{3}-((\D{2,4}|\d{2,3}|\D\d{2,3})\/\d{1,3}|\d{2,3})|NO LABEL|TANPA TUTUP)"
regex_port = r"^(\d{,2}.\d{,2}|\d{,2})"

regex_dc = r"^(\d{1,4})"





logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)

logger = logging.getLogger(__name__)

EXPAND, SC, IN, STO, ODP, OLD_CAPACITY, NEW_CAPACITY, ODP_COORDINATE, QRCODE_PORT,\
PORT_EXPAND, OLD_PORT, NEW_PORT, OLD_ODP, NEW_ODP, NO_INTERNET, NO_TELP, OMSET, MIGRATE, CUSTOMER_NAME, CUSTOMER_ADDRESS, \
NO_HP, PORT, DC, SN_ONT, SN_STB, TECHNICIAN_NAME, MITRA, CUSTOMER_COORDINATE, INPUT_SC, SC_NUMBER, IN_NUMBER, \
CONFIRM, CEK_STO, ODP_REAL, LOCATION, CEK_IN_OMSET, CEK_SC_MIGRATE, CEK_IN_OMSET, CEK_IN_MIGRATE, \
TAG_ODP_MIGRATE, DC_LENGTH, QR_CODE_MIGRATE, QRCODE_DROPCORE, NO_INET_MIGRATE, NO_TELP_MIGRATE, ODP_MIGRATE, CONFIRM_MIGRATE, CEK_STO_MIGRATE, \
CEK_SC_PSB, CHECK_MYIR, CONFIRM_PSB, ODP_PSB, PORT_PSB, DC_PSB, QR_CODE_PSB, ONT_PSB, STB_PSB, TAG_ODP_PSB, TAG_PELANGGAN_PSB, \
RUMAH_PELANGGAN, FOTO_PETUGAS_PELANGGAN, FOTO_PETUGAS_LAYANAN, HASIL_REDAMAN, PERANGKAT_ONTSTB, FOTO_ODP, CHECK_MYIR, CONFIRM_SALES, \
SALES_RUMAH_PELANGGAN, SALES_LOKASI_PELANGGAN, PSB, MYIR = range(71)


def start(update, context):
	global tanggal, pathmedia
	today = date.today()
	tanggal = today.strftime("%Y-%m-%d")
	global path
	pathmedia = "../valdat_web/media/evidence/"+tanggal
	try:
		os.makedirs(pathmedia)
	except OSError:
		print("directory sudah ada %s " % pathmedia)
	else:
		print("Successfully created the directory %s" % pathmedia)
	   
	reply_keyboard = [['EXPAND', 'OMSET', 'MIGRATE', 'PSB', 'MYIR']]
	update.message.reply_text(
		 'Hi!ヽ(^o^)丿 Aku adalah valdat bot. '
		 'Ketik /cancel untuk berhenti .\n\n',
	reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
	
	return INPUT_SC 

def input_sc(update, context): 
	pilihan = update.message.text
	if "EXPAND" == pilihan:
		update.message.reply_text(
			'Masukkan nomor SC.\n\n',
			reply_markup=ReplyKeyboardRemove())
		return SC_NUMBER
	elif "OMSET" == pilihan:
		update.message.reply_text(
			'Masukkan nomor IN.\n\n',
			reply_markup=ReplyKeyboardRemove())
		return CEK_IN_OMSET
	elif "MIGRATE" == pilihan:
		update.message.reply_text(
			'Masukkan nomor SC.\n\n',
			reply_markup=ReplyKeyboardRemove())
		return CEK_SC_MIGRATE
	elif "PSB" == pilihan:
		update.message.reply_text(
			'Masukkan nomor SC.\n\n',
			reply_markup=ReplyKeyboardRemove())
		return CEK_SC_PSB
	else :
		update.message.reply_text(
			'Masukkan Nomor Myir\n\n',
			reply_markup=ReplyKeyboardRemove())
		return CHECK_MYIR


#expand
def sc_number(update, context):

	global data
	reply_keyboard = [['IYA', 'TIDAK']]
	data = {}
	text = update.message.text

	data_ = str(get_sc(text).text)
	json_ = json.loads(data_)

	if len(json_['data']) == 0:
		update.message.reply_text('Nomor SC tidak ditemukan, Masukkan nomor SC lagi :', reply_markup=ReplyKeyboardRemove())
		return SC_NUMBER

	data_json = json_['data'][0]
	data['No. SC'] = data_json['ORDER_ID']
	data['No INET'] = "-" if data_json['SPEEDY'] is None else data_json['SPEEDY'].split('~')[1]
	data['No TELP'] = data_json['PHONE_NO']
	data['PELANGGAN'] = data_json['CUSTOMER_NAME']
	data['ALAMAT'] = data_json['CUSTOMER_ADDR']
	data['STO'] = data_json['XS2']
	data['ODP WO'] = data_json['LOC_ID']

	update.message.reply_text("Data \n" "{}".format(list_data(data)))
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
	global data
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
	global data
	user = update.message.from_user
	data['IN_NUMBER'] = update.message.text
	
	update.message.reply_text("Masukkan data STO :", reply_markup=ReplyKeyboardRemove())

	return CEK_STO

def cek_sto(update, context):
	global data
	user = update.message.from_user
	data['CEK_STO'] = update.message.text
	
	update.message.reply_text("Masukkan data ODP  :", reply_markup=ReplyKeyboardRemove())

	return ODP_REAL

def odp_real(update, context):
	global data, regex_odp
	user = update.message.from_user
	data['ODP_REAL'] =update.message.text

	matches = re.search(regex_odp, update.message.text, re.IGNORECASE)
	if matches:
		update.message.reply_text("Masukkan data kapasitas lama :", reply_markup=ReplyKeyboardRemove())
		return OLD_CAPACITY
	else:
		update.message.reply_text("Format ODP salah silahkan masukkan lagi \nFormat ODP yang benar (ODP-TUR-FA/01) \nJika No Label ditutup ditulis NO LABEL "
								"\n Jika tanpa tutup ditulis TANPA TUTUP", reply_markup=ReplyKeyboardRemove())
		return ODP_REAL

def old_capacity(update, context):
	global data
	user = update.message.from_user
	data['OLD_CAPACITY'] = update.message.text

	update.message.reply_text("Masukkan data kapasitas baru :", reply_markup=ReplyKeyboardRemove())

	return NEW_CAPACITY

def new_capacity(update, context):
	global data
	user = update.message.from_user
	data['NEW_CAPACITY'] = update.message.text

	update.message.reply_text("Masukkan data tag ODP :", reply_markup=ReplyKeyboardRemove())

	return ODP_COORDINATE

def odp_coordinate(update, context):
	global data 
	user = update.message.from_user
	user_location = update.message.location
	location = str(user_location.latitude) + ", " + str(user_location.longitude)
	data['ODP_COORDINATE'] = location

	update.message.reply_text("Masukkan data QR CODE :", reply_markup=ReplyKeyboardRemove())

	return QRCODE_PORT

def qrcode_port(update, context):
	global data
	user = update.message.from_user
	data['QRCODE_PORT'] =update.message.text

	update.message.reply_text("Masukkan data jumlah PORT expand :", reply_markup=ReplyKeyboardRemove())

	return PORT_EXPAND

def port_expand(update, context):
	global data
	user = update.message.from_user
	data['PORT_EXPAND'] = update.message.text
	sql = " insert into valdat_expand values (NULL,NULL,NULL,'"+data['CEK_STO']+"','"+data['ODP_REAL']+"','"+data['No. SC']+"','"+data['IN_NUMBER']+"','"+data['OLD_CAPACITY']+"','"+data['NEW_CAPACITY']+"','"+data['ODP_COORDINATE']+"',1,1,'"+data['QRCODE_PORT']+"',1,NULL,NULL,1,'"+data['PORT_EXPAND']+"')"
	print (sql)
	cursor = psb_sales_conn.query(sql)
	psb_sales_conn.comit()

	data['SC_NUMBER'] = "✔"
	data['IN_NUMBER'] = "✔"
	data['CEK_STO'] = "✔"
	data['ODP_REAL'] = "✔"
	data['OLD_CAPACITY'] = "✔"
	data['NEW_CAPACITY'] = "✔"
	data['ODP_COORDINATE'] = "✔"
	data['QRCODE_PORT'] = "✔"
	data['PORT_EXPAND'] = "✔"

	update.message.reply_text("Data \n" "{}".format(list_data(data)))
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
	#global data
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

def list_data_omset(data):
	facts = list()
	for key, value in data.items():
		facts.append("{} : {}".format(key, value))

	return  "\n".join(facts).join(['\n', '\n'])

def qrcode_dropcore(update, context):

	user = update.message.from_user
	context.user_data['QRCODE_DROPCORE'] = update.message.text
	sql = " insert into valdat_omset values (NULL,1,1,'"+context.user_data['CEK_IN_OMSET']+"','"+context.user_data['OLD_PORT']+"','"+context.user_data['NEW_PORT']+"','"+context.user_data['OLD_ODP']+"','"+context.user_data['NEW_ODP']+"','"+context.user_data['NO_TELP']+"','"+context.user_data['NO_INTERNET']+"','"+context.user_data['QRCODE_DROPCORE']+"',1,NULL,NULL,1)"
	print (sql)
	cursor = psb_sales_conn.query(sql)
	psb_sales_conn.comit()

	context.user_data['CEK_IN_OMSET'] = "✔"
	context.user_data['OLD_PORT'] = "✔"
	context.user_data['NEW_PORT'] = "✔"
	context.user_data['OLD_ODP'] = "✔"
	context.user_data['NEW_ODP'] = "✔"
	context.user_data['NO_INTERNET'] = "✔"
	context.user_data['NO_TELP'] = "✔" 
	context.user_data['QRCODE_DROPCORE'] = "✔"

	update.message.reply_text("Data \n" "{}".format(list_data_omset(context.user_data)))
	update.message.reply_text("Terimakasih Data Telah Tersimpan", reply_markup=ReplyKeyboardRemove())

	
	return ConversationHandler.END 




# migrate conversation
def cek_sc_migrate(update, context):
	global data
	
	reply_keyboard = [['IYA', 'TIDAK']]
	data = {}
	text = update.message.text

	data_ = str(get_sc_migrate(text).text)
	json_ = json.loads(data_)


	if len(json_['data']) == 0:
		update.message.reply_text('Nomor SC tidak ditemukan, Masukkan nomor SC lagi :', reply_markup=ReplyKeyboardRemove())
		return CEK_SC_MIGRATE

	data_json = json_['data'][0]
	data['No. SC'] = data_json['ORDER_ID']
	data['No INET'] = "-" if data_json['SPEEDY'] is None else data_json['SPEEDY'].split('~')[1]
	data['No TELP'] = data_json['PHONE_NO']
	data['PELANGGAN'] = data_json['CUSTOMER_NAME']
	data['ALAMAT'] = data_json['CUSTOMER_ADDR']
	data['STO'] = data_json['XS2']
	data['ODP WO'] = data_json['LOC_ID']

	update.message.reply_text("Data \n" "{}".format(list_data_migrate(data)))
	update.message.reply_text("Apakah data ini yang dimaksud ?",reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

	return CONFIRM_MIGRATE

def get_sc_migrate(sc):
	url = "https://starclick.telkom.co.id/backend/public/api/tracking?_dc=1533002388191&ScNoss=true&Field=ORDER_ID&SearchText=" + sc
	return requests.get(url)

def list_data_migrate(data):
	facts = list()
	for key, value in data.items():
		facts.append("{} : {}".format(key, value))

	return  "\n".join(facts).join(['\n', '\n'])

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
	sql = " insert into valdat_migrate values (NULL,'"+data['No. SC']+"','"+context.user_data['CEK_IN_MIGRATE']+"','"+context.user_data['NO_TELP_MIGRATE']+"','"+context.user_data['NO_INET_MIGRATE']+"','"+context.user_data['CUSTOMER_NAME']+"','"+context.user_data['CUSTOMER_ADDRESS']+"','"+context.user_data['CEK_STO_MIGRATE']+"','"+context.user_data['ODP_MIGRATE']+"','"+context.user_data['PORT']+"','"+context.user_data['DC_LENGTH']+"','"+context.user_data['QR_CODE_MIGRATE']+"','"+context.user_data['SN_ONT']+"','"+context.user_data['SN_STB']+"','"+context.user_data['TECHNICIAN_NAME']+"','"+context.user_data['MITRA']+"','"+context.user_data['TAG_ODP_MIGRATE']+"','"+context.user_data['CUSTOMER_COORDINATE']+"',NULL,1,1,'"+context.user_data['NO_HP']+"') "
	print (sql)
	cursor = psb_sales_conn.query(sql)
	psb_sales_conn.comit()

	context.user_data['CEK_SC_MIGRATE'] = "✔"
	context.user_data['CEK_IN_MIGRATE'] = "✔"
	context.user_data['NO_INET_MIGRATE'] = "✔"
	context.user_data['NO_TELP_MIGRATE'] = "✔"
	context.user_data['CUSTOMER_NAME'] = "✔"
	context.user_data['CUSTOMER_ADDRESS'] = "✔"
	context.user_data['NO_HP'] = "✔"
	context.user_data['CEK_STO_MIGRATE'] = "✔"
	context.user_data['ODP_MIGRATE'] = "✔"
	context.user_data['PORT'] = "✔"
	context.user_data['DC_LENGTH'] = "✔"
	context.user_data['QR_CODE_MIGRATE'] = "✔"
	context.user_data['SN_ONT'] = "✔"
	context.user_data['SN_STB'] = "✔"
	context.user_data['TECHNICIAN_NAME'] = "✔"
	context.user_data['MITRA'] = "✔"
	context.user_data['TAG_ODP_MIGRATE'] = "✔"
	context.user_data['CUSTOMER_COORDINATE'] = "✔"


	update.message.reply_text("Data \n" "{}".format(list_data_migrate(context.user_data)))
	update.message.reply_text("Terimakasih Data Telah Tersimpan", reply_markup=ReplyKeyboardRemove())

	


	return ConversationHandler.END 





#PSB
def cek_sc_psb(update, context):

	global data
	reply_keyboard = [['IYA', 'TIDAK']]
	data = {}
	text = update.message.text

	data_ = str(get_sc(text).text)
	json_ = json.loads(data_)
	# print(data_)
	if len(json_['data']) == 0:
		update.message.reply_text('Nomor SC tidak ditemukan, Masukkan Nomor SC lagi :',reply_markup=ReplyKeyboardRemove())
		return CEK_SC_PSB

	data_json = json_['data'][0]
	data['No. SC'] = data_json['ORDER_ID']
	data['No INET'] = "-" if data_json['SPEEDY'] is None else data_json['SPEEDY'].split('~')[1]
	data['No TELP'] = data_json['PHONE_NO']
	data['PELANGGAN'] = data_json['CUSTOMER_NAME']
	data['ALAMAT'] = data_json['CUSTOMER_ADDR']
	data['STO'] = data_json['XS2']
	data['ODP WO'] = data_json['LOC_ID']

	update.message.reply_text("Data \n" "{}".format(list_data_psb(data)))
	update.message.reply_text("Apakah data ini benar ?",reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

	return CONFIRM_PSB

def get_sc(sc):
	url = "https://starclick.telkom.co.id/backend/public/api/tracking?_dc=1533002388191&ScNoss=true&Field=ORDER_ID&SearchText=" + sc
	return requests.get(url)

def list_data_psb(data):
	facts = list()
	for key, value in data.items():
		facts.append("{} : {}".format(key, value))

	return  "\n".join(facts).join(['\n', '\n'])

def confirm_psb(update,context):
	global data
	reply_keyboard = [['INPUT_DATA']]
	user = update.message.from_user
	text = str(update.message.text)
	print(update.message.text)
	if "IYA" == text:

		update.message.reply_text("Masukkan data ODP REAL :", reply_markup=ReplyKeyboardRemove())
		return ODP_PSB

	else :
		update.message.reply_text(
			'Masukkan nomor SC.\n\n',
			reply_markup=ReplyKeyboardRemove())
		return CEK_SC_PSB

def odp_psb(update, context):
	global data, regex_odp
	user = update.message.from_user
	data['ODP_PSB'] = update.message.text

	matches = re.search(regex_odp, update.message.text, re.IGNORECASE)
	if matches:
		update.message.reply_text("Masukkan data PORT :", reply_markup=ReplyKeyboardRemove())
		return PORT_PSB
	else:
		update.message.reply_text("Format odp salah silahkan masukkan lagi \nFormat ODP yang benar (ODP-TUR-FA/01) \nJika No label ditulis NO LABEL "
								  "\nJika tanpa tutup ditulis TANPA TUTUP", reply_markup=ReplyKeyboardRemove())
		return ODP_PSB

def port_psb(update, context):
	global data, regex_port
	user = update.message.from_user
	data['PORT_PSB'] = update.message.text
	matches = re.search(regex_port, update.message.text, re.IGNORECASE)

	if matches:
		update.message.reply_text("Masukkan data DC :",reply_markup=ReplyKeyboardRemove())
		return DC_PSB
	else:
		update.message.reply_text("Format DC salah silahkan masukkan lagi. \nFormat Port yang benar berupa angka. \n ", reply_markup=ReplyKeyboardRemove())
		return PORT_PSB

def dc_psb(update, context):
	global data
	global regex_dc
	user = update.message.from_user
	data['DC_PSB'] = update.message.text

	matches = re.search(regex_dc, update.message.text, re.IGNORECASE)

	if matches:
		update.message.reply_text("Masukkan data QR Code :",reply_markup=ReplyKeyboardRemove())
		return QR_CODE_PSB
	else :
		update.message.reply_text("Format dc salah silahkan masukkan lagi. \nFormat dc yang benar berupa angka. \n ", reply_markup=ReplyKeyboardRemove())
		return DC_PSB

def qr_code_psb(update, context):
	global data
	user = update.message.from_user
	data['QR_CODE_PSB'] = update.message.text

	update.message.reply_text("Masukkan data SN ONT :",reply_markup=ReplyKeyboardRemove())

	return ONT_PSB

def ont_psb(update, context):
	global data
	user = update.message.from_user
	data['ONT_PSB'] = update.message.text
	update.message.reply_text("Masukkan data SN STB :",reply_markup=ReplyKeyboardRemove())
	return STB_PSB

def stb_psb(update, context):
	global data
	user = update.message.from_user
	data['STB_PSB'] = update.message.text
	update.message.reply_text("Masukkan data tag ODP :",reply_markup=ReplyKeyboardRemove())
	return TAG_ODP_PSB

def tag_odp_psb(update, context):
	global data
	user = update.message.from_user
	user_location = update.message.location
	location = str(user_location.latitude) + ", " + str(user_location.longitude)
	data['TAG_ODP_PSB'] = location

	update.message.reply_text("Masukkan data tag pelanggan :",reply_markup=ReplyKeyboardRemove())
	return TAG_PELANGGAN_PSB

def tag_pelanggan_psb(update, context):
	global data
	user = update.message.from_user
	user_location = update.message.location
	location = str(user_location.latitude) + ", " + str(user_location.longitude)
	data['TAG_PELANGGAN_PSB'] = location
	psb_sales_conn.connect()
	sql = " insert into valdat_psb values (NULL,NULL,'"+data['No. SC']+"',NULL,NULL,'"+data['No TELP']+"','"+data['No INET']+"',NULL,'"+data['PELANGGAN']+"','"+data['ALAMAT']+"',NULL,'"+data['STO']+"','"+data['ODP WO']+"','"+data['ODP_PSB']+"','"+data['PORT_PSB']+"','"+data['DC_PSB']+"','"+data['QR_CODE_PSB']+"','"+data['ONT_PSB']+"','"+data['STB_PSB']+"','"+data['TAG_ODP_PSB']+"','"+data['TAG_PELANGGAN_PSB']+"',NULL,NULL,NULL,NULL,NULL,NULL,NULL) "
	print (sql)
	cursor = psb_sales_conn.query(sql)
	psb_sales_conn.comit()

	update.message.reply_text("Masukkan foto rumah pelanggan :", reply_markup=ReplyKeyboardRemove())
	return RUMAH_PELANGGAN

def rumah_pelanggan(update, context):
	global data, pathmedia
	user = update.message.from_user
	photo_file = update.message.photo[-1].get_file()
	path = pathmedia+'/psb_{}_rumah_pelanggan.jpg'.format(data['No. SC'])
	photo_file.download(path)
	data['RUMAH_PELANGGAN'] = path
	update.message.reply_text("Masukkan foto petugas dengan pelanggan :", reply_markup=ReplyKeyboardRemove())
	return FOTO_PETUGAS_PELANGGAN

def foto_petugas_pelanggan(update, context):
	global pathmedia
	user = update.message.from_user
	photo_file = update.message.photo[-1].get_file()
	path = pathmedia+'/psb_{}_petugas-dengan-pelanggan.jpg'.format(data['No. SC'])
	photo_file.download(path)
	data['FOTO_PETUGAS_PELANGGAN'] = path
	update.message.reply_text("Masukkan foto petugas layanan :", reply_markup=ReplyKeyboardRemove())
	return FOTO_PETUGAS_LAYANAN

def foto_petugas_layanan(update, context):
	global pathmedia
	user = update.message.from_user
	photo_file = update.message.photo[-1].get_file()
	path = pathmedia+'/psb_{}_petugas-dengan-layanan.jpg'.format(data['No. SC'])
	photo_file.download(path)
	data['FOTO_PETUGAS_LAYANAN'] = path
	update.message.reply_text("Masukkan foto redaman :", reply_markup=ReplyKeyboardRemove())
	return HASIL_REDAMAN

def hasil_redaman(update, context):
	global pathmedia
	user = update.message.from_user
	photo_file = update.message.photo[-1].get_file()
	path = pathmedia+'/psb_{}_hasil-redaman.jpg'.format(data['No. SC'])
	photo_file.download(path)
	data['HASIL_REDAMAN'] = path
	update.message.reply_text("Masukkan foto ont/stb :", reply_markup=ReplyKeyboardRemove())
	return PERANGKAT_ONTSTB

def perangkat_ontstb(update, context):
	global pathmedia
	user = update.message.from_user
	photo_file = update.message.photo[-1].get_file()
	path = pathmedia+'/psb_{}_perangkat-ontstb.jpg'.format(data['No. SC'])
	photo_file.download(path)
	data['PERANGKAT_ONTSTB'] = path
	update.message.reply_text("Masukkan foto odp :", reply_markup=ReplyKeyboardRemove())
	return FOTO_ODP

def foto_odp(update, context):
	global pathmedia
	user = update.message.from_user
	photo_file = update.message.photo[-1].get_file()
	path = pathmedia+'/psb_{}_foto-odp.jpg'.format(data['No. SC'])
	photo_file.download(path)
	data['FOTO_ODP'] = path

	data['RUMAH_PELANGGAN'] = " ✔️ "
	data['FOTO_PETUGAS_PELANGGAN'] = " ✔️ "
	data['FOTO_PETUGAS_LAYANAN'] = " ✔️ "
	data['HASIL_REDAMAN'] = " ✔️ "
	data['PERANGKAT_ONTSTB'] = " ✔️ "
	data['FOTO_ODP'] = " ✔️ "

	update.message.reply_text("Data \n" "{}".format(list_data_psb(data)))
	update.message.reply_text("Terimakasih Data Telah Tersimpan", reply_markup=ReplyKeyboardRemove())

	#save kombinasi
	list_im1 = ([pathmedia+'/psb_{}_rumah_pelanggan.jpg'.format(data['No. SC']),pathmedia+'/psb_{}_petugas-dengan-pelanggan.jpg'.format(data['No. SC']), pathmedia+'/psb_{}_petugas-dengan-layanan.jpg'.format(data['No. SC'])])
	list_im2 = ([pathmedia+'/psb_{}_rumah_pelanggan.jpg'.format(data['No. SC']),pathmedia+'/psb_{}_petugas-dengan-pelanggan.jpg'.format(data['No. SC']), pathmedia+'/psb_{}_petugas-dengan-layanan.jpg'.format(data['No. SC'])])

   # list_im2 = ([pathmedia+'/psb_{}_rumah_pelanggan.jpg'.format(data['No. SC']),pathmedia+'/psb_{}_.jpg'.format(data['No. SC']),pathmedia+'/psb_{}_rumah_pelanggan.jpg'.format(data['No. SC'])])

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
	imgs_comb.save(pathmedia+'/psb_{}_kombinasi.jpg'.format(data['No. SC']),'JPEG')
	#imgs_comb.save('psb__kombinasi.jpg','JPEG')
	#imgs_comb.save('psb__kombinasi.jpg')


	return ConversationHandler.END





#myir
def get_myir(myir):
	url = 'http://api.indihome.co.id/api/track-view'
	headers = {"Content-type": "application/x-www-form-urlencoded",
			   "Authorization": "Basic bXlpbmRpaG9tZTpwN2Qya0xYNGI0TkY1OFZNODR2Vw=="}
	payload = 'guid=myindihome#2017&code=&data={"trackId":"%s"}' % myir

	return requests.post(url, data=payload, headers=headers)

def list_data_myir(data):
	facts = list()
	for key, value in data.items():
		facts.append("{} : {}".format(key, value))

	return  "\n".join(facts).join(['\n', '\n'])

def check_myir(update, context):

	global data
	reply_keyboard = [['IYA', 'TIDAK']]
	data = {}
	text = update.message.text
	data_ = str(get_myir(text).text)
	json_ = json.loads(data_)
	if json_['data'] == None:
		update.message.reply_text('MYIR tidak ditemukan, Masukkan Nomor MYIR lagi :',reply_markup=ReplyKeyboardRemove())
		return CHECK_MYIR

	print(data_)
	data_json = json_['data']
	data['TRACK ID'] = data_json['track_id']
	data['K-CONTACT'] = json_['data']['detail'][0]['x3']
	data['NO SC'] = "-" if data_json['scid'] is None else data_json['scid']
	data['TANGGAL ORDER'] = "-" if data_json['orderDate'] is None else data_json['scid']
	data['STATUS'] = data_json['status_name']
	data['NAMA CUSTOMER'] = data_json['user_name']
	data['PAKET'] = data_json['name']
	data['ALAMAT INSTALASI'] = json_['data']['address']['address']
	data['STO'] = json_['data']['data1']['sto']

	update.message.reply_text("Data \n" "{}".format(list_data_myir(data)))
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
	global pathmedia
	user = update.message.from_user
	photo_file = update.message.photo[-1].get_file()
	path = pathmedia +'/sales_{}_rumah_pelanggan.jpg'.format(data['TRACK ID'])
	photo_file.download(path)
	data['SALES_RUMAH_PELANGGAN'] = path
	update.message.reply_text("Masukkan Tag Lokasi Pelanggan :", reply_markup=ReplyKeyboardRemove())
	return SALES_LOKASI_PELANGGAN

def sales_lokasi_pelanggan(update, context):
	global data, pathmedia
	user = update.message.from_user
	user_location = update.message.location
	location = str(user_location.latitude) + ", " + str(user_location.longitude)
	data['SALES_LOKASI_PELANGGAN'] = location
	
	psb_sales_conn.connect()
	sql = " insert into valdat_sales values (NULL,'"+data['TRACK ID']+"','"+data['K-CONTACT']+"','"+data['NO SC']+"','"+data['TANGGAL ORDER']+"','"+data['STATUS']+"','"+data['NAMA CUSTOMER']+"','"+data['PAKET']+"','"+data['ALAMAT INSTALASI']+"','"+data['STO']+"','"+data['SALES_RUMAH_PELANGGAN']+"','"+data['SALES_LOKASI_PELANGGAN']+"') "
	print(sql)
	cursor = psb_sales_conn.query(sql)
	psb_sales_conn.comit()
	data['SALES_RUMAH_PELANGGAN'] = " ✔️ "
	update.message.reply_text("Data \n" "{}".format(list_data_myir(data)))
	update.message.reply_text("Terimakasih Data Telah Tersimpan", reply_markup=ReplyKeyboardRemove())

	list_im1 = ([pathmedia+'/psb_{}_rumah_pelanggan.jpg'.format(data['NO SC']),pathmedia+'/psb_{}_petugas-dengan-pelanggan.jpg'.format(data['NO SC']), pathmedia+'/psb_{}_petugas-dengan-layanan.jpg'.format(data['NO SC'])])
	list_im2 = ([pathmedia+'/psb_{}_hasil-redaman.jpg'.format(data['NO SC']),pathmedia+'/psb_{}_perangkat-ontstb.jpg'.format(data['NO SC']), pathmedia+'/psb_{}_foto-odp.jpg'.format(data['NO SC'])])

   # list_im2 = ([pathmedia+'/psb_{}_rumah_pelanggan.jpg'.format(data['No. SC']),pathmedia+'/psb_{}_.jpg'.format(data['No. SC']),pathmedia+'/psb_{}_rumah_pelanggan.jpg'.format(data['No. SC'])])

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
	#imgs_comb.save(pathmedia+'/psb_{}_kombinasi.jpg'.format(data['No. SC']),'JPEG')
	imgs_comb.save('psb__kombinasi.jpg','JPEG')
	imgs_comb.save('psb__kombinasi.jpg')



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
	# Create the Updater and pass it your bot's token.
	# Make sure to set use_context=True to use the new context based callbacks
	# Post version 12 this will no longer be necessary
	updater = Updater("981505990:AAHF0w1V92Nc2ioenG7ggi_RRP4L-CVuEqI", use_context=True)

	psb_sales_conn.connect()
	# Get the dispatcher to register handlers
	dp = updater.dispatcher

	# Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
	conv_handler = ConversationHandler(
		entry_points=[CommandHandler('start', start)],

		states={
			#expand
			INPUT_SC:[RegexHandler('^(EXPAND|OMSET|MIGRATE|PSB|MYIR)$', input_sc)],
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

			#omset
			CEK_IN_OMSET:[MessageHandler(Filters.text, cek_in_omset)],
			OLD_PORT: [MessageHandler(Filters.text, old_port)],
			NEW_PORT: [MessageHandler(Filters.text, new_port)],
			OLD_ODP: [MessageHandler(Filters.text, oldp_odp)],
			NEW_ODP: [MessageHandler(Filters.text, new_odp)],
			NO_INTERNET: [MessageHandler(Filters.text, no_internet)],
			NO_TELP: [MessageHandler(Filters.text, no_telp)],
			QRCODE_DROPCORE: [MessageHandler(Filters.text, qrcode_dropcore)],

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

			#psb
			ODP_PSB: [MessageHandler(Filters.text, odp_psb)],
			PORT_PSB: [MessageHandler(Filters.text, port_psb)],
			DC_PSB: [MessageHandler(Filters.text, dc_psb)],
			QR_CODE_PSB: [MessageHandler(Filters.text, qr_code_psb)],
			ONT_PSB: [MessageHandler(Filters.text, ont_psb)],
			STB_PSB: [MessageHandler(Filters.text, stb_psb)],
			TAG_ODP_PSB: [MessageHandler(Filters.location, tag_odp_psb)],
			TAG_PELANGGAN_PSB: [MessageHandler(Filters.location, tag_pelanggan_psb)],
			RUMAH_PELANGGAN: [MessageHandler(Filters.photo, rumah_pelanggan)],
			FOTO_PETUGAS_PELANGGAN: [MessageHandler(Filters.photo, foto_petugas_pelanggan)],
			FOTO_PETUGAS_LAYANAN: [MessageHandler(Filters.photo, foto_petugas_layanan)],
			HASIL_REDAMAN: [MessageHandler(Filters.photo, hasil_redaman)],
			PERANGKAT_ONTSTB: [MessageHandler(Filters.photo, perangkat_ontstb)],
			FOTO_ODP: [MessageHandler(Filters.photo, foto_odp)],
			CEK_SC_PSB: [MessageHandler(Filters.text, cek_sc_psb)],
			CONFIRM_PSB: [RegexHandler('^(IYA|TIDAK)$', confirm_psb)],

			#myir
			CHECK_MYIR : [MessageHandler(Filters.text, check_myir)],
			CONFIRM_SALES: [RegexHandler('^(IYA|TIDAK)$', confirm_sales)],
			SALES_RUMAH_PELANGGAN : [MessageHandler(Filters.photo, sales_rumah_pelanggan)],
			SALES_LOKASI_PELANGGAN : [MessageHandler(Filters.location, sales_lokasi_pelanggan)],

			

		},

		fallbacks=[CommandHandler('cancel', cancel)]
	)

	dp.add_handler(conv_handler)

	# log all errors
	dp.add_error_handler(error)

	# Start the Bot
	updater.start_polling()

	logging.basicConfig(level=logging.DEBUG,
		format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

	# summarize_handler = MessageHandler([Filters.text], summarize)

	# Run the bot until you press Ctrl-C or the process receives SIGINT,
	# SIGTERM or SIGABRT. This should be used most of the time, since
	# start_polling() is non-blocking and will stop the bot gracefully.
	updater.idle()


if __name__ == '__main__':
	main()