import math

from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool
from turtlesim.msg import Pose


# Noeud ROS 2 charge de calculer et publier la commande pour atteindre un waypoint.
class SetWayPoint(Node):
    def __init__(self):
        super().__init__('set_way_point')
        self.pose = None
        self.waypoint = (7.0, 7.0)
        self.kp = 2.0
        self.kpl = 1.5
        self.distance_tolerance = 0.1
        self.last_log_time = self.get_clock().now()
        self.goal_reached = False

        self.pose_subscriber = self.create_subscription(
            Pose,
            'pose',
            self.pose_callback,
            10,
        )
        self.cmd_vel_publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        self.is_moving_publisher = self.create_publisher(Bool, 'is_moving', 10)
        self.control_timer = self.create_timer(0.03, self.publish_heading_command)
        self.get_logger().info('set_way_point node started')

    # Met a jour la pose courante de la tortue a chaque message recu sur le topic pose.
    def pose_callback(self, msg: Pose) -> None:
        self.pose = msg

    # Calcule l'orientation a atteindre pour viser le waypoint.
    def compute_desired_heading(self) -> float:
        # Angle de la droite entre la position courante et le waypoint.
        return math.atan2(
            self.waypoint[1] - self.pose.y,
            self.waypoint[0] - self.pose.x,
        )

    # Calcule l'erreur entre l'orientation actuelle et l'orientation desiree.
    def compute_heading_error(self, desired_heading: float) -> float:
        angle_difference = desired_heading - self.pose.theta
        # Ramene l'erreur dans [-pi, pi] pour tourner dans le sens le plus court.
        return math.atan2(math.sin(angle_difference), math.cos(angle_difference))

    # Calcule la distance entre la tortue et le waypoint.
    def compute_distance_error(self) -> float:
        # Distance euclidienne entre la tortue et le waypoint.
        return math.sqrt(
            (self.waypoint[1] - self.pose.y) ** 2 +
            (self.waypoint[0] - self.pose.x) ** 2
        )

    # Calcule puis publie la commande de vitesse en fonction de la pose courante.
    def publish_heading_command(self) -> None:
        if self.pose is None:
            return

        desired_heading = self.compute_desired_heading()
        heading_error = self.compute_heading_error(desired_heading)
        distance_error = self.compute_distance_error()

        cmd_vel = Twist()
        is_moving = Bool()

        if distance_error > self.distance_tolerance:
            # Commande proportionnelle en distance et en cap.
            cmd_vel.linear.x = self.kpl * distance_error
            cmd_vel.angular.z = self.kp * heading_error
            self.cmd_vel_publisher.publish(cmd_vel)
            is_moving.data = True
            self.goal_reached = False
        else:
            is_moving.data = False
            if not self.goal_reached:
                # On publie une commande nulle une seule fois a l'arrivee.
                self.cmd_vel_publisher.publish(Twist())
                self.goal_reached = True

        self.is_moving_publisher.publish(is_moving)

        now = self.get_clock().now()
        elapsed = (now - self.last_log_time).nanoseconds / 1e9
        if elapsed >= 1.0:
            self.get_logger().info(
                f'distance={distance_error:.2f}, '
                f'theta={self.pose.theta:.2f}, '
                f'theta_desired={desired_heading:.2f}, '
                f'error={heading_error:.2f}, '
                f'v={cmd_vel.linear.x:.2f}, '
                f'u={cmd_vel.angular.z:.2f}, '
                f'is_moving={is_moving.data}'
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
