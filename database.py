#This file contains classes that deal with the database
import mysql.connector

#This is the class with connection fucntion
class DatabaseConnection:
    #Constructor
    def __init__(self, host, user, password, database):
        self.host=host
        self.user=user
        self.password=password
        self.database=database
        self.connection=None

    #Connect method
    def connect(self):
        self.connection = mysql.connector.connect(host=self.host, user=self.user, password=self.password, database=self.database)

    #Method to close connection
    def close(self):
        if self.connection is not None:
            self.connection.close()




