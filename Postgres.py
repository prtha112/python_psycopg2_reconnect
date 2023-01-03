import psycopg2
class Postgres:

    # class attribute
    database_address = ''
    database_name = ''
    database_username = ''
    database_password = ''
    database_port = ''

    database_connection = None
    database_query_result = None

    _reconnectTries = 5

    # instance attribute
    def __init__(self, address, dbname, username, password, port):
        #self.name = name
        self.database_address = address
        self.database_name = dbname
        self.database_username = username
        self.database_password = password
        self.database_port = port

    def connect(self):
        conn = psycopg2.connect(
            dbname = self.database_name,
            user = self.database_username,
            password = self.database_password,
            host = self.database_address,
            port = self.database_port
        )
        conn.autocommit = True
        try:
            self.database_connection = conn.cursor()
        except psycopg2.Error as error:
            raise error

    def reset(self):
        if self.database_connection:
            self.database_connection.close()
        self.database_connection = None

    def execute(self, data, retry_count = 0, state = "ALL"):
        sqlState = data
        try:
            self.database_connection.execute(sqlState)
            if state == "ALL":
                self.database_query_result = self.database_connection.fetchall(sqlState)
            else if state == "ONE":
                self.database_query_result = self.database_connection.fetchone(sqlState)
            else if state == "EDIT":
                self.database_query_result = None
            else:
                raise "State query no match"
        except psycopg2.OperationalError as error:
            if retry_count >= self._reconnectTries:
                raise error
            else:
                self._reconnectTries = self._reconnectTries + 1
                self.reset()
                self.connect()
                self.execute(sqlState, retry_count)
        except (Exception, psycopg2.Error) as error:
            raise error
            
    def fetchAll(self, data, retry_count = 0):
        sqlState = data
        self.execute(data, self._reconnectTries, "ALL")
        return self.database_query_result
    
    def fetchOne(self, data, retry_count = 0):
        sqlState = data
        self.execute(data, self._reconnectTries, "ONE")
        return self.database_query_result
