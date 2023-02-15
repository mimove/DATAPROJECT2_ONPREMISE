from flask import Flask, jsonify
from flaskext.mysql import MySQL

import pymysql


global mysql

app = Flask(__name__)

# Configuration of MySQL database
app.config['MYSQL_HOST'] = 'db'
app.config['MYSQL_PORT'] = 3306 
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'my_secret_password'
app.config['MYSQL_DB'] = 'app_db'




# Initializing MySQL read within the Flask app
mysql = MySQL(app)


# Route of the API to get the info of a single panel
@app.route('/power/<string:panel_id>', methods=['GET'])
def get_power(panel_id):
    # Connecting to database
    connection = pymysql.connect(host="db", port=3306, user="root", passwd="my_secret_password", database="app_db")
    cur = connection.cursor()
    
    # Query to obtain the rows of a single panel, filtering by Panel_id
    cur.execute("SELECT Panel_id, power_panel, current_status, time_data FROM panelData WHERE Panel_id = %s", (panel_id,))
    
    # Getting all the rows of the query
    data = cur.fetchall()
    
    # Creation of a list to store all the JSON
    results = []
    
    for row in data:
        result = {}
        result['Panel_id'] = row[0]
        result['power_panel'] = row[1]
        result['current_status'] = row[2]
        result['time_data'] = row[3].strftime('%Y-%m-%d %H:%M:%S')
        results.append(result)
    
    cur.close()
    
    # Return of the response in JSON format with the list of results.
    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)
