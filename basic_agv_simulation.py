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

# Luu tong quang duong va thoi gian
total_distance = 0.0
elapsed_time = 0.0

# Cac diem AGV can di qua
waypoints = [
    (2.0, 0.0),
    (2.0, 3.0),
    (5.0, 3.0)
]

# Thong so mo phong
speed = 0.5
time_step = 0.1

# Trang thai mo phong
is_paused = False
current_target_index = 0
mission_completed = False
last_direction = (1.0, 0.0)

current_target = waypoints[current_target_index]

print("Bat dau mo phong AGV")
print(f"Vi tri ban dau: ({agv_x}, {agv_y})")

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

# Hien thi diem dich hien tai
destination_marker = ax.scatter(
    [current_target[0]],
    [current_target[1]],
    color='purple',
    marker='*',
    s=180,
    label="Current Destination"
)

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

# Huong dan dieu khien mo phong
control_text = ax.text(
    0.98,
    0.95,
    "SPACE: Pause / Resume\nClick: Change destination (when paused)",
    transform=ax.transAxes,
    horizontalalignment="right",
    verticalalignment="top",
    fontsize=9,
    bbox=dict(facecolor="white", alpha=0.8)
)

ax.legend()


# Ham cap nhat tung khung hinh
def update(frame):
    global agv_x, agv_y
    global current_target, current_target_index
    global total_distance, elapsed_time
    global mission_completed, last_direction

    # Di chuyen qua tung waypoint
    if not is_paused and not mission_completed:

        target_x, target_y = current_target

        # Tinh khoang cach den diem dich
        dx = target_x - agv_x
        dy = target_y - agv_y

        distance = math.sqrt(dx**2 + dy**2)

        # Kiem tra AGV da den diem dich chua
        if distance < 0.05:
            old_x = agv_x
            old_y = agv_y

            agv_x = target_x
            agv_y = target_y

            #Tinh quang duong AGV vua di duoc
            moved_distance = math.sqrt(
                (agv_x - old_x)**2 + (agv_y - old_y)**2
            )

            total_distance += moved_distance
            elapsed_time += moved_distance / speed

            if moved_distance > 0:
                path_x.append(agv_x)
                path_y.append(agv_y)

            print(f"Da den waypoint: {current_target}")

            current_target_index += 1

            if current_target_index < len(waypoints):
                current_target = waypoints[current_target_index]
            else:
                mission_completed = True
                print("\nAGV da hoan thanh hanh trinh!")
                print(f"Tong quang duong: {total_distance:.2f} m")
                print(f"Thoi gian di chuyen: {elapsed_time:.2f} s")

        else:
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

            #Tinh quang duong AGV vua di duoc
            moved_distance = math.sqrt(
                (agv_x - old_x)**2 + (agv_y - old_y)**2
            )

            total_distance += moved_distance
            elapsed_time += moved_distance / speed

            if moved_distance > 0:
                direction_x = agv_x - old_x
                direction_y = agv_y - old_y

                direction_length = math.sqrt(
                    direction_x**2 + direction_y**2
                )

                last_direction = (
                    direction_x / direction_length,
                    direction_y / direction_length
                )

    x = agv_x
    y = agv_y

    path_line.set_data(path_x, path_y)

    # Xac dinh huong di cua AGV
    arrow_length = 0.4
    end_x = x + last_direction[0] * arrow_length
    end_y = y + last_direction[1] * arrow_length

    agv_arrow.set_positions(
        (x, y),
        (end_x, end_y)
    )

    #Waypoint Status
    if mission_completed:
        status = "Hoan thanh hanh trinh"
    elif is_paused:
        status = "Tam dung"
    else:
        status = f"Dang den waypoint {current_target_index + 1}"

    # Simulation Info
    status_text.set_text(
        f"AGV Position: ({x:.2f}, {y:.2f}) m\n"
        f"Status: {status}\n"
        f"Destination: ({current_target[0]:.2f}, {current_target[1]:.2f}) m\n"
        f"Total Distance: {total_distance:.2f} m\n"
        f"Elapsed Time: {elapsed_time:.1f} s"
    )

    return path_line, agv_arrow, status_text, destination_marker


# Xu ly su kien ban phim
def on_key_press(event):
    global is_paused

    if event.key in (" ", "space"):
        if is_paused:
            is_paused = False
            ani.event_source.start()
            print("Tiep tuc mo phong AGV")
        else:
            is_paused = True
            ani.event_source.stop()
            update(0)
            fig.canvas.draw_idle()
            print("Da tam dung mo phong AGV")


# Xu ly su kien chuot
def on_mouse_click(event):
    global current_target
    global current_target_index
    global waypoints
    global mission_completed

    # Chi chon diem dich khi AGV dang tam dung
    if not is_paused:
        return

    if event.inaxes != ax:
        return

    if event.xdata is None or event.ydata is None:
        return

    # Cap nhat diem dich moi
    new_target = (float(event.xdata), float(event.ydata))

    current_target = new_target
    waypoints = [new_target]
    current_target_index = 0
    mission_completed = False

    destination_marker.set_offsets([new_target])

    print(f"Da chon diem dich moi: ({new_target[0]:.2f}, {new_target[1]:.2f})")

    update(0)
    fig.canvas.draw_idle()


# Tao hoat anh
ani = FuncAnimation(
    fig,
    update,
    frames=None,
    interval=100,
    repeat=False,
    blit=False,
    cache_frame_data=False
)

# Lang nghe su kien ban phim va chuot
fig.canvas.mpl_connect("key_press_event", on_key_press)
fig.canvas.mpl_connect("button_press_event", on_mouse_click)

plt.show()
