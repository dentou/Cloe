"""
Poricom Settings Menu Components

Copyright (C) `2021-2022` `<Alarcon Ace Belen>`

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from PyQt5.QtGui import (QColor, QPalette, QBrush, QPainter, QPen, QFont)
from PyQt5.QtCore import (Qt, QSize, QSettings)
from PyQt5.QtWidgets import (QComboBox, QLineEdit, QLabel, QInputDialog, QColorDialog, QFontDialog,
    QRubberBand, QCheckBox, QGridLayout, QHBoxLayout, QWidget, QTabWidget, QPushButton, QVBoxLayout)

class CustomBand(QRubberBand):

    def __init__(self, shape, parent, borderColor=Qt.blue, thickness=2):
        super().__init__(shape, parent)
        self.setBorder(borderColor, thickness)
    
    def setBorder(self, color, thickness):
        self._borderColor = color
        self._borderThickness = thickness

    def paintEvent(self, event):
        painter = QPainter()
        pen = QPen(self._borderColor, self._borderThickness)
        pen.setStyle(Qt.SolidLine)
        painter.begin(self)
        painter.setPen(pen)
        painter.drawRect(event.rect())
        painter.end()
        return super().paintEvent(event)

class ViewSettings(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        self.setLayout(QGridLayout(self))
        self.restoreSettings()
        self.initButtons()
        self.initLiveView()
        self.updateLiveView()

# ----------------------------------- View Updates ----------------------------------- #

    def resizeEvent(self, event):
        if self._liveView is not None:
            # Resize rubber band when window size is changed
            w = 0.25 * self._liveView.width() 
            y = 0.05 * self._liveView.height()
            x = self._liveView.width() - w - y
            h = self._liveView.height() - 2*y
            self._rubberBand.setGeometry(x, y, w, h)
        return super().resizeEvent(event)

    def updateLiveView(self, inSettings = True):

        def colorToRGBA(objectName):
            # Convert QColor to a QSS string of the following format:
            # "rgba(<red>, <green>, <blue>, <alpha>)"
            _c = getattr(self, objectName)
            if self._properties[objectName] == 'rgba':
                color = f"rgba({_c.red()}, {_c.green()}, {_c.blue()}, {_c.alpha()})"
                return color

        # Update preview text style
        _previewPadding = f"{self.previewPadding}px"
        _previewColor = colorToRGBA('previewColor')
        _previewBackground = colorToRGBA('previewBackground')
        # TODO: Window color is not set properly since parent color is different
        # BUG: Styles are not being applied to liveView object
        _windowColor = colorToRGBA('windowColor')
        styles = f"""
            QLabel#previewText {{ 
                color: {_previewColor};
                background-color: {_previewBackground}; 
                padding: {_previewPadding};
                font-family: {self.previewFont.family()};
                font-size: {self.previewFont.pointSize()}pt;
                margin-top: 0.02em;
                margin-left: 0.02em;
            }}
        """
        if inSettings:
            self.setStyleSheet(styles)
        elif not inSettings:
            self.parent.setStyleSheet(styles)

        # Update rubberband color scheme
        # BUG: Rubberband not updating on start (in live preview)
        # TODO: Rubberband outline looks bad
        palette = QPalette()
        palette.setBrush(QPalette.Highlight, QBrush(self.selectionBackground))
        self._rubberBand.setPalette(palette)
        self._rubberBand.setBorder(self.selectionBorderColor, self.selectionBorderThickness)

# ------------------------------------- Settings ------------------------------------- #

    def restoreSettings(self):
        self.settings = QSettings("./utils/MangaOCR-view.ini", QSettings.IniFormat)
        # Properties and defaults
        self._defaults = {
            # Preview
            'previewFont': QFont("Arial", 16),
            'previewColor': QColor(239, 240, 241, 255),
            'previewBackground': QColor(72, 75, 106, 230),
            'previewPadding': 10,
            # Selection rubberband
            'selectionBorderColor': QColor(0, 128, 255, 60),
            'selectionBorderThickness': 2,
            'selectionBackground': QColor(0, 128, 255, 255),
            'windowColor': QColor(255, 255, 255, 3)
        }
        self._properties = {
            # Preview
            'previewFont': 'font',
            'previewColor': 'rgba',
            'previewBackground': 'rgba',
            'previewPadding': 'dist',
            # Selection rubberband
            'selectionBorderColor': 'color',
            'selectionBorderThickness': 'dist',
            'selectionBackground': 'color',
            'windowColor': 'rgba'
        }
        for propName, propType in self._properties.items():
            try:
                # Find the property in settings
                # Set it as the value if it exists
                if propType == 'rgba':
                    prop = self.settings.value(propName)
                elif propType == 'color':
                    prop = self.settings.value(propName)
                elif propType == 'dist':
                    prop = int(self.settings.value(propName))
                elif propType == 'font':
                    prop = self.settings.value(propName)
                if prop is not None:
                    setattr(self, propName, prop)
                    self.settings.setValue(propName, prop)
                else: raise TypeError
            except:
                # Property does not exist in settings
                # Use default value
                setattr(self, propName, self._defaults[propName])
                self.settings.setValue(propName, self._defaults[propName])

# -------------------------------- UI Initializations -------------------------------- #

    def initButtons(self):

        # ------------------------------- Preview Text ------------------------------- #

        # Button Initializations
        _previewTitle = QLabel("Preview ")
        _previewFont = QPushButton("Font Style")
        _previewColor = QPushButton("Font Color")
        _previewBackground = QPushButton("Background Color")
        _previewPadding = QPushButton("Padding")

        # Layout
        self.layout().addWidget(_previewTitle, 0, 0, 1, 1)
        self.layout().addWidget(_previewFont, 0, 1, 1, 2)
        self.layout().addWidget(_previewColor, 0, 3, 1, 2)
        self.layout().addWidget(_previewBackground, 0, 5, 1, 2)
        self.layout().addWidget(_previewPadding, 0, 7, 1, 2)

        # Signals and Slots
        _previewColor.clicked.connect(lambda: self.getColor_('previewColor'))        
        _previewBackground.clicked.connect(lambda: self.getColor_('previewBackground'))
        _previewFont.clicked.connect(lambda: self.getFont_('previewFont'))
        _previewPadding.clicked.connect(lambda: self.getInt_('previewPadding'))

        # --------------------------- Selection Rubberband --------------------------- #        

        # Button Initializations
        _selectionTitle = QLabel("Selection ")
        _selectionBorderColor = QPushButton("Border Color")
        _selectionBorderThickness = QPushButton("Border Thickness")
        _selectionBackground = QPushButton("Mask Color")
        _windowColor = QPushButton("Window Color")

        # Layout
        self.layout().addWidget(_selectionTitle, 1, 0, 1, 1)
        self.layout().addWidget(_selectionBorderColor, 1, 1, 1, 2)
        self.layout().addWidget(_selectionBorderThickness, 1, 3, 1, 2)
        self.layout().addWidget(_selectionBackground, 1, 5, 1, 2)
        self.layout().addWidget(_windowColor, 1, 7, 1, 2)

        # Signals and Slots
        _selectionBorderColor.clicked.connect(lambda: self.getColor_('selectionBorderColor'))
        _selectionBackground.clicked.connect(lambda: self.getColor_('selectionBackground'))
        _selectionBorderThickness.clicked.connect(lambda: self.getInt_('selectionBorderThickness'))
        _windowColor.clicked.connect(lambda: self.getColor_('windowColor'))

    def initLiveView(self):
        # Live View
        self._liveView = QWidget()
        self._liveView.setObjectName('liveView')
        self._liveView.setLayout(QGridLayout(self._liveView))

        # Selection Rubberband Live View
        self._rubberBand = CustomBand(CustomBand.Rectangle, self._liveView)
        self._rubberBand.setObjectName('selectionBand')
        
        # Preview Text Live View
        self._previewText = QLabel(" Sample Text ")
        self._previewText.setObjectName('previewText')
        self._previewText.adjustSize()
        self._liveView.layout().addWidget(self._previewText, 0, 0, alignment=Qt.AlignTop | Qt.AlignLeft)
        self._rubberBand.show()
        self.layout().addWidget(self._liveView, 2, 0, -1, -1)

# --------------------------- Property Setters and Getters --------------------------- #

    def setProperty_(self, objectName, value):
        # Set the value of a member of this class with name objectName
        self.settings.setValue(objectName, value)
        setattr(self, objectName, value)
        self.updateLiveView()

    def getColor_(self, objectName):
        try:
            initialColor = self.settings.value(objectName)
        except:
            initialColor = None
        if initialColor is None:
            initialColor = self._defaults[objectName]
        color = QColorDialog().getColor(initial=initialColor, options=QColorDialog.ShowAlphaChannel)
        if color.isValid():
            self.setProperty_(objectName, color)

    def getFont_(self, objectName):
        try:
            initialFont = self.settings.value(objectName)
        except:
            initialFont = None
        if initialFont is None:
            initialFont = self._defaults[objectName]
        font, accepted = QFontDialog().getFont(initialFont)
        if accepted:
            self.setProperty_(objectName, font)

    def getInt_(self, objectName):
        try:
            initialInt = int(self.settings.value(objectName))
        except:
            initialInt = None
        if initialInt is None:
            initialInt = self._defaults[objectName]
        i, accepted = QInputDialog.getInt(
            self,
            "Margin/Padding Settings",
            f"Enter a value between 5 and 100:",
            value=initialInt,
            min=5,
            max=100,
            flags=Qt.CustomizeWindowHint | Qt.WindowTitleHint)

        if accepted:
            self.setProperty_(objectName, i)

class HotkeySettings(QWidget):

    class HotkeyContainer(QWidget):

        def __init__(self, shortcutName):
            super().__init__()

            # Layout and margins
            self.setLayout(QHBoxLayout(self))
            self.layout().setAlignment(Qt.AlignTop)
            _margin = self.layout().contentsMargins()
            _margin.setBottom(0)
            _margin.setTop(7)
            self.layout().setContentsMargins(_margin)

            self.initButtons(shortcutName)
            self.restoreSettings()

        # ----------------------- Settings and Initializations ----------------------- #

        def initButtons(self, shortcutName):
            self.shortcutName = QLabel(shortcutName)

            # Modifiers
            self.shiftCheckBox = QCheckBox("Shift")
            self.ctrlCheckBox = QCheckBox("Ctrl")
            self.altCheckBox = QCheckBox("Alt")
            self.winCheckBox = QCheckBox("Win")

            # Key
            _validKeyList = ["<Unmapped>", "A", "B", "C", "D", "E", "F", "G", 
                            "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q",
                            "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
            self.keyComboBox = QComboBox()
            self.keyComboBox.addItems(_validKeyList)

            # Layout
            self.layout().addWidget(self.shortcutName, alignment=Qt.AlignLeft)
            self.layout().addStretch()
            self.layout().addWidget(self.shiftCheckBox, alignment=Qt.AlignRight)
            self.layout().addWidget(self.ctrlCheckBox, alignment=Qt.AlignRight)
            self.layout().addWidget(self.altCheckBox, alignment=Qt.AlignRight)
            self.layout().addWidget(self.winCheckBox, alignment=Qt.AlignRight)
            self.layout().addWidget(self.keyComboBox, alignment=Qt.AlignRight)

        def restoreSettings(self):
            self.settings = QSettings("./utils/Manga2OCR-hotkey.ini", QSettings.IniFormat)

            # Properties and defaults
            _shortcutText = self.shortcutName.text().split(" ")
            _shortcutName = _shortcutText[0].lower() + "".join(s.title() for s in _shortcutText[1:])
            self._properties = {
                f"{_shortcutName}Shift": 'shiftCheckBox',
                f"{_shortcutName}Ctrl": 'ctrlCheckBox',
                f"{_shortcutName}Alt": 'altCheckBox',
                f"{_shortcutName}Cmd": 'winCheckBox',
                f"{_shortcutName}Key": 'keyComboBox'
            }
            self._defaults = {
                "startCaptureAlt": True,
                "startCaptureKey": 17 # index of Q in _validKeyList
            }

            def setObjectState(objectName, objectState):
                # Check if the object is a checkbox or combo box
                try:
                    getattr(self, objectName).setChecked(objectState)
                except AttributeError:
                    getattr(self, objectName).setCurrentIndex(objectState)

            for propName, propObject in self._properties.items():
                try:
                    # Set default state if it exists
                    if propName in self._defaults:
                        setObjectState(propObject, self._defaults[propName])
                        setattr(self, propName, self._defaults[propName])
                        continue
                    # Override default state if saved in settings
                    prop = self.settings.value(propName)
                    if prop is not None:
                        setObjectState(propObject, prop)
                        setattr(self, propName, prop)
                        # self.settings.setValue(propName, prop)
                    else: raise TypeError
                except:
                    # No existing default or saved settings
                    # Therefore, action is unmapped
                    setObjectState(propObject, 0)
                    setattr(self, propName, 0)
                    # self.settings.setValue(propName, 0)

        def saveSettings(self):
            _shortcut = ""
            _shortcut += "<shift>+" * self.shiftCheckBox.isChecked()
            _shortcut += "<ctrl>+" * self.ctrlCheckBox.isChecked()
            _shortcut += "<alt>+" * self.altCheckBox.isChecked()
            _shortcut += "<cmd>+" * self.winCheckBox.isChecked()

            _key = self.keyComboBox.currentText()
            if _key == "<Unmapped>": _key = ""
            _shortcut += _key

            for propName, _ in self._properties.items():
                self.settings.setValue(propName, getattr(self, propName))

            _shortcutText = self.shortcutName.text().split(" ")
            _shortcutName = _shortcutText[0].lower() + "".join(s.title() for s in _shortcutText[1:])

            return _shortcut, _shortcutName

    def __init__(self):
        super().__init__()

        # Layout and margins
        self.setLayout(QVBoxLayout(self))
        self.layout().setAlignment(Qt.AlignTop)

        self.a = self.HotkeyContainer("Start Capture")

        self.layout().addWidget(self.a)
        self.layout().addWidget(self.HotkeyContainer("Open Settings"))
        self.layout().addWidget(self.HotkeyContainer("Toggle Logging"))
        self.layout().addWidget(self.HotkeyContainer("Close Application"))

    def mouseDoubleClickEvent(self, event):
        self.a.saveSettings()
        return super().mouseDoubleClickEvent(event)

class SettingsMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tabs = QTabWidget()
        self.tabs.addTab(HotkeySettings(), "HOTKEYS")
        self.tabs.addTab(ViewSettings(), "VIEW")

        self.setLayout(QVBoxLayout(self))
        self.layout().addWidget(self.tabs)
        self.setFixedSize(625, 400)

