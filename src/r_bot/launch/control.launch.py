from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():

    robot_description = ParameterValue(
        Command(['xacro ', '/home/deepanshu/My_ROS/src/r_bot/description/new_core.xacro']),
        value_type=str
    )

    return LaunchDescription([

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description}],
            output='screen'
        ),

        Node(
            package='controller_manager',
            executable='ros2_control_node',
            parameters=[{'robot_description': robot_description},
                        '/home/deepanshu/My_ROS/src/r_bot/config/controllers.yaml'],
            output='screen'
        ),

        Node(
            package="controller_manager",
            executable="spawner",
            arguments=["forward_velocity_controller"],
            output="screen"
        ),
    ])