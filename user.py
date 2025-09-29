class User:
    def __init__(self, name, password, birthday, email, interests = []):
        self.name = name
        self.password = password
        self.birthday = birthday
        self.email = email
        self.interests = interests
    def get_name(self):
        return self.name
    def get_birthday(self):
        return self.birthday
    def get_email(self):
        return self.email
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
