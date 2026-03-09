import serial
import time
import logging


class SerialDriver:
    def __init__(self, port='/dev/esp', baudrate=115200, timeout=1.0, boot_delay_s=2.0):
        self.port = port
        self.baudrate = int(baudrate)
        self.timeout = float(timeout)
        self.boot_delay_s = float(boot_delay_s)

        self.serial_conn = None
        self.logger = logging.getLogger("SerialDriver")
        self.connect()

    def connect(self):
        """Mở kết nối Serial."""
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            self.logger.info(f"Đã kết nối ESP32 tại {self.port} (baud={self.baudrate})")
            time.sleep(self.boot_delay_s)  # chờ ESP32 reset sau khi mở cổng
        except serial.SerialException as e:
            self.serial_conn = None
            self.logger.error(f"Không thể kết nối ESP32 tại {self.port}: {e}")

    def write(self, line: str):
        """Gửi 1 dòng raw xuống ESP32 (tự thêm \\n nếu thiếu)."""
        if not isinstance(line, str):
            line = str(line)

        if not line.endswith("\n"):
            line += "\n"

        if self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.write(line.encode("utf-8"))
                self.logger.debug(f"Đã gửi raw: {line.strip()}")
                return True
            except Exception as e:
                self.logger.error(f"Lỗi gửi raw: {e}")
                return False
        else:
            self.logger.warning("Cổng Serial chưa mở, đang thử kết nối lại...")
            self.connect()
            return False

    def send_wheels(self, v_left: float, v_right: float):
        """ESP32 parse theo format: WL:<left>,WR:<right>\\n"""
        line = f"WL:{float(v_left):.3f},WR:{float(v_right):.3f}"
        return self.write(line)

    # giữ tên cũ nếu code khác đang gọi send_velocity()
    def send_velocity(self, v_left: float, v_right: float):
        return self.send_wheels(v_left, v_right)

    def close(self):
        if self.serial_conn:
            try:
                self.serial_conn.close()
            except Exception:
                pass
            self.serial_conn = None
