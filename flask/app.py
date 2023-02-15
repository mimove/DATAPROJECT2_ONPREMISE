from flask import Flask, jsonify
from flaskext.mysql import MySQL

import pymysql


global mysql

app = Flask(__name__)

# Configuración de la base de datos MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3308 # o el puerto que utilices en tu base de datos MySQL
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'my_secret_password'
app.config['MYSQL_DB'] = 'app_db'


# connection = pymysql.connect(host="localhost", user="root", passwd="my_secret_password", database="app_db")
# cursor = connection.cursor()


# Inicialización de la extensión MySQL
mysql = MySQL(app)


# Definición de la ruta de la API para obtener los datos
@app.route('/power/<string:panel_id>', methods=['GET'])
def get_power(panel_id):
    # Conexión a la base de datos
    connection = pymysql.connect(host="db", port=3306, user="root", passwd="my_secret_password", database="app_db")
    cur = connection.cursor()
    
    # Ejecución de la consulta para obtener los datos del panel especificado
    cur.execute("SELECT Panel_id, power_panel, current_status, time_data FROM panelData WHERE Panel_id = %s", (panel_id,))
    
    # Obtención de los resultados de la consulta
    data = cur.fetchall()
    
    # Lista para almacenar los resultados
    results = []
    
    # Recorrido de los resultados de la consulta y agregado de cada fila como un diccionario a la lista de resultados
    for row in data:
        result = {}
        result['Panel_id'] = row[0]
        result['power_panel'] = row[1]
        result['current_status'] = row[2]
        result['time_data'] = row[3].strftime('%Y-%m-%d %H:%M:%S')
        results.append(result)
    
    # Cierre de la conexión a la base de datos
    cur.close()
    
    # Devolución de la respuesta en formato JSON con la lista de resultados
    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)
