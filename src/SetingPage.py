from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import (
    ComboBoxSettingCard,
    FluentIcon,
    ColorSettingCard,
    setCustomStyleSheet,
    OptionsSettingCard,
    BodyLabel,
    setTheme,
    qconfig,
    SingleDirectionScrollArea,
    SwitchSettingCard,
    MSFluentWindow, TransparentToolButton, ToolTipFilter, ToolTipPosition
)


class SetPageWidget(QWidget):

    def __init__(self, text: str, config, float_w, parent: MSFluentWindow = None):
        super().__init__(parent=parent)
        self.text = text
        self.config = config
        self.float_w = float_w
        self.main_window = parent

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

        self.vBoxLayout.setSpacing(1)

        self.title_1 = BodyLabel(text="文字窗设置")
        self.title_2 = BodyLabel(text="个性化")

        self.init()

    def init(self):
        self.vBoxLayout.setContentsMargins(30, 15, 50, 15)

        self.title_1.setFont(QFont('Arial', 16))

        self.title_2.setFont(QFont('Arial', 16))

        self.title_1.setFixedHeight(50)

        self.title_2.setFixedHeight(50)

        font_size_card = ComboBoxSettingCard(
            configItem=self.config.font_size,
            icon=FluentIcon.FONT_SIZE,
            title="字体大小",
            content="设置文字大小",
            texts=[str(i) for i in range(10, 21)],
        )
        self.config.font_size.valueChanged.connect(lambda value: self.font_size_changed(value))

        font_card = ComboBoxSettingCard(
            configItem=self.config.font,
            icon=FluentIcon.FONT,
            title="字体",
            content="设置字体",
            texts=["Arial"],
        )
        self.config.font.valueChanged.connect(
            lambda value: self.float_w.text_label.setFont(QFont(value, self.config.get(self.config.font_size)))
        )

        font_color_card = ColorSettingCard(
            configItem=self.config.font_color,
            icon=FluentIcon.BRUSH,
            title="文字颜色",
            content="设置文字颜色",
            enableAlpha=True
        )
        font_color_rst = TransparentToolButton(FluentIcon.CANCEL)
        font_color_rst.setToolTip('恢复默认值')
        font_color_rst.installEventFilter(ToolTipFilter(font_color_rst, showDelay=300, position=ToolTipPosition.TOP))
        font_color_rst.clicked.connect(self.font_color_rst)
        font_color_card.hBoxLayout.addWidget(font_color_rst)
        font_color_card.hBoxLayout.addSpacing(16)
        self.config.font_color.valueChanged.connect(lambda value: self.font_color_changed(value))

        box_color_card = ColorSettingCard(
            configItem=self.config.box_color,
            icon=FluentIcon.PALETTE,
            title="文字窗颜色",
            content="设置文字窗颜色",
            enableAlpha=True
        )
        box_color_rst = TransparentToolButton(FluentIcon.CANCEL)
        box_color_rst.setToolTip('恢复默认值')
        box_color_rst.installEventFilter(ToolTipFilter(box_color_rst, showDelay=300, position=ToolTipPosition.TOP))
        box_color_rst.clicked.connect(self.box_color_rst)
        box_color_card.hBoxLayout.addWidget(box_color_rst)
        box_color_card.hBoxLayout.addSpacing(16)
        self.config.box_color.valueChanged.connect(lambda value: self.box_color_changed(value))

        mica_effect_card = SwitchSettingCard(
            configItem=self.config.mica_effect_enable,
            icon=FluentIcon.TRANSPARENT,
            title="启用云母效果",
            content="云母效果的视觉体验更好，但是仅支持Win11",
        )
        self.config.mica_effect_enable.valueChanged.connect(lambda value: self.main_window.setMicaEffectEnabled(value))

        theme_card = OptionsSettingCard(
            configItem=qconfig.themeMode,
            icon=FluentIcon.BACKGROUND_FILL,
            title="主题",
            content="设置主题外观",
            texts=["浅色", "深色", "跟随系统"]
        )
        qconfig.themeChanged.connect(lambda value: setTheme(value))

        self.vBoxLayout.addWidget(self.title_1, Qt.AlignmentFlag.AlignLeft)
        self.vBoxLayout.addWidget(font_size_card, 1)
        self.vBoxLayout.addWidget(font_card, 1)
        self.vBoxLayout.addWidget(font_color_card, 1)
        self.vBoxLayout.addWidget(box_color_card, 1)
        self.vBoxLayout.addWidget(self.title_2, 1, Qt.AlignmentFlag.AlignLeft)
        self.vBoxLayout.addWidget(mica_effect_card, 1)
        self.vBoxLayout.addWidget(theme_card, 1)
        self.vBoxLayout.addStretch(1)

        self.scrollArea.setWidget(self.view)

        self.scrollArea.setStyleSheet("QScrollArea{background: transparent; border: none}")
        # 必须给内部的视图也加上透明背景样式
        self.view.setStyleSheet("QWidget{background: transparent}")
        self.hBoxLayout.addWidget(self.scrollArea, 1)

        # 必须给子界面设置全局唯一的对象名
        self.setObjectName(self.text.replace(' ', '-'))

    def font_size_changed(self, value):
        self.float_w.text_label.setFont(QFont(self.config.get(self.config.font), value))
        self.float_w.font_size = value

    def font_color_changed(self, value):
        box_color = self.config.get(self.config.box_color)
        text_label_qss = f"""
                        BodyLabel{{
                        background-color: {'#' + str(hex(box_color.alpha()))[2:] + str(box_color.name())[1:]};
                        color: {'#' + str(hex(value.alpha()))[2:] + str(value.name())[1:]};
                        border-radius:0px;  
                        }}
                        """
        setCustomStyleSheet(self.float_w.text_label, text_label_qss, text_label_qss)

    def font_color_rst(self):
        box_color = self.config.get(self.config.box_color)
        text_label_qss = f"""
                            BodyLabel{{
                            background-color: {'#' + str(hex(box_color.alpha()))[2:] + str(box_color.name())[1:]};
                            color: "#cc00adb5";
                            border-radius:0px;  
                            }}
                            """
        setCustomStyleSheet(self.float_w.text_label, text_label_qss, text_label_qss)
        self.config.set(self.config.font_color, "#cc00adb5")

    def box_color_changed(self, value):
        font_color = self.config.get(self.config.font_color)
        box_qss = f"""
                    BodyLabel{{
                    background-color: {'#' + str(hex(value.alpha()))[2:] + str(value.name())[1:]};
                    color: {'#' + str(hex(font_color.alpha()))[2:] + str(font_color.name())[1:]};
                    border-radius:0px;  
                    }}
                    """
        setCustomStyleSheet(self.float_w.text_label, box_qss, box_qss)

    def box_color_rst(self):
        font_color = self.config.get(self.config.font_color)
        box_qss = f"""
                                BodyLabel{{
                                background-color: #cc212121;
                                color: {'#' + str(hex(font_color.alpha()))[2:] + str(font_color.name())[1:]};
                                border-radius:0px;  
                                }}
                                """
        setCustomStyleSheet(self.float_w.text_label, box_qss, box_qss)
        self.config.set(self.config.box_color, "#cc212121")
