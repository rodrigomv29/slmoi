
class Conversation:
    def __init__(self, user_input: str, output: str, user_name="guest"):
        self.user_name = user_name
        self.user_input = user_input
        self.output = output
    def get_user_name(self):
        return self.user_name
    def get_user_input(self):
        return self.user_input
    def get_output(self):
        return self.output
    