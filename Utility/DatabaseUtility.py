import string

import bcrypt


class DatabaseUtility:
    @staticmethod
    def get_hashed_pwd(password: string):
        byte_pwd = password.encode('utf-8')
        salt = bcrypt.gensalt()
        pwd_hash = bcrypt.hashpw(byte_pwd, salt)

        return pwd_hash.decode()

    @staticmethod
    def check_pwd(password: string, pwd_hash: string):
        password = password.encode('utf-8')
        return bcrypt.checkpw(password, pwd_hash)
