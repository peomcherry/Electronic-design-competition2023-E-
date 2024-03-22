import sensor
import image
import time
import screen
import math
from servo_motor import servo
from pid import PID
import usart
from pyb import Timer
from button import BUTTON
from pyb import millis
# 变量定义
## 需要调整变量
###1.  50*50 边框大小
Square_size = 77
Square_size_2 = int(Square_size / 2)

###2. 红色激光点颜色阈值变量定义
THRESHOLD_Set = [0, 100, 32, 94, -17, 75]  # 手动调整阈值

###3. 舵机初始位置
pan_init = 90  # x轴舵机初始位置
tilt_init = 60 # y轴舵机初始位置

###4. 任务2画线速度
taske2_draw_speed = 15  # 越大速度越快


###5. 任务3矩形缩放比例
rectangle_scale_y = 20  # y
rectangle_scale_x = 20  # x

###6. 定时器中断周期
tim_ms = 15
freq_ms = int(1000/tim_ms)

###7. 画布中心
center_x = 73
center_y = 55

###8. 任务2拐角等待时间
task2_wait_time = 200
task3_wait_time = 100
# 任务句柄
task = 0
# 舵机初始角度赋值
pan_degree = pan_init
tilt_degree = tilt_init

#50*50 画布边框
center_roi = (center_x - Square_size_2, center_y - Square_size_2,
              Square_size, Square_size)

# 寻找色块 roi(roi区域外白色不被识别 减小误差)
roi_find_red = (center_x - Square_size_2 - 5, center_y - Square_size_2 - 2,
                Square_size + 10, Square_size + 10)

stop_flag = 0 # 停止循迹标志位

# PID目标量
x_target = 80
y_target = 60

pid_right_time = 0

# 寻找红光标志
find_red_flag = 1

# 感光重置标志
sensor_reset_flag = 1
# 任务2 开始


task2_proc = 0  # 任务2状态机

task2_corner_flag = 0 #任务2目标量到拐点
task3_corner_flag = 0
task2_cnt = 0
task3_cnt = 0

# 任务3 开始
task3_proc = 0                  # 任务3状态机
task3_start_flag = 0            # 任务3识别到矩形 开始
taske3_draw_speed = 200          # 越小速度越快
task3_div_x = 0
task3_div_y = 0
task3_count = 0

task3_wait_start = 300
task2_corner_wait= 0
task3_corner_wait= 0


corner_sure_time = 0
corner_sure_flag = 0
corner = 0
corner_s = 0


show_roi_flag = 1
cnt = 0     #计数器

# 任务5 开始
target = [0,0,0,0,0,0]
target_cnt = 0
task5_x = 0
task5_y = 0
task5_record_flag = 1
task5_dot_sure_cnt = 0

task5_proc = 0
task5_corner_flag = 0
task5_cnt = 0
task5_wait_time = 100
task5_start_flag = 0


task5_div_x = 0
task5_div_y = 0
taske5_draw_speed = 200
task5_wait_start = 0
task5_count = 0


# screen
button = BUTTON(framesize=2)
lcd_page = [0]

butten_sure_flag = 0
button_x = 0
button_y = 0
# 寻找最大色块
def find_max(blobs):
    max_size = 0
    for blob in blobs:
        if blob[2] * blob[3] > max_size:
            max_blob = blob
            max_size = blob[2] * blob[3]
    return max_blob


