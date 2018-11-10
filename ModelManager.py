from DBManager import DBManager


class _Data:
    def __init__(self, name, value, unit):
        self.name = name
        self.value = value
        self.unit = unit


class _Tech:
    def __init__(self, datas):
        self.engName = datas[0]
        self.korName = datas[1]
        self.constructionCost = _Data("Construction Cost", datas[2], "won/m^2")
        self.materialCost = _Data("Material Cost", datas[3], "won/m^2")
        self.totalCost = _Data("Total Cost", datas[4], "won/m^2")
        self.lightLevel = _Data("Light Impact Reduction Level", datas[5], "level")
        self.heavyLevel = _Data("Heavy Impact Reduction Level", datas[6], "level")
        self.longtermness = _Data("LongTermness", datas[7], "months")
        self.universiality = _Data("Universiality", datas[8], "level(1~3)")
        self.constructionDiff = _Data("Construction Difficulty", datas[9], "level(1~3)")
        self.constructionTime = _Data("Constructoin Time", datas[10], "level(1~3)")

        #normalize
        self.vector = datas[2:]

        self.datas = []
        self.datas.append(self.constructionCost)
        self.datas.append(self.materialCost)
        self.datas.append(self.totalCost)
        self.datas.append(self.lightLevel)
        self.datas.append(self.heavyLevel)
        self.datas.append(self.longtermness)
        self.datas.append(self.universiality)
        self.datas.append(self.constructionDiff)
        self.datas.append(self.constructionTime)
    '''
    def __init__(self, vector):
        self.vector = vector
    '''
    def __str__(self):
        description = self.engName + " / " + self.korName

        for data in self.datas:
            description += '\n' + data.name + ": " + str(data.value) + "[" + data.unit + "]"

        return description


class ModelManager:
    def __init__(self):
        self.db = DBManager()
        self.techs = []

        self.db.deleteTable()
        self.db.createTable('tech2.csv', "TECHS")
        self.db.updateTable('tech2.csv', "TECHS")

    def generateTechs(self):
        for datas in self.db.fetchAllTechs():
            tech = _Tech(datas)
            self.techs.append(tech)

    def printTechs(self):
        for tech in self.techs:
            print(tech)
            print('\n')

    @staticmethod
    def _distance(tech1, tech2):
        l2 = 0.0
        for i in range(len(tech1.vector)):
            l2 += tech1.vector[i]**2 + tech2.vector[i]**2
        return l2**0.5

    def sortBySimilarity(self, tech):
        sorted(self.techs, key=lambda t: self._distance(tech, t))
        print(self.techs[0])
        print(self.techs[1])


if __name__ == "__main__":
    mm = ModelManager()
    mm.generateTechs()
    #mm.printTechs()

    tech = _Tech(("Dummy", "-", 8110, 150000, 158110, 37, 1, -1, 2, 1, 1))
    mm.sortBySimilarity(tech)
