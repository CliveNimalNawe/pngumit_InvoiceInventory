import logging
#This class is for functions that will retrieve data from the database.
class DataFetcher:
    #Constructor
    def __init__(self, database):
        self.database = database
        self.logger = logging.getLogger(__name__)

    #Method to retrieve data tuples from database
    def fetch_data(self, query, datas=None):
        self.database.connect()
        cursor = self.database.connection.cursor()
        try:
            if datas is None:
                cursor.execute(query)

            else:
                cursor.execute(query, datas)

            data = cursor.fetchall()
            self.logger.info(f"Fetched data: {data}")
        except Exception as e:
            self.logger.error(f"Error during fetch_data: {e}")
            raise
            
        finally:
            cursor.close()
            self.database.close()
            self.logger.info("Connection closed")

        return data
            
    #Method to retrieve single row from the database
    def fetch_row(self, query, data=None):
        self.database.connect()
        cursor = self.database.connection.cursor()
        if data is None:
            cursor.execute(query)
            row = cursor.fetchone()
        else:
            cursor.execute(query, data)
            row = cursor.fetchone()

        #row = cursor.fetchone()
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
        
    def update_data(self, query, data):
        try:
            self.database.connect()
            cursor = self.database.connection.cursor()
            cursor.execute(query, data)
            self.database.connection.commit()
            cursor.close()
            return True

        except Exception as e:
            print("Error occurred during update:", str(e))
            cursor.close()
            return False

        finally:
            self.database.close()
            
    def fetch_hashed_password(self, username):
        self.database.connect()
        cursor = self.database.connection.cursor()
        
        # Query the database to retrieve the hashed password and salt
        query = "SELECT password, salt FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()

        cursor.close()
        self.database.close()

        if result:
            hashed_password, salt = result
            return hashed_password, salt
        else:
            return None, None
        
    def bulk_insert_data(self, query, data_list):
        try:
            self.database.connect()
            cursor = self.database.connection.cursor()

            # Use executemany to insert multiple rows at once
            cursor.executemany(query, data_list)

            self.database.connection.commit()
            cursor.close()
            return True

        except Exception as e:
            print("Error occurred during bulk insertion:", str(e))
            cursor.close()
            return False

        finally:
            self.database.close()

    def __enter__(self):
        self.database.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            if self.database.connection.is_connected():
                self.database.connection.close()
        except Exception as e:
            self.logger.error(f"Error during __exit__: {e}")