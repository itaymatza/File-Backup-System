""" Message-U Database - DB manager."""
import uuid
import sqlite3


class DataBase:
    def __init__(self):
        try:
            self.db = sqlite3.connect('server.db')
            self.db.text_factory = bytes
            self.cursor = self.db.cursor()
            sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)
            self.init_sql_tables()
        except sqlite3.Error as e:
            raise sqlite3.Error('Database error: %s' % e)

    def __del__(self):
        self.db.close()

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

    # If not exist, create 'clients' and 'messages' SQL tables.
    def init_sql_tables(self):
        if not self._is_table_exists('clients'):
            self.db.executescript(""" CREATE TABLE clients(
            ID varchar(16) NOT NULL PRIMARY KEY, 
            Name varchar(255), 
            PublicKey varchar(160), 
            LastSeen text);
            """)
        if not self._is_table_exists('messages'):
            self.db.executescript(""" CREATE TABLE messages(
            ID INTEGER PRIMARY KEY,
            ToClient varchar(16),
            FromClient varchar(16), 
            Type INT1, 
            Content Blob);
            """)
        self.db.commit()

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
        uid = uuid.UUID(bytes=uid)
        self.cursor.execute("""
            SELECT COUNT(*)
            FROM clients
            WHERE ID = '{0}'
            """.format(uid))
        if self.cursor.fetchone()[0] != 0:
            return True
        return False

    # Generates new uuid and make sure is not already in clients table.
    def _get_new_uuid(self):
        uid = uuid.uuid4()
        while self.is_id_exists(uid.bytes):
            uid = uuid.uuid4()
        return uid

    # Add new client to clients table.
    def add_client(self, name, key):
        uid = self._get_new_uuid()
        self.cursor.execute("""
                INSERT INTO clients VALUES ('{0}', ?, ?, datetime('now'))
                """.format(uid), [name, key])
        self.db.commit()
        return uid

    # Add new client to clients table.
    def update_client_last_seen(self, uid):
        uid = uuid.UUID(bytes=uid)
        self.cursor.execute("""
                UPDATE clients SET LastSeen = datetime('now')
                WHERE ID = '{0}'
                """.format(uid))
        self.db.commit()
        return uid

    # Returns clients list except of the given uid.
    def get_clients_list(self, uid):
        uid = uuid.UUID(bytes=uid)
        self.cursor.execute("""
            SELECT ID, Name
            FROM clients
            WHERE ID != '{0}'
            """.format(uid))
        return self.cursor.fetchall()

    # Returns public key of the given uid.
    def get_public_key(self, uid):
        uid = uuid.UUID(bytes=uid)
        self.cursor.execute("""
            SELECT ID, PublicKey
            FROM clients
            WHERE ID = '{0}'
            """.format(uid))
        return self.cursor.fetchall()

    # Add message to messages table.
    def add_message(self, to_client, from_client, message_type, message_content):
        to_client = uuid.UUID(bytes=to_client)
        from_client = uuid.UUID(bytes=from_client)
        self.db.execute("""
                    INSERT INTO messages (ToClient, FromClient, Type, Content)
                    VALUES ('{0}', '{1}', ?, ?)
                    """.format(to_client, from_client),
                        [message_type, message_content])
        self.db.commit()

        self.cursor.execute("""
            SELECT last_insert_rowid()
            """)
        return self.cursor.fetchall()[0][0]

    # Pull messages from messages table.
    def pull_messages(self, to_client):
        to_client = uuid.UUID(bytes=to_client)
        self.cursor.execute("""
            SELECT FromClient, ID, Type, Content
            FROM messages
            WHERE ToClient = '{0}'
            """.format(to_client))
        return self.cursor.fetchall()

    # Delete messages from messages table.
    def delete_messages(self, to_client):
        to_client = uuid.UUID(bytes=to_client)
        self.db.executescript("""
                    DELETE FROM messages
                    WHERE ToClient = '{0}'
                    """.format(to_client))
        self.db.commit()
