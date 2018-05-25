import sqlite3
conn = sqlite3.connect('proton.db')
c = conn.cursor()

c.execute('''CREATE TABLE userdata
             (username text, password text, fullname text, lvl integer, other text)''')

c.execute('''CREATE TABLE modules
             (id integer, name text, type text, page integer)''')

conn.commit()
conn.close()