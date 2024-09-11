import json

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLineEdit
from qfluentwidgets import SingleDirectionScrollArea, BodyLabel, OptionsSettingCard, FluentIcon

from Translator import translation_source_selector


class FunConfigPageWidget(QWidget):
    def __init__(self, text: str, config, float_w, mask_w, parent=None):
        super().__init__()
        self.text = text
        self.config = config
        self.float_w = float_w
        self.mask_w = mask_w
        self.parent = parent

        self.scrollArea = SingleDirectionScrollArea(orient=Qt.Orientation.Vertical)
        # 动态调整大小
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.SideLayout = QVBoxLayout(self)
        self.SideLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.view = QWidget()
        self.vBoxLayout = QVBoxLayout()
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.view.setLayout(self.vBoxLayout)

        self.vBoxLayout.setSpacing(1)

        self.title = BodyLabel(text="功能配置")
        self.title_1 = BodyLabel(text="翻译源选择")
        self.title_1_1 = BodyLabel(text="选择自带的翻译源或者配置API")
        self.title_2 = BodyLabel(text="API配置")
        self.title_2_1 = BodyLabel(text="百度API")

        self.bd_apiItem_1 = QHBoxLayout()
        self.bd_apiItem_1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bd_appid_text = BodyLabel(text="APPID")
        self.bd_key_text = BodyLabel(text="KEY")
        self.bd_appid_edit = QLineEdit()
        self.bd_key_edit = QLineEdit()
        self.bd_appid_edit.setPlaceholderText("APPID")
        self.bd_key_edit.setPlaceholderText("KEY")
        self.bd_apiItem_1.setSpacing(10)

        self.init()

    def init(self):
        with open(r'config\api_config.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.bd_appid_edit.setText(data['Baidu_API']['APPID'])
        self.bd_key_edit.setText(data['Baidu_API']['KEY'])
        self.bd_appid_edit.editingFinished.connect(lambda: self.update_api(type_='bd'))
        self.bd_key_edit.editingFinished.connect(lambda: self.update_api(type_='bd'))

        self.bd_apiItem_1.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setContentsMargins(0, 15, 30, 15)
        self.SideLayout.setContentsMargins(30, 15, 0, 15)

        self.title_1.setFixedHeight(50)
        self.title_1_1.setFixedHeight(30)
        self.title_2.setFixedHeight(50)
        self.title_2_1.setFixedHeight(30)

        self.bd_appid_edit.setMinimumHeight(40)
        self.bd_key_edit.setMinimumHeight(40)

        self.title.setFont(QFont('Arial', 20))
        self.title_1.setFont(QFont('Arial', 16))
        self.title_1_1.setFont(QFont('Arial', 12))
        self.title_2.setFont(QFont('Arial', 16))
        self.title_2_1.setFont(QFont('Arial', 12))

        translator_card = OptionsSettingCard(
            configItem=self.config.translator,
            icon=FluentIcon.LANGUAGE,
            title="翻译源",
            content="设置翻译源",
            texts=["百度-在线", "福昕-在线", "有道-在线", "Mirai-在线", "百度-API"],
        )
        self.config.translator.valueChanged.connect(lambda value: self.translator_changed(value))

        self.vBoxLayout.addWidget(self.title_1, Qt.AlignmentFlag.AlignLeft)
        self.vBoxLayout.addWidget(self.title_1_1, Qt.AlignmentFlag.AlignLeft)
        self.vBoxLayout.addWidget(translator_card)
        self.vBoxLayout.addSpacing(20)

        self.vBoxLayout.addWidget(self.title_2, Qt.AlignmentFlag.AlignLeft)
        self.vBoxLayout.addSpacing(10)
        self.vBoxLayout.addWidget(self.title_2_1, Qt.AlignmentFlag.AlignLeft)
        self.vBoxLayout.addLayout(self.bd_apiItem_1)
        self.bd_apiItem_1.addWidget(self.bd_appid_text)
        self.bd_apiItem_1.addWidget(self.bd_appid_edit, 2)
        self.bd_apiItem_1.addStretch(1)
        self.bd_apiItem_1.addWidget(self.bd_key_text)
        self.bd_apiItem_1.addWidget(self.bd_key_edit, 2)
        self.vBoxLayout.addStretch(1)

        self.scrollArea.setWidget(self.view)

        self.scrollArea.setStyleSheet("QScrollArea{background: transparent; border: none}")
        # 必须给内部的视图也加上透明背景样式
        self.view.setStyleSheet("QWidget{background: transparent}")
        self.SideLayout.addWidget(self.title)
        self.SideLayout.addWidget(self.scrollArea)

        # 必须给子界面设置全局唯一的对象名
        self.setObjectName(self.text.replace(' ', '-'))

    def translator_changed(self, value):
        if all((self.float_w.isVisible(), self.mask_w.isVisible())):
            del self.mask_w.Translator
            self.mask_w.Translator = translation_source_selector(value.value)

    def update_api(self, type_):
        path = r'config\api_config.json'
        if type_ == 'bd':
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                data['Baidu_API']['APPID'] = self.bd_appid_edit.text()
                data['Baidu_API']['KEY'] = self.bd_key_edit.text()
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
