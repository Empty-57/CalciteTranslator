from typing import Dict, Union

import mss
import numpy
from paddleocr import PaddleOCR


class OCR:
    def __init__(self):
        self._ocr = PaddleOCR(lang="japan", show_log=False, use_angle_cls=True)

    def execute(self, monitor_: Dict[str, int]) -> Union[str, bool]:
        with mss.mss() as sct:
            img = sct.grab(monitor_)
            img = numpy.array(img)
        result = self._ocr.ocr(img, cls=True)

        # 打印检测框和识别结果
        lines = ' '
        if result[0]:
            for line in result[0]:
                lines += (line[1][0])
        print(f"OCR result is: {lines}")
        return lines if lines != ' ' else False

# eg: monitor = {"top": 1300, "left": 0, "width": 2560, "height": 300}
