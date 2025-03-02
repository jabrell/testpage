class InvalidTokenError(Exception):
    def __init__(self, message="Invalid token"):
        self.message = message
        super().__init__(self.message)


class UserNotFound(Exception):
    def __init__(self, message="User not found"):
        self.message = message
        super().__init__(self.message)


class InvalidPassword(Exception):
    def __init__(self, username):
        self.message = f"Invalid password for user {username}"
        super().__init__(self.message)
