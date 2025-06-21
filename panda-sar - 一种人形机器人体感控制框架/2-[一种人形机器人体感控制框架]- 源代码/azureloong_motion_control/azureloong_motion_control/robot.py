# coding:UTF-8
import socket
import threading
from device import LimbIMU
from algorithm import switch_KeyValue, calculate_AngleDifference
from config import LimbsDict, RobotJointsDict, DeviceLookupLimbDict


class RobotIMUs:
    robotName = "AzureLoong"        # 机器人名称
    port = 1399                     # UDP 端口号
    socket = None                   # UDP 套接字
    isOpen = False                  # UDP 服务开启标志
    isCalibrated = False            # 传感器校准标志
    limbLookupDeviceDict = {}       # 肢体查设备编号字典
    tempBuffer = []                 # 临时缓冲区
    sensorsState = 0x0000           # 传感器状态位标志
    robotLimbIMUList = {}           # 机器人肢体传感器列表 {limb_name: limb_IMU}
    robotLimbsMotionMatrix = {}     # 机器人肢体运动矩阵 {limb_name: [roll_angle, pitch_angle, yaw_angle]}
    robotJointsRotationList = {}    # 机器人关节运动列表 {joint_name: joint_rotate_angle}

    def __init__(self, robot_name: str = None, port: int = None, callback_method: function = None):
        """ 初始化机器人各肢体传感器
        :param robot_name: str | None            机器人名称 (默认: AzureLoong)
        :param port: int | None                  UDP服务端口 (默认: 1399)
        :param callback_method: function | None  数据更新回调方法
        """
        if robot_name is not None: self.robotName = robot_name                          # 机器人名称
        if port is not None: self.port = port                                           # 服务端口
        if callback_method is not None: self.callback_method = callback_method          # 数据更新回调方法
        self.isOpen = False                                                             # 初始化：服务开启标志
        self.limbLookupDeviceList = switch_KeyValue(DeviceLookupLimbDict)               # 初始化：机器人肢体查设备编号字典
        # 初始化：机器人肢体传感器列表 {limb_name: LimbIMU}
        self.robotLimbIMUList = {limb_name: LimbIMU(self.robotName, limb_name, self.limbLookupDeviceDict[limb_name]) for limb_name in LimbsDict.keys()}
        # 初始化：机器人肢体运动矩阵 {limb_name: [roll_angle, pitch_angle, yaw_angle]}
        self.robotLimbsMotionMatrix = {limb_name: [0.0, 0.0, 0.0] for limb_name in LimbsDict.keys()}
        # 初始化：机器人关节运动列表 {joint_name: rotate_angle}
        for joint_name_list in RobotJointsDict.values():            # 遍历：机器人关节字典
            for joint_name in joint_name_list:                      # 遍历：每个机器人肢体的所有关节
                if joint_name is not None:
                    self.robotJointsRotationList[joint_name] = 0.0  # 初始化：机器人关节

    def start(self):
        """ 启动机器人传感器监听服务
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(("0.0.0.0", self.port))
        self.isOpen = True
        # 开启一个线程读取数据
        t = threading.Thread(target=self.onReceive)
        t.start()

    def onReceive(self):
        """ 传感器数据处理模块
        （该方法会阻塞，直到接收到数据。）
        """
        while self.isOpen:
            # 数据提取 Exact
            try:
                data, ip_address = self.socket.recvfrom(1024)   # 接收数据
                deviceID = None                                 # 设备编号
                for var in data:
                    # 逐个字节将接收到的数据存入临时缓冲区
                    self.tempBuffer.append(var)
                    # 校验消息头"WT"
                    if len(self.tempBuffer) == 2 and (self.tempBuffer[0] != 0x57 or self.tempBuffer[1] != 0x54):
                        del self.tempBuffer[0]                  # 向左对齐
                        continue                                # 跳过：检测设备编号、数据包解析环节
                    # 检测设备编号
                    if len(self.tempBuffer) == 12:
                        deviceID = bytes(self.tempBuffer).decode('ascii')          # 提取：设备编号
                        if deviceID not in DeviceLookupLimbDict.keys():            # 防错措施
                            self.tempBuffer.clear()                                # 重置：临时缓冲区
                            deviceID = None                                        # 重置：设备编号
                        else:
                            continue                                               # 跳过：数据包解析环节
                    # 数据包解析
                    if len(self.tempBuffer) == 54:
                        self.robotLimbIMUList[DeviceLookupLimbDict[deviceID]].onDataReceived(self.tempBuffer)     # 数据解析 Data Transfer
                        self.robotLimbIMUList[DeviceLookupLimbDict[deviceID]].setIPv4Address(ip_address)          # 设置：设备 IPv4 地址
                        self.sensor_state |= (1 << LimbsDict[DeviceLookupLimbDict[deviceID]]["num"])              # 设置：传感器状态位标志
                        self.tempBuffer.clear()                 # 重置：临时缓冲区
                        deviceID = None                         # 重置：设备编号
            except:
                print("Error onReceive")
            # 数据加载 Data Load
            if self.sensor_state == 0x7FFF: self.calculate_RobotLimbsMotion()     # 计算：机器人肢体运动矩阵
            if self.isCalibrated: self.update_RobotJointsMotion()                 # 更新：机器人关节运动列表
            # 数据更新回调方法
            if self.callback_method is not None:                                  # 防错措施(考虑频率控制)
                self.callback_method(self.robotJointsRotationList)                # 调用：数据更新回调(机器人关节运动列表)

    def calculate_RobotLimbsMotion(self):
        ''' 计算机器人肢体运动矩阵
        '''
        if self.sensorsState == 0x7FFF and self.isCalibrated:
            # 更新：肢体运动矩阵
            for limb_name, limb_IMU in self.robotLimbIMUList.items():                       # 遍历：机器人肢体传感器列表
                if LimbsDict[limb_name]["parent"] is not None:                              # 防错措施
                    parent_limb_name: str = LimbsDict[limb_name]["parent"]                  # 获取：父节点机器人肢体名
                    parent_limb_IMU: LimbIMU = self.robotLimbIMUList[parent_limb_name]      # 获取：父节点机器人肢体传感器
                    self.robotLimbsMotionMatrix[limb_name] = [
                        calculate_AngleDifference(parent_limb_IMU.roll, limb_IMU.roll),     # 计算：肢体相对于上级的滚转角弧度差
                        calculate_AngleDifference(parent_limb_IMU.pitch, limb_IMU.pitch),   # 计算：肢体相对于上级的俯仰角弧度差
                        calculate_AngleDifference(parent_limb_IMU.yaw, limb_IMU.yaw)        # 计算：肢体相对于上级的偏航角弧度差
                    ]
                else:
                    self.robotLimbsMotionMatrix[limb_name] = [limb_IMU.roll, limb_IMU.pitch, limb_IMU.yaw]   # 获取：肢体运动角弧度
    
    def update_RobotJointsMotion(self):
        ''' 更新机器人关节运动列表
        '''
        if self.sensorsState == 0x7FFF and self.isCalibrated:                               # 完整性措施
            for limb_name, limb_IMU in self.robotLimbIMUList.items():                       # 遍历：机器人肢体传感器列表    
                joint_name_list = RobotJointsDict[limb_name]                                # 获取：机器人肢体关节列表
                for joint_idx, joint_name in enumerate(joint_name_list):
                    if joint_name is not None:
                        if joint_idx == 0: self.robotJointsRotationList[joint_name] = limb_IMU.roll     # 滚转关节运动角弧度 [0, 2π)
                        elif joint_idx == 1: self.robotJointsRotationList[joint_name] = limb_IMU.pitch  # 俯仰关节运动角弧度 [0, 2π)
                        elif joint_idx == 2: self.robotJointsRotationList[joint_name] = limb_IMU.yaw    # 偏航关节运动角弧度 [0, 2π)
                        else: pass
                    else: pass

    def calibrate_AllLimbsIMU(self):
        """ 校准所有肢体传感器
        :return: bool  是否校准成功
        """
        if self.sensorsState == 0x7FFF:
            for limb in self.robotLimbIMUList.values():
                limb.calibrate()
            self.isCalibrated = True
            return True                 # 防错措施
        else:
            self.isCalibrated = False   # 防错措施
            return False

    def stop(self):
        """ 停止 UDP 服务
        """
        self.isOpen = False             # 重置：服务开启标志
        self.sensorsState = 0x0000      # 重置：传感器状态位标志
        self.tempBuffer.clear()         # 重置：临时缓冲区
        try:
            self.socket.close()
        except:
            print("Error socket.close()")


#######################################################################
# 数据更新回调示例
def updateData(jointRotaionDict: dict):
    """
    :param jointRotaionDict: dict  机器人关节旋转角度字典
    :return: None
    """
    print(jointRotaionDict)


if __name__ == '__main__':
    # 加载 UDP 服务
    server = RobotIMUs(port=1399, callback_method=updateData)
    server.start()
