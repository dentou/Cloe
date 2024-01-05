

from typing import Any

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QCheckBox, QComboBox, QHBoxLayout, QLabel

from ..base import BaseSettings
from utils.constants import (
    OCR_DEFAULT,
    OCR_CONFIG,
    # UNMAPPED_KEY,
    VALID_OCR_ENGINE_LIST,
)


class OcrContainer(BaseSettings):
    """Generic container for hotkey settings component

    Args:
        shortcutLabel (str): Text based on the name of the callable in the system tray application.
    """

    def __init__(self):
        super().__init__(None, OCR_CONFIG, self._shortcutName)

        self._defaults = OCR_DEFAULT

        # Layout
        self.setLayout(QHBoxLayout(self))
        self.layout().setAlignment(Qt.AlignTop)
        margin = self.layout().contentsMargins()
        margin.setBottom(0)
        margin.setTop(7)
        self.layout().setContentsMargins(margin)

        self.initWidgets()
        self.loadSettings()

    # ------------------------------ UI Initializations ----------------------------- #

    def initWidgets(self):
        """
        Initialize checkboxes for the modifiers and combobox for the main key
        """
        # self.shortcutLabel = QLabel(shortcutLabel)
        self.engineLabel = QLabel("Engine Name")

        # Key
        self.engineSelect = QComboBox()
        self.engineSelect.addItems(VALID_OCR_ENGINE_LIST)

        # # Layout
        self.layout().addWidget(self.engineLabel, alignment=Qt.AlignLeft)
        self.layout().addStretch()
        self.layout().addWidget(self.engineSelect, alignment=Qt.AlignRight)

    # ----------------------------------- Settings ---------------------------------- #

    def saveSettings(self):
        # hotkey = self.getHotkeyText()
        engineName = self.engineSelect.currentText()
        # if not hotkey:
        #     return self.loadSettings()
        engineSettings = self.settings.value("engine", {}, type=dict)
        engineSettings["name"] = engineName
        # TODO populate engine specific settings
        self.settings.setValue("engine", engineSettings)
        return super().saveSettings(hasMessage=False)

    # ------------------------------ Helpers Functions ------------------------------ #

        

    # def getHotkeyText(self):
    #     """
    #     Computes hotkey combination text based on checkbox and combobox states
    #     """
    #     modifierText = ""
    #     for modifier in self.modifiers:
    #         if modifier.isChecked():
    #             modifierText += f"<{modifier.text()}>+"

    #     key = self.mainKey.currentText()
    #     if key == UNMAPPED_KEY:
    #         return ""
    #     modifierText += key
    #     return modifierText

    def getProperty(self, prop: str):
        # Overridden to handle checkbox and combobox
        obj = getattr(self, prop)
        if isinstance(obj, QCheckBox):
            return obj.isChecked()
        elif isinstance(obj, QComboBox):
            return obj.currentIndex()
        return super().getProperty(prop)

    def setProperty(self, prop: str, value: Any):
        # Overridden to handle checkbox and combobox
        obj = getattr(self, prop)
        if isinstance(obj, QCheckBox):
            return obj.setChecked(value.lower() == "true")
        elif isinstance(obj, QComboBox):
            return obj.setCurrentIndex(int(value))
        return super().setProperty(prop, value)
