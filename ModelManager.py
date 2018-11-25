import sys, copy
from PyQt5 import QtCore, QtGui


class Criterion():

    def __init__(self, criterion, range, idealValue, order, weight):
        self.criterion = criterion
        self.range = range
        self.idealValue = idealValue
        self.order = order
        self.weight = weight

    def __init__(self):
        self.criterion = ""
        self.range = (0, 0)
        self.idealValue = 0
        self.order = None
        self.weight = 1


class ModelManager(QtCore.QAbstractTableModel):

    def __init__(self, data, tableName, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._tableName = tableName
        self._dataManager = data
        self._data = self._dataManager.fetchTable(self._tableName)
        self._dataOrigin = self._dataManager.fetchTable(self._tableName)
        self._dataSource = self._dataManager.fetchTable("sources")
        self._numTech = len(self._data)

    def loadData(self):
        self._data = self._dataManager.fetchTable(self._tableName)

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(str(self._data.iloc[index.row(), index.column()]))
        return None

    def headerData(self, p_int, orientation, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._data.columns[p_int]
        return None

    def getSources(self):
        return list(self._dataSource["소음원"])

    def getCategory(self, source):
        row = self._dataSource.loc[self._dataSource["소음원"] == source]
        return str(row["분류"])

    def getIntensity(self, source):
        row = self._dataSource.loc[self._dataSource["소음원"]==source]
        return int(row["최소 세기"]), int(row["최대 세기"])

    def getTechNames(self):
        return list(self._dataOrigin['구조명'])

    def getTechByIndex(self, index):
        return self._data.iloc[index, :]

    def getCriterions(self):
        criterions = list(self._data.columns.values[4:])
        criterions.remove("유효기간")
        return criterions

    def getRangeOfCriterion(self, criterion):
        minimum = self._data[criterion].min()
        maximum = self._data[criterion].max()
        return minimum, maximum

    def locData(self, criterions):
        for cri in criterions:
            self._data = self._data.loc[self._data[cri.criterion] >= cri.range[0]]
            self._data = self._data.loc[self._data[cri.criterion] <= cri.range[1]]
        return len(self._data)

    def sortData(self, criterions):
        for cri in criterions:
            self._data = self._data.sort_values(by=[cri.criterion], ascending=cri.order)

    def sortNormalizedData(self, criterions):
        self._data_normalized = copy.deepcopy(self._data)
        idealValues = list()
        distances = list()
        scores = list()
        cris = list()
        for i in range(len(criterions)):
            distances.append([None]*self._numTech)
            scores.append([0]*self._numTech)
        for i, cri in enumerate(criterions):
            minimum, maximum = cri.range
            idealValues.append((cri.idealValue-minimum)/(maximum-minimum)/cri.weight)
            self._data_normalized[cri.criterion] = (self._data_normalized[cri.criterion]-minimum)/(maximum-minimum)/cri.weight
            cris.append(cri.criterion)
        self._data_normalized = self._data_normalized[cris]

        for index, row in self._data_normalized.iterrows():
            for j, vec in enumerate(row):
                distance = (idealValues[j]-vec)**2
                distances[j][index] = distance

        for i in range(len(distances)):
            for j in range(len(distances[0])):
                if not distances[i][j] == None:
                    if distances[i][j] == 0:
                        scores[i][j] = sys.maxsize/len(criterions)
                    else:
                        scores[i][j] = 1/distances[i][j]

        totalScores = [0] * self._numTech
        for j in range(len(distances[0])):
            for i in range(len(distances)):
                totalScores[j] += scores[i][j]
        for i in range(len(distances)):
            for j in range(len(distances[0])):
                if totalScores[j] == 0:
                    scores[i][j] = 0
                else:
                    scores[i][j] /= totalScores[j]
        minScore = min(totalScores)
        maxScore = max(totalScores)
        totalScores = [(score-minScore)/(maxScore-minScore)*100 for score in totalScores]
        for i in range(len(distances)):
            for j in range(len(distances[0])):
                scores[i][j] *= totalScores[j]
        sorted_index = sorted(range(len(totalScores)), key=lambda k: totalScores[k])
        for i in range(len(totalScores)):
            if totalScores[i] < 0.0001:
                sorted_index.remove(i)
        sorted_index.reverse()
        print(self._data_normalized)
        print(scores, sorted_index)
        self._data = self._data.reindex(sorted_index)
        return scores, sorted_index[:10]



    '''
    def sortNormalizedData(self, criterions):
        self._data_normalized = copy.deepcopy(self._data)
        idealValues = list()
        scores = []
        sorted_index = []
        for i in range(len(criterions)):
            scores.append([0] * self._numTech)
        cris = []
        if len(self._data) >= 2:
            for cri in criterions:
                miminum = self._data_normalized[cri.criterion].min()
                maximum = self._data_normalized[cri.criterion].max()
                if minimum == maximum:
                    self._data_normalized[cri.criterion] = 0.5
                else:
                    idealValues.append(((cri.idealValue-self._data_normalized[cri.criterion].min())/(self._data_normalized[cri.criterion].max()-self._data_normalized[cri.criterion].min()))/cri.weight)
                    self._data_normalized[cri.criterion] = ((self._data_normalized[cri.criterion]-self._data_normalized[cri.criterion].min())/(self._data_normalized[cri.criterion].max()-self._data_normalized[cri.criterion].min()))
                cris.append(cri.criterion)
        distances = [0] * self._numTech
        self._data_normalized = self._data_normalized[cris]
        for index, row in self._data_normalized.iterrows():
            for j, vec in enumerate(row):
                distance = (idealValues[j]-vec)**2
                distances[index] += distance
                scores[j][index] = 1/distance
        print(self._data)
        print(list(self._data['index']))
        sorted_index = sorted(list(self._data['index']), key=lambda k: distances[k])
        print(sorted_index)
        print(distances)
        return scores, sorted_index
    '''