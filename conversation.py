class Conversation:
    def __init__(self, user_input: str, output: str, is_news=False, user_name="guest"):
        self.user_name = user_name
        self.user_input = user_input
        self.output = output
        self.is_news=is_news
        self.user_name=user_name
        if type(self.output) == list:
            self.is_list = True
    def get_user_name(self):
        return self.user_name
    def get_user_input(self):
        return self.user_input
    def get_output(self):
        return self.output
    