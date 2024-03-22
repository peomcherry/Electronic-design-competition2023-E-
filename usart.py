'''
串口发送 与 接收

'''
from pyb import UART
import ustruct  # 串口要用
import struct
import time

# 串口接收
rx_buf = 0
rxdata = [0] * 50
uart = 0
rx_finish = 0


def init(uart_baud=115200):
    global uart
    uart = UART(3, uart_baud)  # 定义串口3变量
    uart.init(uart_baud, bits=8, parity=None, stop=1)


def send_byte(data1, data2, data3):  # 串口发送数据  # 串口要用
    global uart
    data1 = ord(data1)                  # 将字符转换位ascall码
    data2 = ord(data2)
    data3 = ord(data3)
    data = bytearray([data1, data2, data3])
    uart.write(data)
    # time.sleep_ms(1)                   # 加入延迟更加稳定
    uart.write('\r\n')


# 发送数字
# data1 、 data2 输入范围 0~9
def send_num(data1, data2):  # 串口要用
    global uart
    data1 = data1 + 48
    data2 = data2 + 48
    # uart.write("%c%c"%(str(data1),str(data2)))
    data = bytearray([data1, data2])
    uart.write(data)
    # time.sleep_ms(1)
    uart.write('\r\n')


def send(byte):  # 串口要用
    global uart
    uart.write(byte)
    uart.write('\r\n')

# 串口接收数据
# 接收字符传必须以回车换行结尾(0x0d,0x0a)
# 存在bug  一次只能接收一行数据


def rec_data():
    global rx_buf, rx_finish
    global uart
    res = 0
    while (uart.any() and res != 0x0a):  # 进行串口数据的接收
        res = uart.read(1)  # 表示为读取一个十六进制数,这里的uart必须是例化的
        res = struct.unpack('B', res)
        res = hex(res)
        res = int(res)
        if (rx_buf & 0x8000 == 0):
            if (rx_buf & 0x4000):  # 接收到了0x0d
                if (res != 0x0a):
                    rx_buf = 0  # 接收错误,重新开始
                else:
                    rx_buf |= 0x8000  # 接收完成了
            else:  # 还没收到0X0D
                if (res == 0x0d):
                    rx_buf |= 0x4000
                else:
                    rxdata[rx_buf & 0X3FFF] = res
                    rx_buf = rx_buf + 1
                    if (rx_buf > 49):
                        rx_buf = 0  # 接收数据错误,重新开始接收
    if rx_buf & 0x8000:
        rx_finish = 1
