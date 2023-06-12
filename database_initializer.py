from flask import Flask
from database import DatabaseConnection

#This Method will initialize the database connection
def initialize_database(app):
    #Create instance of database connection
    db_connection = DatabaseConnection(host='localhost', user='root', password='rootpassword', database='it_stock_db')

    #Store connection in flask's object
    app.config['database'] = db_connection
