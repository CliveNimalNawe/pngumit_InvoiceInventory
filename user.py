class User:
    is_active = True
    def __init__ (self, user_id):
        self.id = user_id
    
    def get_id(self):
        return str(self.id)
    
    def is_authenticated(self):
        return True
    
