# import rclpy
# from rclpy.node import Node
# from geometry_msgs.msg import PoseStamped

# class GoalSetter(Node):
#     def __init__(self):
#         super().__init__('goal_setter_node')
#         self.publisher_ = self.create_publisher(PoseStamped, '/goal_pose', 10)
#         # Chờ hệ thống ổn định
#         self.timer = self.create_timer(1.0, self.publish_goal)
#         self.get_logger().info('Đang chuẩn bị gửi đích đến...')

#     def publish_goal(self):
#         msg = PoseStamped()
#         msg.header.stamp = self.get_clock().now().to_msg()
#         msg.header.frame_id = 'map'

#         # Tọa độ điểm đích (Ví dụ: x=2m, y=1m)
#         msg.pose.position.x = 0.4
#         msg.pose.position.y = -0.12
        
#         # Hướng quay (Quaternion) - Quay mặt về phía trước
#         msg.pose.orientation.w = 1.0

#         self.publisher_.publish(msg)
#         self.get_logger().info('Đã gửi Goal Pose: x=0.4, y=-0.12')
#         self.timer.cancel() # Chỉ gửi một lần

# def main(args=None):
#     rclpy.init(args=args)
#     node = GoalSetter()
#     rclpy.spin(node)
#     rclpy.shutdown()



# import rclpy
# from rclpy.node import Node
# from rclpy.action import ActionClient
# from nav2_msgs.action import NavigateToPose
# from geometry_msgs.msg import PoseStamped

# class GoalSetter(Node):
#     def __init__(self):
#         super().__init__('goal_setter_node')
        
#         # Tạo Action Client để giao tiếp với Nav2
#         self._action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        
#         # Cấu hình tọa độ đích đến (Bạn có thể sửa X, Y tại đây)
#         self.target_x = 0.4 
#         self.target_y = -0.12
        
#         self.get_logger().info('Đang khởi động GoalSetter...')
        
#         # Bắt đầu quá trình kết nối
#         self.attempt_connection()

#     def attempt_connection(self):
#         """Kiểm tra xem Action Server đã sẵn sàng chưa"""
#         if not self._action_client.wait_for_server(timeout_sec=1.0):
#             self.get_logger().warn('Nav2 Action Server chưa sẵn sàng, đang đợi...')
#             # Tạo timer để thử lại sau 2 giây (không dùng once=True)
#             self.retry_timer = self.create_timer(2.0, self.retry_callback)
#         else:
#             self.get_logger().info('Đã kết nối thành công với Nav2!')
#             self.send_goal()

#     def retry_callback(self):
#         """Hàm bổ trợ để thử lại kết nối"""
#         self.retry_timer.cancel() # Hủy timer ngay để tránh lặp lại
#         self.attempt_connection()

#     def send_goal(self):
#         """Đóng gói và gửi yêu cầu đích đến"""
#         goal_msg = NavigateToPose.Goal()
#         goal_msg.pose.header.frame_id = 'map'
#         goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        
#         goal_msg.pose.pose.position.x = float(self.target_x)
#         goal_msg.pose.pose.position.y = float(self.target_y)
#         goal_msg.pose.pose.orientation.w = 1.0

#         self.get_logger().info(f'Đang gửi mục tiêu: x={self.target_x}, y={self.target_y}')
        
#         # Gửi yêu cầu và đăng ký hàm phản hồi khi Server nhận được
#         self._send_goal_future = self._action_client.send_goal_async(goal_msg)
#         self._send_goal_future.add_done_callback(self.goal_response_callback)

#     def goal_response_callback(self, future):
#         """Xử lý phản hồi từ Server (Chấp nhận hoặc Từ chối)"""
#         goal_handle = future.result()
#         if not goal_handle.accepted:
#             self.get_logger().error('Mục tiêu bị từ chối (Rejected)! Đang thử lại sau 2 giây...')
#             # Nếu bị từ chối (do Nav2 bận), tạo timer thử lại sau 2 giây
#             self.reloop_timer = self.create_timer(2.0, self.reloop_callback)
#             return

