import pandas as pd
import sqlite3

class DBManager:

    def __init__(self):
        self.conn = sqlite3.connect("tech.db")
        self.cur = self.conn.cursor()

    def updateTable(self, filename, tablename):
        self.deleteTable(tablename)

        df = pd.read_csv(filename)
        df.to_sql(tablename, self.conn)

    def deleteTable(self, tablename):
        try:
            self.cur.execute("DROP TABLE " + tablename)
        except sqlite3.OperationalError:
            print("The table must be created before deleted.")

    def fetchTable(self, tablename):
        qurey = "SELECT * FROM " + tablename
        return pd.read_sql(qurey, self.conn, index_col="tEngName")


if __name__ == "__main__":
    m = DBManager()
    m.updateTable("tech.csv", "techs")
    df = m.fetchTable("techs")
    print(df['n보편성'])