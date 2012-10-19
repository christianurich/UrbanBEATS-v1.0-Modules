# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'delinblocksgui.ui'
#
# Created: Tue Oct 16 09:18:12 2012
#      by: PyQt4 UI code generator 4.8.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_DelinBlocksDialog(object):
    def setupUi(self, DelinBlocksDialog):
        DelinBlocksDialog.setObjectName(_fromUtf8("DelinBlocksDialog"))
        DelinBlocksDialog.resize(641, 371)
        DelinBlocksDialog.setWindowTitle(QtGui.QApplication.translate("DelinBlocksDialog", "Spatial Delineation Module", None, QtGui.QApplication.UnicodeUTF8))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/general/ublogo33.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        DelinBlocksDialog.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(DelinBlocksDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.title_frame = QtGui.QFrame(DelinBlocksDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.title_frame.sizePolicy().hasHeightForWidth())
        self.title_frame.setSizePolicy(sizePolicy)
        self.title_frame.setMinimumSize(QtCore.QSize(0, 50))
        self.title_frame.setMaximumSize(QtCore.QSize(16777215, 50))
        self.title_frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.title_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.title_frame.setObjectName(_fromUtf8("title_frame"))
        self.dbtitle = QtGui.QLabel(self.title_frame)
        self.dbtitle.setGeometry(QtCore.QRect(50, 5, 441, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.dbtitle.setFont(font)
        self.dbtitle.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Spatial Delineation of Building Blocks", None, QtGui.QApplication.UnicodeUTF8))
        self.dbtitle.setObjectName(_fromUtf8("dbtitle"))
        self.dbsubtitle = QtGui.QLabel(self.title_frame)
        self.dbsubtitle.setGeometry(QtCore.QRect(50, 25, 561, 16))
        self.dbsubtitle.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Processes Input Data and creates the grid of cells that represents a discretised version of the case study region.", None, QtGui.QApplication.UnicodeUTF8))
        self.dbsubtitle.setObjectName(_fromUtf8("dbsubtitle"))
        self.bpmlogo = QtGui.QLabel(self.title_frame)
        self.bpmlogo.setGeometry(QtCore.QRect(0, 0, 50, 50))
        self.bpmlogo.setMaximumSize(QtCore.QSize(50, 50))
        self.bpmlogo.setText(_fromUtf8(""))
        self.bpmlogo.setPixmap(QtGui.QPixmap(_fromUtf8(":/general/ublogo50.png")))
        self.bpmlogo.setObjectName(_fromUtf8("bpmlogo"))
        self.line = QtGui.QFrame(self.title_frame)
        self.line.setGeometry(QtCore.QRect(50, 40, 573, 20))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line.sizePolicy().hasHeightForWidth())
        self.line.setSizePolicy(sizePolicy)
        self.line.setMinimumSize(QtCore.QSize(573, 0))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.verticalLayout.addWidget(self.title_frame)
        self.widget = QtGui.QWidget(DelinBlocksDialog)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.widget)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.scrollArea = QtGui.QScrollArea(self.widget)
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 429, 1086))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.gensim_widget = QtGui.QWidget(self.scrollAreaWidgetContents)
        self.gensim_widget.setMinimumSize(QtCore.QSize(0, 60))
        self.gensim_widget.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.gensim_widget.setObjectName(_fromUtf8("gensim_widget"))
        self.blocksize_lbl = QtGui.QLabel(self.gensim_widget)
        self.blocksize_lbl.setGeometry(QtCore.QRect(20, 29, 71, 16))
        self.blocksize_lbl.setWhatsThis(QtGui.QApplication.translate("DelinBlocksDialog", "Width of the square cell in the city grid in metres", None, QtGui.QApplication.UnicodeUTF8))
        self.blocksize_lbl.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Block Size [m]", None, QtGui.QApplication.UnicodeUTF8))
        self.blocksize_lbl.setObjectName(_fromUtf8("blocksize_lbl"))
        self.optionsgs_lbl = QtGui.QLabel(self.gensim_widget)
        self.optionsgs_lbl.setGeometry(QtCore.QRect(10, 5, 111, 16))
        self.optionsgs_lbl.setWhatsThis(QtGui.QApplication.translate("DelinBlocksDialog", "Width of the square cell in the city grid in metres", None, QtGui.QApplication.UnicodeUTF8))
        self.optionsgs_lbl.setText(QtGui.QApplication.translate("DelinBlocksDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt; font-weight:600;\">General Simulation</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.optionsgs_lbl.setObjectName(_fromUtf8("optionsgs_lbl"))
        self.blocksize_in = QtGui.QSpinBox(self.gensim_widget)
        self.blocksize_in.setGeometry(QtCore.QRect(100, 30, 61, 16))
        self.blocksize_in.setMinimum(200)
        self.blocksize_in.setMaximum(5000)
        self.blocksize_in.setSingleStep(50)
        self.blocksize_in.setProperty("value", 500)
        self.blocksize_in.setObjectName(_fromUtf8("blocksize_in"))
        self.blocksize_auto = QtGui.QCheckBox(self.gensim_widget)
        self.blocksize_auto.setGeometry(QtCore.QRect(180, 30, 171, 17))
        self.blocksize_auto.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Auto-determine Block Size", None, QtGui.QApplication.UnicodeUTF8))
        self.blocksize_auto.setObjectName(_fromUtf8("blocksize_auto"))
        self.verticalLayout_3.addWidget(self.gensim_widget)
        self.inputdata_widget = QtGui.QWidget(self.scrollAreaWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.inputdata_widget.sizePolicy().hasHeightForWidth())
        self.inputdata_widget.setSizePolicy(sizePolicy)
        self.inputdata_widget.setMinimumSize(QtCore.QSize(0, 540))
        self.inputdata_widget.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.inputdata_widget.setObjectName(_fromUtf8("inputdata_widget"))
        self.soc_par1_box = QtGui.QLineEdit(self.inputdata_widget)
        self.soc_par1_box.setGeometry(QtCore.QRect(230, 400, 161, 20))
        self.soc_par1_box.setText(_fromUtf8(""))
        self.soc_par1_box.setObjectName(_fromUtf8("soc_par1_box"))
        self.soc_par1_check = QtGui.QCheckBox(self.inputdata_widget)
        self.soc_par1_check.setGeometry(QtCore.QRect(30, 400, 191, 17))
        self.soc_par1_check.setWhatsThis(QtGui.QApplication.translate("DelinBlocksDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Check this box if you would like to experiment with social parameters. DAnCE4Water-BPM (when used as standalone) allows for a maximum of two socio-economic parameters to be specified. Input must be in the form of probabilities (between 0 and 1).</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.soc_par1_check.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Include Social Parameter 1 - Name:", None, QtGui.QApplication.UnicodeUTF8))
        self.soc_par1_check.setObjectName(_fromUtf8("soc_par1_check"))
        self.soc_par2_check = QtGui.QCheckBox(self.inputdata_widget)
        self.soc_par2_check.setGeometry(QtCore.QRect(30, 450, 221, 17))
        self.soc_par2_check.setWhatsThis(QtGui.QApplication.translate("DelinBlocksDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Check this box if you would like to experiment with social parameters. DAnCE4Water-BPM (when used as standalone) allows for a maximum of two socio-economic parameters to be specified. Input must be in the form of probabilities (between 0 and 1).</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.soc_par2_check.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Include Social Parameter 2 - Name:", None, QtGui.QApplication.UnicodeUTF8))
        self.soc_par2_check.setObjectName(_fromUtf8("soc_par2_check"))
        self.soc_par2_box = QtGui.QLineEdit(self.inputdata_widget)
        self.soc_par2_box.setGeometry(QtCore.QRect(230, 450, 161, 20))
        self.soc_par2_box.setText(_fromUtf8(""))
        self.soc_par2_box.setObjectName(_fromUtf8("soc_par2_box"))
        self.optionsadin_lbl = QtGui.QLabel(self.inputdata_widget)
        self.optionsadin_lbl.setGeometry(QtCore.QRect(10, 5, 141, 16))
        self.optionsadin_lbl.setWhatsThis(QtGui.QApplication.translate("DelinBlocksDialog", "Width of the square cell in the city grid in metres", None, QtGui.QApplication.UnicodeUTF8))
        self.optionsadin_lbl.setText(QtGui.QApplication.translate("DelinBlocksDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt; font-weight:600;\">Processing of Input Data</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.optionsadin_lbl.setObjectName(_fromUtf8("optionsadin_lbl"))
        self.planmap_check = QtGui.QCheckBox(self.inputdata_widget)
        self.planmap_check.setGeometry(QtCore.QRect(30, 170, 101, 17))
        self.planmap_check.setWhatsThis(QtGui.QApplication.translate("DelinBlocksDialog", "A raster layer that is aligned the basic inputs zoning and population map. The planner\'s map contains typology-ratios for all land zones, specified according to the user\'s urban planning snapshot for the region in question. Refer to user guide for more information on how to create this map.", None, QtGui.QApplication.UnicodeUTF8))
        self.planmap_check.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Planner\'s Map", None, QtGui.QApplication.UnicodeUTF8))
        self.planmap_check.setObjectName(_fromUtf8("planmap_check"))
        self.localmap_check = QtGui.QCheckBox(self.inputdata_widget)
        self.localmap_check.setGeometry(QtCore.QRect(30, 190, 101, 17))
        self.localmap_check.setWhatsThis(QtGui.QApplication.translate("DelinBlocksDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">A raster layer that contains information on the location of the central business district and/or activity centres for the region.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">1-2 are urban centres</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">1 = CBD</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">2 = Activity Centre</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">3-7 are water-related point landmarks</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">3 = WWTP</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">4 = DWTP</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">5 = Outfall/Outlet</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.localmap_check.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Locality Map", None, QtGui.QApplication.UnicodeUTF8))
        self.localmap_check.setObjectName(_fromUtf8("localmap_check"))
        self.addinputs_lbl = QtGui.QLabel(self.inputdata_widget)
        self.addinputs_lbl.setGeometry(QtCore.QRect(15, 150, 361, 16))
        self.addinputs_lbl.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Additional Planning and Geographic Information:", None, QtGui.QApplication.UnicodeUTF8))
        self.addinputs_lbl.setObjectName(_fromUtf8("addinputs_lbl"))
        self.roadnet_check = QtGui.QCheckBox(self.inputdata_widget)
        self.roadnet_check.setEnabled(False)
        self.roadnet_check.setGeometry(QtCore.QRect(30, 345, 101, 17))
        self.roadnet_check.setWhatsThis(QtGui.QApplication.translate("DelinBlocksDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">A network maps of all road networks (polylines) in the region</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.roadnet_check.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Road Networks", None, QtGui.QApplication.UnicodeUTF8))
        self.roadnet_check.setObjectName(_fromUtf8("roadnet_check"))
        self.soc_params_lbl = QtGui.QLabel(self.inputdata_widget)
        self.soc_params_lbl.setGeometry(QtCore.QRect(15, 375, 221, 16))
        self.soc_params_lbl.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Include Societal/Demographic Information", None, QtGui.QApplication.UnicodeUTF8))
        self.soc_params_lbl.setObjectName(_fromUtf8("soc_params_lbl"))
        self.popdata_lbl = QtGui.QLabel(self.inputdata_widget)
        self.popdata_lbl.setGeometry(QtCore.QRect(15, 30, 121, 16))
        self.popdata_lbl.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Population Data Format:", None, QtGui.QApplication.UnicodeUTF8))
        self.popdata_lbl.setObjectName(_fromUtf8("popdata_lbl"))
        self.spatialanalysis_lbl = QtGui.QLabel(self.inputdata_widget)
        self.spatialanalysis_lbl.setGeometry(QtCore.QRect(15, 500, 171, 16))
        self.spatialanalysis_lbl.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Spatial Analysis of Inputs", None, QtGui.QApplication.UnicodeUTF8))
        self.spatialanalysis_lbl.setObjectName(_fromUtf8("spatialanalysis_lbl"))
        self.spatialpatches_check = QtGui.QCheckBox(self.inputdata_widget)
        self.spatialpatches_check.setGeometry(QtCore.QRect(30, 520, 191, 17))
        self.spatialpatches_check.setWhatsThis(QtGui.QApplication.translate("DelinBlocksDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Runs a patch delineation algorithm across all building blocks to determine the clustering of land use mixes therein. This algorithm takes longer for larger blocks.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Information resulting from this is subsequently used in later parts of the model to determine urban form as well as technological opportunities. This allows more accurate assessment of technological opportunities, but is more computationally intensive.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">A map of patches will be created as an output if the option is checked among the list of desired outputs.</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.spatialpatches_check.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Conduct Patch Delineation", None, QtGui.QApplication.UnicodeUTF8))
        self.spatialpatches_check.setObjectName(_fromUtf8("spatialpatches_check"))
        self.spatialstats_check = QtGui.QCheckBox(self.inputdata_widget)
        self.spatialstats_check.setGeometry(QtCore.QRect(210, 520, 191, 17))
        self.spatialstats_check.setWhatsThis(QtGui.QApplication.translate("DelinBlocksDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Calculates a basic set of spatial indices to describe the nature of land use mix in each building block. These include:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">- Shannon Diversity Index</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">- Shannon Dominance Index</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">- Shannon Evenness Index</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.spatialstats_check.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Calculate Set of Spatial Indices", None, QtGui.QApplication.UnicodeUTF8))
        self.spatialstats_check.setObjectName(_fromUtf8("spatialstats_check"))
        self.socpar1_customize = QtGui.QWidget(self.inputdata_widget)
        self.socpar1_customize.setGeometry(QtCore.QRect(50, 425, 341, 16))
        self.socpar1_customize.setObjectName(_fromUtf8("socpar1_customize"))
        self.socpar1binary_radio = QtGui.QRadioButton(self.socpar1_customize)
        self.socpar1binary_radio.setGeometry(QtCore.QRect(130, 0, 91, 17))
        self.socpar1binary_radio.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Binary Yes/No", None, QtGui.QApplication.UnicodeUTF8))
        self.socpar1binary_radio.setObjectName(_fromUtf8("socpar1binary_radio"))
        self.socpar1prop_radio = QtGui.QRadioButton(self.socpar1_customize)
        self.socpar1prop_radio.setGeometry(QtCore.QRect(230, 0, 91, 17))
        self.socpar1prop_radio.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Proportions", None, QtGui.QApplication.UnicodeUTF8))
        self.socpar1prop_radio.setObjectName(_fromUtf8("socpar1prop_radio"))
        self.socpar1format_lbl = QtGui.QLabel(self.socpar1_customize)
        self.socpar1format_lbl.setGeometry(QtCore.QRect(20, 0, 91, 16))
        self.socpar1format_lbl.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Select Format:", None, QtGui.QApplication.UnicodeUTF8))
        self.socpar1format_lbl.setObjectName(_fromUtf8("socpar1format_lbl"))
        self.socpar2_customize = QtGui.QWidget(self.inputdata_widget)
        self.socpar2_customize.setGeometry(QtCore.QRect(50, 475, 341, 16))
        self.socpar2_customize.setObjectName(_fromUtf8("socpar2_customize"))
        self.socpar2binary_radio = QtGui.QRadioButton(self.socpar2_customize)
        self.socpar2binary_radio.setGeometry(QtCore.QRect(130, 0, 91, 17))
        self.socpar2binary_radio.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Binary Yes/No", None, QtGui.QApplication.UnicodeUTF8))
        self.socpar2binary_radio.setObjectName(_fromUtf8("socpar2binary_radio"))
        self.socpar2prop_radio = QtGui.QRadioButton(self.socpar2_customize)
        self.socpar2prop_radio.setGeometry(QtCore.QRect(230, 0, 91, 17))
        self.socpar2prop_radio.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Proportions", None, QtGui.QApplication.UnicodeUTF8))
        self.socpar2prop_radio.setObjectName(_fromUtf8("socpar2prop_radio"))
        self.socpar2format_lbl = QtGui.QLabel(self.socpar2_customize)
        self.socpar2format_lbl.setGeometry(QtCore.QRect(20, 0, 91, 16))
        self.socpar2format_lbl.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Select Format:", None, QtGui.QApplication.UnicodeUTF8))
        self.socpar2format_lbl.setObjectName(_fromUtf8("socpar2format_lbl"))
        self.rivers_check = QtGui.QCheckBox(self.inputdata_widget)
        self.rivers_check.setGeometry(QtCore.QRect(30, 255, 101, 17))
        self.rivers_check.setWhatsThis(QtGui.QApplication.translate("DelinBlocksDialog", "A raster layer that is aligned the basic inputs zoning and population map. The planner\'s map contains typology-ratios for all land zones, specified according to the user\'s urban planning snapshot for the region in question. Refer to user guide for more information on how to create this map.", None, QtGui.QApplication.UnicodeUTF8))
        self.rivers_check.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Rivers", None, QtGui.QApplication.UnicodeUTF8))
        self.rivers_check.setObjectName(_fromUtf8("rivers_check"))
        self.lakes_check = QtGui.QCheckBox(self.inputdata_widget)
        self.lakes_check.setGeometry(QtCore.QRect(30, 275, 101, 17))
        self.lakes_check.setWhatsThis(QtGui.QApplication.translate("DelinBlocksDialog", "A raster layer that is aligned the basic inputs zoning and population map. The planner\'s map contains typology-ratios for all land zones, specified according to the user\'s urban planning snapshot for the region in question. Refer to user guide for more information on how to create this map.", None, QtGui.QApplication.UnicodeUTF8))
        self.lakes_check.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Lakes", None, QtGui.QApplication.UnicodeUTF8))
        self.lakes_check.setObjectName(_fromUtf8("lakes_check"))
        self.employment_check = QtGui.QCheckBox(self.inputdata_widget)
        self.employment_check.setGeometry(QtCore.QRect(30, 210, 101, 17))
        self.employment_check.setWhatsThis(QtGui.QApplication.translate("DelinBlocksDialog", "A raster layer that is aligned the basic inputs zoning and population map. The planner\'s map contains typology-ratios for all land zones, specified according to the user\'s urban planning snapshot for the region in question. Refer to user guide for more information on how to create this map.", None, QtGui.QApplication.UnicodeUTF8))
        self.employment_check.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Employment Map", None, QtGui.QApplication.UnicodeUTF8))
        self.employment_check.setObjectName(_fromUtf8("employment_check"))
        self.addinputs_lbl_2 = QtGui.QLabel(self.inputdata_widget)
        self.addinputs_lbl_2.setGeometry(QtCore.QRect(15, 235, 361, 16))
        self.addinputs_lbl_2.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Information on Natural Features:", None, QtGui.QApplication.UnicodeUTF8))
        self.addinputs_lbl_2.setObjectName(_fromUtf8("addinputs_lbl_2"))
        self.sewermains_check = QtGui.QCheckBox(self.inputdata_widget)
        self.sewermains_check.setEnabled(False)
        self.sewermains_check.setGeometry(QtCore.QRect(140, 345, 141, 17))
        self.sewermains_check.setWhatsThis(QtGui.QApplication.translate("DelinBlocksDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">A network maps of all road networks (polylines) in the region</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.sewermains_check.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Sewer System Mains", None, QtGui.QApplication.UnicodeUTF8))
        self.sewermains_check.setObjectName(_fromUtf8("sewermains_check"))
        self.supplymains_check = QtGui.QCheckBox(self.inputdata_widget)
        self.supplymains_check.setEnabled(False)
        self.supplymains_check.setGeometry(QtCore.QRect(270, 345, 131, 17))
        self.supplymains_check.setWhatsThis(QtGui.QApplication.translate("DelinBlocksDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">A network maps of all road networks (polylines) in the region</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.supplymains_check.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Water Supply Mains", None, QtGui.QApplication.UnicodeUTF8))
        self.supplymains_check.setObjectName(_fromUtf8("supplymains_check"))
        self.groundwater_check = QtGui.QCheckBox(self.inputdata_widget)
        self.groundwater_check.setGeometry(QtCore.QRect(30, 295, 111, 17))
        self.groundwater_check.setWhatsThis(QtGui.QApplication.translate("DelinBlocksDialog", "A raster layer that is aligned the basic inputs zoning and population map. The planner\'s map contains typology-ratios for all land zones, specified according to the user\'s urban planning snapshot for the region in question. Refer to user guide for more information on how to create this map.", None, QtGui.QApplication.UnicodeUTF8))
        self.groundwater_check.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Groundwater Table", None, QtGui.QApplication.UnicodeUTF8))
        self.groundwater_check.setObjectName(_fromUtf8("groundwater_check"))
        self.soildata_lbl = QtGui.QLabel(self.inputdata_widget)
        self.soildata_lbl.setGeometry(QtCore.QRect(15, 55, 121, 16))
        self.soildata_lbl.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Soil Data Format:", None, QtGui.QApplication.UnicodeUTF8))
        self.soildata_lbl.setObjectName(_fromUtf8("soildata_lbl"))
        self.pop_options_widget = QtGui.QWidget(self.inputdata_widget)
        self.pop_options_widget.setGeometry(QtCore.QRect(150, 30, 251, 20))
        self.pop_options_widget.setObjectName(_fromUtf8("pop_options_widget"))
        self.popdata_densradio = QtGui.QRadioButton(self.pop_options_widget)
        self.popdata_densradio.setGeometry(QtCore.QRect(130, 0, 111, 17))
        self.popdata_densradio.setWhatsThis(QtGui.QApplication.translate("DelinBlocksDialog", "Input data given as a population density [people/ ha]", None, QtGui.QApplication.UnicodeUTF8))
        self.popdata_densradio.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Population Density", None, QtGui.QApplication.UnicodeUTF8))
        self.popdata_densradio.setObjectName(_fromUtf8("popdata_densradio"))
        self.popdata_totradio = QtGui.QRadioButton(self.pop_options_widget)
        self.popdata_totradio.setGeometry(QtCore.QRect(20, 0, 101, 17))
        self.popdata_totradio.setWhatsThis(QtGui.QApplication.translate("DelinBlocksDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Input data given as a total population [no. of people]</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.popdata_totradio.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Total Population", None, QtGui.QApplication.UnicodeUTF8))
        self.popdata_totradio.setObjectName(_fromUtf8("popdata_totradio"))
        self.soil_options_widget = QtGui.QWidget(self.inputdata_widget)
        self.soil_options_widget.setGeometry(QtCore.QRect(150, 55, 251, 41))
        self.soil_options_widget.setObjectName(_fromUtf8("soil_options_widget"))
        self.soildata_infil = QtGui.QRadioButton(self.soil_options_widget)
        self.soildata_infil.setGeometry(QtCore.QRect(130, 0, 111, 17))
        self.soildata_infil.setWhatsThis(QtGui.QApplication.translate("DelinBlocksDialog", "Input data given as a population density [people/ ha]", None, QtGui.QApplication.UnicodeUTF8))
        self.soildata_infil.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Infiltration Rates", None, QtGui.QApplication.UnicodeUTF8))
        self.soildata_infil.setObjectName(_fromUtf8("soildata_infil"))
        self.soildata_classify = QtGui.QRadioButton(self.soil_options_widget)
        self.soildata_classify.setGeometry(QtCore.QRect(20, 0, 101, 17))
        self.soildata_classify.setWhatsThis(QtGui.QApplication.translate("DelinBlocksDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Input data given as a total population [no. of people]</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.soildata_classify.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Classification", None, QtGui.QApplication.UnicodeUTF8))
        self.soildata_classify.setObjectName(_fromUtf8("soildata_classify"))
        self.soildata_unitscombo = QtGui.QComboBox(self.soil_options_widget)
        self.soildata_unitscombo.setGeometry(QtCore.QRect(170, 20, 61, 16))
        self.soildata_unitscombo.setObjectName(_fromUtf8("soildata_unitscombo"))
        self.soildata_unitscombo.addItem(_fromUtf8(""))
        self.soildata_unitscombo.setItemText(0, QtGui.QApplication.translate("DelinBlocksDialog", "mm/hr", None, QtGui.QApplication.UnicodeUTF8))
        self.soildata_unitscombo.addItem(_fromUtf8(""))
        self.soildata_unitscombo.setItemText(1, QtGui.QApplication.translate("DelinBlocksDialog", "m/sec", None, QtGui.QApplication.UnicodeUTF8))
        self.soildataunits_lbl = QtGui.QLabel(self.soil_options_widget)
        self.soildataunits_lbl.setGeometry(QtCore.QRect(130, 20, 31, 20))
        self.soildataunits_lbl.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Units:", None, QtGui.QApplication.UnicodeUTF8))
        self.soildataunits_lbl.setObjectName(_fromUtf8("soildataunits_lbl"))
        self.groundwater_datumlbl = QtGui.QLabel(self.inputdata_widget)
        self.groundwater_datumlbl.setGeometry(QtCore.QRect(170, 295, 81, 20))
        self.groundwater_datumlbl.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Choose Datum:", None, QtGui.QApplication.UnicodeUTF8))
        self.groundwater_datumlbl.setObjectName(_fromUtf8("groundwater_datumlbl"))
        self.addinputs_lbl_3 = QtGui.QLabel(self.inputdata_widget)
        self.addinputs_lbl_3.setGeometry(QtCore.QRect(15, 325, 361, 16))
        self.addinputs_lbl_3.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Network Structures:", None, QtGui.QApplication.UnicodeUTF8))
        self.addinputs_lbl_3.setObjectName(_fromUtf8("addinputs_lbl_3"))
        self.elevdata_lbl = QtGui.QLabel(self.inputdata_widget)
        self.elevdata_lbl.setGeometry(QtCore.QRect(15, 100, 141, 16))
        self.elevdata_lbl.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Elevation Reference Point:", None, QtGui.QApplication.UnicodeUTF8))
        self.elevdata_lbl.setObjectName(_fromUtf8("elevdata_lbl"))
        self.elev_options_widget = QtGui.QWidget(self.inputdata_widget)
        self.elev_options_widget.setGeometry(QtCore.QRect(150, 100, 251, 41))
        self.elev_options_widget.setObjectName(_fromUtf8("elev_options_widget"))
        self.elev_custom = QtGui.QRadioButton(self.elev_options_widget)
        self.elev_custom.setGeometry(QtCore.QRect(20, 20, 71, 17))
        self.elev_custom.setWhatsThis(QtGui.QApplication.translate("DelinBlocksDialog", "Input data given as a population density [people/ ha]", None, QtGui.QApplication.UnicodeUTF8))
        self.elev_custom.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Custom", None, QtGui.QApplication.UnicodeUTF8))
        self.elev_custom.setObjectName(_fromUtf8("elev_custom"))
        self.elev_sealevel = QtGui.QRadioButton(self.elev_options_widget)
        self.elev_sealevel.setGeometry(QtCore.QRect(20, 0, 101, 17))
        self.elev_sealevel.setWhatsThis(QtGui.QApplication.translate("DelinBlocksDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Input data given as a total population [no. of people]</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.elev_sealevel.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Sea Level", None, QtGui.QApplication.UnicodeUTF8))
        self.elev_sealevel.setObjectName(_fromUtf8("elev_sealevel"))
        self.elev_referencebox = QtGui.QLineEdit(self.elev_options_widget)
        self.elev_referencebox.setGeometry(QtCore.QRect(90, 20, 51, 16))
        self.elev_referencebox.setObjectName(_fromUtf8("elev_referencebox"))
        self.elev_referencelbl = QtGui.QLabel(self.elev_options_widget)
        self.elev_referencelbl.setGeometry(QtCore.QRect(150, 20, 91, 16))
        self.elev_referencelbl.setText(QtGui.QApplication.translate("DelinBlocksDialog", "m above sea level", None, QtGui.QApplication.UnicodeUTF8))
        self.elev_referencelbl.setObjectName(_fromUtf8("elev_referencelbl"))
        self.groundwater_datumcombo = QtGui.QComboBox(self.inputdata_widget)
        self.groundwater_datumcombo.setGeometry(QtCore.QRect(260, 295, 121, 16))
        self.groundwater_datumcombo.setObjectName(_fromUtf8("groundwater_datumcombo"))
        self.groundwater_datumcombo.addItem(_fromUtf8(""))
        self.groundwater_datumcombo.setItemText(0, QtGui.QApplication.translate("DelinBlocksDialog", "Sea Level", None, QtGui.QApplication.UnicodeUTF8))
        self.groundwater_datumcombo.addItem(_fromUtf8(""))
        self.groundwater_datumcombo.setItemText(1, QtGui.QApplication.translate("DelinBlocksDialog", "Natural Surface", None, QtGui.QApplication.UnicodeUTF8))
        self.job_options_widget = QtGui.QWidget(self.inputdata_widget)
        self.job_options_widget.setGeometry(QtCore.QRect(150, 210, 251, 20))
        self.job_options_widget.setObjectName(_fromUtf8("job_options_widget"))
        self.jobdata_densradio = QtGui.QRadioButton(self.job_options_widget)
        self.jobdata_densradio.setGeometry(QtCore.QRect(130, 0, 111, 17))
        self.jobdata_densradio.setWhatsThis(QtGui.QApplication.translate("DelinBlocksDialog", "Input data given as a population density [people/ ha]", None, QtGui.QApplication.UnicodeUTF8))
        self.jobdata_densradio.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Job Density [/ha]", None, QtGui.QApplication.UnicodeUTF8))
        self.jobdata_densradio.setObjectName(_fromUtf8("jobdata_densradio"))
        self.jobdata_totradio = QtGui.QRadioButton(self.job_options_widget)
        self.jobdata_totradio.setGeometry(QtCore.QRect(20, 0, 101, 17))
        self.jobdata_totradio.setWhatsThis(QtGui.QApplication.translate("DelinBlocksDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Input data given as a total population [no. of people]</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.jobdata_totradio.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Total Jobs", None, QtGui.QApplication.UnicodeUTF8))
        self.jobdata_totradio.setObjectName(_fromUtf8("jobdata_totradio"))
        self.verticalLayout_3.addWidget(self.inputdata_widget)
        self.connectivity_widget = QtGui.QWidget(self.scrollAreaWidgetContents)
        self.connectivity_widget.setMinimumSize(QtCore.QSize(0, 240))
        self.connectivity_widget.setObjectName(_fromUtf8("connectivity_widget"))
        self.radioVNeum = QtGui.QRadioButton(self.connectivity_widget)
        self.radioVNeum.setGeometry(QtCore.QRect(80, 110, 101, 16))
        self.radioVNeum.setWhatsThis(QtGui.QApplication.translate("DelinBlocksDialog", "Von Neumann, four cardinal directions on either side of the central block.", None, QtGui.QApplication.UnicodeUTF8))
        self.radioVNeum.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Von Neumann", None, QtGui.QApplication.UnicodeUTF8))
        self.radioVNeum.setChecked(False)
        self.radioVNeum.setObjectName(_fromUtf8("radioVNeum"))
        self.img_Moore = QtGui.QLabel(self.connectivity_widget)
        self.img_Moore.setGeometry(QtCore.QRect(30, 55, 41, 41))
        self.img_Moore.setText(_fromUtf8(""))
        self.img_Moore.setPixmap(QtGui.QPixmap(_fromUtf8(":/delinblocks/MooreNH.png")))
        self.img_Moore.setObjectName(_fromUtf8("img_Moore"))
        self.neighb_lbl = QtGui.QLabel(self.connectivity_widget)
        self.neighb_lbl.setGeometry(QtCore.QRect(20, 30, 231, 16))
        self.neighb_lbl.setWhatsThis(QtGui.QApplication.translate("DelinBlocksDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">How many blocks to consider when determining drainage fluxes (the greater the number, the greater the computational burden).</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.neighb_lbl.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Select Neighbourhood (default: Moore):", None, QtGui.QApplication.UnicodeUTF8))
        self.neighb_lbl.setObjectName(_fromUtf8("neighb_lbl"))
        self.img_vNeum = QtGui.QLabel(self.connectivity_widget)
        self.img_vNeum.setGeometry(QtCore.QRect(30, 100, 41, 41))
        self.img_vNeum.setText(_fromUtf8(""))
        self.img_vNeum.setPixmap(QtGui.QPixmap(_fromUtf8(":/delinblocks/vNeumann.png")))
        self.img_vNeum.setObjectName(_fromUtf8("img_vNeum"))
        self.radioMoore = QtGui.QRadioButton(self.connectivity_widget)
        self.radioMoore.setEnabled(True)
        self.radioMoore.setGeometry(QtCore.QRect(80, 65, 82, 16))
        self.radioMoore.setWhatsThis(QtGui.QApplication.translate("DelinBlocksDialog", "Moore, all eight neighbours around the central block.", None, QtGui.QApplication.UnicodeUTF8))
        self.radioMoore.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Moore", None, QtGui.QApplication.UnicodeUTF8))
        self.radioMoore.setCheckable(True)
        self.radioMoore.setObjectName(_fromUtf8("radioMoore"))
        self.optionsmc_lbl = QtGui.QLabel(self.connectivity_widget)
        self.optionsmc_lbl.setGeometry(QtCore.QRect(10, 5, 231, 16))
        self.optionsmc_lbl.setWhatsThis(QtGui.QApplication.translate("DelinBlocksDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">How many blocks to consider when determining drainage fluxes (the greater the number, the greater the computational burden).</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.optionsmc_lbl.setText(QtGui.QApplication.translate("DelinBlocksDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt; font-weight:600;\">Local Extents &amp; Map Connectivity</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.optionsmc_lbl.setObjectName(_fromUtf8("optionsmc_lbl"))
        self.flowpath_lbl = QtGui.QLabel(self.connectivity_widget)
        self.flowpath_lbl.setGeometry(QtCore.QRect(20, 150, 131, 16))
        self.flowpath_lbl.setWhatsThis(QtGui.QApplication.translate("DelinBlocksDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Method of finding flow direction in the digital elevation model or in this case the grid of blocks. Refer to publications for further information.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">D-infinity - Tarboton, 1997. A new method for the determination of flow directions and upslope areas in grid digital elevation models. Water Resources Research v33.2, 309-319</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">D8 - O\'Callaghan &amp; Mark, 1984. The Extraction of Drainage Networks from Digital Elevation Data. Computer Vision, Graphics and Image Processing v28, 323-344</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Divergent Flows - Freeman, 1991</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.flowpath_lbl.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Flow Path Method:", None, QtGui.QApplication.UnicodeUTF8))
        self.flowpath_lbl.setObjectName(_fromUtf8("flowpath_lbl"))
        self.flowpath_combo = QtGui.QComboBox(self.connectivity_widget)
        self.flowpath_combo.setGeometry(QtCore.QRect(30, 175, 271, 22))
        self.flowpath_combo.setObjectName(_fromUtf8("flowpath_combo"))
        self.flowpath_combo.addItem(_fromUtf8(""))
        self.flowpath_combo.setItemText(0, QtGui.QApplication.translate("DelinBlocksDialog", "Adapted version of D-infinity (Tarboton, 1997)", None, QtGui.QApplication.UnicodeUTF8))
        self.flowpath_combo.addItem(_fromUtf8(""))
        self.flowpath_combo.setItemText(1, QtGui.QApplication.translate("DelinBlocksDialog", "D8 (O\'Callaghan & Mark, 1984)", None, QtGui.QApplication.UnicodeUTF8))
        self.demsmooth_check = QtGui.QCheckBox(self.connectivity_widget)
        self.demsmooth_check.setGeometry(QtCore.QRect(30, 210, 161, 17))
        self.demsmooth_check.setWhatsThis(QtGui.QApplication.translate("DelinBlocksDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Applies a weighted average smoothing filter over the DEM layer. </span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.demsmooth_check.setText(QtGui.QApplication.translate("DelinBlocksDialog", "DEM Smoothing (no. passes)", None, QtGui.QApplication.UnicodeUTF8))
        self.demsmooth_check.setObjectName(_fromUtf8("demsmooth_check"))
        self.demsmooth_spin = QtGui.QSpinBox(self.connectivity_widget)
        self.demsmooth_spin.setGeometry(QtCore.QRect(190, 210, 31, 20))
        self.demsmooth_spin.setMinimum(1)
        self.demsmooth_spin.setMaximum(2)
        self.demsmooth_spin.setObjectName(_fromUtf8("demsmooth_spin"))
        self.neighb_vnfp_check = QtGui.QCheckBox(self.connectivity_widget)
        self.neighb_vnfp_check.setGeometry(QtCore.QRect(210, 100, 191, 17))
        self.neighb_vnfp_check.setWhatsThis(QtGui.QApplication.translate("DelinBlocksDialog", "Check if you want to avoid localised ponds forming in the region. If this is of particular interest because the DEM\'s accuracy has been assured and the purpose of the simulation is to assess these problem spots, then leave this box unchecked.\n"
"\n"
"Correction proceeds as follows:\n"
"- If cell cannot transfer water downhill, but there is an adjacent cell with identical elevation within tolerance limit, it will transfer the water into this.\n"
"- If tolerance limit is not met, cell\'s water is routed directly to catchment outlet.", None, QtGui.QApplication.UnicodeUTF8))
        self.neighb_vnfp_check.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Flow Path Delineation", None, QtGui.QApplication.UnicodeUTF8))
        self.neighb_vnfp_check.setObjectName(_fromUtf8("neighb_vnfp_check"))
        self.neighb_vnpd_check = QtGui.QCheckBox(self.connectivity_widget)
        self.neighb_vnpd_check.setGeometry(QtCore.QRect(210, 120, 191, 17))
        self.neighb_vnpd_check.setWhatsThis(QtGui.QApplication.translate("DelinBlocksDialog", "Check if you want to avoid localised ponds forming in the region. If this is of particular interest because the DEM\'s accuracy has been assured and the purpose of the simulation is to assess these problem spots, then leave this box unchecked.\n"
"\n"
"Correction proceeds as follows:\n"
"- If cell cannot transfer water downhill, but there is an adjacent cell with identical elevation within tolerance limit, it will transfer the water into this.\n"
"- If tolerance limit is not met, cell\'s water is routed directly to catchment outlet.", None, QtGui.QApplication.UnicodeUTF8))
        self.neighb_vnpd_check.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Spatial Averaging Operations", None, QtGui.QApplication.UnicodeUTF8))
        self.neighb_vnpd_check.setObjectName(_fromUtf8("neighb_vnpd_check"))
        self.neighb_lbl2 = QtGui.QLabel(self.connectivity_widget)
        self.neighb_lbl2.setGeometry(QtCore.QRect(180, 80, 221, 16))
        self.neighb_lbl2.setWhatsThis(QtGui.QApplication.translate("DelinBlocksDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Method of finding flow direction in the digital elevation model or in this case the grid of blocks. Refer to publications for further information.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">D-infinity - Tarboton, 1997. A new method for the determination of flow directions and upslope areas in grid digital elevation models. Water Resources Research v33.2, 309-319</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">D8 - O\'Callaghan &amp; Mark, 1984. The Extraction of Drainage Networks from Digital Elevation Data. Computer Vision, Graphics and Image Processing v28, 323-344</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Divergent Flows - Freeman, 1991</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.neighb_lbl2.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Apply Von Neumann Neighbourhood to: ", None, QtGui.QApplication.UnicodeUTF8))
        self.neighb_lbl2.setObjectName(_fromUtf8("neighb_lbl2"))
        self.verticalLayout_3.addWidget(self.connectivity_widget)
        self.regiongeography_widget = QtGui.QWidget(self.scrollAreaWidgetContents)
        self.regiongeography_widget.setMinimumSize(QtCore.QSize(0, 210))
        self.regiongeography_widget.setObjectName(_fromUtf8("regiongeography_widget"))
        self.cbdoption_lbl = QtGui.QLabel(self.regiongeography_widget)
        self.cbdoption_lbl.setGeometry(QtCore.QRect(20, 60, 231, 16))
        self.cbdoption_lbl.setWhatsThis(QtGui.QApplication.translate("DelinBlocksDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">How many blocks to consider when determining drainage fluxes (the greater the number, the greater the computational burden).</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.cbdoption_lbl.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Select an option for determining CBD Location:", None, QtGui.QApplication.UnicodeUTF8))
        self.cbdoption_lbl.setObjectName(_fromUtf8("cbdoption_lbl"))
        self.optionsmc_lbl_2 = QtGui.QLabel(self.regiongeography_widget)
        self.optionsmc_lbl_2.setGeometry(QtCore.QRect(10, 5, 231, 16))
        self.optionsmc_lbl_2.setWhatsThis(QtGui.QApplication.translate("DelinBlocksDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">How many blocks to consider when determining drainage fluxes (the greater the number, the greater the computational burden).</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.optionsmc_lbl_2.setText(QtGui.QApplication.translate("DelinBlocksDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt; font-weight:600;\">Regional Geography</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.optionsmc_lbl_2.setObjectName(_fromUtf8("optionsmc_lbl_2"))
        self.cbd_combo = QtGui.QComboBox(self.regiongeography_widget)
        self.cbd_combo.setGeometry(QtCore.QRect(220, 85, 181, 16))
        self.cbd_combo.setObjectName(_fromUtf8("cbd_combo"))
        self.cbd_combo.addItem(_fromUtf8(""))
        self.cbd_combo.setItemText(0, QtGui.QApplication.translate("DelinBlocksDialog", "Adelaide, Australia", None, QtGui.QApplication.UnicodeUTF8))
        self.cbd_combo.addItem(_fromUtf8(""))
        self.cbd_combo.setItemText(1, QtGui.QApplication.translate("DelinBlocksDialog", "Brisbane, Australia", None, QtGui.QApplication.UnicodeUTF8))
        self.cbd_combo.addItem(_fromUtf8(""))
        self.cbd_combo.setItemText(2, QtGui.QApplication.translate("DelinBlocksDialog", "Cairns, Australia", None, QtGui.QApplication.UnicodeUTF8))
        self.cbd_combo.addItem(_fromUtf8(""))
        self.cbd_combo.setItemText(3, QtGui.QApplication.translate("DelinBlocksDialog", "Canberra, Australia", None, QtGui.QApplication.UnicodeUTF8))
        self.cbd_combo.addItem(_fromUtf8(""))
        self.cbd_combo.setItemText(4, QtGui.QApplication.translate("DelinBlocksDialog", "Copenhagen, Denmark", None, QtGui.QApplication.UnicodeUTF8))
        self.cbd_combo.addItem(_fromUtf8(""))
        self.cbd_combo.setItemText(5, QtGui.QApplication.translate("DelinBlocksDialog", "Innsbruck, Austria", None, QtGui.QApplication.UnicodeUTF8))
        self.cbd_combo.addItem(_fromUtf8(""))
        self.cbd_combo.setItemText(6, QtGui.QApplication.translate("DelinBlocksDialog", "Kuala Lumpur, Malaysia", None, QtGui.QApplication.UnicodeUTF8))
        self.cbd_combo.addItem(_fromUtf8(""))
        self.cbd_combo.setItemText(7, QtGui.QApplication.translate("DelinBlocksDialog", "London, UK", None, QtGui.QApplication.UnicodeUTF8))
        self.cbd_combo.addItem(_fromUtf8(""))
        self.cbd_combo.setItemText(8, QtGui.QApplication.translate("DelinBlocksDialog", "Melbourne, Australia", None, QtGui.QApplication.UnicodeUTF8))
        self.cbd_combo.addItem(_fromUtf8(""))
        self.cbd_combo.setItemText(9, QtGui.QApplication.translate("DelinBlocksDialog", "Munich, Germany", None, QtGui.QApplication.UnicodeUTF8))
        self.cbd_combo.addItem(_fromUtf8(""))
        self.cbd_combo.setItemText(10, QtGui.QApplication.translate("DelinBlocksDialog", "Perth, Australia", None, QtGui.QApplication.UnicodeUTF8))
        self.cbd_combo.addItem(_fromUtf8(""))
        self.cbd_combo.setItemText(11, QtGui.QApplication.translate("DelinBlocksDialog", "Singapore, Singapore", None, QtGui.QApplication.UnicodeUTF8))
        self.cbd_combo.addItem(_fromUtf8(""))
        self.cbd_combo.setItemText(12, QtGui.QApplication.translate("DelinBlocksDialog", "Sydney, Australia", None, QtGui.QApplication.UnicodeUTF8))
        self.cbd_combo.addItem(_fromUtf8(""))
        self.cbd_combo.setItemText(13, QtGui.QApplication.translate("DelinBlocksDialog", "Vienna, Austria", None, QtGui.QApplication.UnicodeUTF8))
        self.considergeo_check = QtGui.QCheckBox(self.regiongeography_widget)
        self.considergeo_check.setGeometry(QtCore.QRect(20, 30, 361, 17))
        self.considergeo_check.setWhatsThis(QtGui.QApplication.translate("DelinBlocksDialog", "Check if you want to avoid localised ponds forming in the region. If this is of particular interest because the DEM\'s accuracy has been assured and the purpose of the simulation is to assess these problem spots, then leave this box unchecked.\n"
"\n"
"Correction proceeds as follows:\n"
"- If cell cannot transfer water downhill, but there is an adjacent cell with identical elevation within tolerance limit, it will transfer the water into this.\n"
"- If tolerance limit is not met, cell\'s water is routed directly to catchment outlet.", None, QtGui.QApplication.UnicodeUTF8))
        self.considergeo_check.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Consider location of nearest Central Business District in Simulation", None, QtGui.QApplication.UnicodeUTF8))
        self.considergeo_check.setObjectName(_fromUtf8("considergeo_check"))
        self.cbdknown_radio = QtGui.QRadioButton(self.regiongeography_widget)
        self.cbdknown_radio.setGeometry(QtCore.QRect(20, 85, 211, 17))
        self.cbdknown_radio.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Select from a list of known locations", None, QtGui.QApplication.UnicodeUTF8))
        self.cbdknown_radio.setObjectName(_fromUtf8("cbdknown_radio"))
        self.cbdmanual_radio = QtGui.QRadioButton(self.regiongeography_widget)
        self.cbdmanual_radio.setGeometry(QtCore.QRect(20, 110, 211, 17))
        self.cbdmanual_radio.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Manually enter coordinates of CBD", None, QtGui.QApplication.UnicodeUTF8))
        self.cbdmanual_radio.setObjectName(_fromUtf8("cbdmanual_radio"))
        self.cbdlong_box = QtGui.QLineEdit(self.regiongeography_widget)
        self.cbdlong_box.setGeometry(QtCore.QRect(220, 130, 113, 20))
        self.cbdlong_box.setObjectName(_fromUtf8("cbdlong_box"))
        self.cbdlat_box = QtGui.QLineEdit(self.regiongeography_widget)
        self.cbdlat_box.setGeometry(QtCore.QRect(220, 155, 113, 20))
        self.cbdlat_box.setObjectName(_fromUtf8("cbdlat_box"))
        self.cbdlong_lbl = QtGui.QLabel(self.regiongeography_widget)
        self.cbdlong_lbl.setGeometry(QtCore.QRect(160, 130, 61, 16))
        self.cbdlong_lbl.setWhatsThis(QtGui.QApplication.translate("DelinBlocksDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">How many blocks to consider when determining drainage fluxes (the greater the number, the greater the computational burden).</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.cbdlong_lbl.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Longitude", None, QtGui.QApplication.UnicodeUTF8))
        self.cbdlong_lbl.setObjectName(_fromUtf8("cbdlong_lbl"))
        self.cbdlat_lbl = QtGui.QLabel(self.regiongeography_widget)
        self.cbdlat_lbl.setGeometry(QtCore.QRect(160, 155, 61, 16))
        self.cbdlat_lbl.setWhatsThis(QtGui.QApplication.translate("DelinBlocksDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">How many blocks to consider when determining drainage fluxes (the greater the number, the greater the computational burden).</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.cbdlat_lbl.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Latitude", None, QtGui.QApplication.UnicodeUTF8))
        self.cbdlat_lbl.setObjectName(_fromUtf8("cbdlat_lbl"))
        self.cbdmark_check = QtGui.QCheckBox(self.regiongeography_widget)
        self.cbdmark_check.setGeometry(QtCore.QRect(20, 180, 181, 20))
        self.cbdmark_check.setWhatsThis(QtGui.QApplication.translate("DelinBlocksDialog", "Check if you want to avoid localised ponds forming in the region. If this is of particular interest because the DEM\'s accuracy has been assured and the purpose of the simulation is to assess these problem spots, then leave this box unchecked.\n"
"\n"
"Correction proceeds as follows:\n"
"- If cell cannot transfer water downhill, but there is an adjacent cell with identical elevation within tolerance limit, it will transfer the water into this.\n"
"- If tolerance limit is not met, cell\'s water is routed directly to catchment outlet.", None, QtGui.QApplication.UnicodeUTF8))
        self.cbdmark_check.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Mark this location on output map", None, QtGui.QApplication.UnicodeUTF8))
        self.cbdmark_check.setObjectName(_fromUtf8("cbdmark_check"))
        self.verticalLayout_3.addWidget(self.regiongeography_widget)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.horizontalLayout.addWidget(self.scrollArea)
        self.widget_2 = QtGui.QWidget(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_2.sizePolicy().hasHeightForWidth())
        self.widget_2.setSizePolicy(sizePolicy)
        self.widget_2.setMinimumSize(QtCore.QSize(151, 0))
        self.widget_2.setMaximumSize(QtCore.QSize(151, 16777215))
        self.widget_2.setObjectName(_fromUtf8("widget_2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.widget_2)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.img_blocks = QtGui.QLabel(self.widget_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.img_blocks.sizePolicy().hasHeightForWidth())
        self.img_blocks.setSizePolicy(sizePolicy)
        self.img_blocks.setMinimumSize(QtCore.QSize(0, 90))
        self.img_blocks.setMaximumSize(QtCore.QSize(16777215, 90))
        self.img_blocks.setText(_fromUtf8(""))
        self.img_blocks.setPixmap(QtGui.QPixmap(_fromUtf8(":/delinblocks/BBcells.png")))
        self.img_blocks.setObjectName(_fromUtf8("img_blocks"))
        self.verticalLayout_2.addWidget(self.img_blocks)
        self.descr_blocks = QtGui.QTextBrowser(self.widget_2)
        self.descr_blocks.setHtml(QtGui.QApplication.translate("DelinBlocksDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Set basic simulation parameters for creating the block map of input region. Define additional inputs and specify neighbourhood and DEM analysis rules.</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.descr_blocks.setObjectName(_fromUtf8("descr_blocks"))
        self.verticalLayout_2.addWidget(self.descr_blocks)
        self.horizontalLayout.addWidget(self.widget_2)
        self.verticalLayout.addWidget(self.widget)
        self.widget_4 = QtGui.QWidget(DelinBlocksDialog)
        self.widget_4.setMinimumSize(QtCore.QSize(0, 38))
        self.widget_4.setMaximumSize(QtCore.QSize(16777215, 38))
        self.widget_4.setObjectName(_fromUtf8("widget_4"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.widget_4)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.remarks = QtGui.QLabel(self.widget_4)
        self.remarks.setText(QtGui.QApplication.translate("DelinBlocksDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt; font-style:italic;\">UrbanBEATS Version 1.0</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.remarks.setObjectName(_fromUtf8("remarks"))
        self.horizontalLayout_2.addWidget(self.remarks)
        self.remarks2 = QtGui.QLabel(self.widget_4)
        self.remarks2.setText(QtGui.QApplication.translate("DelinBlocksDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt; font-style:italic;\">- (C) 2012 Peter M. Bach</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.remarks2.setObjectName(_fromUtf8("remarks2"))
        self.horizontalLayout_2.addWidget(self.remarks2)
        self.buttonBox = QtGui.QDialogButtonBox(self.widget_4)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout_2.addWidget(self.buttonBox)
        self.helpButton = QtGui.QPushButton(self.widget_4)
        self.helpButton.setEnabled(True)
        self.helpButton.setWhatsThis(QtGui.QApplication.translate("DelinBlocksDialog", "You do not need help right now! :)", None, QtGui.QApplication.UnicodeUTF8))
        self.helpButton.setText(QtGui.QApplication.translate("DelinBlocksDialog", "Help", None, QtGui.QApplication.UnicodeUTF8))
        self.helpButton.setObjectName(_fromUtf8("helpButton"))
        self.horizontalLayout_2.addWidget(self.helpButton)
        self.verticalLayout.addWidget(self.widget_4)

        self.retranslateUi(DelinBlocksDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), DelinBlocksDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), DelinBlocksDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(DelinBlocksDialog)

    def retranslateUi(self, DelinBlocksDialog):
        pass

import dialogimg_rc
