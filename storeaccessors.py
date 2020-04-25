import mysql.connector

mydb = mysql.connector.connect(host=f"localhost", user=f"root",
password=f"bruhprenk", database=f"toughguy")
#db name is storedb
'''
  `store` 
  `item` 
  `count`
  `latitude` 
  `longitude` 
  `ID`  -> only not null option for now
'''

mydb.autocommit = True
mycursor = mydb.cursor()

def add(store, item, count, latitude, longitude, ID = None):
	if(ID == None):
		#set the comm here
		data = (store, item, count, latitude, longitude)
		comm = (
    		"INSERT INTO storedb (store, item, count, latitude, longitude) VALUES (%s, %s, %s, %s, %s)"
 		)
	else:
		data = (store, item, count, latitude, longitude, ID)
		comm = (
    		"INSERT INTO storedb (store, item, count, latitude, longitude, ID) VALUES (%s, %s, %s, %s, %s, %s)"
 		)
 	mycursor.execute(comm, data)
def update(store, item, count, latitude, longitude):
	data = (store, item, count, latitude, longitude)
	comm = 	