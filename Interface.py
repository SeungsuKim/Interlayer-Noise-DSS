import sys
from InterfaceUI import *
from DBManager import DBManager
from ModelManager import ModelManager
from PyQt5.QtWidgets import QApplication, QMainWindow


class Interface(QMainWindow):

    def __init__(self, model, parent=None):
        super(Interface, self).__init__(parent)

        self.modelManager = model

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.initComboBox(self.ui.comboBoxFirstCriterion)

    def initComboBox(self, comboBox):
        comboBox.addItems(self.modelManager.getCriterions())


if __name__ == "__main__":
    data = DBManager()
    model = ModelManager(data)

    app = QApplication(sys.argv)
    interface = Interface(model)
    interface.show()
    sys.exit(app.exec_())