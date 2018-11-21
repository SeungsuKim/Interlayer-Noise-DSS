import sys, copy
from InterfaceUI import *
from DBManager import DBManager
from ModelManager import ModelManager, Criterion
from PyQt5.QtWidgets import QApplication, QErrorMessage, QMainWindow
from PyQt5.QtGui import QStandardItemModel, QStandardItem


class Interface(QMainWindow):

    def __init__(self, model, parent=None):
        super(Interface, self).__init__(parent)

        self.modelManager = model

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.numCriterion = 2
        self.sourceList = self.ui.listViewSource
        self.comboBoxs = [self.ui.comboBoxFirstCriterion, self.ui.comboBoxSecondCriterion]
        self.sliders = [[self.ui.sliderMinimumFirstCriterion, self.ui.sliderMaximumFirstCriterion],
                        [self.ui.sliderMinimumSecondCriterion, self.ui.sliderMaximumSecondCriterion]]
        self.labelsValue = [[self.ui.labelMinimumValueFirstCriterion, self.ui.labelMaximumValueFirstCriterion],
                            [self.ui.labelMinimumValueSecondCriterion, self.ui.labelMaximumValueSecondCriterion]]
        self.spinBoxs = [self.ui.spinBoxFirstCriterionWeight, self.ui.spinBoxSecondCriterionWeight]
        self.lineEdits = [self.ui.lineFirstCriterionIdealValue, self.ui.lineSecondCriterionIdealValue]
        self.radioButtons = [[self.ui.radioButtonFirstCriterionAscendingOrder, self.ui.radioButtonFirstCriterionDescendingOrder],
                             [self.ui.radioButtonSecondCriterionAscendingOrder, self.ui.radioButtonSecondCriterionDescendingOrder]]
        self.radioButtonsDisabled = [False, False]

        self.initSourceList(self.sourceList)
        for i in range(self.numCriterion):
            self.initComboBox(self.comboBoxs[i])
            for j in range(2):
                self.initSlider(self.sliders[i][j], self.comboBoxs[i], self.labelsValue[i][j])
            self.initSpinBox(self.spinBoxs[i])
        self.ui.tableResult.setModel(self.modelManager)
        self.errorDialog = QErrorMessage()
        for i in range(self.numCriterion):
            for j in range(2):
                self.connectComboBoxSliderAndLabel(self.comboBoxs[i], self.sliders[i][j], self.labelsValue[i][j])
        self.ui.lineFirstCriterionIdealValue.textChanged.connect(lambda: self.changeStateRadioButton(self.radioButtons[0], 0))
        self.ui.lineSecondCriterionIdealValue.textChanged.connect(lambda: self.changeStateRadioButton(self.radioButtons[1], 1))
        self.ui.pushButtonCriterionDone.clicked.connect(self.calculateResult)
        self.ui.pushButtonSourceDone.clicked.connect(self.analyzeSource)

    def initComboBox(self, comboBox):
        comboBox.addItems(self.modelManager.getCriterions())

    def initSlider(self, slider, comboBox, label):
        self.modelManager.loadData()
        minimum, maximum = self.modelManager.getRangeOfCriterion(comboBox.currentText())
        slider.setMinimum(int(minimum))
        slider.setMaximum(int(maximum))
        slider.setSingleStep(1)
        slider.setValue((minimum+maximum)//2)
        self.initLabel(label, slider.value())

    def initLabel(self, label, text):
        label.setText(str(text))

    def initSpinBox(self, spinBox):
        spinBox.setMinimum(1)
        spinBox.setMaximum(10)

    def initSourceList(self, sourceList):
        model = QStandardItemModel()
        for source in self.modelManager.getSources():
            item = QStandardItem(source)
            item.setCheckable(True)
            model.appendRow(item)
        sourceList.setModel(model)

    def changeStateRadioButton(self, radioButtons, i):
        if self.lineEdits[i].text() != "":
            radioButtons[0].setDisabled(True)
            radioButtons[1].setDisabled(True)
            self.radioButtonsDisabled[i] = True
        else:
            radioButtons[0].setDisabled(False)
            radioButtons[1].setDisabled(False)
            self.radioButtonsDisabled[i] = False

    def calculateResult(self):
        self.modelManager.loadData()

        criterions = []
        for i in range(self.numCriterion):
            criterions.append(Criterion())

        for i in range(self.numCriterion):
            if i != self.numCriterion-1:
                if self.comboBoxs[i].currentText() == self.comboBoxs[i+1].currentText():
                    self.errorDialog.showMessage("Two criterions must be different.")
                    return
            criterions[i].criterion = self.comboBoxs[i].currentText()

            minimum, maximum = self.sliders[i][0].value(), self.sliders[i][1].value()
            if minimum > maximum:
                self.errorDialog.showMessage("The minimum value must be smaller or equal than the maximum value.")
                return
            criterions[i].range = (minimum, maximum)

            idealValue = self.lineEdits[i].text()
            if idealValue != "":
                try:
                    idealValue = int(idealValue)
                    if minimum > idealValue or maximum < idealValue:
                        self.errorDialog.showMessage("The ideal value must be between the maximum and minimum value.")
                        return
                except ValueError:
                    self.errorDialog.showMessage("The ideal value must be an integer")
                    return
            criterions[i].idealValue = idealValue

            if self.radioButtons[i][0].isChecked():
                order = True
            elif self.radioButtons[i][1].isChecked():
                order = False
            else:
                order = None
            if not self.radioButtonsDisabled[i]:
                if order is None:
                    self.errorDialog.showMessage("Choose the order.")
                    return
                criterions[i].order = order

        self.modelManager.locData(criterions)
        if (not self.radioButtonsDisabled[0]) and (not self.radioButtonsDisabled[1]):
            self.modelManager.sortData(criterions)
        else:
            scores= self.modelManager.sortNormalizedData(criterions)
            print(scores)

    def analyzeSource(self):
        model = self.sourceList.model()
        for i in range(model.rowCount()):
            item = model.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                print(item.text())

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