def scale_rectangle(rectangle_coords, scale_factor_x, scale_factor_y):
    # 计算长方形的中心点坐标
    # center_x = (rectangle_coords[0][0] + rectangle_coords[1][0] + rectangle_coords[2][0] + rectangle_coords[3][0]) / 4
    # center_y = (rectangle_coords[0][1] + rectangle_coords[1][1] + rectangle_coords[2][1] + rectangle_coords[3][1]) / 4
    x_0_2 = ((rectangle_coords[0][0] - rectangle_coords[2][0]) / scale_factor_x)
    y_0_2 = ((rectangle_coords[0][1] - rectangle_coords[2][1]) / scale_factor_y)

    x_1_3 = ((rectangle_coords[1][0] - rectangle_coords[3][0]) / scale_factor_x)
    y_1_3 = ((rectangle_coords[1][1] - rectangle_coords[3][1]) / scale_factor_y)
    # 缩放比例
    # scaled_width = (rectangle_coords[2][0] - rectangle_coords[0][0]) * scale_factor
    # scaled_height = (rectangle_coords[2][1] - rectangle_coords[0][1]) * scale_factor

    # 缩放后的顶点坐标
    scaled_x1 = int(rectangle_coords[0][0] - x_0_2)
    scaled_y1 = int(rectangle_coords[0][1] - y_0_2)
    scaled_x2 = int(rectangle_coords[1][0] - x_1_3)
    scaled_y2 = int(rectangle_coords[1][1] - y_1_3)
    scaled_x3 = int(rectangle_coords[2][0] + x_0_2)
    scaled_y3 = int(rectangle_coords[2][1] + y_0_2)
    scaled_x4 = int(rectangle_coords[3][0] + x_1_3)
    scaled_y4 = int(rectangle_coords[3][1] + y_1_3)

    return [[scaled_x1, scaled_y1], [scaled_x2, scaled_y2], [scaled_x3, scaled_y3], [scaled_x4, scaled_y4]]

def task3_pre():
    global corner_sure_time,corner_sure_flag,task3_start_flag
    global corner,corner_s ,find_red_flag,sensor_reset_flag
    # 设置寻矩形 感光环境
    # 感光标志为高 并且未识别到矩形
    if (sensor_reset_flag == 1 and corner_sure_flag == 0):
        find_red_flag = 0
        sensor_reset_flag = 0
        sensor.set_auto_exposure(False, 50000)
    # 感光标志为高 并且识别到矩形
    elif (sensor_reset_flag == 1 and corner_sure_flag == 1):
        sensor_reset_flag = 0
        sensor.set_auto_exposure(False, 3000)
    if (corner_sure_flag == 0):  # 未识别到矩形
        img.draw_string(0, 0, "F", color=(255, 0, 0))
        for r in img.find_rects(threshold=25000, roi=roi_find_red):
            img.draw_rectangle(r.rect(), color=(255, 0, 0))
            # 在同一点同时识别到4次矩形 确定识别
            if (corner_sure_flag == 0):
                if (corner != r.corners()):
                    corner = r.corners()
                    corner_sure_time = 0
                elif (corner == r.corners()):
                    corner_sure_time = corner_sure_time + 1
                    if (corner_sure_time >= 4):
                        corner_sure_flag = 1
                        task3_start_flag = 0
                        sensor_reset_flag = 1
                        find_red_flag = 1
                        corner_s = scale_rectangle(
                            corner, rectangle_scale_x, rectangle_scale_y)  # 缩放 rectangle_scale


