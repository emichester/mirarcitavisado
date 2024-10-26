#!/usr/bin/env python3
from config.data import TOKEN, MI_CHAT_ID, GROUPO_CHAT_ID
from environ import *

import logging
import os
import time
import json
import requests

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, JobQueue)

""" -------- Funciones -------- """

def guarda_linea(path_archivo, log):
    with open(path_archivo, 'at') as f:
        f.write(log + '\n')

def leer_archivo_lista(path_archivo):
    lista=[]
    with open(path_archivo, 'r') as f:
        for i in f:
            lista.append(int(i))
    return lista

def leer_archivo_lista_string(path_archivo):
    lista=[]
    with open(path_archivo, 'rt') as f:
        for i in f:
            lista.append(i)
    return lista

def limpiar_archivo_lista(path_archivo):
    with open(path_archivo, 'wt') as f:
        f.write('')

def escribir_archivo_lista_int(path_archivo, lista):
    with open(path_archivo, 'at') as f:
        for i in lista:
            f.write(str(i) + '\n')

def escribir_archivo_lista(path_archivo, lista):
    with open(path_archivo, 'at') as f:
        for i in lista:
            if i[len(i)-1] == '\n':
                f.write(str(i))
            else:
                f.write(str(i) + '\n')

""" &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& """
""" -------- Manejadores -------- """

def start(update, context):
    reply_keyboard = [['/ayuda', '/estado']]

    reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

    update.message.reply_text(
        'Hola mi nombre es emibot y estoy aquí para ayudar en lo que pueda.\n'
        'Para saber las distintas cosas que puedo hacer por ti usa "/ayuda".\n'
        'De todas formas te dejo este menu rápido para que elijas:',
        reply_markup=reply_markup
        )

    user = update.message.from_user
    logging.info("Opción de %s: %s", user.first_name, update.message.text)

def ayuda(update, context):
    update.message.reply_text(
        'Estos son los comandos que entiendo:\n%s'%'\n'.join(METODOS)
        )
    user = update.message.from_user
    logging.info("Opción de %s: %s", user.first_name, update.message.text)

def buscar(update, context):
    update.message.reply_text(
        'Por el momento estamos trabajando en ello, pronto estará lista esta funcionalidad.'
        )
    user = update.message.from_user
    logging.info("Opción de %s: %s", user.first_name, update.message.text)

def contactar(update, context):
    update.message.reply_text(
        'Aquí tienes varios modos de contactar a Emi:\n'
        'email: emiliohesal@gmail.com\n'
        'telegram: @emichester'
        )
    user = update.message.from_user
    logging.info("Opción de %s: %s", user.first_name, update.message.text)

def contribuir(update, context):
    update.message.reply_text(
        'Por el momento estamos trabajando en ello, pronto estará lista esta funcionalidad.'
        )
    user = update.message.from_user
    logging.info("Opción de %s: %s", user.first_name, update.message.text)

def estado(update, context):
    with open("config/session/shared_file.memory","r") as f:
        text = f.read()
    update.message.reply_text(
        f'El estado actual es: {text}'
        )
    user = update.message.from_user
    logging.info("Opción de %s: %s", user.first_name, update.message.text)

def temperatura_habitacion(update , context):
    user = update.message.from_user
    if update.message.chat_id == MI_CHAT_ID:
        #temp=arduino() # cuando se usa el puerto serie con Arduino
        temp=DHT11() # cuando se usa el módulo DHT11 en los gpio (RPi)
        t=temp.leer()
        update.message.reply_text( t )
    else:
        update.message.reply_text(
            'Ups... esto sólo puede verlo Emi'
            )
    logging.info("Opción de %s: %s", user.first_name, update.message.text)

def decir_temperatura( update , context ):
    user = update.message.from_user
    tl = temp_lector()
    update.message.reply_text(
        'T_cpu = %sºC'%tl.imprimir_temperatura()
        )
    logging.info("Opción de %s: %s", user.first_name, update.message.text)

def apagar( update , context ):
    user = update.message.from_user

    if update.message.chat_id == MI_CHAT_ID:
        os.system('shutdown now')
    else:
        # update.sendMessage(chat_id=MI_CHAT_ID, text='Alguien intenta apagar la raspberry')
        update.message.reply_text(
            'Ups... esto sólo puede verlo Emi'
            )

    logging.warning("Opción de %s: %s ¡Alguien intenta apagar la raspberry!", user.first_name, update.message.text)

