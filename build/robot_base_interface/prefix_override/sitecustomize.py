import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/radxa/turtlebot3_ws/install/robot_base_interface'
