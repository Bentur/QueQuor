import sys
from PyQt5.QtWidgets import QDesktopWidget, QStyle, QComboBox, QCheckBox, QStyleOptionButton, QProxyStyle, QLineEdit, QAbstractItemView, QLabel, qApp, QStyleFactory, QMainWindow, QPushButton, QApplication, QWidget, QAction, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QGridLayout, QTextEdit
from PyQt5.QtGui import QIcon, QTextDocument, QFont, QPixmap, QColor, QImage, QPainter, QPalette, QPainterPath, QBrush, QPen, QPolygon
from PyQt5.QtCore import pyqtSlot, QSize, Qt, QPoint, QRect
import numpy as np
import time
import os
from abc import ABCMeta, abstractmethod

import scan

StyleSheet = '''
        QPushButton {
            border: none;
        }
        #Button {
            background-color: #9c27b0;
            border-radius: 5px;       
        }
        #Button:hover {
            background-color: #da5cff;
            color: #fff;              s
        }
        #Button:pressed {
            background-color: #ffc9e4;
        }
        '''

class Popup_Base(QMainWindow):
    def __init__(self, main, parent=None):
        super(Popup_Base, self).__init__(parent)
        __metaclass__ = ABCMeta
        self.main = main
        self.parent = parent
        #crée un fenêtre de type popup, sans bordure et au desssus des autres fenetres
        self.setWindowFlags(Qt.Popup);
        self.hide()

        self.setGeometry(100, 100, 400, 200)

    def keyPressEvent(self, event):
        self.parent.keyPressEvent(event)

    @abstractmethod
    def hide_popup(self):
        pass

class Popup_escape(Popup_Base):
    def __init__(self, main, parent=None):
        super().__init__(main, parent)

        layout = QVBoxLayout()
        font = QFont("Times", 18)

        button_source = QPushButton("Source", self, objectName="Button")
        button_source.setFont(font)
        button_source.setStyleSheet(StyleSheet)
        button_source.clicked.connect(self.on_bouton_source_click)
        layout.addWidget(button_source)

        button_categories = QPushButton("Categories", self, objectName="Button")
        button_categories.setFont(font)
        button_categories.setStyleSheet(StyleSheet)
        button_categories.clicked.connect(self.on_bouton_categories_click)
        layout.addWidget(button_categories)

        button_quit = QPushButton("Quit", self, objectName="ButtonQuit")
        button_quit.setFont(font)
        #button_quit.setAlignment(Qt.AlignCenter)
        StyleSheet2 = '''
        QPushButton {
            border: none;
        }
        #ButtonQuit {
            background-color: #ff0000;
            min-width: 104px;
            max-width: 104px;
            min-height: 104px;
            max-height: 104px;
            border-radius: 52px;
        }
        #ButtonQuit:hover {
            background-color: #ffaaaa;
        }
        #ButtonQuit:pressed {
            background-color: #ffaa00;
        }
        '''
        button_quit.setStyleSheet(StyleSheet2)
        button_quit.clicked.connect(parent.quit)
        layout.addWidget(button_quit)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def hide_popup(self):
        print("hiding popup escape")
        self.hide()

    def on_bouton_source_click(self):
        self.parent.pile_add(self.parent.popup_source)

    def on_bouton_categories_click(self):
        self.parent.pile_add(self.parent.popup_categories)

class Popup_source(Popup_Base):
    def __init__(self, main, parent=None):
        super().__init__(main, parent)

        font = QFont("Times", 18)
        layout = QVBoxLayout()
        label = QLabel("Sélection des sources : ", self)
        label.setFont(QFont("Times", 24))
        layout.addWidget(label)

        self.check_box = []
        self.bout_del = []
        for i in range(len(parent.main.sources)):
            source = parent.main.sources[i]
            layo = QHBoxLayout()
            case = QCheckBox(source[0], self)
            case.setFont(font)
            if(not(source[1])):
                case.setChecked(False)
            else :
                case.setChecked(True)
            case.clicked.connect(self.on_case_check)
            layo.addWidget(case)
            layout.addLayout(layo)
            self.check_box.append(case)

        button_ok = QPushButton("OK", self, objectName="Button")
        button_ok.setStyleSheet(StyleSheet)
        button_ok.clicked.connect(self.on_button_ok_click)
        button_ok.setFont(font)
        layout.addWidget(button_ok)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def on_case_check(self):
        print("coucou")

        for i in range(len(self.check_box)):
            checked = self.check_box[i].isChecked()
            if(checked):
                print(self.parent.main.sources[i][0], "is checked")
                if(scan.verify_source(self.parent.main.sources[i][0])):
                    self.parent.main.sources[i][1] = True
                else:
                    self.check_box[i].setChecked(False)
            else:
                print(self.parent.main.sources[i][0], "is not checked")

                self.parent.main.sources[i][1] = False

        self.parent.main.update_films()
        self.parent.update_HUD()
        self.parent.updateTableWidget(self.main.films)

    def hide_popup(self):
        print("hiding popup source")
        self.hide()

    @pyqtSlot()
    def on_button_ok_click(self):
        self.parent.on_escape_key_pressed()

class Popup_categories(Popup_Base):
    def __init__(self, main, parent=None):
        super().__init__(main, parent)
        font = QFont("Times", 18)

        layout = QVBoxLayout()

        self.l_categories = []
        for cat in parent.main.categories:
            case = QCheckBox('&' + cat, self)
            case.setChecked(True)
            case.setFont(font)
            self.l_categories.append([case, cat])
            case.stateChanged.connect(self.on_categories_checked)
            layout.addWidget(case)

        button_ok = QPushButton("OK", self, objectName= "Button")
        button_ok.setStyleSheet(StyleSheet)
        button_ok.clicked.connect(self.on_button_ok_click)
        button_ok.setFont(font)
        layout.addWidget(button_ok)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def hide_popup(self):
        print("hiding popup categories")
        self.hide()

    @pyqtSlot()
    def on_button_ok_click(self):
        self.parent.on_escape_key_pressed()

    @pyqtSlot()
    def on_categories_checked(self):
        self.main.categories_selected = []
        for c in self.l_categories:
            if (c[0].isChecked()):
                self.main.categories_selected.append(c[1])
        self.main.update_selection()
        self.parent.updateTableWidget(self.main.selection_films)
        self.main.film_selected = 0
        self.parent.tableWidget.setCurrentCell(0, 0)
        self.parent.update_HUD()