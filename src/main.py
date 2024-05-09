# -*- coding:utf-8 -*-
import sys
from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from qfluentwidgets import FluentIcon as FIF, qconfig, FluentTranslator, MSFluentWindow, setTheme
from qfluentwidgets import NavigationItemPosition
from Config import MyConfig
from FloatingWindow import FloatingWindow
from HomePage import HomePageWidget
from MaskWindow import MaskWindow
from SetingPage import SetPageWidget
from FunConfigPage import FunConfigPageWidget


class Window(MSFluentWindow):
    """ 主界面 """

    def __init__(self):
        super().__init__()
        self.config = MyConfig()
        qconfig.load(r'config/config.json', self.config)
        self.initWindow()
        self.float_w = FloatingWindow(config=self.config)
        self.mask_w = MaskWindow(float_w=self.float_w, config=self.config)
        self.mask_w.signer.connect(self.float_w.set_text)
        # 创建子界面，实际使用时将 Widget 换成自己的子界面
        self.homeInterface = HomePageWidget(text='Home Page',
                                            mask_w=self.mask_w,
                                            float_w=self.float_w,
                                            config=self.config,
                                            parent=self
                                            )
        self.homeInterface.translator_check_signer.connect(self.homeInterface.translator_check_info)
        self.homeInterface.translator_start_signer.connect(self.homeInterface.translator_start_info)
        self.settingInterface = SetPageWidget(
            'Setting Page',
            config=self.config,
            float_w=self.float_w,
            mask_w=self.mask_w,
            parent=self
        )
        self.funInterface = FunConfigPageWidget(text='Function Config page')

        self.initNavigation()

    def initWindow(self):
        setTheme(qconfig.get(qconfig.themeMode))
        self.setMicaEffectEnabled(self.config.get(self.config.mica_effect_enable))

        self.setWindowOpacity(0.9)

        self.setWindowIcon(QIcon(':/qfluentwidgets/images/logo.png'))
        self.setWindowTitle('CalciteTranslator')

        self.resize(800, 600)
        self.setMinimumSize(600, 400)

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, '主页', FIF.HOME)
        self.addSubInterface(self.funInterface, FIF.DEVELOPER_TOOLS, '配置', FIF.DEVELOPER_TOOLS)

        self.addSubInterface(self.settingInterface, FIF.SETTING, '设置', FIF.SETTING, NavigationItemPosition.BOTTOM)


if __name__ == '__main__':
    # dpi adaptation
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    QApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    translator = FluentTranslator()  # translation
    app.installTranslator(translator)
    w = Window()
    w.show()
    app.exec()
