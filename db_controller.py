import sqlite3 as sl
DB_NAME = "Inventory_IL.db"

class DB():
    def __init__(self):
        con = self.get_connection()
        with con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS WATCHLIST (
                    description TEXT,
                    user_id TEXT NOT NULL,
                    website TEXT NOT NULL,
                    serial_number TEXT NOT NULL, 
                    PRIMARY KEY (user_id, website, serial_number) 
                );
            """)

            con.execute("""
            CREATE TABLE IF NOT EXISTS MODE (
            mode TEXT,
            user_id TEXT NOT NULL,
            PRIMARY KEY (user_id)
            );
            """)

    def get_connection(self):
        return sl.connect(DB_NAME)

    def add_to_watchlist(self, website, serial, description, user_id):
        con = self.get_connection()
        try:
            with con:
                con.execute("INSERT INTO WATCHLIST (website, serial_number, description, user_id) VALUES (?, ?, ?, ?)", (website, serial, description, user_id))
        except Exception as e:
            print(e)
            return -1
        return 0

    def remove_from_watchlist(self, website, serial, user_id):
        con = self.get_connection()
        try:
            with con:
                con.execute("DELETE FROM WATCHLIST WHERE website = ? AND serial_number = ? and user_id = ?", (website, serial, user_id))
        except Exception as e:
            print(e)
            return -1
        return 0

    def get_watchlist(self, website, user_id):
        con = self.get_connection()
        try:
            with con:
                cursor = con.execute("SELECT serial_number, description from WATCHLIST WHERE website = ? AND user_id = ?", (website, user_id ))
                all_serials = cursor.fetchall()
                items = []
                for (serial,description, ) in all_serials:
                    items.append((serial, description))
        except Exception as e:
            print(e)
            return -1
        return items

    def set_mode(self, new_mode, user_id):
        con = self.get_connection()
        try:
            with con:
                con.execute("INSERT OR REPLACE INTO MODE (user_id, mode) VALUES (?, ?);", (user_id, new_mode, ))
        except Exception as e:
            print(e)
            return -1
        return 0

    def get_mode(self, user_id):
        con = self.get_connection()
        try:
            with con:
                cursor = con.execute("SELECT mode FROM MODE WHERE user_id = ?", (user_id,))
                (mode,) = cursor.fetchone()
                return mode
        except:
            pass
        return None
    
    def get_users_in_mode(self, mode):
        con = self.get_connection()
        try:
            with con:
                cursor = con.execute("SELECT user_id FROM MODE WHERE mode = ?", (mode,))
                many = cursor.fetchall()
                uids = []
                for (uid, ) in many:
                    uids.append(uid)
                return uids
        except:
            pass
        return []

    def get_users(self):
        con = self.get_connection()
        try:
            with con:
                cursor = con.execute("SELECT user_id FROM MODE")
                all_users = cursor.fetchall()
                uids = []
                for (uid, ) in all_users:
                    uids.append(uid)
                return uids
        except:
            pass
        return []

        