# 定时器创建
def tick(timer):
    ## 全任务变量
    global x_target,y_target,task,center_x,center_y,cnt,task2_cnt,stop_flag
    global pan_error,tilt_error,pid_right_time

    ## 任务3变量
    global task3_div_x, task3_div_y,corner_sure_flag,taske3_draw_speed,task3_wait_start
    global task3_count,task3_proc,task3_start_flag,corner_s,sensor_reset_flag,task3_corner_flag
    global task3_wait_time,task3_cnt
    ## 任务2变量
    global Square_size_2, task2_proc,task2_corner_flag,task2_wait_time,taske2_draw_speed

    ## 任务5变量
    global target,task5_proc,task5_cnt,task5_wait_time
    global task5_div_x, task5_div_y,taske5_draw_speed,task5_wait_start
    global task5_count,task5_proc,task5_start_flag


    if(stop_flag == 0):
        ## 任务1
        if(task == 1):
            x_target = center_x
            y_target = center_y
            if(abs(pan_error)<3 and abs(tilt_error)<3):
                pid_right_time = pid_right_time + 1
                if(pid_right_time >= 10):
                    task = 0
                    pid_right_time = 0
        ## 任务2
        elif(task == 2):
            if (task2_proc <= 6):
                if(task2_corner_flag == 1):
                    if(task2_cnt < task2_wait_time-1):
                        task2_cnt = task2_cnt + 1
                    else:
                        task2_corner_flag = 0
                        task2_cnt=0
                else:
                    if (task2_proc == 0):
                        y_target = y_target - taske2_draw_speed
                        if (y_target <= center_y - Square_size_2):
                            task2_corner_flag = 1
                            y_target = center_y - Square_size_2
                            task2_proc = 1
                    elif (task2_proc == 1):  # 状态0  上左
                        x_target = x_target + taske2_draw_speed
                        if (x_target >= center_x + Square_size_2):#如果目标值大于等于最高限度,就赋值最高限度,开启下一个环节
                            x_target = center_x + Square_size_2
                            task2_corner_flag = 1
                            task2_proc = 2
                    elif (task2_proc == 2):  # 状态1  右边
                        y_target = y_target + taske2_draw_speed
                        if (y_target >= center_y + Square_size_2):
                            y_target = center_y + Square_size_2
                            task2_corner_flag = 1
                            task2_proc = 3
                    elif (task2_proc == 3):  # 状态2  下边
                        x_target = x_target - taske2_draw_speed
                        if (x_target <= center_x - Square_size_2):
                            x_target = center_x - Square_size_2
                            task2_corner_flag = 1
                            task2_proc = 4
                    elif (task2_proc == 4):  # 状态3  左边
                        y_target = y_target - taske2_draw_speed
                        if (y_target <= center_y - Square_size_2):
                            y_target = center_y - Square_size_2
                            task2_corner_flag = 1
                            task2_proc = 5
                    elif (task2_proc == 5):  # 状态4  上左
                        x_target = x_target + taske2_draw_speed
                        if (x_target >= center_x):
                            x_target = center_x
                            task2_corner_flag = 1
                            task2_proc = 6
                    elif (task2_proc == 6):  # 状态5  任务2结束
                        x_target = center_x
                        y_target = center_y - Square_size_2
                        task = 1
        ## 任务3
        elif(task == 3 and corner_sure_flag):
            if(task3_proc <= 4):
                if(task3_corner_flag == 1):
                    if(task3_cnt < task3_wait_time-1):
                        task3_cnt = task3_cnt + 1
                    else:
                        task3_corner_flag = 0
                        task3_cnt=0
                else:
                    if(task3_proc == 0):  # 状态0 0->3
                        if (task3_start_flag == 0):
                            task3_count = task3_count + 1      #如果task3_start_flag==0,则把拐角值赋给目标
                            x_target = corner_s[0][0]          #
                            y_target = corner_s[0][1]
                            task3_start_flag = 1
                            task3_div_x = (corner_s[3][0] - corner_s[0]
                                          [0]) / taske3_draw_speed
                            task3_div_y = (corner_s[3][1] - corner_s[0]
                                          [1]) / taske3_draw_speed
                        else:
                            if(cnt < task3_wait_start):        #如果task3_start_flag==0,则把拐角值赋给目标
                                cnt = cnt + 1                  #这里是计数十次,确认初始化
                                x_target = corner_s[0][0]
                                y_target = corner_s[0][1]
                            if(cnt >= task3_wait_start):      #这里跳出if,进行下一次判断,其中不断进行巡线
                                if(task3_count <= taske3_draw_speed):#count相当于i    taske3_draw_speed是加的次数
                                    task3_count = task3_count + 1
                                    x_target = x_target + task3_div_x
                                    y_target = y_target + task3_div_y
                                elif(task3_count > taske3_draw_speed):#加到次数之后就跳出来,然后清零
                                    task3_corner_flag = 1
                                    task3_count = 0
                                    task3_start_flag = 0
                                    task3_proc = 1
                    elif(task3_proc == 1):  # 状态1 3->2
                        if(task3_start_flag == 0):
                            task3_count = task3_count + 1
                            x_target = corner_s[3][0]
                            y_target = corner_s[3][1]
                            task3_start_flag = 1
                            task3_div_x = (corner_s[2][0] - corner_s[3]
                                            [0]) / taske3_draw_speed
                            task3_div_y = (corner_s[2][1] - corner_s[3]
                                            [1]) / taske3_draw_speed
                        else:
                            if(task3_count <= taske3_draw_speed):
                                task3_count = task3_count + 1
                                x_target = x_target + task3_div_x
                                y_target = y_target + task3_div_y
                            elif(task3_count > taske3_draw_speed):
                                task3_corner_flag = 1
                                task3_count = 0
                                task3_start_flag = 0
                                task3_proc = 2
                    elif(task3_proc == 2):  # 状态2 2->1
                        if(task3_start_flag == 0):
                            task3_count = task3_count + 1
                            x_target = corner_s[2][0]
                            y_target = corner_s[2][1]
                            task3_start_flag = 1
                            task3_div_x = (corner_s[1][0] - corner_s[2]
                                          [0]) / taske3_draw_speed
                            task3_div_y = (corner_s[1][1] - corner_s[2]
                                          [1]) / taske3_draw_speed
                        else:
                            if(task3_count <= taske3_draw_speed):
                                task3_count = task3_count + 1
                                x_target = x_target + task3_div_x
                                y_target = y_target + task3_div_y
                            elif(task3_count > taske3_draw_speed):
                                task3_corner_flag = 1
                                task3_count = 0
                                task3_start_flag = 0
                                task3_proc = 3
                    elif(task3_proc == 3):  # 状态3 1->0
                        if(task3_start_flag == 0):
                            task3_count = task3_count + 1
                            x_target = corner_s[1][0]
                            y_target = corner_s[1][1]
                            task3_start_flag = 1
                            task3_div_x = (corner_s[0][0] - corner_s[1]
                                            [0]) / taske3_draw_speed
                            task3_div_y = (corner_s[0][1] - corner_s[1]
                                            [1]) / taske3_draw_speed
                        else:
                            if(task3_count <= taske3_draw_speed):
                                task3_count = task3_count + 1
                                x_target = x_target + task3_div_x
                                y_target = y_target + task3_div_y
                            elif(task3_count > taske3_draw_speed):
                                task3_corner_flag = 1
                                task3_count = 0
                                task3_start_flag = 0
                                task3_proc = 4
                    elif(task3_proc == 4):  # 状态4 任务3结束
                        task = 1
                        cnt = 0
                        x_target = corner_s[0][0]
                        y_target = corner_s[0][1]
                        task3_proc = 0
                        task3_count = 0
                        task3_start_flag = 0
                        corner_sure_flag = 0
                        sensor_reset_flag = 1
        elif(task == 4):        # 任务4 去任意指定目标点
            if(abs(pan_error)<3 and abs(tilt_error)<3):
                pid_right_time = pid_right_time + 1
                if(pid_right_time >= 10):
                    task = 1
                    pid_right_time = 0
        elif(task == 5 ):
            if(task5_proc <= 3):
                if (task5_proc == 0):  # 状态0 0->1
                    if (task5_start_flag == 0):
                        task5_count = task5_count + 1
                        x_target = target[0]
                        y_target = target[1]
                        task5_start_flag = 1
                        task5_div_x = (target[2] - target[0]
                                       ) / taske5_draw_speed
                        task5_div_y = (target[3] - target[1]
                                       ) / taske5_draw_speed
                    else:
                        if(cnt < task5_wait_start):
                            cnt = cnt + 1
                            x_target = target[0]
                            y_target = target[1]
                        if(cnt >= task5_wait_start):
                            if (task5_count <= taske5_draw_speed):
                                task5_count = task5_count + 1
                                x_target = x_target + task5_div_x
                                y_target = y_target + task5_div_y
                            elif (task5_count > taske5_draw_speed):
                                task5_count = 0
                                task5_start_flag = 0
                                task5_proc = 1
                elif (task5_proc == 1):  # 状态1 1->2
                    if (task5_start_flag == 0):
                        task5_count = task5_count + 1
                        x_target = target[2]
                        y_target = target[3]
                        task5_start_flag = 1
                        task5_div_x = (target[4] - target[2]
                                       ) / taske5_draw_speed
                        task5_div_y = (target[5] - target[3]
                                       ) / taske5_draw_speed
                    else:
                        if (task5_count <= taske5_draw_speed):
                            task5_count = task5_count + 1
                            x_target = x_target + task5_div_x
                            y_target = y_target + task5_div_y
                        elif (task5_count > taske5_draw_speed):
                            task5_count = 0
                            task5_start_flag = 0
                            task5_proc = 2
                elif (task5_proc == 2):  # 状态1 2->0
                    if (task5_start_flag == 0):
                        task5_count = task5_count + 1
                        x_target = target[4]
                        y_target = target[5]
                        task5_start_flag = 1
                        task5_div_x = (target[0] - target[4]
                                       ) / taske5_draw_speed
                        task5_div_y = (target[1] - target[5]
                                       ) / taske5_draw_speed
                    else:
                        if (task5_count <= taske5_draw_speed):
                            task5_count = task5_count + 1
                            x_target = x_target + task5_div_x
                            y_target = y_target + task5_div_y
                        elif (task5_count > taske5_draw_speed):
                            task5_count = 0
                            task5_start_flag = 0
                            task5_proc = 3
                elif (task5_proc == 3):  # 状态4 任务3结束
                    task = 1
                    x_target = target[0]
                    y_target = target[1]
                    #target = [0,0,0,0,0,0]
                    task5_proc = 0
                    task5_count = 0
                    task5_start_flag = 0
    print(x_target,y_target)



