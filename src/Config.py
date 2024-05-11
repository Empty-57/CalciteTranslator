from enum import Enum

from qfluentwidgets import (
    QConfig,
    OptionsConfigItem,
    OptionsValidator,
    ColorConfigItem,
    EnumSerializer,
    ConfigItem,
    BoolValidator,
)


class TranslatorEnum(Enum):
    BD_T = 0
    FX_T = 1
    YD_T = 2
    Mirai_T = 3

    @staticmethod
    def get_name(index):
        __name_dict__ = {
            TranslatorEnum.BD_T: '百度翻译',
            TranslatorEnum.FX_T: '福昕翻译',
            TranslatorEnum.YD_T: '有道翻译',
            TranslatorEnum.Mirai_T: 'Mirai翻译',
        }
        return __name_dict__[index]


class MyConfig(QConfig):
    font_size = OptionsConfigItem("FloatingWindow", "FontSize", 16, OptionsValidator([i for i in range(10, 21)]))
    font = OptionsConfigItem("FloatingWindow", "Font", "Arial", OptionsValidator(["Arial"]))
    font_color = ColorConfigItem("FloatingWindow", "FontColor", "#cc00adb5")
    box_color = ColorConfigItem("FloatingWindow", "BoxColor", "#cc212121")
    translator = OptionsConfigItem(
        "Main",
        "Translator",
        TranslatorEnum.BD_T,
        OptionsValidator(TranslatorEnum),
        EnumSerializer(TranslatorEnum)
    )
    mica_effect_enable = ConfigItem("Main", "EnableMicaEffect", False, BoolValidator())
