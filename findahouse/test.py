import mysql.connector 
config_connexion = {'user':'tipi', 'password':'tipi', 'host':'127.0.0.1','database':'geodata'}


cnx = mysql.connector.connect(**config_connexion)
cursor = cnx.cursor()
cursor.execute("SELECT * FROM commune WHERE numero_insee='95690'")
commune = cursor.fetchall()
print(commune)



cnx.close()
