import mysql.connector
from mysql.connector import errorcode

config = {'user': 'tipi',
          'password': 'tipi'}

DB_NAME = "geodata"
 
# Connexion a MySQL
cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()

# Suppresion de la base geodata
cursor.execute("DROP DATABASE {};".format(DB_NAME))

# Deconnexion a mysql
cursor.close()
cnx.close()
