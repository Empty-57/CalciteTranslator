from PySide6.QtWidgets import QWidget


class FunConfigPageWidget(QWidget):
    def __init__(self, text: str, parent=None):
        super().__init__()
        self.text = text
        self.init()

    def init(self):
        # 必须给子界面设置全局唯一的对象名
        self.setObjectName(self.text.replace(' ', '-'))
