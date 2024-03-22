import image
import colorthr
import screen
import usart
import button
from pid import PID
rho_pid = PID(p=0.4, i=0)
theta_pid = PID(p=0.001, i=0)


def find_max(blobs):
    max_size = 0
    for blob in blobs:
        if blob[2] * blob[3] > max_size:
            max_blob = blob
            max_size = blob[2] * blob[3]
    return max_blob


def find_inroi(img, roi):
    for rec in roi:
        img.draw_rectangle(rec, color=(255, 0, 0))
        if img.find_blobs([(100, 100)], roi=roi[0]):
            print(1)
        if img.find_blobs([(100, 100)], roi=roi[1]):
            print(2)
        if img.find_blobs([(100, 100)], roi=roi[2]):
            print(3)
        if img.find_blobs([(100, 100)], roi=roi[3]):
            print(4)
        if img.find_blobs([(100, 100)], roi=roi[4]):
            print(5)


def track_line(img):
    line = img.get_regression([(100, 100)], robust=True)
    if (line):
        rho_err = abs(line.rho()) - img.width() / 2
        if line.theta() > 90:
            theta_err = line.theta() - 180
        else:
            theta_err = line.theta()
        img.draw_line(line.line(), color=127)

        if line.magnitude() > 8:
            rho_output = rho_pid.get_pid(rho_err, 1)
            theta_output = theta_pid.get_pid(theta_err, 1)
            output = rho_output + theta_output
            output = round(output * 5) + 1000
            print(output)
            byte = "a%d" % (output)
            usart.send(byte)


def find_dot(img, button, blob_cnt):
    # img.dilate(3)
    blobs = img.find_blobs([(100, 255)], pixels_threshold=1, area_threshold=1)
    if (blobs):
        blob_cnt[0] = blob_cnt[0] + 1
        max_blob = find_max(blobs)
        x = max_blob.cx()
        y = max_blob.cy()
        img.draw_cross(x, y, color=colorthr.red)
        img.draw_string(5, 20, str(x), color=colorthr.red)
        img.draw_string(5, 40, str(y), color=colorthr.red)
        if (blob_cnt[0] >= 3):
            if (y >= button.height - 5):
                usart.send_num(4, 0)
            if (abs(x - button.width // 2) <= 5):  # 物体在屏幕中间可接受范围  直行
                usart.send_num(0, 0)
            elif (abs(x - button.width // 2) <= 20):
                if (x - button.width // 2 < 0):  # 物体偏左  右转
                    usart.send_num(1, 1)
                else:  # 物体偏右  左转
                    usart.send_num(2, 1)
            elif (abs(x - button.width // 2) <= 35):
                if (x - button.width // 2 < 0):
                    usart.send_num(1, 2)
                else:
                    usart.send_num(2, 2)
            elif (abs(x - button.width // 2) <= 50):
                if (x - button.width // 2 < 0):
                    usart.send_num(1, 3)
                else:
                    usart.send_num(2, 3)
            elif (abs(x - button.width // 2) <= 65):
                if (x - button.width // 2 < 0):
                    usart.send_num(1, 4)
                else:
                    usart.send_num(2, 4)
            elif (abs(x - button.width // 2) <= 80):
                if (x - button.width // 2 < 0):
                    usart.send_num(1, 5)
                else:
                    usart.send_num(2, 5)
        else:  # 未发现任何物体
            usart.send_num(3, 0)
            blob_cnt[0] = 0