#         self.get_logger().info('Nav2 đã nhận lệnh! Robot bắt đầu di chuyển.')

#     def reloop_callback(self):
#         """Hàm bổ trợ để gửi lại Goal khi bị từ chối"""
#         self.reloop_timer.cancel() # Hủy timer ngay
#         self.send_goal()

# def main(args=None):
#     rclpy.init(args=args)
#     node = GoalSetter()
#     try:
#         rclpy.spin(node)
#     except KeyboardInterrupt:
#         pass
#     finally:
#         node.destroy_node()
#         rclpy.shutdown()





import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped

class GoalSetter(Node):
    def __init__(self):
        super().__init__('goal_setter_node')
        
        self._action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        
        # --- DANH SÁCH CÁC ĐIỂM CẦN ĐI (X, Y) ---
        self.goal_list = [
            [0.17, -0.23],
            [0.39, -0.016],
        ]
        self.current_goal_index = 0
        
        self.get_logger().info(f'Khởi động tuần tra {len(self.goal_list)} điểm...')
        self.attempt_connection()

    def attempt_connection(self):
        if not self._action_client.wait_for_server(timeout_sec=1.0):
            self.get_logger().warn('Đợi Nav2 Server...')
            self.retry_timer = self.create_timer(2.0, self.retry_callback)
        else:
            self.send_next_goal()

    def retry_callback(self):
        self.retry_timer.cancel()
        self.attempt_connection()

    def send_next_goal(self):
        """Hàm lấy điểm tiếp theo từ danh sách để gửi"""
        if self.current_goal_index < len(self.goal_list):
            target = self.goal_list[self.current_goal_index]
            
            goal_msg = NavigateToPose.Goal()
            goal_msg.pose.header.frame_id = 'map'
            goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
            goal_msg.pose.pose.position.x = float(target[0])
            goal_msg.pose.pose.position.y = float(target[1])
            goal_msg.pose.pose.orientation.w = 1.0

            self.get_logger().info(f'--- Đang đi đến điểm {self.current_goal_index + 1}: x={target[0]}, y={target[1]} ---')
            
            send_goal_future = self._action_client.send_goal_async(goal_msg)
            send_goal_future.add_done_callback(self.goal_response_callback)
        else:
            self.get_logger().info('ĐÃ HOÀN THÀNH TẤT CẢ CÁC ĐIỂM!')
            # Nếu muốn đi lặp lại vô tận, hãy bỏ comment dòng dưới:
            # self.current_goal_index = 0; self.send_next_goal()

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Điểm bị từ chối, thử lại...')
            self.reloop_timer = self.create_timer(2.0, self.reloop_callback)
            return

        # Đăng ký hàm để biết khi nào robot thực sự ĐẾN ĐÍCH (Result)
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        """Hàm này chạy khi robot đã hoàn thành hành trình đến 1 điểm"""
        self.get_logger().info(f'Đã đến điểm {self.current_goal_index + 1}!')
        self.current_goal_index += 1
        # Đợi 1 giây rồi đi tiếp điểm sau cho robot ổn định
        self.create_timer(1.0, self.next_goal_timer_callback)

    def next_goal_timer_callback(self):
        # Tắt timer tạm thời và gửi điểm tiếp theo
        # Lưu ý: rclpy.timer.Timer không có thuộc tính để tự hủy, nên ta phải hủy thủ công
        # Cách an toàn nhất là dùng timer lặp và cancel ngay
        for timer in [t for t in self.timers if t.timer_period_ns == 1000000000]: # Tìm timer 1s
             timer.cancel()
        self.send_next_goal()

    def reloop_callback(self):
        self.reloop_timer.cancel()
        self.send_next_goal()

def main(args=None):
    rclpy.init(args=args)
    node = GoalSetter()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()