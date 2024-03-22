import image
import colorthr
import screen

# 分辨率
# 1 QQQVGA    80*60
# 2 QQVGA     160*120
# 3 QVGA      320*240
# 4 VGA       640*480


class BUTTON:
    width = 80
    height = 60
    _width_3 = 26
    _height_2 = 30
    _scale = 1
    _coordinate_div = 1
    # 25x25 center of QQVGA.
    center_roi = [(160 // 2) - (25 // 2), (120 // 2) - (25 // 2), 25, 25]

    def __init__(self, framesize=1):
        self.width = 80 * (2 ** (framesize - 1))
        self.height = 60 * (2 ** (framesize - 1))
        self._width_3 = self.width // 3
        self._height_2 = self.height // 2
        if framesize == 4:
            self._scale = 3
            self._coordinate_div = 0.5
        elif framesize == 3:
            self._scale = 2
        elif framesize == 2:
            self._coordinate_div = 2
        elif framesize == 1:
            self._coordinate_div = 4

    def page(self, img, lcd_page):  # 页面选择按钮
        img.draw_string(self._width_3 // 4, self._height_2 // 4,
                        '1', color=colorthr.blue, scale=self._scale)
        img.draw_rectangle(self._width_3 // 4, self._height_2 // 4,
                           self._width_3 // 2, self._height_2 // 2, color=colorthr.red)

        img.draw_string(self._width_3 // 4, self._height_2 * 5 // 4,
                        'hand', color=colorthr.blue, scale=self._scale)
        img.draw_rectangle(self._width_3 // 4, self._height_2 * 5 // 4,
                           self._width_3 // 2, self._height_2 // 2, color=colorthr.red)

        img.draw_string(self._width_3 * 9 // 4, self._height_2 // 4,
                        'auto', color=colorthr.blue, scale=self._scale)
        img.draw_rectangle(self._width_3 * 9 // 4, self._height_2 // 4,
                           self._width_3 // 2, self._height_2 // 2, color=colorthr.red)

        if screen.press:
            if (screen.x // self._coordinate_div > self._width_3 // 4 and screen.x // self._coordinate_div < self._width_3 * 3 // 4):
                if (screen.y // self._coordinate_div > self._height_2 // 4 and screen.y // self._coordinate_div < self._height_2 * 3 // 4):
                    lcd_page[0] = 1
                elif (screen.y // self._coordinate_div > self._height_2 * 5 // 4 and screen.y // self._coordinate_div < self._height_2 * 7 // 4):
                    lcd_page[0] = 4
            elif (screen.x // self._coordinate_div > self._width_3 * 9 // 4 and screen.x // self._coordinate_div < self._width_3 * 11 // 4):
                if (screen.y // self._coordinate_div > self._height_2 // 4 and screen.y // self._coordinate_div < self._height_2 * 3 // 4):
                    lcd_page[0] = 3

    def ret(self, img, lcd_page):  # 返回按钮
        img.draw_rectangle(0, 0, self._width_3 // 2, self._height_2 //
                           4, color=colorthr.red)
        img.draw_string(1, 1, 'ret', color=colorthr.peachpuff,
                        scale=self._scale)
        if screen.press:
            if (screen.x // self._coordinate_div < self._width_3 // 2 and screen.y // self._coordinate_div < self._height_2 // 4):
                lcd_page[0] = 0


    def sure(self, img, lcd_page):  # 返回按钮
        temp = 0
        img.draw_rectangle(40, 0, self._width_3 // 2, self._height_2 //
                           4, color=colorthr.red)
        img.draw_string(41, 1, 'sure', color=colorthr.peachpuff,
                        scale=self._scale)
        if screen.press:
            if (screen.x // self._coordinate_div <40 + self._width_3 // 2 and screen.x // self._coordinate_div > 40
                 and screen.y // self._coordinate_div < self._height_2 // 4):
                lcd_page[0] = 0
                temp = 1
        return temp

    def Threshold_Adj_Nauto(self, img, THRESHOLD_Set, THRESHOLD_Auto):  # 绘制手动阈值调整按钮
        # 绘制阈值选择框
        img.draw_rectangle(self._width_3 // 4, self._height_2 * 3 // 8,
                           self._width_3 // 2, self._height_2 // 4, color=colorthr.red)
        img.draw_rectangle(self._width_3 * 5 // 4, self._height_2 * 3 //
                           8, self._width_3 // 2, self._height_2 // 4, color=colorthr.red)
        img.draw_rectangle(self._width_3 * 9 // 4, self._height_2 * 3 //
                           8, self._width_3 // 2, self._height_2 // 4, color=colorthr.red)
        img.draw_rectangle(self._width_3 // 4, self._height_2 * 6 // 8,
                           self._width_3 // 2, self._height_2 // 4, color=colorthr.red)
        img.draw_rectangle(self._width_3 * 5 // 4, self._height_2 * 6 //
                           8, self._width_3 // 2, self._height_2 // 4, color=colorthr.red)
        img.draw_rectangle(self._width_3 * 9 // 4, self._height_2 * 6 //
                           8, self._width_3 // 2, self._height_2 // 4, color=colorthr.red)
        img.draw_rectangle(self._width_3 // 4, self._height_2 * 9 // 8,
                           self._width_3 // 2, self._height_2 // 4, color=colorthr.red)
        img.draw_rectangle(self._width_3 * 5 // 4, self._height_2 * 9 //
                           8, self._width_3 // 2, self._height_2 // 4, color=colorthr.red)
        img.draw_rectangle(self._width_3 * 9 // 4, self._height_2 * 9 //
                           8, self._width_3 // 2, self._height_2 // 4, color=colorthr.red)
        img.draw_rectangle(self._width_3 // 4, self._height_2 * 12 // 8,
                           self._width_3 // 2, self._height_2 // 4, color=colorthr.red)
        img.draw_rectangle(self._width_3 * 5 // 4, self._height_2 * 12 //
                           8, self._width_3 // 2, self._height_2 // 4, color=colorthr.red)
        img.draw_rectangle(self._width_3 * 9 // 4, self._height_2 * 12 //
                           8, self._width_3 // 2, self._height_2 // 4, color=colorthr.red)

        # 绘制当前阈值
        img.draw_string(self._width_3 // 4, self._height_2 * 3 // 8,
                        str(int(THRESHOLD_Set[0])), color=colorthr.peachpuff, scale=self._scale)
        img.draw_string(self._width_3 // 4, self._height_2 * 9 // 8,
                        str(int(THRESHOLD_Set[1])), color=colorthr.peachpuff, scale=self._scale)
        img.draw_string(self._width_3 * 5 // 4, self._height_2 * 3 // 8,
                        str(int(THRESHOLD_Set[2])), color=colorthr.peachpuff, scale=self._scale)
        img.draw_string(self._width_3 * 5 // 4, self._height_2 * 9 // 8,
                        str(int(THRESHOLD_Set[3])), color=colorthr.peachpuff, scale=self._scale)
        img.draw_string(self._width_3 * 9 // 4, self._height_2 * 3 // 8,
                        str(int(THRESHOLD_Set[4])), color=colorthr.peachpuff, scale=self._scale)
        img.draw_string(self._width_3 * 9 // 4, self._height_2 * 9 // 8,
                        str(int(THRESHOLD_Set[5])), color=colorthr.peachpuff, scale=self._scale)

        # 绘制自动识别到的阈值
        img.draw_string(self._width_3 // 4, self._height_2 * 6 // 8,
                        str(THRESHOLD_Auto[0]), color=colorthr.blue, scale=self._scale)
        img.draw_string(self._width_3 * 5 // 4, self._height_2 * 6 // 8,
                        str(THRESHOLD_Auto[2]), color=colorthr.blue, scale=self._scale)
        img.draw_string(self._width_3 * 9 // 4, self._height_2 * 6 // 8,
                        str(THRESHOLD_Auto[4]), color=colorthr.blue, scale=self._scale)
        img.draw_string(self._width_3 // 4, self._height_2 * 12 // 8,
                        str(THRESHOLD_Auto[1]), color=colorthr.blue, scale=self._scale)
        img.draw_string(self._width_3 * 5 // 4, self._height_2 * 12 // 8,
                        str(THRESHOLD_Auto[3]), color=colorthr.blue, scale=self._scale)
        img.draw_string(self._width_3 * 9 // 4, self._height_2 * 12 // 8,
                        str(THRESHOLD_Auto[5]), color=colorthr.blue, scale=self._scale)

        # 按钮扫描
        if screen.press:
            x = screen.x // self._coordinate_div
            y = screen.y // self._coordinate_div
            if (x > self._width_3 // 4 and x < self._width_3 * 3 // 4):  # L调整
                if (y > self._height_2 * 3 // 8 and y < self._height_2 * 5 // 8):
                    THRESHOLD_Set[0] = THRESHOLD_Set[0] + 1
                    if (THRESHOLD_Set[0] > 100):
                        THRESHOLD_Set[0] = 100
                elif (y > self._height_2 * 6 // 8 and y < self._height_2 * 8 // 8):
                    THRESHOLD_Set[0] = THRESHOLD_Set[0] - 1
                    if (THRESHOLD_Set[0] < 0):
                        THRESHOLD_Set[0] = 0
                elif (y > self._height_2 * 9 // 8 and y < self._height_2 * 11 // 8):
                    THRESHOLD_Set[1] = THRESHOLD_Set[1] + 1
                    if (THRESHOLD_Set[1] > 100):
                        THRESHOLD_Set[1] = 100
                elif (y > self._height_2 * 12 // 8 and y < self._height_2 * 14 // 8):
                    THRESHOLD_Set[1] = THRESHOLD_Set[1] - 1
                    if (THRESHOLD_Set[1] < 0):
                        THRESHOLD_Set[1] = 0
            elif (x > self._width_3 * 5 // 4 and x < self._width_3 * 7 // 4):  # A调整
                if (y > self._height_2 * 3 // 8 and y < self._height_2 * 5 // 8):
                    THRESHOLD_Set[2] = THRESHOLD_Set[2] + 1
                    if (THRESHOLD_Set[2] > 127):
                        THRESHOLD_Set[2] = 127
                elif (y > self._height_2 * 6 // 8 and y < self._height_2 * 8 // 8):
                    THRESHOLD_Set[2] = THRESHOLD_Set[2] - 1
                    if (THRESHOLD_Set[2] < -128):
                        THRESHOLD_Set[2] = -128
                elif (y > self._height_2 * 9 // 8 and y < self._height_2 * 11 // 8):
                    THRESHOLD_Set[3] = THRESHOLD_Set[3] + 1
                    if (THRESHOLD_Set[3] > 127):
                        THRESHOLD_Set[3] = 127
                elif (y > self._height_2 * 12 // 8 and y < self._height_2 * 14 // 8):
                    THRESHOLD_Set[3] = THRESHOLD_Set[3] - 1
                    if (THRESHOLD_Set[3] < -128):
                        THRESHOLD_Set[3] = -128
            elif (x > self._width_3 * 9 // 4 and x < self._width_3 * 11 // 4):  # B调整
                if (y > self._height_2 * 3 // 8 and y < self._height_2 * 5 // 8):
                    THRESHOLD_Set[4] = THRESHOLD_Set[4] + 1
                    if (THRESHOLD_Set[4] > 127):
                        THRESHOLD_Set[4] = 127
                elif (y > self._height_2 * 6 // 8 and y < self._height_2 * 8 // 8):
                    THRESHOLD_Set[4] = THRESHOLD_Set[4] - 1
                    if (THRESHOLD_Set[4] < -128):
                        THRESHOLD_Set[4] = -128
                elif (y > self._height_2 * 9 // 8 and y < self._height_2 * 11 // 8):
                    THRESHOLD_Set[5] = THRESHOLD_Set[5] + 1
                    if (THRESHOLD_Set[5] > 127):
                        THRESHOLD_Set[5] = 127
                elif (y > self._height_2 * 12 // 8 and y < self._height_2 * 14 // 8):
                    THRESHOLD_Set[5] = THRESHOLD_Set[5] - 1
                    if (THRESHOLD_Set[5] < -128):
                        THRESHOLD_Set[5] = -128

    def auto_threshlod_adj_button(self, img, rgb_Auto_adj_flag, THRESHOLD_Auto):
        # 绘制颜色阈值自动识别按钮
        if (rgb_Auto_adj_flag == 0):
            img.draw_string(self.width // 4 + 1, 1, 'aut',
                            color=colorthr.peachpuff, scale=self._scale)
            img.draw_rectangle(self.width // 4, 0, self._width_3 // 2,
                               self._height_2 // 4, color=colorthr.red)
            img.draw_rectangle(self.center_roi, color=colorthr.yellow)
        else:
            img.draw_rectangle(self.center_roi, color=colorthr.red)
        img.draw_string(self._width_3 // 4, self._height_2 * 3 // 8,
                        str(THRESHOLD_Auto[0]), color=colorthr.peachpuff)
        img.draw_string(self._width_3 // 4, self._height_2 * 5 // 8,
                        str(THRESHOLD_Auto[1]), color=colorthr.peachpuff)
        img.draw_string(self._width_3 // 4, self._height_2 * 7 // 8,
                        str(THRESHOLD_Auto[2]), color=colorthr.peachpuff)
        img.draw_string(self._width_3 // 4, self._height_2 * 9 // 8,
                        str(THRESHOLD_Auto[3]), color=colorthr.peachpuff)
        img.draw_string(self._width_3 // 4, self._height_2 * 11 // 8,
                        str(THRESHOLD_Auto[4]), color=colorthr.peachpuff)
        img.draw_string(self._width_3 // 4, self._height_2 * 13 // 8,
                        str(THRESHOLD_Auto[5]), color=colorthr.peachpuff)
        # 按钮扫描
        if screen.press:
            x = screen.x // self._coordinate_div
            y = screen.y // self._coordinate_div
            if (x > self.width // 4 and x < self.width // 4 + self._width_3 // 2 and y < self._height_2 // 4):
                return 1
            else:
                return 0
