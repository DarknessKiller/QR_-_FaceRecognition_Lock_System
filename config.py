# Configuration Python for MySQL

import mysql.connector
import numpy

mysql = mysql.connector.connect(
	host="localhost",
	user="root",
	password="askmydad",
	database="testdb"
	)
