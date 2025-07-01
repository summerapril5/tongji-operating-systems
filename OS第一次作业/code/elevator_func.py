from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtCore import QTimer
import win32api, win32con

from elevator_ui import *
import numpy as np
import time, threading

MAXINF = 100  # 定义"无穷大量"
MAXINF_ex = 1000
OPEN = 0  # 开门状态
CLOSED = 1  # 关门状态
NOPE = 0  # 空
READY_START = 1  # 电梯即将运动
READY_STOP = 2  # 电梯即将停止

STANDSTILL = 0  # 静止状态
RUNNING_UP = 1  # 电梯上行状态
RUNNING_DOWN = 2  # 电梯下行状态
GO_UP = 1  # 用户要上行
GO_DOWN = 2  # 用户要下行

class MyElevator(object):
    def __init__(self, Elev):
        # 与界面文件建立连接
        self.elev = Elev
        # 创建定时器, 1s中更新一次电梯状态
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateElevState)
        self.timer.start(1000)
        # 5个电梯内部消息列表
        self.messageQueue = []
        for i in range(0, 5):
            self.messageQueue.append([])
        # 5个电梯内部不顺路消息列表
        self.messageQueue_reverse = []
        for i in range(0, 5):
            self.messageQueue_reverse.append([])

    # 警报器函数
    def warnCtrl(self, which_elev):
        self.elev.elevEnabled[which_elev] = False  # 该电梯禁用
        self.elev.warning[which_elev].setEnabled(False)  # 报警键禁用
        for i in range(0, 20):
            self.elev.Floor[which_elev][i].setStyleSheet("background-color: red;")
            self.elev.Floor[which_elev][i].setEnabled(False)  # 楼层按键禁用
        self.elev.open[which_elev].setStyleSheet("border-image: url(image/open_ban.png)")
        self.elev.open[which_elev].setEnabled(False)  # 开门键禁用
        self.elev.close[which_elev].setStyleSheet("border-image: url(image/close_ban.png)")
        self.elev.close[which_elev].setEnabled(False)  # 关门键禁用
        self.elev.Floor_now[which_elev].setEnabled(False)  # 数码管禁用
        self.elev.up_logo[which_elev].setStyleSheet("border-image: url(image/upEle_ban.png)")
        self.elev.down_logo[which_elev].setStyleSheet("border-image: url(image/downEle_ban.png)")
        self.elev.up_logo[which_elev].setEnabled(False)  # 上下行标志禁用
        self.elev.down_logo[which_elev].setEnabled(False)
        self.elev.up[which_elev].setStyleSheet("border-image: url(image/up_ban.png)")
        self.elev.down[which_elev].setStyleSheet("border-image: url(image/down_ban.png)")
        self.elev.up[which_elev].setEnabled(False)  # 门口上行按钮禁用
        self.elev.down[which_elev].setEnabled(False)  # 门口下行按钮禁用
        self.elev.door[which_elev].setStyleSheet("border-image: url(image/door_close.png)")

        # 将点击警报的电梯未完成的调度信息传递给其他电梯
        for i in range(0, len(self.messageQueue[which_elev])):
            self.outerCtrl(self.messageQueue[which_elev][i], 1)
        for i in range(0, len(self.messageQueue_reverse[which_elev])):
            self.outerCtrl(self.messageQueue_reverse[which_elev][i], 1)

        self.messageQueue[which_elev].clear()  # 清空该电梯的消息列表，终止操作
        self.messageQueue_reverse[which_elev].clear()

        # 五部电梯全部禁用
        arr = np.array(self.elev.elevEnabled)
        if (arr == False).all():
            self.elev.Floor_now_total.setEnabled(False)  # 下拉框禁用
            self.elev.up_total.setStyleSheet("border-image: url(image/up_ban.png)")
            self.elev.down_total.setStyleSheet("border-image: url(image/down_ban.png)")
            self.elev.up_total.setEnabled(False)  # 上行按钮禁用
            self.elev.down_total.setEnabled(False)  # 下行按钮禁用
            for i in range(0, 20):
                self.elev.up_ex[i].setStyleSheet("border-image: url(image/up_ban.png)")
                self.elev.down_ex[i].setStyleSheet("border-image: url(image/down_ban.png)")
                self.elev.up_ex[i].setEnabled(False)  # 上行按钮禁用
                self.elev.down_ex[i].setEnabled(False)  # 下行按钮禁用
            win32api.MessageBox(0, "所有电梯已损坏!\n请关闭电梯调度页面", "警告", win32con.MB_ICONASTERISK)

    # 开关门函数
    def doorCtrl(self, which_elev, which_command):
        if which_command == 0:  # 如果用户要开门
            # 开门动画
            self.elev.door[which_elev].setStyleSheet("border-image:url(image/door_open.png)")
            # 如果当前门是关闭状态并且电梯是静止的
            if self.elev.doorState[which_elev] == CLOSED and self.elev.elevState[which_elev] == STANDSTILL:
                self.elev.doorState[which_elev] = OPEN  # 先将门状态更新为打开
                self.elev.elevEnabled[which_elev] = False
        else:  # 如果用户要关门
            # 关门动画
            self.elev.door[which_elev].setStyleSheet("border-image:url(image/door_close.png)")
            # 如果当前门是打开状态并且电梯是静止的
            if self.elev.doorState[which_elev] == OPEN and self.elev.elevState[which_elev] == STANDSTILL:
                self.elev.doorState[which_elev] = CLOSED  # 先将门状态更新为关闭
                self.elev.elevEnabled[which_elev] = True

    # 内命令
    def innerCtrl(self, which_elev, dest):
        nowFloor = self.elev.floor_now[which_elev]  # 获取当前电梯位置

        if nowFloor < dest:  # 如果按键大于当前楼层
            if self.elev.elevState[which_elev] == STANDSTILL:  # 电梯处于静止状态
                self.messageQueue[which_elev].append(dest)  # 将目标楼层加入 消息队列
            else:
                if self.elev.elevState[which_elev] == RUNNING_UP:  # 电梯正在向上运行
                    self.messageQueue[which_elev].append(dest)  # 将目标楼层加入 消息队列并排序
                    self.messageQueue[which_elev].sort()
                elif self.elev.elevState[which_elev] == RUNNING_DOWN:  # 电梯正在向下运行
                    self.messageQueue_reverse[which_elev].append(dest)  # 将目标楼层加入 不顺路消息队列并排序
                    self.messageQueue_reverse[which_elev].sort()

        elif nowFloor > dest:  # 如果按键小于当前楼层
            if self.elev.elevState[which_elev] == STANDSTILL:
                self.messageQueue[which_elev].append(dest)  # 将目标楼层加入 消息队列

            else:
                if self.elev.elevState[which_elev] == RUNNING_DOWN:
                    self.messageQueue[which_elev].append(dest)  # 将目标楼层加入 消息队列并反向排序
                    self.messageQueue[which_elev].sort()
                    self.messageQueue[which_elev].reverse()
                elif self.elev.elevState[which_elev] == RUNNING_UP:
                    self.messageQueue_reverse[which_elev].append(dest)  # 将目标楼层加入 不顺路消息队列并反向排序
                    self.messageQueue_reverse[which_elev].sort()
                    self.messageQueue_reverse[which_elev].reverse()

        else:  # 如果按键就为当前楼层
            print("该楼层即为当前楼层，直接结束")
            if self.elev.elevState[which_elev] == STANDSTILL:  # 电梯静止 => 打开门
                self.elev.doorState[which_elev] = OPEN
                # 开门动画
                self.elev.door[which_elev].setStyleSheet("border-image:url(image/door_open.png)")
                # 关门动画
                self.elev.door[which_elev].setStyleSheet("border-image:url(image/door_close.png)")
                self.elev.doorState[which_elev] = CLOSED
            # 如果到达目标楼层，且目标楼层与总数码管一致，则熄灭上升或下降键
            self.elev.up_ex[dest-1].setStyleSheet(
                        "QPushButton{border-image: url(image/up.png)}")
            self.elev.up_ex[dest-1].setEnabled(True)
            self.elev.down_ex[dest - 1].setStyleSheet(
                "QPushButton{border-image: url(image/down.png)}")
            self.elev.down_ex[dest - 1].setEnabled(True)

            for j in range(0, 5):
                    if self.elev.up[j].isEnabled() == False:
                        self.elev.up[j].setStyleSheet(
                            "QPushButton{border-image: url(image/up.png)}")
                        self.elev.up[j].setEnabled(True)
                    if self.elev.down[j].isEnabled() == False:
                        self.elev.down[j].setStyleSheet(
                            "QPushButton{border-image: url(image/down.png)}")
                        self.elev.down[j].setEnabled(True)

            button = self.elev.findChild(QtWidgets.QPushButton,
                                         "Floor_{}_{}".format(which_elev + 1, nowFloor))  # 恢复按键背景并重新允许点击
            button.setStyleSheet("border-style: outset;\n"
                                 "border-width: 2px;\n"
                                 "border-radius: 15px;\n"
                                 "border-color: black;\n"
                                 "padding: 4px;\n"
                                 "background-color: white;")
            button.setEnabled(True)

    # 外命令
    def outerCtrl(self, which_floor, choice):
        # 防止已经禁用的电梯又被启动
        for i in range(0, 5):
            if self.elev.warning[i].isEnabled() == False:
                self.elev.elevEnabled[i] = False  # 该电梯禁用
        # 初步筛选没损坏的电梯
        EnabledList = []
        for i in range(0, 5):
            if self.elev.elevEnabled[i]:
                EnabledList.append(i)
        print("未损坏的电梯为：" + str(EnabledList) + "该处01234对应12345电梯")
        if len(EnabledList) == 0:
            print("所有电梯均故障，调度无法进行")
            return

        # 计算每部可用电梯的"可调度性"
        dist = [MAXINF] * 5  # 可使用电梯距离用户的距离
        for EnabledElev in EnabledList:
            # 如果该电梯正在上升，并且该选择是上升，且目标楼层在当前楼层之上
            if self.elev.elevState[EnabledElev] == RUNNING_UP and choice == GO_UP \
                    and which_floor > self.elev.floor_now[EnabledElev]:
                dist[EnabledElev] = which_floor - self.elev.floor_now[EnabledElev]
            # 如果该电梯正在下降，并且该选择是下降，且目标楼层在当前楼层之下
            elif self.elev.elevState[EnabledElev] == RUNNING_DOWN and choice == GO_DOWN and which_floor < \
                    self.elev.floor_now[EnabledElev]:
                dist[EnabledElev] = self.elev.floor_now[EnabledElev] - which_floor
            # 如果该电梯静止
            elif self.elev.elevState[EnabledElev] == STANDSTILL:
                dist[EnabledElev] = abs(self.elev.floor_now[EnabledElev] - which_floor)

        # 防止已经禁止的电梯参与调度
        for i in range(0, 5):
            if self.elev.warning[i].isEnabled() == False:
                dist[i] = MAXINF_ex

        BestElev = dist.index(min(dist))  # 选择可调度性最好的电梯作为最佳电梯
        print("该条指令选中第{}电梯".format(BestElev + 1))


        # 如果外部指令要添加内容电梯里已经存在，则无效
        flag = 1
        for i in range(0, len(self.messageQueue[BestElev])):
                if self.messageQueue[BestElev][i] == which_floor:
                    flag = 0
                    print("该指令重复，无效")
                    break
        if flag == 1:
                for i in range(0, len(self.messageQueue_reverse[BestElev])):
                    if self.messageQueue_reverse[BestElev][i] == which_floor:
                        flag = 0
                        print("该指令重复，无效")
                        break
        if flag:
                button = self.elev.findChild(QtWidgets.QPushButton,
                                             "Floor_{0}_{1}".format(BestElev + 1, which_floor))  # 将用户的目标楼层设定为特殊颜色
                button.setStyleSheet("border-style: outset;\n"
                                     "border-width: 2px;\n"
                                     "border-radius: 15px;\n"
                                     "border-color: black;\n"
                                     "padding: 4px;\n"
                                     "background-color: orange;")
                button.setEnabled(False)
                self.innerCtrl(BestElev, which_floor)  # 调用控制器进行innerCtrl处理

    # 更新电梯状态
    def updateElevState(self):

        # 初步筛选没损坏的电梯
        EnabledList = []
        for i in range(0, 5):
            if self.elev.elevEnabled[i]:
                EnabledList.append(i)

        for i in range(0, 5):  # 遍历五部电梯
            if self.elev.warning[i].isEnabled() == False:
                continue
            if self.elev.doorState[i] == OPEN:  # 如果电梯门是打开的 => 等待电梯关门
                self.elev.door[i].setStyleSheet("border-image:url(image/door_close.png)")  # 关门动画
                self.elev.doorState[i] = CLOSED

            if len(self.messageQueue[i]) > 0:  # 某个电梯的消息队列不为空
                if self.elev.elevState[i] == STANDSTILL:  # 电梯处于静止状态
                    self.elev.door[i].setStyleSheet("border-image:url(image/door_open.png)")  # 开门动画

                    if self.elev.floor_now[i] < self.messageQueue[i][0]:  # 根据即将运行的方向更新电梯状态
                        self.elev.elevState[i] = RUNNING_UP
                    elif self.elev.floor_now[i] > self.messageQueue[i][0]:
                        self.elev.elevState[i] = RUNNING_DOWN

                    self.elev.ReadyState[i] = READY_START  # 变为就绪运行状态

                elif self.elev.ReadyState[i] == READY_START:  # 处于就绪运行状态
                    # 关门动画
                    self.elev.door[i].setStyleSheet("border-image:url(image/door_close.png)")
                    self.elev.ReadyState[i] = NOPE  # 变为空状态

                elif self.elev.ReadyState[i] == READY_STOP:  # 处于就绪停止状态
                    self.messageQueue[i].pop(0)  # 结束该命令的处理

                    self.elev.door[i].setStyleSheet("border-image:url(image/door_close.png)")  # 关门动画
                    self.elev.ReadyState[i] = NOPE  # 变为空状态
                    self.elev.elevState[i] = STANDSTILL  # 电梯变为静止状态
                    self.elev.up_logo[i].setStyleSheet("QGraphicsView{border-image: url(image/upEle.png)}")
                    self.elev.down_logo[i].setStyleSheet("QGraphicsView{border-image: url(image/downEle.png)}")

                else:
                    destFloor = self.messageQueue[i][0]  # 获取第一个目标楼层
                    if self.elev.floor_now[i] < destFloor:  # 向上运动
                        self.elev.elevState[i] = RUNNING_UP
                        self.elev.up_logo[i].setStyleSheet("QGraphicsView{border-image: url(image/upEle_work.png)}")
                        self.elev.floor_now[i] = self.elev.floor_now[i] + 1  # 将当前楼层加一并设置数码管显示
                        self.elev.Floor_now[i].setProperty("value", self.elev.floor_now[i])

                    elif self.elev.floor_now[i] > destFloor:  # 向下运动
                        self.elev.elevState[i] = RUNNING_DOWN
                        self.elev.down_logo[i].setStyleSheet("QGraphicsView{border-image: url(image/downEle_work.png)}")
                        self.elev.floor_now[i] = self.elev.floor_now[i] - 1  # 将当前楼层减一并设置数码管显示
                        self.elev.Floor_now[i].setProperty("value", self.elev.floor_now[i])

                    else:  # 电梯到达目的地
                        self.elev.door[i].setStyleSheet("border-image:url(image/door_open.png)")  # 开门动画
                        self.elev.doorState[i] = OPEN

                        self.elev.ReadyState[i] = READY_STOP  # 到达目的地 => 变为就绪停止状态
                        # 如果到达目标楼层，且目标楼层与总数码管一致，则熄灭上升或下降键
                        if self.elev.up_ex[destFloor - 1].isEnabled() == False:
                            self.elev.up_ex[destFloor - 1].setStyleSheet(
                                "QPushButton{border-image: url(image/up.png)}")
                            self.elev.up_ex[destFloor - 1].setEnabled(True)
                        if self.elev.down_ex[destFloor - 1].isEnabled() == False:
                            self.elev.down_ex[destFloor - 1].setStyleSheet(
                                "QPushButton{border-image: url(image/down.png)}")
                            self.elev.down_ex[destFloor - 1].setEnabled(True)
                        if destFloor == int(self.elev.Floor_now_total.currentText()):
                            for j in EnabledList:
                                if self.elev.up[j].isEnabled() == False:
                                    self.elev.up[j].setStyleSheet(
                                        "QPushButton{border-image: url(image/up.png)}")
                                    self.elev.up[j].setEnabled(True)
                                elif self.elev.down[j].isEnabled() == False:
                                    self.elev.down[j].setStyleSheet(
                                        "QPushButton{border-image: url(image/down.png)}")
                                    self.elev.down[j].setEnabled(True)

                        button = self.elev.findChild(QtWidgets.QPushButton,
                                                     "Floor_{0}_{1}".format(i + 1, self.elev.floor_now[i]))  # 恢复该按钮的状态
                        button.setStyleSheet(
                            "border-style: outset;\n"
                            "border-width: 2px;\n"
                            "border-radius: 15px;\n"
                            "border-color: black;\n"
                            "padding: 4px;\n"
                            "background-color: white;\n")
                        button.setEnabled(True)

            elif len(self.messageQueue_reverse[i]):  # 如果消息队列为空 & 不顺路消息队列不为空
                self.messageQueue[i] = self.messageQueue_reverse[i].copy()  # 交替两个队列
                self.messageQueue_reverse[i].clear()
