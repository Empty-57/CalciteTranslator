import time
import pyautogui
from PySide6.QtCore import QSize, Qt, QPoint, QThread, Signal
from PySide6.QtWidgets import QWidget, QGridLayout, QHBoxLayout
from qfluentwidgets import CommandBar, Action, FluentIcon, TransparentToolButton
from TextRecognition import OCR
from Translator import translation_source_selector


def time_keeper(func):
    def _(*args, **kwargs):
        time_ = time.time()
        func_ = func(*args, **kwargs)
        print(f"Time taken is: < {time.time() - time_:.4f}s >", )
        time_ = f"{time.time() - time_:.2f}"
        return func_, time_

    return _


class MaskWindow(QWidget):
    signer = Signal(tuple)
    ocr = OCR()

    def __init__(self, float_w, config, parent=None):
        super().__init__(parent)
        self._startPos = None
        self._endPos = None

        self._changed = False
        self._auto = False
        self._move = False

        self.float_w = float_w
        self.config = config
        self.ocr_thread = OCRThread(self)
        self.translator_index = self.config.get(self.config.translator).value
        self.Translator = translation_source_selector(self.translator_index)

        # setThemeColor('#393e46')

        self.commandBar = CommandBar()
        self.commandBar.setIconSize(QSize(12, 12))

        self.flushed = Action(FluentIcon.PLAY_SOLID.icon(color='green'), '翻译')
        self._hide = Action(FluentIcon.HIDE.icon(color='#3fc1c9'), '隐藏', checkable=True)

        self._closed = Action(FluentIcon.CLOSE.icon(color='red'), '关闭')
        self._resize = TransparentToolButton(FluentIcon.MINIMIZE.icon(color='#dbe2ef'), '调整大小')

        self._mask = QWidget()
        self._mask1 = QWidget()

        self.hQGridLayout = QGridLayout(self)
        self.hQHBoxLayout = QHBoxLayout()

        self.resize(400, 100)
        self.setMinimumSize(250, 50)
        self.setWindowOpacity(0.8)

        self.init()

    def init(self):
        self.flushed.triggered.connect(lambda: self.__execute__())
        self._hide.triggered.connect(lambda: self.__hide__())
        self._closed.triggered.connect(lambda: self.__close__())
        self._resize.clicked.connect(lambda: self.__resize__())
        self._resize.setToolTip("调整大小")

        self.commandBar.addActions([
            self.flushed,
            self._hide,
            self._closed
        ])

        self.hQGridLayout.addWidget(self._mask, 0, 0)
        self.hQGridLayout.addWidget(self._mask1, 1, 0)

        self._mask1.setLayout(self.hQHBoxLayout)
        self._mask1.setMaximumHeight(35)
        self.hQHBoxLayout.addWidget(self.commandBar, 2)
        self.hQHBoxLayout.addWidget(self._resize, 1, Qt.AlignmentFlag.AlignRight)

        self.hQGridLayout.setSpacing(2)
        self.hQGridLayout.setContentsMargins(0, 0, 0, 0)
        self.hQHBoxLayout.setContentsMargins(0, 0, 0, 0)

        self.setWindowTitle("MaskWindow")
        self.setWindowFlags(
            Qt.WindowType.SplashScreen |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # 窗口透明

        self._mask.setStyleSheet(
            '''
            background-color: rgba(0, 0, 0, 0.1);
            border:2px dashed rgba(255, 0, 0,0.5);
            '''
        )
        self._mask1.setStyleSheet(
            '''
            background-color: rgba(34, 40, 49,0.8);
            '''
        )

    def __execute__(self):
        self.signer.emit(((), False))
        if not self.ocr_thread.isRunning():
            self.ocr_thread.start()

    def __hide__(self):
        if self._hide.isChecked():
            self._mask.setStyleSheet(
                '''
                background-color: rgba(0, 0, 0, 0);
                border:2px dashed rgba(0, 0, 0,0);
                '''
            )
            self._mask1.setStyleSheet(
                '''
                background-color: rgba(34, 40, 49,0.4);
                '''
            )
        else:
            self._mask.setStyleSheet(
                '''
                background-color: rgba(0, 0, 0, 0.1);
                border:2px dashed rgba(255, 0, 0,0.5);
                '''
            )
            self._mask1.setStyleSheet(
                '''
                background-color: rgba(34, 40, 49,0.8);
                '''
            )

    def __close__(self):
        self.float_w.reset()
        self.__reset__()
        self.float_w.close()
        self.float_w.destroy()
        self.close()
        self.destroy()

    def __resize__(self):
        self.windowHandle().startSystemResize(Qt.Edge.RightEdge | Qt.Edge.BottomEdge)

    def __reset__(self):
        self._hide.setChecked(False)
        self.resize(400, 100)
        self._mask.setStyleSheet(
            '''
            background-color: rgba(0, 0, 0, 0.1);
            border:2px dashed rgba(255, 0, 0,0.5);
            '''
        )
        self._mask1.setStyleSheet(
            '''
            background-color: rgba(34, 40, 49,0.8);
            '''
        )

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
            self._changed = True

    # 鼠标释放事件
    def mouseReleaseEvent(self, event):
        if self._changed and self._auto:
            self.__execute__()

        # flag ret
        if event.button() == Qt.MouseButton.LeftButton:
            self._changed = False
            self._move = False
            self._startPos = None
            self._endPos = None


class OCRThread(QThread):
    def __init__(self, mask_obj: MaskWindow):
        super().__init__()
        self.result = None
        self.mask_obj = mask_obj

    def run(self):
        self.mask_obj.signer.emit(self.__execute__())

    @time_keeper
    def __execute__(self):
        _window = pyautogui.getWindowsWithTitle("MaskWindow")[0]
        left, top, width, height = _window.left, _window.top, _window.width, _window.height
        monitor = {"left": left,
                   "top": top,
                   "width": width,
                   "height": int(height - (height / self.mask_obj.height()) * 35)
                   }
        print(monitor)
        self.result = MaskWindow.ocr.execute(monitor)
        self.result = self.result if self.result else 'None(ocr未识别到,请重试)'
        try:
            trans_result = self.mask_obj.Translator.execute(ocr_text=self.result, from_lang='jp', to_lang='zh')
            return trans_result
        except IOError:
            return 'ConnectionError(网络错误或API已失效)', False
