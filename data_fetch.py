#This class is for functions that will retrieve data from the database.
class DataFetcher:
    #Constructor
    def __init__(self, database):
        self.database = database

    #Method to retrieve data tuples from database
    def fetch_data(self, query):
        self.database.connect()
        cursor = self.database.connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        self.database.close()
        return data
    #Method to retrieve single row from the database
    def fetch_row(self, query):
        self.database.connect()
        cursor = self.database.connection.cursor()
        cursor.execute(query)
        row = cursor.fetchone()
        cursor.close()
        self.database.close()
        return row
    
    def insert_data(self, query, data):
        self.database.connect()
        cursor = self.database.connection.cursor()
        cursor.execute(query, data)
        self.database.connection.commit()
        cursor.close()
        self.database.close()
    
   