from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout
from qfluentwidgets import PushButton, InfoBar, InfoBarPosition

from Config import TranslatorEnum
from Translator import translation_source_selector


class HomePageWidget(QWidget):
    translator_check_signer = Signal(str, int, int)
    translator_start_signer = Signal(int)

    def __init__(self, text: str, mask_w, float_w, config, parent=None):
        super().__init__(parent=parent)
        self.text = text
        self.mask_w = mask_w
        self.float_w = float_w
        self.config = config
        self.main_window = parent

        self.translator_check_thread = TranslatorCheackThread(hp_obj=self)
        self.translator_start_thread = TranslatorStartThread(hp_obj=self)
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
            if not self.translator_start_thread.isRunning():
                InfoBar.info(
                    title='开始初始化',
                    content="",
                    orient=Qt.Orientation.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.BOTTOM_RIGHT,
                    duration=2000,
                    parent=self
                )
                self.translator_start_thread.start()
        else:
            InfoBar.warning(
                title='上一个启动的实例还未关闭！',
                content="",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=3000,
                parent=self
            )

    def __translator_check__(self):
        if not self.translator_check_thread.isRunning():
            self.translator_check_thread.start()
            self.translator_check_btn.setText("执行中……")
            self.translator_check_btn.setEnabled(False)

    def translator_check_info(self, name, delay, type_=1):
        if type_ == 0:
            InfoBar.success(
                title=f'{name}:正常！',
                content=f"延迟：{delay}ms",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM_RIGHT,
                duration=3000,
                parent=self
            )
        elif type_ == 1:
            InfoBar.error(
                title=f'{name}:错误！',
                content="检查未通过，请查看日志！",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=5000,
                parent=self
            )

    def translator_start_info(self, type_):
        if type_ == 0:
            InfoBar.success(
                title='启动成功',
                content=f"当前翻译源：{TranslatorEnum.get_name(self.config.get(self.config.translator))}",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM_RIGHT,
                duration=2000,
                parent=self
            )
            self.float_w.show()
            self.float_w.move(200, 200)
            self.mask_w.show()
            self.mask_w.move(200, 200)
        if type_ == 1:
            InfoBar.error(
                title='启动失败',
                content="详情请查看日志",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=-1,
                parent=self
            )


class TranslatorCheackThread(QThread):
    def __init__(self, hp_obj: HomePageWidget):
        super().__init__()
        self.parent = hp_obj

    def run(self):
        for i in [t for t in TranslatorEnum]:
            try:
                time_cnt = translation_source_selector(i.value).execute()[-1]
                self.parent.translator_check_signer.emit(TranslatorEnum.get_name(i), time_cnt * 1000, 0)
            except Exception as e:
                print(f'{self.__class__.__name__}:{e}')
                self.parent.translator_check_signer.emit(TranslatorEnum.get_name(i), -1, 1)
        self.parent.translator_check_btn.setText("翻译源测试")
        self.parent.translator_check_btn.setEnabled(True)


class TranslatorStartThread(QThread):
    def __init__(self, hp_obj: HomePageWidget):
        super().__init__()
        self.hp_obj = hp_obj

    def run(self):
        if self.initTranslator():
            self.hp_obj.translator_start_signer.emit(0)
        else:
            self.hp_obj.translator_start_signer.emit(1)

    def initTranslator(self):
        try:
            translator_index = self.hp_obj.config.get(self.hp_obj.config.translator).value
            self.hp_obj.mask_w.Translator = translation_source_selector(translator_index)
            self.hp_obj.mask_w.Translator.execute()
            return True
        except Exception as e:
            print(f'{self.__class__.__name__}:{e}')
            return False
