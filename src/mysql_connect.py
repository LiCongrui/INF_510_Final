import pymysql.cursors

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='cl',
                             password='123456',
                             db='career',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

def create_position():

    pass

def create_companies():
    pass

def create_visa():
    pass

if __name__ == '__main__':
    try:
        with connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT * FROM `test`"
            cursor.execute(sql)
            result = cursor.fetchone()
            print(result)
    finally:
        connection.close()