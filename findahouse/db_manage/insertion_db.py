# coding: utf8
import mysql.connector
from mysql.connector import errorcode
from exploitation_source import extraction_geofla_commune, extraction_poste,\
        extraction_csv_communes_france, extraction_geofla_departement,\
        extraction_csv_departement

config = {'user': 'tipi',
          'password': 'tipi'}

DB_NAME = "geodata"

# Connexion a MySQL
cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()
cnx.database = DB_NAME

# Ajout commune(donnee) a communes(db)
ajout_commune = ("INSERT INTO communes("
              "  insee_com, nom_com_maj, nom_com_min, status, x_chf_lieu,"
              "  y_chf_lieu, x_centroid, y_centroid, z_min, z_moyen, z_max, superficie,"
              "  population, code_arr, code_dep, code_reg, code_postal," 
              "  limite_com) "
              "  VALUES (%(insee_com)s, %(nom_com_maj)s, %(nom_com_min)s,"
              "  %(status)s, %(x_chf_lieu)s, %(y_chf_lieu)s, %(x_centroid)s,"
              "  %(y_centroid)s, %(z_min)s, %(z_moyen)s, %(z_max)s, %(superficie)s, %(population)s,"
              "  %(code_arr)s, %(code_dep)s, %(code_reg)s, %(code_postal)s,"
              "  %(limite_com)s)")

# Ajout departement(donnee) a departement(db)
ajout_departement = ("INSERT INTO departements("
              "  code_dep, nom_dep_maj, nom_dep_min, numero_insee_prefecture,"
              "  x_centroid, y_centroid, code_reg, limite_dep) "
              "  VALUES (%(code_dep)s, %(nom_dep_maj)s, %(nom_dep_min)s,"
              "  %(numero_insee_prefecture)s, %(x_centroid)s, %(y_centroid)s,"
              "  %(code_reg)s, %(limite_dep)s)")

# Insertion des donnees communes geofla
communes = extraction_geofla_commune('../data/COMMUNE/COMMUNE')
for ind, commune in enumerate(communes):
    try :
        cursor.execute(ajout_commune, commune)
    except :
        print(ind)
        print(commune)
        cursor.execute(ajout_commune, commune)
        break
cnx.commit()

# Insertion des donnees departement geofla
departements = extraction_geofla_departement('../data/DEPARTEMENT/DEPARTEMENT')
for ind, dep in enumerate(departements):
    try :
        #print("Ok")
        #print(dep)
        cursor.execute(ajout_departement, dep)
    except :
        print("Nok")
        print(dep["nom_dep_min"])
        cursor.execute(ajout_departement, dep)
        break
cnx.commit()

# Insertion du code postal
codes_postaux = extraction_poste('../data/POSTE/laposte_hexasmal')
modification_commune = ("UPDATE communes "
                     "  SET code_postal = %s "
                     "  WHERE insee_com = %s;")
for code_postal in codes_postaux:
    cursor.execute(modification_commune, (code_postal[2], code_postal[0]))
cnx.commit()

# Insertion du nom accentue des COMMUNES et de l'altitude min et max
communes_info_suplementaires = extraction_csv_communes_france('../data/villes_france.csv')
for commune in communes_info_suplementaires:
    if commune[25] == "NULL":
        modification_commune = ("UPDATE communes "
                     "  SET nom_com_min = %s "
                     "  WHERE insee_com = %s;")
        cursor.execute(modification_commune, (commune[5], commune[10]))
    else :
        modification_commune = ("UPDATE communes "
                     "  SET nom_com_min = %s , z_min = %s, z_max = %s "
                     "  WHERE insee_com = %s;")
        cursor.execute(modification_commune, (commune[5], int(commune[25]),\
                   int(commune[26]), commune[10]))
cnx.commit()

# Insertion du nom accenute des DEPARTEMENTS
departements_info_suplementaires = extraction_csv_departement('../data/departement.csv')
for departement in departements_info_suplementaires:
    modification_departement = ("UPDATE departements "
            " SET nom_dep_min = %s "
            " WHERE code_dep = %s;")
    cursor.execute(modification_departement, (departement[2], departement[1]))
cnx.commit()

# Deconnexion a MySQL
cursor.close()
cnx.close()



