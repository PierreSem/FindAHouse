from findahouse import app
from flask import session, g, escape, redirect, url_for, render_template,\
                                request, Flask, Response, abort, jsonify
from flask_login import LoginManager, UserMixin, \
                                login_required, login_user, logout_user 
import mysql.connector
# create some users with ids 1 to 20       
#users = User('pierre') 


CONFIG = {'user': 'tipi',
          'password': 'tipi'}

DB_NAME = "geodata"


def connexion_db(DB_NAME):
    cnx = mysql.connector.connect(**CONFIG)
    cursor = cnx.cursor()
    cnx.database = DB_NAME
    return cnx, cursor


def active_page(page):
    '''Use to select the active html page'''
    html_page = {'identification': '', 'inscription': '', 'geoinformation': '', 'contact': '', 'espace_personnel': ''}
    html_page[page] = ' class=active'
    return html_page

@app.route('/geodata/<ville>')
def geodata(ville):
    #departement = Departement.query.filter_by(numero_departement = '2A').first()
    #return jsonify(departement.limite_departement)
    commune = Commune.query.filter_by(nom_commune = ville).first()
    print(commune)
    return jsonify(commune.limite_commune)


@app.route('/autocomplete')
def autocomplete():
    search = request.args.get('term') 
    search = '%' + search + '%'
    print(search)
    cnx, cursor = connexion_db(DB_NAME)
    query = ('SELECT * FROM communes WHERE nom_com_maj = "ANTONY";')
    cursor.execute(query)
    for i in cursor:
        print(i)
    print(cursor)
    commune = Commune.query.filter(Commune.nom_commune.ilike(search))
    nom_commune = []
    if commune.first() != None:
        tmp = 0
        for i in commune:
            #nom_commune.append(i.nom_commune)
            nom_commune.append({"value" : i.nom_commune, "label" : i.nom_commune, "desc": i.numero_departement})
            tmp = tmp + 1
            if tmp == 10: break
    return jsonify(nom_commune) 

@app.route('/contact')
def contact():
    g.active_page = active_page('contact')
    return render_template('contact.html')

@app.route('/geoinformation', methods=['GET', 'POST'])
def geoinformation():
    if request.method == "GET":
        g.active_page = active_page('geoinformation')
        ville = ''
        return render_template('geoinformation_old.html', ville = ville)
    elif request.method == "POST":
        g.active_page = active_page('geoinformation')
        ville = request.form["search_ville"]
        return render_template('geoinformation_old.html', ville = ville)
