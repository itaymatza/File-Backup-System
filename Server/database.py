""" File Backup System Database - DB manager."""
import uuid
import sqlite3

DATABASE = 'server.db'

sql_create_clients_table = """ CREATE TABLE IF NOT EXISTS clients( 
                                ID varchar(16) NOT NULL PRIMARY KEY, 
                                Name varchar(256), 
                                Password varchar(64)
                                ); """
sql_create_files_table = """ CREATE TABLE IF NOT EXISTS files( 
                                ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                OwnerID varchar(16),
                                FileName varchar(255),
                                Content Blob)
                                ); """


class DataBase:
    def __init__(self):
        try:
            self.db = sqlite3.connect(DATABASE)
            self.db.text_factory = bytes
            self.cursor = self.db.cursor()
            sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes)
            self.init_sql_tables()
        except sqlite3.Error as error:
            raise sqlite3.Error('Database error: %s' % error)

    def create_table(self, create_table_sql):
        """
        Gets the table details (str) and create table
        """
        try:
            self.cursor.execute(create_table_sql)
            print(self.cursor.fetchall())
        except sqlite3.Error as e:
            print(e)

    def init_sql_tables(self):
        """
        Initials the database
        """
        if self.db is not None:
            self.create_table(sql_create_clients_table)  # create clients table
            self.create_table(sql_create_files_table)  # create messages table
            self.db.commit()
        else:
            print("Error! cannot create the database connection.")

    def insert_new_client_to_the_table(self, client_id, name, password):
        """
        # Add new client to clients table.
        """
        self.cursor.execute("INSERT INTO clients VALUES (?, ?, ?)", (client_id, name, password))
        self.db.commit()

    def insert_new_file_to_the_table(self, client_id, file_name, file_content):
        """
        # Add new file to files table and return the index of the file.
        """
        self.cursor.execute("INSERT INTO files(OwnerID, FileName, Content) VALUES (?, ?, ?)", (client_id, file_name, file_content))
        self.db.commit()

        self.cursor.execute("""SELECT last_insert_rowid()""")
        return self.cursor.fetchall()[0][0]

    def delete_file(self, client_id, file_name):
        """
        Delete file from files table
        """
        self.db.execute("DELETE FROM files WHERE Owner = ? and FileName = ?", (client_id, file_name))
        self.db.commit()

    # .
    def pull_file(self, client_id, file_name):
        """
        Pull file from files table
        """
        self.cursor.execute("SELECT Content FROM files WHERE Owner = ? and FileName = ?", (client_id, file_name))
        return self.cursor.fetchall()

    # Get files list owned by client.
    def get_files_list(self, client_id):
        """
        Get files list owned by client
        """
        self.cursor.execute("SELECT FileName FROM files WHERE Owner = ?", (client_id,))
        return self.cursor.fetchall()

    def __del__(self):
        """
        Destructor method
        """
        self.cursor.close()
        self.db.close()

    def is_client_exists(self, name):
        """
        Return true if username is already exists in clients table
        """
        self.cursor.execute("SELECT COUNT(*) FROM clients WHERE Name = ? ", (name,))
        s = self.cursor.fetchone()
        return True if s else False

    """
    not in use
    """

    # Check if given ID is already exists in clients table.
    def is_id_exists(self, uid):
        _uid = uuid.UUID(bytes=uid)
        self.cursor.execute("""
            SELECT COUNT(*)
            FROM clients
            WHERE ID = '{0}'
            """.format(_uid))
        if self.cursor.fetchone()[0] != 0:
            return True
        return False

    # Generates new uuid and make sure is not already in clients table.
    def _get_new_uuid(self):
        _uid = uuid.uuid4()
        while self.is_id_exists(_uid.bytes):
            _uid = uuid.uuid4()
        return _uid
