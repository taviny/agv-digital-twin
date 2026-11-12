import math

# Vi tri ban dau cua AGV
agv_x = 0.0
agv_y = 0.0

# Cac diem AGV can di qua
waypoints = [
    (2.0, 0.0),
    (2.0, 3.0),
    (5.0, 3.0)
]

# Thong so mo phong
speed = 0.5       # Toc do AGV (m/s)
time_step = 1.0   # Thoi gian moi buoc (s)

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

        print(f"Vi tri AGV: ({agv_x:.2f}, {agv_y:.2f})")

    print(f"Da den waypoint {i + 1}")

print("\nAGV da hoan thanh hanh trinh!")
