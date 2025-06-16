class UserDetail():
    """A simple user model for authentication & authorization"""
    def __init__(self, userId: str, email: str = "", role: list[str] = []):
        self.userId = userId
        self.email = email
        self.role = role

    def __str__(self):
        return """User(userId="{}", email="{}", roles=[{}])""".format(
            self.userId, self.email, ", ".join(self.role)
        )