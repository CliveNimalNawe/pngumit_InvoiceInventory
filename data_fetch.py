#This class is for functions that will retrieve data from the database.
class DataFetcher:
    #Constructor
    def __init__(self, database):
        self.database = database

    #Method to retrieve data tuples from database
    def fetch_data(self, query, datas=None):
        self.database.connect()
        cursor = self.database.connection.cursor()
        if datas is None:
            cursor.execute(query)

        else:
            cursor.execute(query, datas)
        data = cursor.fetchall()
        cursor.close()
        self.database.close()
        return data
    #Method to retrieve single row from the database
    def fetch_row(self, query, data=None):
        self.database.connect()
        cursor = self.database.connection.cursor()
        if data is None:
            cursor.execute(query)
        else:
            cursor.execute(query, data)

        row = cursor.fetchone()
        cursor.close()
        self.database.close()
        return row
    
    def insert_data(self, query, data):
        try:
            self.database.connect()
            cursor = self.database.connection.cursor()
            cursor.execute(query, data)
            self.database.connection.commit()
            cursor.close()
            return True
        
        except Exception as e:
            print("Error occurred during insertion:", str(e))
            cursor.close()
            return False

        finally:
            self.database.close()

    def delete_data(self, query, data=None):
        try:
            self.database.connect()
            cursor=self.database.connection.cursor()
            cursor.execute(query, data)
            self.database.connection.commit()
            cursor.close()
            self.database.close()
            return True
        
        except Exception as e:
            print(e)
            self.database.connection.rollback()
            cursor.close()
            self.database.close()
            return False
   