from PyQt5 import QtCore, QtGui


class Criterion():

    def __init__(self, criterion, range, order):
        self.criterion = criterion
        self.range = range
        self.order = order


class ModelManager(QtCore.QAbstractTableModel):

    def __init__(self, data, tableName, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._tableName = tableName
        self._dataManager = data
        self._data = self._dataManager.fetchTable(tableName)

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

    def getCriterions(self):
        return list(self._data.columns.values[3:])

    def getRangeOfCriterion(self, criterion):
        minimum = self._data[criterion].min()
        maximum = self._data[criterion].max()
        return minimum, maximum

    def locData(self, cri):
        self._data = self._data.loc[self._data[cri.criterion] >= cri.range[0]]
        self._data = self._data.loc[self._data[cri.criterion] <= cri.range[1]]
        self._data = self._data.sort_values(by=[cri.criterion], ascending=cri.order)