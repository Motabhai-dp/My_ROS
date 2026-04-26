import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node


def generate_launch_description():

    package_name = 'r_bot'

    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory(package_name),
                'launch',
                'rsp.launch.py'
            )
        ),
        launch_arguments={'use_sim_time': 'true'}.items()
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('gazebo_ros'),
                'launch',
                'gazebo.launch.py'
            )
        )
    )

    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', 'robot_description',
            '-entity', 'my_bot'
        ],
        output='screen'
    )

    # run your python file directly (bypass setup.py)
    omni_node = ExecuteProcess(
        cmd=[
            'python3',
            '/home/deepanshu/My_ROS/src/r_bot/r_bot/omni_kinematics.py'
        ],
        output='screen'
    )

    load_controllers = TimerAction(
        period=5.0,
        actions=[
            ExecuteProcess(
                cmd=[
                    'ros2', 'control', 'load_controller',
                    '--set-state', 'active',
                    'joint_state_broadcaster'
                ],
                output='screen'
            ),
            ExecuteProcess(
                cmd=[
                    'ros2', 'control', 'load_controller',
                    '--set-state', 'active',
                    'forward_velocity_controller'
                ],
                output='screen'
            )
        ]
    )

    return LaunchDescription([
        rsp,
        gazebo,
        spawn_entity,
        load_controllers,
        omni_node
    ])