# 二、设置摄像头
usart.init()  # 串口初始化
screen.init()  # 初始化屏幕
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_auto_exposure(False, 3000)
# 关闭自动白平衡
sensor.set_auto_exposure(False)
sensor.set_auto_whitebal(False)
sensor.set_auto_gain(False)
sensor.set_framesize(sensor.QQVGA)

sensor.skip_frames(time=1000)  # 延迟1秒等待摄像头校准亮度、白平衡

clock = time.clock()                # to process a frame sometimes.


tim = Timer(3, freq=freq_ms)      # 使用定时器2创建定时器对象-以1Hz触发
tim.callback(tick)                # 将回调设置为tick函数

# 舵机和PID
pan_servo = servo(1)
tilt_servo = servo(2)

pan_pid = PID(p=0.01, i=0, d=0.0009, imax=90)  # 脱机运行或者禁用图像传输,使用这个PID
tilt_pid = PID(p=0.01, i=0, d=0.0009, imax=90)  # 脱机运行或者禁用图像传输,使用这个PID

pan_servo.degrees(pan_init)
tilt_servo.degrees(tilt_init)

time.sleep_ms(2000)

def HMI(data1,data2):
    global task,find_red_flag,center_x,center_y,roi_find_red
    global x_target,y_target,task2_proc,cnt,center_roi
    global Square_size,Square_size_2,show_roi_flag,stop_flag
    if(data1 == 84):
        if(data2 == 49):        #任务1 复位
            task = 1
            find_red_flag = 1
        elif(data2 == 50):      # 任务2 画布矩形循迹
            task = 2
            x_target = center_x
            y_target = center_y
            task2_proc = 0
            find_red_flag = 1
        elif(data2 == 51):      # 任务3 小矩形循迹
            task = 3
            cnt = 0
            find_red_flag = 1
        elif(data2 == 52):
            task = 3
            cnt = 0
            find_red_flag = 1
        elif(data2 == 56):
            if(stop_flag == 0):
                stop_flag = 1
            else:
                stop_flag = 0
    if(data1 == 75):
        if(data2 == 51):
            center_x = center_x - 1
        elif(data2 == 52):
            center_x = center_x + 1
        elif(data2 == 49):
            center_y = center_y - 1
        elif(data2 == 50):
            center_y = center_y + 1
        elif(data2 == 53):
            Square_size = Square_size + 2
        elif(data2 == 54):
            Square_size = Square_size - 2
        elif(data2 == 55):
            if(show_roi_flag == 1):
                show_roi_flag = 0
            else:
                show_roi_flag = 1
        Square_size_2 = int(Square_size / 2)
        center_roi = (center_x - Square_size_2, center_y - Square_size_2,
                      Square_size, Square_size)
        roi_find_red = (center_x - Square_size_2 - 5, center_y - Square_size_2 - 2,
                Square_size + 10, Square_size + 10)
    if(data1 == 66):
        center_x = data2
        Square_size_2 = int(Square_size / 2)
        center_roi = (center_x - Square_size_2, center_y - Square_size_2,
                      Square_size, Square_size)
        roi_find_red = (center_x - Square_size_2 - 5, center_y - Square_size_2 - 2,
                Square_size + 10, Square_size + 10)
        print("Aok")
    if(data1 == 65):
        center_y = data2
        Square_size_2 = int(Square_size / 2)
        center_roi = (center_x - Square_size_2, center_y - Square_size_2,
                      Square_size, Square_size)
        roi_find_red = (center_x - Square_size_2 - 5, center_y - Square_size_2 - 2,
                Square_size + 10, Square_size + 10)
        print("Bok")
    if(data1 == 67):
        Square_size = data2
        Square_size_2 = int(Square_size / 2)
        center_roi = (center_x - Square_size_2, center_y - Square_size_2,
                      Square_size, Square_size)
        roi_find_red = (center_x - Square_size_2 - 5, center_y - Square_size_2 - 2,
                        Square_size + 10, Square_size + 10)
        print("Cok")
