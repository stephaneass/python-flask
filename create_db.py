import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="stephane",
    password="stephaneP%40ssw0rd",
    auth_plugin='mysql_native_password'  # Ajoutez cette ligne
)

my_cursor = mydb.cursor()

#my_cursor.execute("CREATE DATABASE flaskers")
#mydb.commit()

my_cursor.execute("SHOW DATABASES")

for db in my_cursor:
    print(db)