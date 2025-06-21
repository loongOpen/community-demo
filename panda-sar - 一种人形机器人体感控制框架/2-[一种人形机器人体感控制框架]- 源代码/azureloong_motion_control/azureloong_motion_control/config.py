# coding:UTF-8
from datetime import datetime

# 传感器数据字典 {key: value}
IMU_DeviceData = {
    "Time": datetime.now(),     # 时间
    "AccX": 0.0,                # 加速度 X
    "AccY": 0.0,                # 加速度 Y
    "AccZ": 0.0,                # 加速度 Z
    "AsX":  0.0,                # 角速度 X
    "AsY":  0.0,                # 角速度 Y
    "AsZ":  0.0,                # 角速度 Z
    "GX":   0.0,                # 磁场 X
    "GY":   0.0,                # 磁场 Y
    "GZ":   0.0,                # 磁场 Z
    "AngleX": 0.0,              # 角度 X [-180, 180) -> [0, 360)
    "AngleY": 0.0,              # 角度 Y [-180, 180) -> [0, 360)
    "AngleZ": 0.0,              # 角度 Z [-180, 180) -> [0, 360)
    "Temperature": 0.0,         # 温度
    "Rssi": 0.0,                # 信号强度
    "Version": None,            # 版本号
    "ElectricPercentage": 0.0   # 电量百分比
}

# 传感器校准项列表 [calibration_item]
CalibrationItemList = [
    "Time",                         # 时间
    "AccX",   "AccY",   "AccZ",     # 加速度
    "AsX",    "AsY",    "AsZ",      # 角速度
    "GX",     "GY",     "GZ",       # 磁场
    "AngleX", "AngleY", "AngleZ",   # 角度
    "Temperature",                  # 温度
    "Rssi",                         # 信号强度
    "ElectricPercentage"            # 电量百分比
]

# 设备编号绑定机器人肢体表 {device_id: limb_name}
DeviceLookupLimbDict = {
    "WT5500002652": "robot_body",       # 机器人 躯干
    "WT5500006896": "robot_head",       # 机器人 头部
    "WT5500006713": "robot_waist",      # 机器人 腰部
    "WT5500006892": "robot_arm_r",      # 机器人 右上臂
    "WT5500006888": "robot_arm_l",      # 机器人 左上臂
    "WT5500006705": "robot_forearm_r",  # 机器人 右前臂
    "WT5500006893": "robot_forearm_l",  # 机器人 左前臂
    "WT5500006886": "robot_hand_r",     # 机器人 右手
    "WT5500006697": "robot_hand_l",     # 机器人 左手
    "WT5500006696": "robot_thigh_r",    # 机器人 右大腿
    "WT5500006895": "robot_thigh_l",    # 机器人 左大腿
    "WT5500006903": "robot_calf_r",     # 机器人 右小腿
    "WT5500003998": "robot_calf_l",     # 机器人 左小腿
    "WT5500004016": "robot_foot_r",     # 机器人 右脚
    "WT5500003997": "robot_foot_l",     # 机器人 左脚
}

# 机器人运动学模型 {limb_name: {"num": numbered, "parent": parent_limb_name, "children": [child_limb_name]}}
LimbsDict = {
    "robot_body":       {"num": 1,  "parent": None,              "children": ["robot_head", "robot_waist", "robot_arm_r", "robot_arm_l"]},
    "robot_head":       {"num": 2,  "parent": "robot_body",      "children": []},
    "robot_waist":      {"num": 3,  "parent": "robot_body",      "children": ["robot_thigh_r", "robot_thigh_l"]},
    "robot_arm_r":      {"num": 4,  "parent": "robot_body",      "children": ["robot_forearm_r"]},
    "robot_arm_l":      {"num": 5,  "parent": "robot_body",      "children": ["robot_forearm_l"]},
    "robot_forearm_r":  {"num": 6,  "parent": "robot_arm_r",     "children": ["robot_hand_r"]},
    "robot_forearm_l":  {"num": 7,  "parent": "robot_arm_l",     "children": ["robot_hand_l"]},
    "robot_hand_r":     {"num": 8,  "parent": "robot_forearm_r", "children": []},
    "robot_hand_l":     {"num": 9,  "parent": "robot_forearm_l", "children": []},
    "robot_thigh_r":    {"num": 10, "parent": "robot_waist",     "children": ["robot_calf_r"]},
    "robot_thigh_l":    {"num": 11, "parent": "robot_waist",     "children": ["robot_calf_l"]},
    "robot_calf_r":     {"num": 12, "parent": "robot_thigh_r",   "children": ["robot_foot_r"]},
    "robot_calf_l":     {"num": 13, "parent": "robot_thigh_l",   "children": ["robot_foot_l"]},
    "robot_foot_r":     {"num": 14, "parent": "robot_calf_r",    "children": []},
    "robot_foot_l":     {"num": 15, "parent": "robot_calf_l",    "children": []}
}

# 机器人关节字典 {limb_name: [roll_joint_name, pitch_joint_name, yaw_joint_name]}
RobotJointsDict = {
    "robot_body":  [None, None, None],                                                                       # 机器人 躯干
    "robot_head":  [None, "robot_head_pitch_joint", "robot_head_yaw_joint"],                                 # 机器人 头部
    "robot_waist": ["robot_waist_roll_joint", "robot_waist_pitch_joint", "robot_waist_yaw_joint"],           # 机器人 腰部
    "robot_arm_r": ["robot_arm_r_roll_joint", "robot_arm_r_pitch_joint", None],                              # 机器人 右上臂
    "robot_arm_l": ["robot_arm_l_roll_joint", "robot_arm_l_pitch_joint", None],                              # 机器人 左上臂
    "robot_forearm_r": ["robot_forearm_r_roll_joint", "robot_forearm_r_pitch_joint", None],                  # 机器人 右前臂
    "robot_forearm_l": ["robot_forearm_l_roll_joint", "robot_forearm_l_pitch_joint", None],                  # 机器人 左前臂
    "robot_hand_r":  ["robot_hand_r_roll_joint", "robot_hand_r_pitch_joint", "robot_hand_r_yaw_joint"],      # 机器人 右手
    "robot_hand_l":  ["robot_hand_l_roll_joint", "robot_hand_l_pitch_joint", "robot_hand_l_yaw_joint"],      # 机器人 左手
    "robot_thigh_r": ["robot_thigh_r_roll_joint", "robot_thigh_r_pitch_joint", "robot_thigh_r_yaw_joint"],   # 机器人 右大腿
    "robot_thigh_l": ["robot_thigh_l_roll_joint", "robot_thigh_l_pitch_joint", "robot_thigh_l_yaw_joint"],   # 机器人 左大腿
    "robot_calf_r":  [None, "robot_calf_r_pitch_joint", None],                                               # 机器人 右小腿
    "robot_calf_l":  [None, "robot_calf_l_pitch_joint", None],                                               # 机器人 左小腿
    "robot_foot_r":  ["robot_foot_r_roll_joint", "robot_foot_r_pitch_joint", None],                          # 机器人 右脚
    "robot_foot_l":  ["robot_foot_l_roll_joint", "robot_foot_l_pitch_joint", None],                          # 机器人 左脚
}