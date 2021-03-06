""" File Backup System Database - DB manager."""
import uuid
import sqlite3
#from prettytable import PrettyTable
DATABASE = 'server.db'

sql_create_clients_table = """CREATE TABLE IF NOT EXISTS clients( 
                                ID varchar(16) PRIMARY KEY, 
                                Name varchar(256), 
                                Password varchar(64)
                                ); """
sql_create_files_table = """ CREATE TABLE IF NOT EXISTS files( 
                                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                OwnerID varchar(16),
                                FileName varchar(255),
                                Content Blob
                                ); """


class DataBase:
    def __init__(self):
        try:
            self.db = sqlite3.connect(DATABASE, check_same_thread=False)
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
            # print(self.cursor.fetchall())
        except sqlite3.Error as e:
            print(e)
    
    def init_sql_tables(self):
        """
        Initials the database
        """
        if self.db is not None:
            self.create_table(sql_create_clients_table)
            self.create_table(sql_create_files_table)
            self.db.commit()
        else:
            print("Error! cannot create the database connection.")

    def insert_new_client_to_the_table(self, client_id, name, password):
        """
        Add new client to clients table.
        """
        self.cursor.execute("INSERT INTO clients VALUES (?, ?, ?)", (client_id, name, password))
        self.db.commit()

    def insert_new_file_to_the_table(self, client_id, file_name, file_content):
        """
        # Add new file to files table and return the index of the file.
        """
        self.cursor.execute("INSERT INTO files(OwnerID, FileName, Content) "
                            "VALUES (?, ?, ?)", (client_id, file_name, file_content))
        self.db.commit()

        self.cursor.execute("""SELECT last_insert_rowid()""")
        return self.cursor.fetchall()[0][0]

    def pull_password(self, client_id):
        """
        Pull password from clients table
        """
        self.cursor.execute("SELECT Password FROM clients WHERE ID = ?", (client_id,))
        return self.cursor.fetchall()[0][0].decode('utf-8')

    def is_file_exists(self, client_id, file_name):
        """
        Return true if file exists for a given client
        """
        self.cursor.execute("SELECT COUNT(*) FROM files WHERE OwnerID = ? and FileName = ?", (client_id, file_name))
        s = self.cursor.fetchone()
        return True if s[0] > 0 else False

    def add_client(self, client_id, name, password):
        """
        Return true if the user was added successfully, otherwise false because the user already exists
        """
        if self.is_client_id_exists(client_id):
            return False
        self.insert_new_client_to_the_table(client_id, name, password)
        return True

    def add_file(self, client_id, file_name, file_content):
        """
        If the user already has a file with the same name, delete the file before adding it
        """
        if self.is_file_exists(client_id, file_name):
            self.delete_file(client_id, file_name)
        self.insert_new_file_to_the_table(client_id, file_name, file_content)

    def delete_file(self, client_id, file_name):
        """
        Delete file from files table
        """
        self.db.execute("DELETE FROM files WHERE OwnerID = ? and FileName = ?", (client_id, file_name))
        self.db.commit()

    def pull_file(self, client_id, file_name):
        """
        Pull file from files table
        """
        self.cursor.execute("SELECT Content FROM files WHERE OwnerID = ? and FileName = ?", (client_id, file_name))
        return self.cursor.fetchall()[0][0]

    def get_files_list(self, client_id):
        """
        Get files list owned by client
        """
        self.cursor.execute("SELECT FileName FROM files WHERE OwnerID = ?", (client_id,))
        return self.cursor.fetchall()

    def __del__(self):
        """
        Destructor method
        """
        self.cursor.close()
        self.db.close()

    def is_client_name_exists(self, name):
        """
        Return true if username is already exists in clients table
        """
        self.cursor.execute("SELECT COUNT(*) FROM clients WHERE Name = ? ", (name,))
        s = self.cursor.fetchone()
        return True if s[0] > 0 else False

    def get_client_uid(self, name):
        """
        Returns client's uid
        """
        self.cursor.execute("SELECT ID FROM clients WHERE Name = ? ", (name,))
        return self.cursor.fetchall()[0][0]

    def is_client_id_exists(self, client_id):
        """
        Return true if client id is already exists in clients table
        """
        self.cursor.execute("SELECT COUNT(*) FROM clients WHERE ID = ? ", (client_id,))
        s = self.cursor.fetchone()
        return True if s[0] > 0 else False

"""
    To print the tables you can remove the notes, install PrettyTable
    And run database.py
"""
""" - if
    def print_table_clients(self):
        self.cursor.execute("SELECT * FROM clients")
        l = [list(i) for i in self.cursor.fetchall()]
        table = PrettyTable(['ID', 'Name', 'Password'])
        print('Table Clients:')
        for rec in l:
            table.add_row(rec)
        print(table)

    def print_table_files(self):
        self.cursor.execute("SELECT * FROM files")
        l = [list(i) for i in self.cursor.fetchall()]
        table = PrettyTable(['ID', 'OwnerID','FileName','Content'])
        print('Table Files:')
        for rec in l:
            table.add_row(rec)
        print(table)


def printdb():
    db = DataBase()
    db.print_table_clients()
    db.print_table_files()
    
printdb()    
"""
