import mysql.connector
import requests
import time
db = mysql.connector.connect(host="localhost",user="root",passwd="password",db="monitoring_db")
cur = db.cursor()
while True:
	cur.execute("SELECT id, url FROM websites")
	websites_array=cur.fetchall()
	for website in websites_array:
		try:
			req = requests.get(website[1]).status_code
		except Exception as e:
			req=000
		strSQL="insert into checks(websites, request_result) values ("+str(website[0])+","+str(req)+")"
		cur.execute(strSQL)
	db.commit()
	time.sleep(120)
db.close()
