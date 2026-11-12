import math
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import FancyArrowPatch

# Vi tri ban dau cua AGV
agv_x = 0.0
agv_y = 0.0

# Luu lai cac vi tri AGV da di qua
path_x = [agv_x]
path_y = [agv_y]
path_target = [0]

# Luu tong quang duong va thoi gian
total_distance = [0.0]
elapsed_time = [0.0]

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

            path_x.append(agv_x)
            path_y.append(agv_y)
            path_target.append(i + 1)
            total_distance.append(total_distance[-1])
            elapsed_time.append(elapsed_time[-1])
            break

        # Quang duong di duoc trong mot buoc
        step_distance = speed * time_step

        old_x = agv_x
        old_y = agv_y

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
        path_target.append(i + 1)

        #Tinh quang duong AGV vua di duoc
        moved_distance = math.sqrt(
            (agv_x - old_x)**2 + (agv_y - old_y)**2
        )

        total_distance.append(
            total_distance[-1] + moved_distance
        )

        elapsed_time.append(
            elapsed_time[-1] + moved_distance / speed
        )

        print(f"Vi tri AGV: ({agv_x:.2f}, {agv_y:.2f})")

    print(f"Da den waypoint {i + 1}")

print("\nAGV da hoan thanh hanh trinh!")
print(f"Tong quang duong: {total_distance[-1]:.2f} m")
print(f"Thoi gian di chuyen: {elapsed_time[-1]:.2f} s")

# Tao giao dien mo phong 2D
fig, ax = plt.subplots(figsize=(9, 6))

# Cau hinh khu vuc hien thi
ax.set_xlim(-1, 6)
ax.set_ylim(-1, 4)
ax.set_xlabel("X (m)")
ax.set_ylabel("Y (m)")
ax.set_title("AGV Movement Simulation")
ax.grid(True)
ax.set_aspect("equal")

# Hien thi cac waypoint
waypoint_x = [point[0] for point in waypoints]
waypoint_y = [point[1] for point in waypoints]

ax.scatter(
    waypoint_x,
    waypoint_y,
    color='red',
    marker='x',
    s=100,
    label="Waypoints"
)

# Hien thi vi tri bat dau
ax.scatter(0, 0, color='green', s=100, label="Start")

# Tao duong di va ky hieu AGV
path_line, = ax.plot([], [], 'b-', label="AGV Path")

# Hien thi huong di chuyen cua AGV
agv_arrow = FancyArrowPatch(
    (0, 0),
    (0.4, 0),
    arrowstyle='-|>',
    mutation_scale=18,
    color='orange',
    linewidth=3
)
ax.add_patch(agv_arrow)

#cap nhat thong tin vi tri hien tai
status_text = ax.text(
    0.02,
    0.95,
    "",
    transform=ax.transAxes,
    verticalalignment="top",
    fontsize=10,
    bbox=dict(facecolor="white", alpha=0.8)
)

ax.legend()

# Ham cap nhat tung khung hinh
def update(frame):
    x = path_x[frame]
    y = path_y[frame]

    path_line.set_data(path_x[:frame + 1], path_y[:frame + 1])

    # Xac dinh huong di cua AGV
    if frame < len(path_x) - 1:
        dx = path_x[frame + 1] - x
        dy = path_y[frame + 1] - y
    else:
        dx = x - path_x[frame - 1]
        dy = y - path_y[frame - 1]

    distance = math.sqrt(dx**2 + dy**2)

    if distance > 0:
        arrow_length = 0.4
        end_x = x + (dx / distance) * arrow_length
        end_y = y + (dy / distance) * arrow_length

        agv_arrow.set_positions(
            (x, y),
            (end_x, end_y)
        )

    #Waypoint Status
    current_waypoint = path_target[frame]

    if frame == len(path_x) - 1:
        status = "Hoan thanh hanh trinh"
    else:
        status = f"Dang den waypoint {current_waypoint}"

    # Simulation Info
    status_text.set_text(
        f"AGV Position: ({x:.2f}, {y:.2f}) m\n"
        f"Status: {status}\n"
        f"Total Distance: {total_distance[frame]:.2f} m\n"
        f"Elapsed Time: {elapsed_time[frame]:.1f} s"
    )

    return path_line, agv_arrow, status_text


# Tao hoat anh
ani = FuncAnimation(
    fig,
    update,
    frames=len(path_x),
    interval=300,
    repeat=False,
    blit=True
)

plt.show()
