class UserInfo:
    def __init__(self, email=None, password=None, firstName=None, lastName=None, medicine=None):
        self.email = email
        self.password = password
        self.firstName = firstName
        self.lastName = lastName
        self.medicine = medicine

    def get_user_info(self):
        return f"{self.email} {self.firstName} {self.lastName} {self.medicine}"
