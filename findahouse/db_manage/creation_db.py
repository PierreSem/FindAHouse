# __future__ import print_function

import mysql.connector
from mysql.connector import errorcode

config = {'user': 'tipi',
          'password': 'tipi'}

DB_NAME = "geodata"
         
TABLES = {}
TABLES['communes'] = (
    "CREATE TABLE communes ("
    "  insee_com CHAR(5) NOT NULL,"
    "  nom_com_maj VARCHAR(50),"
    "  nom_com_min VARCHAR(50),"
    "  status ENUM('capitale', 'prefecture_region', 'prefecture_departement', 'sous-prefecture', 'commune_simple'),"
    "  x_chf_lieu FLOAT,"
    "  y_chf_lieu FLOAT,"
    "  x_centroid FLOAT,"
    "  y_centroid FLOAT,"
    "  z_min SMALLINT,"
    "  z_moyen SMALLINT,"
    "  z_max SMALLINT,"
    "  superficie INT,"
    "  population INT,"
    "  code_arr CHAR(1),"
    "  code_dep CHAR(3),"
    "  code_reg CHAR(2),"
    "  code_postal CHAR(5),"
    "  limite_com JSON,"
    "  PRIMARY KEY (insee_com)"
    ") ENGINE=InnoDB") 
TABLES['departements'] = (
    "  CREATE TABLE departements ("
    "  code_dep CHAR(3) NOT NULL,"
    "  nom_dep_maj VARCHAR(50),"
    "  nom_dep_min VARCHAR(50),"
    "  numero_insee_prefecture CHAR(5), "
    "  x_centroid FLOAT,"
    "  y_centroid FLOAT,"
    "  code_reg CHAR(2),"
    "  limite_dep JSON,"
    "  PRIMARY KEY (code_dep)"
    ") ENGINE=InnoDB")

def create_database(cursor):
    try:
        cursor.execute(
             "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)

# Connexion a MySQL
cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()

# Connexion a la base de donnee
try:
    cnx.database = DB_NAME  
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_BAD_DB_ERROR:
        create_database(cursor)
        cnx.database = DB_NAME
    else:
        print(err)
        exit(1)

#print(TABLES['communes'])

# Creation de l'ensemble des tables
for name, ddl in TABLES.items():
    try:
        print("Creating table {}: ".format(name), end='')
        cursor.execute(ddl)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("OK")

# Deconnexion a MySQL
cursor.close()
cnx.close()

