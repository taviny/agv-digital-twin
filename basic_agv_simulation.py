import math
import matplotlib.pyplot as plt

# Vi tri ban dau cua AGV
agv_x = 0.0
agv_y = 0.0

# Luu lai cac vi tri AGV da di qua
path_x = [agv_x]
path_y = [agv_y]

# Cac diem AGV can di qua
waypoints = [
    (2.0, 0.0),
    (2.0, 3.0),
    (5.0, 3.0)
]

# Thong so mo phong
speed = 0.5
time_step = 1.0

print("Bat dau mo phong AGV")
print(f"Vi tri ban dau: ({agv_x}, {agv_y})")

# Di chuyen qua tung waypoint
for i, target in enumerate(waypoints):

    target_x, target_y = target

    print(f"\nDi chuyen den waypoint {i + 1}: {target}")

    while True:
        # Tinh khoang cach den diem dich
        dx = target_x - agv_x
        dy = target_y - agv_y

        distance = math.sqrt(dx**2 + dy**2)

        # Kiem tra AGV da den diem dich chua
        if distance < 0.05:
            agv_x = target_x
            agv_y = target_y
            break

        # Quang duong di duoc trong mot buoc
        step_distance = speed * time_step

        # Cap nhat vi tri AGV
        if distance <= step_distance:
            agv_x = target_x
            agv_y = target_y
        else:
            agv_x += (dx / distance) * step_distance
            agv_y += (dy / distance) * step_distance

        # Luu vi tri moi
        path_x.append(agv_x)
        path_y.append(agv_y)

        print(f"Vi tri AGV: ({agv_x:.2f}, {agv_y:.2f})")

    print(f"Da den waypoint {i + 1}")

print("\nAGV da hoan thanh hanh trinh!")

# Hien thi duong di cua AGV
plt.figure(figsize=(8, 6))

# Ve duong di
plt.plot(path_x, path_y, 'b-', label="AGV Path")

# Danh dau vi tri ban dau
plt.scatter(0, 0, color='green', s=100, label="Start")

# Danh dau cac waypoint
waypoint_x = [point[0] for point in waypoints]
waypoint_y = [point[1] for point in waypoints]

plt.scatter(
    waypoint_x,
    waypoint_y,
    color='red',
    marker='x',
    s=100,
    label="Waypoints"
)

# Danh dau vi tri ket thuc
plt.scatter(agv_x, agv_y, color='orange', s=100, label="Final Position")

plt.xlabel("X (m)")
plt.ylabel("Y (m)")
plt.title("AGV Movement Simulation")
plt.grid(True)
plt.legend()
plt.axis("equal")

plt.show()
