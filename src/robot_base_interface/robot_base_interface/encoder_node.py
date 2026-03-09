import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32 # Hoặc Float32 tùy vào dữ liệu ESP32 gửi
from .serial_module import SerialDriver

class EncoderReader(Node):
    def __init__(self):
        super().__init__('encoder_reader_node')
        
        # Khởi tạo Serial Driver
        self.driver = SerialDriver(port='/dev/ttyACM1', baudrate=115200)
        
        # Tạo Publisher để gửi dữ liệu encoder lên ROS 2
        self.encoder_pub = self.create_publisher(Int32, 'encoder_ticks', 10)
        
        # Tạo timer để đọc dữ liệu liên tục (ví dụ 20Hz)
        self.timer = self.create_timer(0.05, self.read_encoder_callback)

    def read_encoder_callback(self):
        if self.driver.serial_conn and self.driver.serial_conn.in_waiting > 0:
            try:
                # Đọc một dòng từ Serial
                line = self.driver.serial_conn.readline().decode('utf-8').strip()
                
                # Giả sử ESP32 gửi dạng số nguyên: "1234"
                if line.isdigit():
                    msg = Int32()
                    msg.data = int(line)
                    self.encoder_pub.publish(msg)
                    self.get_logger().info(f'Encoder Ticks: {msg.data}')
            except Exception as e:
                self.get_logger().error(f'Lỗi đọc Serial: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = EncoderReader()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.driver.close()
        node.destroy_node()
        rclpy.shutdown()