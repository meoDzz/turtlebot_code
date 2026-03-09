import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
from rclpy.qos import QoSProfile, ReliabilityPolicy
from serial_moduleV2 import SerialDriver


class EspSerialBridge(Node):
    def __init__(self):
        super().__init__('esp_serial_bridge')

        self.declare_parameter('port', '/dev/esp')
        self.declare_parameter('baud', 115200)
        self.declare_parameter('track_width', 0.20)

        port = self.get_parameter('port').value
        baud = int(self.get_parameter('baud').value)
        self.L = float(self.get_parameter('track_width').value)

        self.driver = SerialDriver(port=port, baudrate=baud)
        qos_profile = QoSProfile(reliability=ReliabilityPolicy.BEST_EFFORT, depth=10)
        self.create_subscription(TwistStamped, '/cmd_vel', self.cmd_vel_callback, 10)
        print('as')
        self.get_logger().info(f"Bridge ready. port={port}, baud={baud}, track_width={self.L} m")

    def cmd_vel_callback(self, msg: TwistStamped):
        print("Đã nhận được dữ liệu!")
        v = float(msg.twist.linear.x)
        w = float(msg.twist.angular.z)

        v_right = v + (w * self.L / 2.0)
        v_left  = v - (w * self.L / 2.0)

        self.driver.send_wheels(v_left, v_right)
        self.get_logger().info(f"cmd_vel_nav v={v:.2f} w={w:.2f} => WL={v_left:.3f} WR={v_right:.3f}")

def main(args=None):
    rclpy.init(args=args)
    node = EspSerialBridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
