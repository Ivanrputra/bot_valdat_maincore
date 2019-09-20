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

OMSET, CEK_IN_OMSET, OLD_PORT, NEW_PORT, OLD_ODP, NEW_ODP, NO_INTERNET, NO_TELP, QRCODE_DROPCORE = range(9)

db_conn.connect()

def start_omset(update, context):
	context.user_data.clear()
	update.message.reply_text(
		 'Hi!ヽ(^o^)丿 Aku adalah valdat bot. '
		 'Ketik /cancel untuk berhenti .\n\n',reply_markup=ReplyKeyboardRemove())	
	update.message.reply_text(
		'Masukkan nomor IN.\n\n',
		reply_markup=ReplyKeyboardRemove())

	return CEK_IN_OMSET

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

	#context.user_data['CEK_IN_OMSET'] = "✔"
	#context.user_data['OLD_PORT'] = "✔"
	#context.user_data['NEW_PORT'] = "✔"
	#context.user_data['OLD_ODP'] = "✔"
	#context.user_data['NEW_ODP'] = "✔"
	#context.user_data['NO_INTERNET'] = "✔"
	#context.user_data['NO_TELP'] = "✔" 
	#context.user_data['QRCODE_DROPCORE'] = "✔"

	update.message.reply_text("Data \n" "{}".format(list_data(context.user_data)))
	update.message.reply_text("Terimakasih Data Telah Tersimpan", reply_markup=ReplyKeyboardRemove())

	
	return ConversationHandler.END 

def cancel(update, context):
	user = update.message.from_user
	logger.info("User %s canceled the conversation.", user.first_name)
	update.message.reply_text('ヽ(^o^)丿Bye! aku harap kita dapat berbicara dilain waktu. Terimakasih!(๑˃̵ᴗ˂̵)ﻭ.',reply_markup=ReplyKeyboardRemove())

	return ConversationHandler.END

def list_data(data):
	facts = list()
	for key, value in data.items():
		facts.append("{} : {}".format(key, value))

	return  "\n".join(facts).join(['\n', '\n'])

def main():
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

	return omset_handler