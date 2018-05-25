import sqlite3
conn = sqlite3.connect('proton.db')
c = conn.cursor()

usr = input("Enter username: ")
pwd = input("Enter password: ")
fn = input("Enter Full Name: ")
lvl = input("Enter Clearance Level (1-99): ")
other = input("Enter other (if applicable): ")
if other == "":
    other = "N/A"

c.execute("INSERT INTO userdata VALUES ('"+usr+"','"+pwd+"','"+fn+"',"+str(lvl)+",'"+other+"')")

conn.commit()
conn.close()