# 六、主循环
while (True):
    clock.tick()  # 用于获取帧速
    img = sensor.snapshot()
    usart.rec_data()
    if (usart.rx_finish == 1):
        usart.rx_finish = 0
        usart.rx_buf = 0
        HMI(usart.rxdata[0],usart.rxdata[1])
        print("uart= ", usart.rxdata)
    if(task == 0):      #空闲任务期间 启动触摸屏
        find_red_flag = 0
        if(lcd_page[0] == 0):
            button.page(img,lcd_page)
            img.draw_string(0,0,"waitting task")
            img.draw_string(0,10,"c_x = "+str(center_x))
            img.draw_string(0,20,"c_y = "+str(center_y))
            img.draw_string(0,30,"size = "+str(Square_size))
        if(lcd_page[0] == 4):           #手动调整阈值
            img.binary([THRESHOLD_Set])
            img.dilate(1)
            img.draw_rectangle(center_roi, color=(0, 0, 255))
            button.Threshold_Adj_Nauto(img, THRESHOLD_Set, [0, 0, 0, 0, 0, 0] )
            button.ret(img, lcd_page)
        if(lcd_page[0] == 1):
            show_roi_flag = 0
            button.ret(img, lcd_page)
            butten_sure_flag = button.sure(img, lcd_page)
            if(butten_sure_flag == 0):
                if(screen.press):               #屏幕被按下
                    button_x = screen.x//2
                    button_y = screen.y//2
            else:
                show_roi_flag = 1
                find_red_flag = 1
                butten_sure_flag = 0
                x_target = button_x
                y_target = button_y
                task = 4
            img.draw_cross(button_x,button_y,color=(255, 0, 0))
        if(lcd_page[0] == 3):
            show_roi_flag = 0
            button.ret(img, lcd_page)
            butten_sure_flag = button.sure(img, lcd_page)
            img.draw_cross(target[0],target[1],color=(255, 0, 0))
            img.draw_cross(target[2],target[3],color=(255, 0, 0))
            img.draw_cross(target[4],target[5],color=(255, 0, 0))
            if(butten_sure_flag == 0):
                if(screen.press):               #屏幕被按下
                    if(target_cnt < 3):
                        if(task5_record_flag):
                            task5_record_flag = 0
                            task5_x = screen.x//2
                            task5_y = screen.y//2
                        else:
                            if(screen.x//2 > task5_x - 5 and screen.x//2 < task5_x + 5
                                and screen.y //2 > task5_y - 5 and screen.y//2 < task5_y + 5):
                                task5_dot_sure_cnt = task5_dot_sure_cnt + 1
                                if(task5_dot_sure_cnt > 30):    #识别成功
                                    if(target_cnt == 0):
                                        target[0] = task5_x
                                        target[1] = task5_y
                                    elif(target_cnt == 1):
                                        target[2] = task5_x
                                        target[3] = task5_y
                                    elif(target_cnt == 2):
                                        target[4] = task5_x
                                        target[5] = task5_y
                                    print(target)
                                    task5_dot_sure_cnt = 0
                                    target_cnt = target_cnt + 1
                                    task5_record_flag = 1
                            else:                               #识别失败
                                task5_record_flag = 1
                                task5_dot_sure_cnt = 0
            else:
                show_roi_flag = 1
                find_red_flag = 1
                butten_sure_flag = 0
                target_cnt = 0
                task = 5
    if(task == 3):
        task3_pre()

    if (find_red_flag == 1):
        # 1）获取图像,并识别小球位置
        img.binary([THRESHOLD_Set])
        # img.erode(1)
        img.dilate(1)
        if(stop_flag == 0):
            blobs = img.find_blobs(
                [(100, 255)], pixels_threshold=0, area_threshold=0, merge=True, roi=roi_find_red)
            if blobs:  # 如果找到结果
                # 按结果的像素值,找最大值的数据。也就是找最大的色块。
                max_blob = find_max(blobs)
                img.draw_rectangle(max_blob.rect(), color=(255, 0, 0))
                pan_error = max_blob.cx() - x_target
                tilt_error = max_blob.cy() - y_target
                pan_output = pan_pid.get_pid(pan_error, 1)
                tilt_output = tilt_pid.get_pid(tilt_error, 1)
                pan_servo.degrees(pan_degree + pan_output)
                tilt_servo.degrees(tilt_degree - tilt_output)
                # print("x", pan_error, "y", tilt_error)
                pan_degree = pan_degree + pan_output
                tilt_degree = tilt_degree - tilt_output

# 7）显示图像到屏幕
    # 识别到准确方框
    if (corner_sure_flag):
        # 画出 方框四角
        img.draw_line(corner[0][0], corner[0][1], corner[1]
                      [0], corner[1][1], color=(0, 255, 0))
        img.draw_line(corner[1][0], corner[1][1], corner[2]
                      [0], corner[2][1], color=(0, 255, 0))
        img.draw_line(corner[2][0], corner[2][1], corner[3]
                      [0], corner[3][1], color=(0, 255, 0))
        img.draw_line(corner[3][0], corner[3][1], corner[0]
                      [0], corner[0][1], color=(0, 255, 0))
        img.draw_line(corner_s[0][0], corner_s[0][1],
                      corner_s[1][0], corner_s[1][1], color=(255, 255,0 ))
        img.draw_line(corner_s[1][0], corner_s[1][1],
                      corner_s[2][0], corner_s[2][1], color=(255, 255, 0))
        img.draw_line(corner_s[2][0], corner_s[2][1],
                      corner_s[3][0], corner_s[3][1], color=(255, 255, 0))
        img.draw_line(corner_s[3][0], corner_s[3][1],
                      corner_s[0][0], corner_s[0][1], color=(255, 255, 0))
    if(task == 5):
        img.draw_line(target[0], target[1], target[2], target[3], color=(0, 255, 0))
        img.draw_line(target[2], target[3], target[4], target[5], color=(0, 255, 0))
        img.draw_line(target[4], target[5], target[0], target[1], color=(0, 255, 0))
    if(show_roi_flag == 1):
        img.draw_cross(center_x, center_y, color=(0, 0, 255), size=3)
        img.draw_rectangle(center_roi, color=(0, 0, 255))
    #img.draw_rectangle(roi_find_red, color=(0, 255, 0))
    screen.display(img)  # 在屏幕上显示图像
