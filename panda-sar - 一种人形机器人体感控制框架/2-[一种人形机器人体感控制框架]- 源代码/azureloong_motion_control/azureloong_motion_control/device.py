# coding:UTF-8
from datetime import datetime
from algorithm import get_SignInt16, angleToRadian, convert_AngleRangeExplicit
from config import IMU_DeviceData, CalibrationItemList

class LimbIMU:
    robotName = "AzureLoong"        # 机器人名称
    limbName = "robot_body"         # 肢体名称
    deviceID = "WT5500000000"       # 设备编号
    deviceAddress = "127.0.0.1"     # 设备 IPv4 地址
    deviceData = {}                 # 传感器设备数据字典
    deviceCalibration = {}          # 传感器设备校准字典
    roll = 0.0                      # 滚转角弧度（AngleY -> roll_Radian）
    pitch = 0.0                     # 俯仰角弧度（AngleX -> pitch_Radian）
    yaw = 0.0                       # 偏航角弧度（AngleZ -> yaw_Radian）
    isOpen = False                  # 设备开启标志
    isCalibrated = False            # 设备校准标志
    TempBytes = []                  # 临时缓冲区
    callback_method = None          # 数据回调方法

    def __init__(self, robotName=None, limbName=None, deviceID=None, callback_method=None):
        ''' 初始化肢体 IMU 传感器
        :param robotName: str | None        机器人名称
        :param limbName: str | None         机器人肢体名称
        :param deviceID: str | None         设备编号
        :param callback_method: Any | None  数据回调方法
        '''
        if robotName is not None: self.robotName = robotName    # 初始化：机器人名称
        if limbName is not None: self.limbName = limbName       # 初始化：机器人肢体名称
        if deviceID is not None: self.deviceID = deviceID       # 初始化：设备编号
        # 初始化：传感器设备数据字典
        self.deviceData = {k: v for k, v in IMU_DeviceData.items()}
        # 初始化: 传感器设备数据校准字典
        self.deviceCalibration = {item: None for item in CalibrationItemList}
        self.isOpen = False                                     # 初始化：设备开启标志
        self.isCalibrated = False                               # 初始化：设备校准标志
        self.callback_method = callback_method                  # 初始化：数据回调方法

    def set(self, key: str, value = None):
        ''' 将传感器数据存储到指定的键值中
        :param key: str             键名
        :param value: Any | None    键值 (默认: None)
        '''
        if key in self.deviceData.keys():
            if value is None:                                   # 防错措施
                if key in ["Time"]: self.deviceData["Time"] = datetime.now()    # 设置：终端时间戳
                else: self.deviceData[key] = 0.0                                # 设置：关节默认运动角弧度
            else:
                # 解析：文本到时间戳
                if key in ["Time"]: self.deviceData["Time"] = datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f")
                # 解析：来源值
                else: self.deviceData[key] = value
        else:
            pass
    
    # 读取设备数据
    def get(self, key: str):
        # 从键值中获取数据，没有则返回 None
        if key in self.deviceData.keys():
            return self.deviceData[key]
        else:
            return None

    # 删除设备数据
    def remove(self, key: str):
        # 删除设备键值
        if key in self.deviceData.keys():
            if key in ["Time"]:
                # 将时间设为当前接收终端时间
                self.deviceData["Time"] = datetime.now()
            else:
                # 如果值为 None，则将对应的键值设为 0.0（避免后续计算异常）
                self.deviceData[key] = 0.0

    # 数据解析
    def onDataReceived(self, data: bytes):
        if self.deviceID == bytes(data[:12]).decode('ascii'):
            # 时间
            self.set("Time", "20{}-{}-{} {}:{}:{}.{}".format(data[12], data[13], data[14], data[15], data[16], data[17], (data[19] << 8 | data[18])))
            # 加速度（单位：g）
            AccX = get_SignInt16(data[21] << 8 | data[20]) / 32768 * 16
            AccY = get_SignInt16(data[23] << 8 | data[22]) / 32768 * 16
            AccZ = get_SignInt16(data[25] << 8 | data[24]) / 32768 * 16
            self.set("AccX", round(AccX, 3))
            self.set("AccY", round(AccY, 3))
            self.set("AccZ", round(AccZ, 3))
            # 角速度（单位：度每秒）
            AsX = get_SignInt16(data[27] << 8 | data[26]) / 32768 * 2000
            AsY = get_SignInt16(data[29] << 8 | data[28]) / 32768 * 2000
            AsZ = get_SignInt16(data[31] << 8 | data[30]) / 32768 * 2000
            self.set("AsX", round(AsX, 3))
            self.set("AsY", round(AsY, 3))
            self.set("AsZ", round(AsZ, 3))
            # 磁场（单位：μT）
            GX = get_SignInt16(data[33] << 8 | data[32]) * 100 / 1024
            GY = get_SignInt16(data[35] << 8 | data[34]) * 100 / 1024
            GZ = get_SignInt16(data[37] << 8 | data[36]) * 100 / 1024
            self.set("GX", round(GX, 3))
            self.set("GY", round(GY, 3))
            self.set("GZ", round(GZ, 3))
            # 角度（单位：度）
            AngX = get_SignInt16(data[39] << 8 | data[38]) / 32768 * 180
            AngY = get_SignInt16(data[41] << 8 | data[40]) / 32768 * 180
            AngZ = get_SignInt16(data[43] << 8 | data[42]) / 32768 * 180
            self.set("AngleX", convert_AngleRangeExplicit(round(AngX, 2)))   # [-180, 180) -> [0, 360) 
            self.set("AngleY", convert_AngleRangeExplicit(round(AngY, 2)))   # [-180, 180) -> [0, 360) 
            self.set("AngleZ", convert_AngleRangeExplicit(round(AngZ, 2)))   # [-180, 180) -> [0, 360) 
            # 温度（单位：摄氏度）
            Temp = get_SignInt16(data[45] << 8 | data[44]) / 100
            self.set("Temperature", round(Temp, 2))
            # 电量（百分比）
            quantity = data[47] << 8 | data[46]
            if quantity > 396:
                self.set("ElectricPercentage", "100")
            elif 393 < quantity <= 396:
                self.set("ElectricPercentage", "90")
            elif 387 < quantity <= 393:
                self.set("ElectricPercentage", "75")
            elif 382 < quantity <= 387:
                self.set("ElectricPercentage", "60")
            elif 379 < quantity <= 382:
                self.set("ElectricPercentage", "50")
            elif 377 < quantity <= 379:
                self.set("ElectricPercentage", "40")
            elif 373 < quantity <= 377:
                self.set("ElectricPercentage", "30")
            elif 370 < quantity <= 373:
                self.set("ElectricPercentage", "20")
            elif 368 < quantity <= 370:
                self.set("ElectricPercentage", "15")
            elif 350 < quantity <= 368:
                self.set("ElectricPercentage", "10")
            elif 340 < quantity <= 350:
                self.set("ElectricPercentage", "5")
            elif quantity <= 340:
                self.set("ElectricPercentage", "0")
            # 信号
            rssi = get_SignInt16(data[49] << 8 | data[48])
            self.set("Rssi", rssi)
            # 版本
            version = get_SignInt16(data[51] << 8 | data[50])
            self.set("Version", version)
            # 设备数据校准处理
            if self.isCalibrated:
                self.roll = angleToRadian(self.deviceData["AngleY"] - self.deviceCalibration["AngleY"])    # 修正：滚转角弧度 [0, 2π) 
                self.pitch = angleToRadian(self.deviceData["AngleX"] - self.deviceCalibration["AngleX"])   # 修正：俯仰角弧度 [0, 2π) 
                self.yaw = angleToRadian(self.deviceData["AngleZ"] - self.deviceCalibration["AngleZ"])     # 修正：偏航角弧度 [0, 2π) 
            else:
                self.roll = angleToRadian(self.deviceData["AngleY"])   # 滚转角弧度 [0, 2π) 
                self.pitch = angleToRadian(self.deviceData["AngleX"])  # 俯仰角弧度 [0, 2π) 
                self.yaw = angleToRadian(self.deviceData["AngleZ"])    # 偏航角弧度 [0, 2π) 
            # 如果回调方法不为空，则调用回调方法
            if self.callback_method is not None:
                self.callback_method(self)

    def calibrate(self):
        # 开启校准模式
        for key in self.deviceCalibration.keys():                                               # 遍历：传感器设备校准字典
            if key in self.deviceData.keys():                                                   # 防错措施
                if key == "Time":
                    self.deviceCalibration["Time"] = datetime.now() - self.deviceData["Time"]   # 时间偏差
                else:
                    self.deviceCalibration[key] = self.deviceData[key]                          # 归零偏差
        # 设备校准标志
        self.isCalibrated = True

    def exitCalibration(self):
        # 退出校准模式
        self.deviceCalibration = {name: None for name in CalibrationItemList}        # 重置: 传感器设备校准字典
        self.isCalibrated = False                                                    # 重置设备校准标志

    def setIPv4Address(self, deviceAddress: str):
        '''
        设置设备 IPv4 地址
        :param deviceAddress: str       设备 IPv4 地址
        '''
        self.deviceAddress = deviceAddress
        self.isOpen = True

    def __str__(self):
        # 返回设备数据的字符串表示
        return f"{self.robotName} - {self.limbName} - {self.deviceID} - Roll: {self.roll:.2f} rad, Pitch: {self.pitch:.2f} rad, Yaw: {self.yaw:.2f} rad"
    
    def __repr__(self):
        # 返回设备数据的字符串表示
        return self.__str__()

    def __eq__(self, other: object):
        # 判断两个设备是否是同一个设备
        if isinstance(other, LimbIMU):
            return self.deviceID == other.deviceID
        else:
            return False