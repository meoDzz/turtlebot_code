# import rclpy
# from rclpy.node import Node
# from geometry_msgs.msg import PoseWithCovarianceStamped
# import time

# class InitialPoseSetter(Node):
#     def __init__(self):
#         super().__init__('initial_pose_setter')
#         # Publisher gửi đến topic chuẩn của Nav2/AMCL
#         self.publisher_ = self.create_publisher(
#             PoseWithCovarianceStamped, 
#             '/initialpose', 
#             10)
        
#         # Chờ 1 giây để đảm bảo kết nối publisher ổn định
#         time.sleep(2)
#         self.set_pose()

#     def set_pose(self):
#         msg = PoseWithCovarianceStamped()
        
#         # 1. Cấu hình Header
#         msg.header.stamp = self.get_clock().now().to_msg()
#         msg.header.frame_id = 'map' # Hệ tọa độ bản đồ

#         # 2. Set vị trí (x, y, z)
#         msg.pose.pose.position.x = 0.0
#         msg.pose.pose.position.y = 0.0
#         msg.pose.pose.position.z = 0.0

#         # 3. Set hướng (Quaternion) - Ở đây là hướng nhìn thẳng (0 độ)
#         msg.pose.pose.orientation.x = 0.0
#         msg.pose.pose.orientation.y = 0.0
#         msg.pose.pose.orientation.z = 0.0
#         msg.pose.pose.orientation.w = 1.0

#         # 4. Cấu hình Covariance (Độ tin tưởng)
#         # Ma trận 6x6 (36 phần tử), số càng nhỏ thì độ chính xác tin tưởng càng cao
#         msg.pose.covariance = [0.0] * 36
#         msg.pose.covariance[0] = 0.25 # Sai số x
#         msg.pose.covariance[7] = 0.25 # Sai số y
#         msg.pose.covariance[35] = 0.06 # Sai số góc quay

#         self.publisher_.publish(msg)
#         self.get_logger().info('Đã gửi lệnh Initial Pose: x=0, y=0, hướng=0 độ')

# def main(args=None):
#     rclpy.init(args=args)
#     node = InitialPoseSetter()
#     # Sau khi gửi xong thì tắt node vì chỉ cần set 1 lần
#     node.destroy_node()
#     rclpy.shutdown()

# if __name__ == '__main__':
#     main()


import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseWithCovarianceStamped

class InitialPoseSetter(Node):
    def __init__(self):
        super().__init__('initial_pose_setter')
        
        # Publisher gửi đến topic chuẩn của Nav2/AMCL
        self.publisher_ = self.create_publisher(
            PoseWithCovarianceStamped, 
            '/initialpose', 
            10)
        
        self.count = 0
        self.max_attempts = 10 # Thử gửi 5 lần để chắc chắn hệ thống nhận được
        
        # Thay vì dùng sleep, ta dùng Timer để gửi mỗi 0.5 giây
        self.timer = self.create_timer(0.5, self.timer_callback)
        self.get_logger().info('Đang bắt đầu gửi Initial Pose...')

    def timer_callback(self):
        if self.count < self.max_attempts:
            self.set_pose()
            self.count += 1
        else:
            self.get_logger().info('Hoàn thành việc set pose. Đang tắt node...')
            self.timer.cancel()
            # Tắt node sau khi đã gửi đủ số lần
            raise SystemExit 

    def set_pose(self):
        msg = PoseWithCovarianceStamped()
        
        # Sử dụng thời gian thực từ clock của node
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'map'

        # Tọa độ gốc (0,0)
        msg.pose.pose.position.x = 0.0
        msg.pose.pose.position.y = 0.0
        msg.pose.pose.orientation.w = 1.0

        # Covariance cực nhỏ để ép Nav2 tin tưởng hoàn toàn vào vị trí này
        msg.pose.covariance = [0.0] * 36
        msg.pose.covariance[0] = 0.01 
        msg.pose.covariance[7] = 0.01 
        msg.pose.covariance[35] = 0.01 

        self.publisher_.publish(msg)
        self.get_logger().info(f'Lần thử {self.count + 1}: Đã gửi Initial Pose (0,0)')

def main(args=None):
    rclpy.init(args=args)
    node = InitialPoseSetter()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()