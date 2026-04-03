import math

from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose


class SetWayPoint(Node):
    def __init__(self):
        super().__init__('set_way_point')
        self.pose = None
        self.waypoint = (7.0, 7.0)
        self.kp = 6.0
        self.last_log_time = self.get_clock().now()

        self.pose_subscriber = self.create_subscription(
            Pose,
            'pose',
            self.pose_callback,
            10,
        )
        self.cmd_vel_publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        self.control_timer = self.create_timer(0.03, self.publish_heading_command)
        self.get_logger().info('set_way_point node started')

    def pose_callback(self, msg: Pose) -> None:
        self.pose = msg

    def compute_desired_heading(self) -> float:
        return math.atan2(
            self.waypoint[1] - self.pose.y,
            self.waypoint[0] - self.pose.x,
        )

    def compute_heading_error(self, desired_heading: float) -> float:
        angle_difference = desired_heading - self.pose.theta
        return math.atan2(math.sin(angle_difference), math.cos(angle_difference))

    def publish_heading_command(self) -> None:
        if self.pose is None:
            return

        desired_heading = self.compute_desired_heading()
        heading_error = self.compute_heading_error(desired_heading)

        cmd_vel = Twist()
        cmd_vel.angular.z = self.kp * heading_error
        self.cmd_vel_publisher.publish(cmd_vel)

        now = self.get_clock().now()
        elapsed = (now - self.last_log_time).nanoseconds / 1e9
        if elapsed >= 1.0:
            self.get_logger().info(
                f'theta={self.pose.theta:.2f}, '
                f'theta_desired={desired_heading:.2f}, '
                f'error={heading_error:.2f}, '
                f'u={cmd_vel.angular.z:.2f}'
            )
            self.last_log_time = now


def main(args=None) -> None:
    rclpy.init(args=args)
    node = SetWayPoint()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
