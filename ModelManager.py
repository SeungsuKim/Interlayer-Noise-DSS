from DBManager import DBManager

class ModelManager:

    def __init__(self):
        self.dbManager = DBManager()

        self.dbManager.updateTable("tech.csv", "techs")

    def loadDB(self, tablename):
        self.db = self.dbManager.fetchTable(tablename)


if __name__ == "__main__":
    m = ModelManager()