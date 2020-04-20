import mysql.connector

mydb = mysql.connector.connect(host=f"localhost", user=f"root",
password=f"bruhprenk", database=f"toughguy")

mydb.autocommit = True
mycursor = mydb.cursor()

