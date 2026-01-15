import datetime
class User:
    def __init__(self, full_name, user_name, birthday, password, interests = []):
        current_time = datetime.datetime.now()
        self.name = full_name
        self.user_name = user_name
        self.password = password
        self.birthday = birthday
        self.created_at = current_time.strftime('%Y-%m-%d_%H:%M:%S')
        self.interests = interests
    def __str__(self):
        return f"User: {self.user_name}\n ({self.name}), joined on {self.created_at}, born on {self.birthday}"
    def __repr__(self):
        return f"User(name={self.name}, user_name={self.user_name}, password=***, birthday={self.birthday}, interests={self.interests})"
    def get_username(self):
        return self.user_name
    def get_name(self):
        return self.name
    def get_birthday(self):
        return self.birthday
    def get_interests(self):
        return self.interests
class UserInput:
    def __init__(self, inp, user_name):
        self.inp =inp
        self.user_name = user_name
    def get_inp(self):
        return self.inp
    def get_user_name(self):
        return self.user_name
