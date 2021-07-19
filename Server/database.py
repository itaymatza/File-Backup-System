""" File Backup System Database - DB manager."""
import uuid
import sqlite3

DATABASE = 'server.db'


class DataBase:
    def __init__(self):
        try:
            self.db = sqlite3.connect(DATABASE)
            self.db.text_factory = bytes
            self.cursor = self.db.cursor()
            sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)
            self.init_sql_tables()
        except sqlite3.Error as error:
            raise sqlite3.Error('Database error: %s' % error)

    # Initials the database. If not exist, create 'clients' and 'files' SQL tables.
    def init_sql_tables(self):
        if not self._is_table_exists('clients'):
            self.db.executescript(""" CREATE TABLE clients(
            ID varchar(16) NOT NULL PRIMARY KEY, 
            Name varchar(255), 
            password varchar(160);
            """)
        if not self._is_table_exists('files'):
            self.db.executescript(""" CREATE TABLE files(
            ID INTEGER PRIMARY KEY,
            Owner varchar(16),
            Name varchar(255),
            Content Blob);
            """)
        self.db.commit()

    # Check if given table_name exists in given SQL DB.
    def _is_table_exists(self, table_name):
        self.cursor.execute("""
            SELECT COUNT(*)
            FROM sqlite_master
            WHERE type='table' AND name = '{0}'
            """.format(table_name.replace('\'', '\'\'')))
        if self.cursor.fetchone()[0] == 1:
            return True
        return False

    # Check if given client username is already exists in clients table.
    def is_client_exists(self, name):
        self.cursor.execute("""
            SELECT COUNT(*)
            FROM clients
            WHERE Name = ?
            """, [name])
        if self.cursor.fetchone()[0] != 0:
            return True
        return False

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

    # Add new client to clients table.
    def add_client(self, name, password):
        _uid = self._get_new_uuid()
        self.cursor.execute("""
                INSERT INTO clients VALUES ('{0}', ?, ?)
                """.format(_uid), [name, password])
        self.db.commit()
        return _uid

    # Add file to files table.
    # Returns file's ID.
    def add_file(self, client, file_name, file_content):
        _client = uuid.UUID(bytes=client)
        self.db.execute("""
                    INSERT INTO files (Owner, Name, Content)
                    VALUES ('{0}', ?, ?)
                    """.format(_client), [file_name, file_content])
        self.db.commit()

        self.cursor.execute("""
            SELECT last_insert_rowid()
            """)
        return self.cursor.fetchall()[0][0]

    # Pull file from files table.
    def pull_files(self, client, file_name):
        _client = uuid.UUID(bytes=client)
        self.cursor.execute("""
            SELECT Content
            FROM files
            WHERE Owner = '{0}' and Name = ?
            """.format(_client), [file_name])
        return self.cursor.fetchall()

    # Delete file from files table.
    def delete_file(self, client, file_name):
        _client = uuid.UUID(bytes=client)
        self.db.executescript("""
                    DELETE FROM files
                    WHERE Owner = '{0}' and Name = ?
                    """.format(_client))
        self.db.commit()

    # Destructor method
    def __del__(self):
        self.db.close()
