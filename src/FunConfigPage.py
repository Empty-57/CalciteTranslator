from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
from qfluentwidgets import SingleDirectionScrollArea, BodyLabel, OptionsSettingCard, FluentIcon

from Translator import translation_source_selector


class FunConfigPageWidget(QWidget):
    def __init__(self, text: str, config,float_w, mask_w):
        super().__init__()
        self.text = text
        self.config = config
        self.float_w = float_w
        self.mask_w = mask_w

        self.scrollArea = SingleDirectionScrollArea(orient=Qt.Orientation.Vertical)
        # 动态调整大小
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.view = QWidget()
        self.vBoxLayout = QVBoxLayout()
        self.view.setLayout(self.vBoxLayout)

        self.title_2 = BodyLabel(text="翻译源设置")
        self.title_2_1 = BodyLabel(text="免费翻译源，无需配置，但不稳定")

        self.vBoxLayout.setSpacing(1)

        self.init()

    def init(self):
        self.title_2.setFixedHeight(50)
        self.title_2_1.setFixedHeight(30)

        self.title_2.setFont(QFont('Arial', 16))
        self.title_2_1.setFont(QFont('Arial', 12))

        translator_card = OptionsSettingCard(
            configItem=self.config.translator,
            icon=FluentIcon.LANGUAGE,
            title="翻译源",
            content="设置翻译源",
            texts=["百度翻译", "福昕翻译", "有道翻译", "Mirai翻译"],
        )
        self.config.translator.valueChanged.connect(lambda value: self.translator_changed(value))

        self.vBoxLayout.addWidget(self.title_2, Qt.AlignmentFlag.AlignLeft)
        self.vBoxLayout.addWidget(self.title_2_1, Qt.AlignmentFlag.AlignLeft)
        self.vBoxLayout.addWidget(translator_card, 1)
        self.vBoxLayout.addStretch(1)

        self.scrollArea.setWidget(self.view)

        self.scrollArea.setStyleSheet("QScrollArea{background: transparent; border: none}")
        # 必须给内部的视图也加上透明背景样式
        self.view.setStyleSheet("QWidget{background: transparent}")
        self.hBoxLayout.addWidget(self.scrollArea, 1)

        # 必须给子界面设置全局唯一的对象名
        self.setObjectName(self.text.replace(' ', '-'))

    def translator_changed(self, value):
        if all((self.float_w.isVisible(), self.mask_w.isVisible())):
            del self.mask_w.Translator
            self.mask_w.Translator = translation_source_selector(value.value)
