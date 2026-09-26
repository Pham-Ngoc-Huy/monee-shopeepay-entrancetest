from database.database import DataBase
path_database = "database/sql_questions.db"

conn = DataBase(path=path_database)

print(conn.query("select * from dim_user"))
