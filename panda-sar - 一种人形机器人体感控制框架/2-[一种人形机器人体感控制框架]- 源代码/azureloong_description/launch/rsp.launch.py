import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node
from launch.conditions import IfCondition, UnlessCondition

import xacro


def generate_launch_description():

    # 启动参数
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_gui = LaunchConfiguration('use_gui_control')
    
    # 获取包路径
    # 这里的包名可以根据您的实际情况修改
    pkg_name = 'azureloong_description'
    pkg_path = os.path.join(get_package_share_directory(pkg_name))

    # 转换 Xacro 到 URDF
    # ros2 run xacro xacro --inorder -o $(pkg_path)/urdf/robot.urdf $(pkg_path)/description/robot.xacro
    xacro_file = os.path.join(pkg_path, 'description', 'robot.xacro')
    robot_description_config = xacro.process_file(xacro_file)
    urdf_file = os.path.join(pkg_path, 'urdf', 'robot.urdf')
    with open(urdf_file, 'w') as file:
        file.write(robot_description_config.toxml())
    
    # 发布机器人定义
    # ros2 run robot_state_publisher robot_state_publisher --ros-args -p robot_description:=$(cat $(pkg_path)/urdf/robot.urdf)
    params = {
        'robot_description': robot_description_config.toxml(),
        'use_sim_time': use_sim_time
    }
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[params],
    )

    # 可视化机器人模型
    # ros2 run rviz2 rviz2 -d ${pkg_path}/config/robot.rviz
    node_robot_rviz2_viewer = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        arguments=['-d', os.path.join(pkg_path, 'config', 'robot.rviz')],
        condition=IfCondition(use_gui),
    )

    # GUI 关节控制模式
    # ros2 run joint_state_publisher_gui joint_state_publisher_gui --ros-args -r joint_states:=arm/joint_states
    node_robot_joint_state_gui_publisher = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        output='screen',
        remappings=[('joint_states', 'arm/joint_states'),],
        condition=IfCondition(use_gui),
    )
    
    # Launch!
    return LaunchDescription([
        # Launch 回调参数定义
        DeclareLaunchArgument('use_sim_time', default_value='false', description='Use sim time if true'),
        DeclareLaunchArgument('use_gui_control', default_value='true', description='Launch GUI control tools'),
        # Launch 和 Run 节点
        node_robot_state_publisher,
        node_robot_rviz2_viewer,
        node_robot_joint_state_gui_publisher,
    ])
