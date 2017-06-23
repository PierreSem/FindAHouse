# -*- coding: utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from shapefile import Reader
from pyproj import Proj, transform

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://tipi:tipi@localhost/geodata'

db = SQLAlchemy(app)
lambert_93 = Proj("+init=EPSG:2154")
wgs_84 = Proj("+init=EPSG:4326")

CHG_DB = True

def conversion_lambert93_wgs84(limite_lambert):
    '''
    Conversion des coordonnées lambert en WGS84
    Prise en compte des iles et des enclaves
    '''
    nb_points_limite = len(limite_lambert)
    limite_wgs84_tmp = []
    limite_wgs84 = []
    lon_tmp, lat_tmp =  transform(lambert_93, wgs_84, limite_lambert[0][0],\
               limite_lambert[0][1])
    ind_tmp = 0
    limite_wgs84_tmp.append([lon_tmp, lat_tmp])
    for ind, coord in enumerate(limite_lambert):
        lon, lat = transform(lambert_93, wgs_84, coord[0], coord[1])
        if [lon_tmp, lat_tmp] != [lon, lat]:
            limite_wgs84_tmp.append([lon, lat])
        else :
            if ind_tmp == ind:
                pass
            else :
                limite_wgs84.append(limite_wgs84_tmp)
                if ind + 1 < nb_points_limite:
                    lon_tmp, lat_tmp = transform(lambert_93, wgs_84,\
                          limite_lambert[ind+1][0], limite_lambert[ind+1][1])
                    ind_tmp = ind + 1
                    limite_wgs84_tmp = []
    return limite_wgs84

def creer_departement_json(info, limite):
    departement_json = {}
    departement_json["type"] = "Feature"
    departement_json["properties"] = {"numero_departement": info[1],\
        "nom_departement": info[2], "code_prefecture": info[3],\
        "code_region": info[9]}
    departement_json["geometry"] = {"type": "Polygon", "coordinates":  limite}
    return departement_json

def creer_commune_json(info, limite):
    commune_json = {}
    commune_json["type"] = "Feature"
    commune_json["properties"] = {"numero_commune": info[2],\
        "nom_departement": info[14], "numero_departement": info[13]}
    commune_json["geometry"] = {"type": "Polygon", "coordinates":  limite}
    return commune_json

def extraction_shp_departement(chemin):
    '''Structure info_departement
     0  :   Numéro departement
     1  :   Nom departement en majuscule
     2  :   Code geographique de la prefecture
     3  :   Code region
     4  :   limite en coordonne wgs84'''
    sf = Reader(chemin)
    shapeRecs = sf.shapeRecords()
    points = shapeRecs[5].shape.points
    record = shapeRecs[5].record
    info_departement = []
    for dep in shapeRecs:
        info = dep.record
        limite = conversion_lambert93_wgs84(dep.shape.points)
        departement_json = creer_departement_json(info, limite)
        info_departement.append([info[1], info[2], info[3], info[9],\
            departement_json])
    return info_departement

def extraction_shp_commune(chemin):
    '''Structure info_departement
     0  :   Numéro departement
     1  :   Nom departement en majuscule
     2  :   Code geographique de la prefecture
     3  :   Code region
     4  :   limite en coordonne wgs84'''
    sf = Reader(chemin)
    shapeRecs = sf.shapeRecords()
    points = shapeRecs[5].shape.points
    record = shapeRecs[5].record
    info_commune = []
    for dep in shapeRecs:
        info = dep.record
        limite = conversion_lambert93_wgs84(dep.shape.points)
        commune_json = creer_commune_json(info, limite)
        info_commune.append([info[2], info[3], info[4], info[9], info[10],\
                             info[11], info[13], commune_json])
    return info_commune

class Departement(db.Model):
    numero_departement = db.Column(db.String(3), primary_key=True)
    nom_departement = db.Column(db.String(80), unique=True)
    code_prefecture = db.Column(db.String(5))
    code_region = db.Column(db.String(5))
    limite_departement = db.Column(db.JSON)

    def __init__(self, numero_departement, nom_departement, code_prefecture,\
                 code_region, limite_departement):
        self.numero_departement = numero_departement
        self.nom_departement = nom_departement
        self.code_prefecture = code_prefecture
        self.code_region = code_region
        self.limite_departement = limite_departement

    def __repr__(self):
        return '<Departement %r %r>' % (self.nom_departement,\
                                        self.numero_departement)

class Commune(db.Model):
    '''Structure de la classe commune OGN
    numero_insee : numero insee de la commune
    nom_commune : nom de la commune
    status : status administratif
               - Capitale etat
               - Prefecture region
               - Prefecture departement
               - Sous-prefecture
               - Commune simple
    altitude_moyenne : altitude moyenne en metres
    superficie : superficie en hectares
    population : population
    numero_departement : numero_departement
    limite_commune : limite commune en coordonnee wgs84'''
    numero_insee =  db.Column(db.String(5), primary_key=True)
    nom_commune =  db.Column(db.String(50))
    status =  db.Column(db.String(25))
    altitude_moyenne = db.Column(db.Integer)
    superficie = db.Column(db.Integer)
    population = db.Column(db.Integer)
    numero_departement = db.Column(db.String(3))
    limite_commune = db.Column(db.JSON)

    def __init__(self, numero_insee, nom_commune, status, altitude_moyenne,\
                 superficie, population, numero_departement, limite_commune):
        self.numero_insee = numero_insee
        self.nom_commune = nom_commune
        status = str(status)
        if status.find('partement') != -1:
            status = "Préfecture de département"
        elif status.find('Sous') != -1:
            status = "Sous-préfecture"
        elif status.find('gion') != -1:
            status = "Préfecture de région"
        elif status.find('tat') != -1:
            status = "Capitale d'état"
        self.status = status
        self.altitude_moyenne = altitude_moyenne
        self.superficie = superficie
        self.population = population
        self.numero_departement = numero_departement
        self.limite_commune = limite_commune

    def __repr__(self):
        return '<Commune %r %r %r %r %r %r %r>' % (self.numero_insee,\
             self.nom_commune, self.status, self.altitude_moyenne,\
             self.superficie, self.population, self.numero_departement)

if __name__ == '__main__':
    if CHG_DB == True : db.create_all()

    departements = extraction_shp_departement('./data/DEPARTEMENT/DEPARTEMENT')
    for dep_tmp in departements:
        ligne = Departement(dep_tmp[0], dep_tmp[1], dep_tmp[2], dep_tmp[3],\
            dep_tmp[4])
        #print ligne
        if CHG_DB == True : 
            db.session.add(ligne)
            db.session.commit()
    if CHG_DB == True : print('Mise en DB departement finie')

    communes = extraction_shp_commune('./data/COMMUNE/COMMUNE')
    long_communes = len(communes)
    tmp = 0
    for com_tmp in communes:
        tmp = tmp + 1
        ligne = Commune(com_tmp[0], com_tmp[1], com_tmp[2], com_tmp[3],\
                        com_tmp[4], com_tmp[5], com_tmp[6], com_tmp[7])
        #print ligne
        if CHG_DB == True : 
            db.session.add(ligne)
            db.session.commit()
            print(100. * tmp / long_communes)
    if CHG_DB == True : print('Mise en DB commune finie')
    


