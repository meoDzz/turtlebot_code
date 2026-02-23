
sửa file .lua
```
  map_frame = "map",
  tracking_frame = "base_link",               -- Đổi thành "base_link" nếu KHÔNG có IMU ổn định
  published_frame = "base_link",             -- Frame chính publish pose (thay nếu cần)
  odom_frame = "odom",                       -- Chỉ dùng nếu provide_odom_frame = true
  provide_odom_frame = true,                -- Tắt vì không có odom thật
  publish_frame_projected_to_2d = true,      -- Rất quan trọng cho 2D handheld
  use_odometry = false,  
```
Cách build lại bằng symlink mềm

cd ~/turtlebot3_ws
colcon build --symlink-install --packages-select turtlebot3_cartographer turtlebot3_navigation2
source install/setup.bash

# Trong file cartographer.launch.py

# Chỗ 1: Node cartographer_node (để nó không phát bản đồ đè lên map cũ)
cartographer_node = Node(
    package='cartographer_ros',
    executable='cartographer_node',
    # ... các dòng khác giữ nguyên ...
    remappings=[('map', 'map_live')] 
)

# Chỗ 2: Node occupancy_grid_node (đây mới là node tạo ra cái hình ảnh bản đồ đen trắng)
occupancy_grid_node = Node(
    package='cartographer_ros',
    executable='occupancy_grid_node',
    # ... các dòng khác giữ nguyên ...
    remappings=[('map', 'map_live')]
)
 
# Lưu map mới

```
ros2 run nav2_map_server map_saver_cli -f /home/radxa/turtlebot3_ws/map/map_2.yaml
```


# Run bring up devices

```
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_bringup robot.launch.py
```
 
# Odom carto
```
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_cartographer cartographer.launch.py use_sim_time:=False
```

# Launch Navigation
```
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_navigation2 navigation2.launch.py use_sim_time:=False map:=/home/radxa/turtlebot3_ws/map/map_2.yaml
```
