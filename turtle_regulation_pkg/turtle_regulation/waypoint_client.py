import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool
from turtle_interfaces.srv import SetWayPoint


# Noeud client qui envoie trois waypoints au service set_waypoint_service.
class WayPointClient(Node):
    def __init__(self):
        super().__init__('waypoint_client')
        self.waypoints = [
            (2.0, 2.0),
            (8.0, 2.0),
            (8.0, 8.0),
        ]
        self.current_index = 0
        self.is_moving = True
        self.request_in_progress = False

        # Client du service qui modifie le waypoint du noeud de regulation.
        self.client = self.create_client(SetWayPoint, 'set_waypoint_service')
        # Subscriber qui attend que la tortue ait fini son mouvement.
        self.is_moving_subscriber = self.create_subscription(
            Bool,
            'is_moving',
            self.is_moving_callback,
            10,
        )
        # Timer qui verifie regulierement si un nouvel appel peut etre envoye.
        self.control_timer = self.create_timer(0.2, self.try_send_next_waypoint)
        self.get_logger().info('waypoint_client node started')

    # Met a jour l'etat du deplacement de la tortue.
    def is_moving_callback(self, msg: Bool) -> None:
        self.is_moving = msg.data

    # Envoie le waypoint suivant seulement si la tortue est a l'arret.
    def try_send_next_waypoint(self) -> None:
        if self.current_index >= len(self.waypoints):
            return

        if not self.client.wait_for_service(timeout_sec=0.1):
            self.get_logger().info('Waiting for set_waypoint_service...')
            return

        if self.is_moving or self.request_in_progress:
            return

        waypoint = self.waypoints[self.current_index]
        request = SetWayPoint.Request()
        request.x = waypoint[0]
        request.y = waypoint[1]

        self.request_in_progress = True
        future = self.client.call_async(request)
        future.add_done_callback(self.handle_service_response)
        self.get_logger().info(
            f'Sending waypoint {self.current_index + 1}: '
            f'x={request.x:.2f}, y={request.y:.2f}'
        )

    # Traite la reponse du service avant de passer au waypoint suivant.
    def handle_service_response(self, future) -> None:
        self.request_in_progress = False

        try:
            response = future.result()
        except Exception as exc:
            self.get_logger().error(f'Service call failed: {exc}')
            return

        if response.res:
            self.current_index += 1
            self.get_logger().info('Waypoint updated successfully')


# Initialise ROS 2 puis lance le noeud client.
def main(args=None) -> None:
    rclpy.init(args=args)
    node = WayPointClient()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
