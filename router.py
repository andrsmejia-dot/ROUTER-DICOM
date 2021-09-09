import os
import sqlite3

# def conection():
#     cmd='python -m pynetdicom qrscp' #uso del dcmtk
#     os.system(cmd)

#conection()

def sql_fetch(con):

    cursorObj = con.cursor()

    cursorObj.execute("SELECT * FROM instance WHERE patient_id='54879843'")

    rows = cursorObj.fetchall()

    for row in rows:

        print(row)

def GetTables(db_file = 'instances.sqlite'):
    try:
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()
        cur.execute("select name from sqlite_master where type='table' order by name")
        print (cur.fetchall())
    except sqlite3.Error:
        print("error")

con = sqlite3.connect ('instances.sqlite')
GetTables()
sql_fetch(con)