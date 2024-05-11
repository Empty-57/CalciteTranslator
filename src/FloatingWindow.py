from PySide6.QtCore import Qt, QPoint, QSize
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QSizePolicy, QLabel
from qfluentwidgets import CommandBar, Action, FluentIcon, SingleDirectionScrollArea


class FloatingWindow(QWidget):
    def __init__(self, config, parent=None):
        super().__init__(parent=parent)
        self._startPos = None
        self._endPos = None
        self._move = False

        self.config = config
        self.font_size: int = self.config.get(self.config.font_size)
        self.font: str = self.config.get(self.config.font)
        self.font_color: QColor = self.config.get(self.config.font_color)
        self.box_color: QColor = self.config.get(self.config.box_color)

        self.scrollArea = SingleDirectionScrollArea(orient=Qt.Orientation.Vertical)
        # 动态调整大小
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.commandBar = CommandBar()
        self.commandBar.setIconSize(QSize(12, 12))
        self._fontsize_inc = Action(FluentIcon.ADD.icon(color='#f08a5d'), '字号+')
        self._fontsize_dec = Action(FluentIcon.REMOVE.icon(color='#30e3ca'), '字号-')

        self.vBoxLayout_side = QVBoxLayout(self)
        self.vBoxLayout_side.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.vBoxLayout = QVBoxLayout()
        self.view = QWidget()
        self.view.setLayout(self.vBoxLayout)
        self.hBoxLayout = QHBoxLayout()
        self.text_label = QLabel(text="デフォルト値")

        self.status_bar = QWidget(self)
        self.status_text = QLabel(text="waiting...")

        self.init()
        self.resize(600, 100)

    def init(self):
        self.setWindowFlags(
            Qt.WindowType.SplashScreen |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._fontsize_inc.triggered.connect(lambda: self.__fontsize_inc__())
        self._fontsize_dec.triggered.connect(lambda: self.__fontsize_dec__())

        self.commandBar.addActions([
            self._fontsize_inc,
            self._fontsize_dec,
        ])
        self.commandBar.addSeparator()

        self.text_label.setFont(QFont(self.font, self.font_size))
        self.text_label.setWordWrap(True)
        self.text_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.status_text.setFont(QFont(self.font, 12))
        self.status_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout_side.setSpacing(1)
        self.vBoxLayout_side.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)

        self.status_bar.setLayout(self.hBoxLayout)
        self.hBoxLayout.addWidget(self.commandBar, 1)
        self.hBoxLayout.addWidget(self.status_text, 3, Qt.AlignmentFlag.AlignLeft)
        self.vBoxLayout.addWidget(self.text_label)

        self.scrollArea.setWidget(self.view)

        self.scrollArea.setStyleSheet("QScrollArea{background: transparent; border: none}")
        # 必须给内部的视图也加上透明背景样式
        self.view.setStyleSheet("QWidget{background: transparent}")
        self.vBoxLayout_side.addWidget(self.status_bar)
        self.vBoxLayout_side.addWidget(self.scrollArea)

        text_label_qss = f"""
                background-color: #{hex(self.box_color.rgba())[2:]:0>8};
                color: #{hex(self.font_color.rgba())[2:]:0>8};
                border-radius:0px;
                """
        self.text_label.setStyleSheet(text_label_qss)

        self.status_text.setStyleSheet(
            """
            color: #66ffffff;
            background-color: rgba(33, 33, 33,0);
            """
        )

        self.status_bar.setStyleSheet(
            """
            background-color: rgba(48, 56, 65,0.8);
            """
        )

    def set_text(self, text):
        if text[0]:
            self.text_label.setText(text[0][0])
        if not text[1]:
            self.status_text.setText("翻译中……")
        else:
            self.status_text.setText(f"翻译用时:{text[1]}s 翻译源:{self.config.get(self.config.translator).value}")

    def __fontsize_inc__(self):
        if self.font_size < 20:
            self.font_size += 1
            self.config.set(self.config.font_size, self.font_size)
            self.text_label.setFont(QFont(self.font, self.font_size))

    def __fontsize_dec__(self):
        if self.font_size > 10:
            self.font_size -= 1
            self.config.set(self.config.font_size, self.font_size)
            self.text_label.setFont(QFont(self.font, self.font_size))

    def reset(self):
        self.text_label.setText("デフォルト値")
        self.text_label.setFont(QFont(self.font, self.font_size))
        self.status_text.setText("waiting...")

    # 单击鼠标触发事件
    def mousePressEvent(self, event):
        # move event
        if event.button() == Qt.MouseButton.LeftButton:
            self._startPos = QPoint(event.x(), event.y())
            self._move = True

    # 鼠标移动事件
    def mouseMoveEvent(self, event):
        # move event
        if self._move:
            self._endPos = event.pos() - self._startPos
            self.move(self.pos() + self._endPos)

    # 鼠标释放事件
    def mouseReleaseEvent(self, event):
        # flag ret
        if event.button() == Qt.MouseButton.LeftButton:
            self._move = False
            self._startPos = None
            self._endPos = None