def leer_ip_local( update , context ):
    user = update.message.from_user
    if update.message.chat_id == MI_CHAT_ID:
        update.message.reply_text(
            'IP %s'%get_ip()
            )
    else:
        update.message.reply_text(
            'Ups... esto sólo puede verlo Emi'
            )
    logging.warning("Opción de %s: %s", user.first_name, update.message.text)

def renovador( update ):
    logging.debug('\t->Iniciando tarea periódica: renovador')
    fa = time.localtime()[0:6] # fecha actual
    f=leer_archivo_lista(FECHA_PATH)
    if f != []:
        logging.debug('\t->Última fecha de renovado: %s/%s/%s a las %s:%s:%s'%(f[2],f[1],f[0],f[3],f[4],f[5]))
    if (f == [] or (fa[1] != f[1]) or (fa[0] != f[0]) or (int(fa[2]) - int(f[2]) >= 3)):
        logging.debug("\t->Se va a proceder a renovar los libros")
        b = g_bot(True)
        respuesta = b.renovar_libros()[1]
        logging.debug(respuesta)
        b.close()
        limpiar_archivo_lista(FECHA_PATH)
        escribir_archivo_lista_int(FECHA_PATH,fa)
        logging.debug("\t->Fin del proceso de renovado")
    else:
        logging.debug("\t->Libros ya renovados")

def ultima_renovacion( update , context ):
    guarda_linea(LOGS_PATH, '%s: En ultima_renovacion'%update.message.chat_id)
    f=leer_archivo_lista(FECHA_PATH)
    update.message.reply_text( "Se renovaron los libros el %s/%s/%s a las %s:%s:%s"%(f[2],f[1],f[0],f[3],f[4],f[5]) )
    user = update.message.from_user
    logging.info("Opción de %s: %s", user.first_name, update.message.text)

def pronostico( update , context ):
    guarda_linea(LOGS_PATH, '%s: En pronostico'%update.message.chat_id)
    if len(context.args)>1:
        p = Prediccion( dia=context.args[0], municipio=context.args[1])
    else:
        p = Prediccion( dia=context.args[0], municipio='Málaga')
    update.message.reply_text( p.devolver_todo() )
    user = update.message.from_user
    logging.info("Opción de %s: %s", user.first_name, update.message.text)


def mirar_archivo_callback(context):
    logging.debug('\t->Iniciando tarea periódica: mirar_archivo')
    with open("config/session/shared_file.memory","r") as f:
        text = f.read()
    if text.find("Cita disponible") >= 0 or \
       text.find("¡¡Hay algo raro, mirar la web!!") >= 0:
        context.bot.send_message(chat_id=GROUPO_CHAT_ID,text=text)
    else:
        pass


""" &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& """
""" -------- Main -------- """

def main():
    # Cleaning debug info
    with open("debug.log","w") as f:
        f.write("")

    # Enable logging
    logging.basicConfig(filename="debug.log",
        format='%(asctime)s-%(levelname)s-%(message)s',
        level=logging.INFO)
    import sys
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # crear manejadores ------------------------------------------------------
    handlers = [
        CommandHandler('start',start) ,
        CommandHandler('ayuda',ayuda) ,
        CommandHandler('estado',estado) ,
        CommandHandler('buscar',buscar) ,
        CommandHandler('contactar',contactar) ,
        CommandHandler('contribuir',contribuir) ,
        CommandHandler('temp', temperatura_habitacion),
        CommandHandler('tCPU', decir_temperatura),
        CommandHandler('pron', pronostico),
        CommandHandler('apagar', apagar),
        CommandHandler('ipLocal', leer_ip_local),
        CommandHandler( 'renov' , ultima_renovacion )
    ]

    # añadir manejadores
    for h in handlers:
        dp.add_handler(h)

    # --------- Jobs -------------

    #new_job = updater.job_queue.run_repeating(callback=renovador, interval=TIME_INTERVAL_RENOVADOR, first=0)
    #new_job = updater.job_queue.run_repeating(callback=pronostico, interval=TIME_INTERVAL_ENVIAR_TIEMPO, first=0)

    new_job = updater.job_queue.run_repeating(callback=mirar_archivo_callback, interval=30, first=0)

    # ------------------------------------------------------------------------

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.warning("Exiting with code 0 on %s"%str(time.ctime()))
        print("\n")
