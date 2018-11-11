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
        self.initSlider(self.ui.sliderMinimumFirstCriterion, self.ui.comboBoxFirstCriterion, self.ui.labelMinimumValueFirstCriterion)
        self.initSlider(self.ui.sliderMaximumFirstCriterion, self.ui.comboBoxFirstCriterion, self.ui.labelMaximumValueFirstCriterion)
        self.connectComboBoxSliderAndLabel(self.ui.comboBoxFirstCriterion, self.ui.sliderMinimumFirstCriterion, self.ui.labelMinimumValueFirstCriterion)
        self.connectComboBoxSliderAndLabel(self.ui.comboBoxFirstCriterion, self.ui.sliderMaximumFirstCriterion, self.ui.labelMaximumValueFirstCriterion)

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

    def connectComboBoxSliderAndLabel(self, comboBox, slider, label):
        comboBox.currentIndexChanged.connect(lambda: self.initSlider(slider, comboBox, label))
        slider.sliderMoved.connect(lambda text=str(slider.value()): self.initLabel(label, text))


if __name__ == "__main__":
    data = DBManager()
    model = ModelManager(data)

    app = QApplication(sys.argv)
    interface = Interface(model)
    interface.show()
    sys.exit(app.exec_())