import sys, random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

from operator import add
from InterfaceUI import *
from TechnologyUI import *
from MessageUI import *
from DBManager import DBManager
from ModelManager import ModelManager, Criterion
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QErrorMessage, QMainWindow, QWidget, QVBoxLayout, QGraphicsScene, QSizePolicy
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QPixmap

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class Interface(QMainWindow):

    def __init__(self, model, parent=None):
        super(Interface, self).__init__(parent)

        self.modelManager = model

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.detailDialog = QWidget()
        self.detailUI = Ui_Form()
        self.detailUI.setupUi(self.detailDialog)

        self.messageDialog = QWidget()
        self.messageUI = Ui_Message()
        self.messageUI.setupUi(self.messageDialog)

        self.errorDialog = QErrorMessage()

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
        self.initPlotTab()
        for i in range(self.numCriterion):
            self.initComboBox(self.comboBoxs[i])
            for j in range(2):
                self.initSlider(self.sliders[i][j], self.comboBoxs[i], self.labelsValue[i][j])
            self.initSpinBox(self.spinBoxs[i])
        self.ui.tableResult.setModel(self.modelManager)

        for i in range(self.numCriterion):
            for j in range(2):
                self.connectComboBoxSliderAndLabel(self.comboBoxs[i], self.sliders[i][j], self.labelsValue[i][j])
        self.ui.lineFirstCriterionIdealValue.textChanged.connect(lambda: self.changeStateRadioButton(self.radioButtons[0], 0))
        self.ui.lineSecondCriterionIdealValue.textChanged.connect(lambda: self.changeStateRadioButton(self.radioButtons[1], 1))
        self.ui.tableResult.doubleClicked.connect(self.showDetail)
        self.ui.pushButtonCriterionDone.clicked.connect(self.calculateResult)
        self.ui.pushButtonSourceDone.clicked.connect(self.analyzeSource)
        self.messageUI.pushButtonNo.clicked.connect(self.messageDialog.close)
        self.messageUI.pushButtonYes.clicked.connect(self.locIntensity)

    def locIntensity(self):
        self.modelManager.loadData()

        lightCriterion = Criterion()
        heavyCriterion = Criterion()
        lightCriterion.criterion = "경량충격음 차단성능 (등급)"
        heavyCriterion.criterion = "중량충격음 차단성능 (등급)"
        lightCriterion.range = (1, self.recomLight)
        heavyCriterion.range = (1, self.recomHeavy)
        self.modelManager.locData([lightCriterion, heavyCriterion])

        self.messageDialog.close()

    def showDetail(self, signal):
        row = signal.row()
        detailData = self.modelManager.getTechByIndex(row)

        self.detailUI.labelTechName.setText(str(detailData["구조명"]))
        self.detailUI.labelCategoryValue.setText(str(detailData["분류"]) + "(" + str(detailData["기타"]) + ")")
        self.detailUI.labelLightLevelValue.setText(str(detailData["경량충격음 차단성능 (등급)"]))
        self.detailUI.labelHeavyLevelValue.setText(str(detailData["중량충격음 차단성능 (등급)"]))
        self.detailUI.labelBufferCostValue.setText(str(detailData["완충재 추산가격 (원)"]))
        self.detailUI.labelBufferLabelCostValue.setText(str(detailData["완충재 노무비 (원)"]))
        self.detailUI.labelMortarThicknessValue.setText(str(detailData["마감 모르타르 두께 (mm)"]))
        self.detailUI.labelConcereteThicknessValue.setText(str(detailData["경량기포 콘크리트 두께 (mm)"]))
        self.detailUI.labelTotalThicknessValue.setText(str(detailData["전체 두께 (mm)"]))
        self.detailUI.labelTotalCostValue.setText(str(detailData["전체 가격 (원)"]))

        imgName = "thumbnails/" + str(detailData["구조명"]) + " 1.png"
        size = self.detailUI.graphicsViewThumnail.size()
        pixmap = QPixmap(imgName).scaled(size, Qt.KeepAspectRatio)
        scene = QGraphicsScene()
        scene.addPixmap(pixmap)
        self.detailUI.graphicsViewThumnail.setScene(scene)
        self.detailUI.graphicsViewThumnail.show()

        self.detailDialog.show()

    def initPlotTab(self):
        font_name = fm.FontProperties(fname="malgun.ttf").get_name()
        plt.rc('font', family=font_name)

        self.plotTab = QWidget()
        self.ui.tabWidget.addTab(self.plotTab, "Plotted Result")
        self.figure = plt.figure(figsize=(10, 5))
        self.canvas = FigureCanvas(self.figure)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.ui.tabWidget.widget(2).setLayout(layout)

    def initComboBox(self, comboBox):
        print(self.modelManager.getCriterions())
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
            if minimum >= maximum:
                self.errorDialog.showMessage("The minimum value must be smaller than the maximum value.")
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

        numData = self.modelManager.locData(criterions)
        if numData == 0:
            self.errorDialog.showMessage("There is no technology satisfying the conditions.")
            return

        if (not self.radioButtonsDisabled[0]) and (not self.radioButtonsDisabled[1]):
            self.modelManager.sortData(criterions)
        else:
            scores, sorted_index = self.modelManager.sortNormalizedData(criterions)

            plt.gcf().clear()
            ind = np.arange(len(sorted_index))
            ax = self.figure.add_subplot(111)
            bars = []
            '''
            if len(sorted_index) > 10:
                sorted_index = sorted_index[:10]
            '''
            for i in range(len(scores)):
                scores[i] = [scores[i][j] for j in sorted_index]
                bottom = None if i==0 else scores[i-1]
                bars.append(ax.bar(ind, scores[i], bottom=bottom))
            plt.ylabel('Scores')
            plt.title('Scores of each technology by selected criterions.')
            legend = []
            for cri in criterions:
                legend.append(cri.criterion)
            techNames = self.modelManager.getTechNames()
            xticks = [techNames[i] for i in sorted_index]
            plt.xticks(ind, xticks, rotation=20, fontsize="x-small")
            plt.legend(bars, legend)

            self.canvas.draw()

    def analyzeSource(self):
        model = self.sourceList.model()
        sourceNames = list()
        for i in range(model.rowCount()):
            item = model.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                sourceNames.append(item.text())
        maxLight = 0
        maxHeavy = 0
        for sourceName in sourceNames:
            _, maximum = self.modelManager.getIntensity(sourceName)
            if self.modelManager.getCategory(sourceName) == "경량":
                if maximum > maxLight:
                    maxLight = maximum
            else:
                if maximum > maxHeavy:
                    maxHeavy = maximum
        self.recomLight = self.recommendedLevel(maxLight)
        self.recomHeavy = self.recommendedLevel(maxHeavy)
        message = "The minimum legal standard for light and heavy impact sound is 50 and 58dB. To satisfy this" \
                  "standard, technology with light impact reduction grade of " + str(self.recomLight) + "and heavy impact" \
                  "reduction grade of " + str(self.recomHeavy) + " is required. Do you want to add this to the searching condition?"
        self.messageUI.textBrowserMessage.setText(message)
        self.messageDialog.show()

    def recommendedLevel(self, intensity):
        if intensity < 20:
            return 4
        if intensity < 40:
            return 3
        if intensity < 60:
            return 2
        return 1

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