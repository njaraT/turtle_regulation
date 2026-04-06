## Partie 1

- `Kp` faible (`0.5`) : la tortue tourne lentement et la correction est douce.
- `Kp` fort (`6.0`) : la tortue tourne tres vite, avec un comportement plus brusque.
- `Kp` choisi (`2.0`) : bon compromis entre rapidite de correction et stabilite.

Commandes a lancer pour voir le resultat :

```bash
cd ~/njara_ws
colcon build --packages-select turtle_interfaces turtle_regulation
source install/setup.bash
ros2 run turtlesim turtlesim_node
```

Dans un autre terminal :

```bash
cd ~/njara_ws
source install/setup.bash
ros2 run turtle_regulation set_way_point --ros-args \
  -r pose:=/turtle1/pose \
  -r cmd_vel:=/turtle1/cmd_vel
```

## Partie 2

- `Kpl` faible (`0.5`) : la tortue avance lentement vers le waypoint.
- `Kpl` fort (`1.5`) : la tortue avance plus vite, avec un comportement plus agressif.
- `Kpl` choisi (`1.0`) : bon compromis entre vitesse de deplacement et stabilite.

Commandes a lancer pour voir le resultat :

```bash
cd ~/njara_ws
source install/setup.bash
ros2 topic echo /is_moving
```

Le noeud `set_way_point` et `turtlesim_node` doivent deja etre lances comme dans la partie 1.

## Partie 3

Commandes a lancer pour voir le resultat :

Le noeud `set_way_point` et `turtlesim_node` doivent deja etre lances.

Dans un autre terminal :

```bash
cd ~/njara_ws
source install/setup.bash
ros2 service call /set_waypoint_service turtle_interfaces/srv/SetWayPoint "{x: 5.0, y: 8.0}"
```
