import pyodbc

from user_info import UserInfo

SERVER = 'pharmabotdb1.database.windows.net'
DATABASE = 'pharmadb'
USERNAME = 'azureuser'
PASSWORD = 'pharmabotproject2022!'
DRIVER = '{ODBC Driver 17 for SQL Server}'


def insert_user(email, firstname, lastname, password):
    with pyodbc.connect(
            'DRIVER=' + DRIVER + ';SERVER=tcp:' + SERVER + ';PORT=1433;DATABASE=' + DATABASE + ';UID=' + USERNAME + ';PWD=' + PASSWORD) as conn:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO dbo.users([email],[pwd],[firstName],[lastName]) VALUES (?,?,?,?)", email,
                           password, firstname, lastname)
            return True


def get_pwd(email):
    try:
        with pyodbc.connect(
                'DRIVER=' + DRIVER + ';SERVER=tcp:' + SERVER + ';PORT=1433;DATABASE=' + DATABASE + ';UID=' + USERNAME + ';PWD=' + PASSWORD) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT pwd FROM dbo.users WHERE [email] = ?", email)
                row = cursor.fetchall()

                return row[0][0]
    except:
        return False


def login(email):
    with pyodbc.connect(
            'DRIVER=' + DRIVER + ';SERVER=tcp:' + SERVER + ';PORT=1433;DATABASE=' + DATABASE + ';UID=' + USERNAME + ';PWD=' + PASSWORD) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT email,firstName,lastName FROM dbo.users WHERE [email] = ?", email)
            row = cursor.fetchall()
            email = row[0][0]
            firstName = row[0][1]
            lastName = row[0][2]
            cursor.execute(
                "SELECT medicineName,medicineType,medicineGrams,expirationDate FROM dbo.medicine WHERE [email] = ?",
                email)
            rows = cursor.fetchall()
            medicineLi = []
            for row in rows:
                medicine = {}
                medicine['name'] = row[0]
                medicine['type'] = row[1]
                medicine['grams'] = row[2]
                medicine['expirationDate'] = row[3]
                medicineLi.append(medicine)
            user = UserInfo(email=email, firstName=firstName, lastName=lastName, medicine=medicineLi)

    return user


def delete_account(email):
    try:
        with pyodbc.connect(
                'DRIVER=' + DRIVER + ';SERVER=tcp:' + SERVER + ';PORT=1433;DATABASE=' + DATABASE + ';UID=' + USERNAME + ';PWD=' + PASSWORD) as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM dbo.medicine WHERE [email] = ?", email)
                cursor.execute("DELETE FROM dbo.users WHERE [email] = ?", email)
                return True
    except Exception as e:
        return False
