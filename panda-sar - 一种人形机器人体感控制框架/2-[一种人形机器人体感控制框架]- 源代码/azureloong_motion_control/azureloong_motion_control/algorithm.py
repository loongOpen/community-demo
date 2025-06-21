# coding:UTF-8
import math

def switch_KeyValue(original_dict: dict) -> dict:
    """ 交换字典中的键和值
    :param original_dict: 原始字典
    :return: 键值对交换后的新字典
    """
    return {v: k for k, v in original_dict.items()}


def switch_KeyValuesList(original_dict: dict) -> dict:
    """ 从字典中获取所有值
    :param original_dict: dict  输入的字典
    :return: dict               包含所有值的字典              
    """
    new_dict = {}
    for key, value_list in original_dict.items():
        if isinstance(value_list, list):                # 防错措施
            for idx, value in enumerate(value_list):
                if value is not None:                   # 跳过空值
                    new_dict[value] = [key, idx]
        else:
            if value_list is not None:                  # 跳过空值
                new_dict[value_list] = [key, 0]
    return new_dict


def get_SignInt16(num: int) -> int:
    """ 获取int16有符号数
    :param num: int     输入的整数
    """
    if num >= pow(2, 15):
        num -= pow(2, 16)
    return num


def angleToRadian(angle: float | int) -> float:
    """ 将角度转换为弧度
    :param angle: float | int  输入角度
    :return: float             转换后的弧度
    """
    return angle * math.pi / 180.0


def radianToAngle(radian: float | int) -> float:
    '''  将弧度转换为角度
    :param radian: float | int  输入弧度
    :return: float              转换后的角度
    '''
    return radian * 180.0 / math.pi


def calculate_AngleDifference(angle1: float | int, angle2: float | int, mode: str = "degree") -> float:
    """ 计算两个角度之间的差值
    :param angle1: float | int  角1
    :param angle2: float | int  角2
    :param mode: str            角度模式 ("degree" 或 "radian")
    :return: float              角度差值
    """
    if mode == "degree":
        # 规范化角度到[0, 360)范围
        angle1 = convert_AngleRangeExplicit(angle1, mode="degree")
        angle2 = convert_AngleRangeExplicit(angle2, mode="degree")
        # 计算初始角度差值
        raw_diff = angle2 - angle1
        # 计算最小角度差值（考虑方向）
        angle_diff = (raw_diff + 180) % 360 - 180
    else:
        # 规范化角弧度到[0, 2π)范围
        angle1 = convert_AngleRangeExplicit(angle1, mode="radian")
        angle2 = convert_AngleRangeExplicit(angle2, mode="radian")
        # 计算初始角弧度差值
        raw_diff = angle2 - angle1
        # 计算最小角弧度差值（考虑方向）
        angle_diff = (raw_diff + math.pi) % (2 * math.pi) - math.pi
    return angle_diff


def convert_AngleRangeExplicit(angle_deg: float | int, mode: str = "degree") -> float:
    """ 将角度从[-180, 180)范围转换到[0, 360)范围，或将角度从[-π, π)范围转换到[0, 2π)范围
    param angle_deg: float | int    输入角度
    param mode: str                 角度模式 ("degree" 或 "radian") 
    return: float                   转换后的角度
    """
    if mode == "degree":
        return (angle_deg + 360.0) % 360.0
    else:
        return (angle_deg + (2 * math.pi)) % (2 * math.pi)
