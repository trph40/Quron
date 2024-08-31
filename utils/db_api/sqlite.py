import sqlite3


class DatabaseForSurahs:
    def __init__(self, path_to_db="surahs_file_id.db"):
        self.path_to_db = path_to_db

    @property
    def connection(self):
        return sqlite3.connect(self.path_to_db, timeout=1)

    def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        if not parameters:
            parameters = ()
        connection = self.connection
        connection.set_trace_callback(logger)
        cursor = connection.cursor()
        data = None
        cursor.execute(sql, parameters)

        if commit:
            connection.commit()
        if fetchall:
            data = cursor.fetchall()
        if fetchone:
            data = cursor.fetchone()
        connection.close()
        return data

    def create_table_surah_audio_ar(self):
        sql = """
        CREATE TABLE Audio_ar (
            surah_num int NOT NULL,
            file_id varchar(255) NOT NULL,
            PRIMARY KEY (surah_num)
            );
"""
        self.execute(sql, commit=True)

    def create_table_surah_audio_uz(self):
        sql = """
        CREATE TABLE  Audio_uz(
            surah_num int NOT NULL,
            file_id varchar(255) NOT NULL,
            PRIMARY KEY (surah_num)
            );
"""
        self.execute(sql, commit=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ?" for item in parameters
        ])
        return sql, tuple(parameters.values())

    def add_file_id_ar(self, surah_num: int, file_id: str):
        # SQL_EXAMPLE = "INSERT INTO Users(id, Name, email) VALUES(1, 'John', 'John@gmail.com')"

        sql = """
        INSERT INTO Audio_ar(surah_num, file_id) VALUES(?, ?)
        """
        self.execute(sql, parameters=(surah_num, file_id), commit=True)

    def add_file_id_uz(self, surah_num: int, file_id: str):
        # SQL_EXAMPLE = "INSERT INTO Users(id, Name, email) VALUES(1, 'John', 'John@gmail.com')"

        sql = """
        INSERT INTO Audio_uz(surah_num, file_id) VALUES(?, ?)
        """
        self.execute(sql, parameters=(surah_num, file_id), commit=True)

    def select_surah_ar(self, **kwargs):
        # SQL_EXAMPLE = "SELECT * FROM Users where id=1 AND Name='John'"
        sql = "SELECT file_id FROM Audio_ar WHERE "
        sql, parameters = self.format_args(sql, kwargs)
        return self.execute(sql, parameters=parameters, fetchone=True)

    def select_surah_uz(self, **kwargs):
        # SQL_EXAMPLE = "SELECT * FROM Users where id=1 AND Name='John'"
        sql = "SELECT file_id FROM Audio_uz WHERE "
        sql, parameters = self.format_args(sql, kwargs)
        return self.execute(sql, parameters=parameters, fetchone=True)


    def count_surahs_ar(self):
        return self.execute("SELECT COUNT(*) FROM Audio_ar;", fetchone=True)


    def count_surahs_uz(self):
        return self.execute("SELECT COUNT(*) FROM Audio_uz;", fetchone=True)

    def connec_stop(self):
        return self.connection.close()
def logger(statement):
    print(f"""
_____________________________________________________        
Executing: 
{statement}
_____________________________________________________
""")
