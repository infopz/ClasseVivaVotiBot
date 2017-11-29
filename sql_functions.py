import sqlite3

# TODO: try except

def get_user_list():
    conn = sqlite3.connect('voti.db')
    with conn:
        cur = conn.cursor()
        cur.execute('SELECT * FROM Utenti WHERE Status=""')
        return cur.fetchall()


def get_old_grades(telegramID):
    conn = sqlite3.connect('voti.db')
    with conn:
        cur = conn.cursor()
        cur.execute('SELECT * FROM Voti WHERE user=?', (telegramID,))
        return cur.fetchall()


def check_user(telegramID):
    conn = sqlite3.connect('voti.db')
    with conn:
        cur = conn.cursor()
        cur.execute('SELECT * FROM Utenti WHERE TelegramID=?', (telegramID,))
        return cur.fetchall()


def change_status(new_status, telegramID):
    conn = sqlite3.connect('voti.db')
    with conn:
        cur = conn.cursor()
        cur.execute('UPDATE Utenti SET Status=? WHERE TelegramID=?', (new_status, telegramID))


def register_user(telegramID, status):
    conn = sqlite3.connect('voti.db')
    with conn:
        cur = conn.cursor()
        cur.execute('INSERT INTO Utenti (TelegramID, Status) VALUES (?, ?)', (telegramID, status))


def register_username(telegramID, username):
    conn = sqlite3.connect('voti.db')
    with conn:
        cur = conn.cursor()
        cur.execute('UPDATE Utenti SET Username=? WHERE TelegramID=?', (username, telegramID))


def register_password(telegramID, password):
    conn = sqlite3.connect('voti.db')
    with conn:
        cur = conn.cursor()
        cur.execute('UPDATE Utenti SET Password=? WHERE TelegramID=?', (password, telegramID))


def register_vote(telegramID, gradesID, value, subject, date):
    conn = sqlite3.connect('voti.db')
    with conn:
        cur = conn.cursor()
        cur.execute('INSERT INTO Voti (user, gradesID, value, subject, date) VALUES (?, ?, ?, ?, ?)', (telegramID, gradesID, value, subject, date))
