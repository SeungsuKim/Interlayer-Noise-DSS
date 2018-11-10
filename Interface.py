import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QAction, QTableView, QVBoxLayout
from PyQt5.QtGui import QIcon
from DBManager import DBManager
from ModelManager import ModelManager


class Interface(QWidget):

    def __init__(self, title, model):
        super().__init__()

        self.title = title
        self.model = model
        self.geometry = (10, 10, 640, 480)
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(*self.geometry)

        self.createTable()

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableView)
        self.setLayout(self.layout)

        self.show()

    def createTable(self):
        self.tableView = QTableView()
        self.tableView.setModel(self.model)
        self.tableView.move(0, 0)


if __name__ == "__main__":
    dbm = DBManager()
    mm = ModelManager(dbm.fetchTable("techs"))

    app = QApplication(sys.argv)
    ex = Interface("Sample Window", mm)
    sys.exit(app.exec_())