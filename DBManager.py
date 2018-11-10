import csv
import sqlite3

typeDict = {"t": "text", "n": "real"}


class DBManager:
    def __init__(self):
        # Connect with SQLite DB
        self.conn = sqlite3.connect("tech.db")

        # Create a cursor from the connection
        self.cur = self.conn.cursor()

        self.datatypes = []

    # filename, tablename
    def createTable(self, filename, tablename):
        try:
            with open(filename, encoding='utf-8-sig') as fin:
                rows = csv.DictReader(fin)
                cols = []
                for fieldname in rows.fieldnames:
                    try:
                        datatype = typeDict[fieldname[0]]
                        cols.append("%s %s" % (fieldname[1:], datatype))
                        self.datatypes.append(datatype)
                    except:
                        print("Can't find a type indicated by " + fieldname[0])
                        return -1

                sqlCreateTable = "CREATE TABLE %s (%s)" % (tablename, ",".join(cols))
                self.cur.execute(sqlCreateTable)
        except FileNotFoundError:
            print('No source .csv file exists at current directory.')

    def updateTable(self, filename, tablename):
        try:
            with open(filename, encoding='utf-8-sig') as fin:
                rows = csv.reader(fin)
                techs = []
                rowIndex = 0
                for row in rows:
                    if rowIndex != 0:
                        tech = []
                        for j in range(len(row)):
                            if self.datatypes[j] == 'text':
                                tech.append(row[j])
                            elif self.datatypes[j] == 'real':
                                tech.append(float(row[j]))
                            else:
                                print("Data type error")
                                return
                        techs.append(tech)
                    rowIndex += 1

                sqlUpdateTable = "INSERT INTO %s VALUES (%s)" % (tablename, ','.join('?' * len(techs[0])))
                self.cur.executemany(sqlUpdateTable, techs)
        except FileNotFoundError:
            print('No source .csv file exists at current directory.')

    def deleteTable(self):
        try:
            self.cur.execute("DROP TABLE TECHS")
        except:
            print("createTable() must be executed before calling deleteTable()")

    def escapingGenerator(self, f):
        for line in f:
            yield line.encode("ascii", "xmlcharrefreplace").decode("ascii")

    def fetchAllTechs(self):
        self.cur.execute("SELECT * FROM TECHS")
        return self.cur.fetchall()


if __name__ == "__main__":
    m = DBManager()
    m.deleteTable()
    m.createTable('tech2.csv')
    m.updateTable('tech2.csv')
    print(m.fetchAllTechs())