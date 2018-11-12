import sys
from InterfaceUI import *
from DBManager import DBManager
from ModelManager import ModelManager, Criterion
from PyQt5.QtWidgets import QApplication, QErrorMessage, QMainWindow


class Interface(QMainWindow):

    def __init__(self, model, parent=None):
        super(Interface, self).__init__(parent)

        self.modelManager = model

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.initComboBox(self.ui.comboBoxFirstCriterion)
        self.initSlider(self.ui.sliderMinimumFirstCriterion, self.ui.comboBoxFirstCriterion, self.ui.labelMinimumValueFirstCriterion)
        self.initSlider(self.ui.sliderMaximumFirstCriterion, self.ui.comboBoxFirstCriterion, self.ui.labelMaximumValueFirstCriterion)
        self.ui.tableResult.setModel(self.modelManager)
        self.errorDialog = QErrorMessage()
        self.connectComboBoxSliderAndLabel(self.ui.comboBoxFirstCriterion, self.ui.sliderMinimumFirstCriterion, self.ui.labelMinimumValueFirstCriterion)
        self.connectComboBoxSliderAndLabel(self.ui.comboBoxFirstCriterion, self.ui.sliderMaximumFirstCriterion, self.ui.labelMaximumValueFirstCriterion)
        self.ui.pushButtonDone.clicked.connect(self.calculateResult)

    def initComboBox(self, comboBox):
        comboBox.addItems(self.modelManager.getCriterions())

    def initSlider(self, slider, comboBox, label):
        minimum, maximum = self.modelManager.getRangeOfCriterion(comboBox.currentText())
        slider.setMinimum(minimum)
        slider.setMaximum(maximum)
        slider.setSingleStep(1)
        slider.setValue((minimum+maximum)//2)
        self.initLabel(label, slider.value())

    def initLabel(self, label, text):
        label.setText(str(text))

    def calculateResult(self):
        firstCriterion = self.ui.comboBoxFirstCriterion.currentText()
        minimum = self.ui.sliderMinimumFirstCriterion.value()
        maximum = self.ui.sliderMaximumFirstCriterion.value()
        if self.ui.radioButtonAscendingOrder.isChecked():
            order = True
        elif self.ui.radioButtonDescendingOrder.isChecked():
            order = False
        else:
            order = None

        if minimum > maximum:
            self.errorDialog.showMessage("The minimum value must be smaller or equal than the maximum value.")
            return

        if order == None:
            self.errorDialog.showMessage("Choose the order.")
            return

        self.modelManager.locData(Criterion(firstCriterion, (minimum, maximum), order))

    def connectComboBoxSliderAndLabel(self, comboBox, slider, label):
        comboBox.currentIndexChanged.connect(lambda: self.initSlider(slider, comboBox, label))
        slider.sliderMoved.connect(lambda text=str(slider.value()): self.initLabel(label, text))


if __name__ == "__main__":
    data = DBManager()
    model = ModelManager(data, "techs")

    app = QApplication(sys.argv)
    interface = Interface(model)
    interface.show()
    sys.exit(app.exec_())