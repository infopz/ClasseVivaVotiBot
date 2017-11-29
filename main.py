import classeviva
import time
import pzgram
from pyDes import *

import sql_functions
import key

bot = pzgram.Bot(key.bot_key)


def check_vote():
    users = sql_functions.get_user_list()
    for u in users:
        s = classeviva.Session()
        password = triple_des(key.master_key).decrypt(u[2], padmode=2).decode('utf-8')
        s.login(u[1], password)
        old_grades = sql_functions.get_old_grades(u[0])
        old_grades_list = []
        for i in old_grades:
            old_grades_list.append(i[1])
        newgrades = s.grades()['grades']
        m = "Ehi, hai nuovi voti:\n"
        for g in newgrades:
            if g['evtId'] not in old_grades_list:
                sql_functions.register_vote(u[0], g['evtId'], g['decimalValue'], g['subjectDesc'], g['evtDate'])
                m += f"{g['subjectDesc']}\n*{g['decimalValue']}* - {g['evtDate']}\n"
        if m != "Ehi, hai nuovi voti:\n":
            pzgram.Chat(u[0], bot).send(m)
        time.sleep(2)


def write_first_vote(userID):
    u = sql_functions.check_user(userID)[0]
    s = classeviva.Session()
    password = triple_des(key.master_key).decrypt(u[2], padmode=2).decode('utf-8')
    s.login(u[1], password)
    g = s.grades()['grades']
    for i in g:
        sql_functions.register_vote(userID, i['evtId'], i['decimalValue'], i['subjectDesc'], i['evtDate'])


def start(chat, message):
    user = sql_functions.check_user(message.sender.id)
    chat.send("Benvenuto su NomeBot")
    if user:
        if user[0][1] is None or user[0][2] is None:
            chat.send("Sei gia registrato, ma devi reinserire i dati, inviami il tuo username:")
            sql_functions.change_status('start1', message.sender.id)
        else:
            chat.send("Ti sei gia registrato, ora puoi utilizzare il bot!")
    else:
        sql_functions.register_user(message.sender.id, 'start1')
        chat.send("Ti sei registrato sul database, ora per completare la registrazione inviami il tuo username di ClasseViva")


def start1(chat, message):
    sql_functions.register_username(message.sender.id, message.text)
    chat.send("Username registrato, ora inviami la password")
    sql_functions.change_status('start2', message.sender.id)


def start2(chat, message):
    s = classeviva.Session()
    s.login(sql_functions.check_user(message.sender.id)[0][0], message.text)
    if s.logged_in:
        password_crypted = triple_des(key.master_key).encrypt(message.text, padmode=2)
        sql_functions.register_password(message.sender.id, password_crypted)
        chat.send("Ottimo, registrazione completata\n"
                  "Ora il bot controllera' se ti arriveranno nuovi voti!\n"
                  "Intanto puoi visualizzare quelli che hai adesso usando i comandi qua sotto")
        sql_functions.change_status("", message.sender.id)
        write_first_vote(message.sender.id)
    else:
        chat.send("I dati di login che hai inserito non sono corretti")
        chat.send("Scrivimi il tuo username/email:")
        sql_functions.change_status("start1", message.sender.id)


def check_status(chat, message):
    status = sql_functions.check_user(message.sender.id)[0][3]
    if status == 'start1':
        start1(chat, message)
    elif status == 'start2':
        start2(chat, message)


bot.set_commands({"/start": start})
bot.set_function({"after_division": check_status})
bot.set_timers({60: check_vote})
bot.run()
