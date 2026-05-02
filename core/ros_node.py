import json
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class ROSNode(Node):
    def __init__(self, cfg):
        super().__init__(cfg['ros2']['node_name'])
        self.publisher = self.create_publisher(
            String,
            cfg['ros2']['topic'],
            cfg['ros2']['qos_depth']
        )

    def send_packet(self, packet: dict):
        msg = String()
        msg.data = json.dumps(packet)
        self.publisher.publish(msg)
        self.get_logger().info(f'GUI → ROS2 PACKET: {msg.data}')