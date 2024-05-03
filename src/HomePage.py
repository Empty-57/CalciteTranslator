from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout
from qfluentwidgets import PushButton, InfoBar, InfoBarPosition
from Translator import translation_source_selector
from Config import TranslatorEnum


class HomePageWidget(QWidget):
    signer = Signal(str, int, int)

    def __init__(self, text: str, mask_w: QWidget, float_w: QWidget, config, parent=None):
        super().__init__(parent=parent)
        self.text = text
        self.mask_w = mask_w
        self.float_w = float_w
        self.config = config
        self.main_window = parent

        self.translator_check_thread = TranslatorCheackThread(hp_obj=self)
        self.start_btn = PushButton(text='开始使用')
        self.translator_check_btn = PushButton(text='翻译源测试')

        self.hBoxLayout = QHBoxLayout(self)
        self.init()

    def init(self):
        self.start_btn.clicked.connect(lambda: self.__start__())
        self.translator_check_btn.clicked.connect(lambda: self.__translator_check__())
        self.hBoxLayout.addWidget(self.start_btn, 1, Qt.AlignmentFlag.AlignCenter)
        self.hBoxLayout.addWidget(self.translator_check_btn, 1, Qt.AlignmentFlag.AlignCenter)
        # 必须给子界面设置全局唯一的对象名
        self.setObjectName(self.text.replace(' ', '-'))

    def __start__(self):
        if not all((self.float_w.isVisible(), self.mask_w.isVisible())):
            self.float_w.show()
            self.float_w.move(200, 200)
            self.mask_w.show()
            self.mask_w.move(200, 200)

            InfoBar.success(
                title='启动成功',
                content=f"当前翻译源：{TranslatorEnum.get_name(self.config.get(self.config.translator))}",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM_RIGHT,
                duration=2000,
                parent=self
            )
        else:
            InfoBar.warning(
                title='上一个启动的实例还未关闭！',
                content="",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM_RIGHT,
                duration=3000,
                parent=self
            )

    def __translator_check__(self):
        if not self.translator_check_thread.isRunning():
            self.translator_check_thread.start()
        else:
            InfoBar.warning(
                title='测试正在进行中！',
                content="",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=3000,
                parent=self
            )

    def check_info(self, name, status_code, type_=1):
        if type_ == 0:
            InfoBar.success(
                title=f'{name}:正常！',
                content="状态码：200 OK",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM_RIGHT,
                duration=3000,
                parent=self
            )
        elif type_ == 1:
            InfoBar.error(
                title=f'{name}:错误！',
                content=f"状态码：{status_code} API可能已经失效",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM_RIGHT,
                duration=5000,
                parent=self
            )
        else:
            InfoBar.error(
                title=f'{name}:错误！',
                content="InternalErrors(网络错误或API已失效)",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM_RIGHT,
                duration=5000,
                parent=self
            )


class TranslatorCheackThread(QThread):
    def __init__(self, hp_obj: HomePageWidget):
        super().__init__()
        self.parent = hp_obj

    def run(self):
        __dict = {
            0: '百度翻译',
            1: '福昕翻译',
            2: '有道翻译',
            3: 'Mirai翻译',
        }
        status_code = None
        for i in [t.value for t in TranslatorEnum]:
            try:
                tra = translation_source_selector(i)
                tra_ = tra.execute()
                status_code = tra_[2]
                status_text = tra_[3]
                if status_code == 200 and status_text == 'ok':
                    self.parent.signer.emit(__dict[i], status_code, 0)
                else:
                    self.parent.signer.emit(__dict[i], status_code, 1)
            except Exception:
                self.parent.signer.emit(__dict[i], status_code, 2)
