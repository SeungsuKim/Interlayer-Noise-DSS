import copy
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

    def getCriterions(self):
        return list(self._data.columns.values[3:])

    def getRangeOfCriterion(self, criterion):
        minimum = self._data[criterion].min()
        maximum = self._data[criterion].max()
        return minimum, maximum

    def locData(self, criterions):
        for cri in criterions:
            self._data = self._data.loc[self._data[cri.criterion] >= cri.range[0]]
            self._data = self._data.loc[self._data[cri.criterion] <= cri.range[1]]

    def sortData(self, criterions):
        for cri in criterions:
            self._data = self._data.sort_values(by=[cri.criterion], ascending=cri.order)

    def sortNormalizedData(self, criterions):
        self._data_normalized = copy.deepcopy(self._data)
        idealValues = list()
        scores = [[],[]]
        cris = []
        for cri in criterions:
            idealValues.append(((cri.idealValue-self._data_normalized[cri.criterion].min())/(self._data_normalized[cri.criterion].max()-self._data_normalized[cri.criterion].min()))/cri.weight)
            self._data_normalized[cri.criterion] = ((self._data_normalized[cri.criterion]-self._data_normalized[cri.criterion].min())/(self._data_normalized[cri.criterion].max()-self._data_normalized[cri.criterion].min()))
            cris.append(cri.criterion)
        distances = [0] * self._numTech
        self._data_normalized = self._data_normalized[cris]
        for index, row in self._data_normalized.iterrows():
            for j, vec in enumerate(row):
                distance = (idealValues[j]-vec)**2
                print(index, len(distances))
                distances[index] += distance
                scores[j].append(1/distance)
        print(self._data_normalized)
        print(self._data)
        print(list(self._data['index']))
        sorted_index = sorted(list(self._data['index']), key=lambda k: distances[k])
        print(sorted_index)
        self._data = self._data.loc[sorted_index]
        return scores


class SourceModelManager(QtCore.QAbstractListModel):

    def __init__(self, data, tableName, parent=None, *args):
        super(SourceModelManager, self).__init__(parent, *args)

        self._tableName = tableName
        self._dataManager = data
        self._data = self._dataManager.fetchTable(self._tableName)

    def loadData(self):
        self._data = self._dataManager.fetchTable(self._tableName)

    def data(self, index, role):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(str(self._data.iloc[1, index.column()]))
        return None

