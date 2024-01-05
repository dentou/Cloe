

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout, QWidget

from ..tab import BaseSettingsTab
from .container import OcrContainer
from utils.constants import OCR_CONFIG


class OcrSettingsTab(BaseSettingsTab):
    """
    Settings tab for hotkey-related settings
    """

    def __init__(self, parent: QWidget):
        super().__init__(parent, OCR_CONFIG)

        # Layout and margins
        self.setLayout(QGridLayout(self))
        self.layout().setAlignment(Qt.AlignTop)

        self.initializeHotkeyContainers()
        self.layout().addWidget(QWidget())
        self.layout().setRowStretch(self.layout().rowCount() - 1, 1)
        self.addButtonBar(self.layout().rowCount())

# ---------------------------- UI Initializations --------------------------- #

    def initializeContainers(self):
        """Initialize HotkeyContainer widgets for the given actions

        *Note: The action must be a callable name in the system tray app
        (converted to TitleCase separated by whitespace).
        """

        self.containers: dict[str, QWidget] = {}

        engineContainer = OcrContainer()
        self.containers["Engine"] = engineContainer
        self.layout().addWidget(engineContainer)
        # actions = ["Start Capture", "Open Settings", "Close Application"]
        # for action in actions:
        #     self.containers.append(HotkeyContainer(action))
        #     self.layout().addWidget(self.containers[-1])

# --------------------------------- Settings -------------------------------- #

    def saveSettings(self):
        for container in self.containers.values():
            container.saveSettings()
        super().saveSettings()
        self.menu.onSaveHotkeys()

    def loadSettings(self):
        for container in self.containers.values():
            container.loadSettings()
