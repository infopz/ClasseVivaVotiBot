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
        s0 = classeviva.Session()
        password = triple_des(key.master_key).decrypt(u[2], padmode=2).decode('utf-8')
        s = login(s0, u[1], password)
        old_grades = sql_functions.get_old_grades(u[0])
        old_grades_list = []
        for i in old_grades:
            old_grades_list.append(i[1])
        newgrades = get_grades(s)
        m = "Ehi, hai nuovi voti:\n"
        for g in newgrades:
            if g['evtId'] not in old_grades_list:
                sql_functions.register_vote(u[0], g['evtId'], g['decimalValue'], g['subjectDesc'], g['evtDate'])
                m += f"{g['subjectDesc']}\n*{g['decimalValue']}* - {g['evtDate']}\n"
        if m != "Ehi, hai nuovi voti:\n":
            pzgram.Chat(u[0], bot).send(m)
            print("NEWVOTE "+str(u[0]))
        time.sleep(2)


def write_first_vote(userID, s):
    g = get_grades(s)
    sql_functions.delete_user_grades(userID)
    for i in g:
        sql_functions.register_vote(userID, i['evtId'], i['decimalValue'], i['subjectDesc'], i['evtDate'])

def voti_command(chat, message):
    chat.send("Work in progress")


def login(s, username, password):
   while True:
       try:
           s.login(username, password)
           return s
       except classeviva.AuthenticationFailedError:
           return False
       except Exception:
           print("ClassevivaConnectionError - Retry")
           time.sleep(0.5)

def get_grades(s):
    while True:
        try:
            grades = s.grades()['grades']
            return grades
        except Exception:
            print("ClassevivaConnectionError - Retry")

def start(chat, message):
    print("START from"+message.sender.first_name)
    user = sql_functions.check_user(message.sender.id)
    chat.send("Benvenuto su ClasseVivaVotiBot")
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
    chat.sendAction('typing')
    s0 = classeviva.Session()
    s = login(s0, sql_functions.check_user(message.sender.id)[0][1], message.text)
    if s == False:
        chat.send("I dati di login che hai inserito non sono corretti")
        chat.send("Scrivimi il tuo username/email")
        sql_functions.change_status("start1", message.sender.id)
        return
    password_crypted = triple_des(key.master_key).encrypt(message.text, padmode=2)
    sql_functions.register_password(message.sender.id, password_crypted)
    sql_functions.change_status("", message.sender.id)
    write_first_vote(message.sender.id, s)
    print("REGISTER "+message.sender.first_name)
    chat.send("Ottimo, registrazione completata\n"
              "Ora il bot controllera' se ti arriveranno nuovi voti!\n"
              "Intanto puoi visualizzare quelli che hai adesso usando i comandi qua sotto")


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
