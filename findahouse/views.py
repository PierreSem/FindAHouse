from findahouse import app
from flask import session, g, escape, redirect, url_for, render_template,\
                                request, Flask, Response, abort, jsonify
from flask_login import LoginManager, UserMixin, \
                                login_required, login_user, logout_user 
from flask_sqlalchemy import SQLAlchemy
from .gestion_db import Departement, Commune

db = SQLAlchemy(app)

app.config.update(
    DEBUG = True,
    SECRET_KEY = 'secret_xxx')

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "identification"

# silly user model
class User(UserMixin):
    def __init__(self, id):
        self.id = id
        self.name = str(id)
        self.password =  str(id)
        
    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)


# create some users with ids 1 to 20       
#users = User('pierre') 


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

@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    search = request.args.get('term') 
    search = '%' + search + '%'
    print(search)
    commune = Commune.query.filter(Commune.nom_commune.ilike(search))
    nom_commune = []
    if commune.first() != None:
        tmp = 0
        for i in commune:
            nom_commune.append(i.nom_commune)
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
        g.ville = 'DOMONT'
        return render_template('geoinformation.html')
    elif request.method == "POST":
        g.active_page = active_page('geoinformation')
        ville = request.form["search_ville"]
        g.ville = ville
        return render_template('geoinformation.html')

@app.route('/inscription')
def inscription():
    g.active_page = active_page('inscription')
    return render_template('inscription.html')


@app.route('/espace_personnel')
@login_required
def espace_personnel():
    g.active_page = active_page('espace_personnel')
    return render_template('espace_personnel.html')
 
# somewhere to login
@app.route("/identification", methods=["GET", "POST"])
def identification():
    g.active_page = active_page('identification')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']        
        if password == 'pierre':
            user = User(id)
            login_user(user)
            return redirect(request.args.get("next") or url_for('geoinformation'))
        else:
            return abort(401)
    else:
        return render_template('identification.html')
        #return Response('''
        #<form action="" method="post">
        #    <p><input type=text name=username>
        #    <p><input type=password name=password>
        #    <p><input type=submit value=Login>
        #</form>
        #''')


# somewhere to logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return Response('<p>Logged out</p>')


# handle login failed
@app.errorhandler(401)
def page_not_found(e):
    return Response('<p>Login failed</p>')
    
    
# callback to reload the user object        
@login_manager.user_loader
def load_user(userid):
    return User(userid)
 


