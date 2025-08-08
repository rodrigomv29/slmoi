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
