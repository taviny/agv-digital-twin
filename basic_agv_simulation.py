import math
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import FancyArrowPatch, Rectangle

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
default_waypoints = [
    (2.0, 0.0),
    (2.0, 3.0),
    (5.0, 3.0)
]
waypoints = default_waypoints.copy()

# Thong so mo phong
default_speed = 0.5
speed = default_speed
time_step = 0.1

# Gioi han ban do
x_min = -1
x_max = 6
y_min = -1
y_max = 4

# Cac vung cam tren ban do
no_go_zones = [
    (0.8, 0.8, 0.8, 1.0),
    (3.2, 0.8, 0.9, 1.0)
]

# Trang thai mo phong
is_paused = False
current_target_index = 0
mission_completed = False
last_direction = (1.0, 0.0)
current_target = waypoints[current_target_index]
message = "Mo phong dang san sang"

print("Bat dau mo phong AGV")
print(f"Vi tri ban dau: ({agv_x}, {agv_y})")


# Kiem tra mot diem co nam trong vung cam khong
def diem_trong_vung_cam(x, y, zone):
    zone_x, zone_y, width, height = zone

    return (
        zone_x <= x <= zone_x + width
        and zone_y <= y <= zone_y + height
    )


# Kiem tra doan duong co cat qua vung cam khong
def doan_cat_vung_cam(x1, y1, x2, y2, zone):
    zone_x, zone_y, width, height = zone

    zone_right = zone_x + width
    zone_top = zone_y + height

    dx = x2 - x1
    dy = y2 - y1

    p = [-dx, dx, -dy, dy]
    q = [
        x1 - zone_x,
        zone_right - x1,
        y1 - zone_y,
        zone_top - y1
    ]

    u1 = 0.0
    u2 = 1.0

    for pi, qi in zip(p, q):
        if pi == 0:
            if qi < 0:
                return False
        else:
            t = qi / pi

            if pi < 0:
                u1 = max(u1, t)
            else:
                u2 = min(u2, t)

            if u1 > u2:
                return False

    return True


# Kiem tra diem dich moi co hop le khong
def kiem_tra_diem_dich(x, y):
    if not (x_min <= x <= x_max and y_min <= y <= y_max):
        return False, "Diem nam ngoai ban do"

    for zone in no_go_zones:
        if diem_trong_vung_cam(x, y, zone):
            return False, "Diem nam trong vung cam"

        if doan_cat_vung_cam(agv_x, agv_y, x, y, zone):
            return False, "Duong di cat qua vung cam"

    return True, "Diem dich hop le"


# Tao giao dien mo phong 2D
fig, ax = plt.subplots(figsize=(9, 6))

# Cau hinh khu vuc hien thi
ax.set_xlim(x_min - 0.3, x_max + 0.3)
ax.set_ylim(y_min - 0.3, y_max + 0.3)
ax.set_xlabel("X (m)")
ax.set_ylabel("Y (m)")
ax.set_title("AGV Movement Simulation")
ax.grid(True)
ax.set_aspect("equal")

# Hien thi ranh gioi khu vuc hoat dong
boundary = Rectangle(
    (x_min, y_min),
    x_max - x_min,
    y_max - y_min,
    fill=False,
    edgecolor="green",
    linewidth=2,
    label="Operating Area"
)
ax.add_patch(boundary)

# Hien thi cac vung cam
for i, zone in enumerate(no_go_zones):
    zone_x, zone_y, width, height = zone

    obstacle = Rectangle(
        (zone_x, zone_y),
        width,
        height,
        facecolor="red",
        edgecolor="darkred",
        alpha=0.3,
        label="No-go Zone" if i == 0 else "_nolegend_"
    )
    ax.add_patch(obstacle)

# Hien thi cac waypoint
waypoint_x = [point[0] for point in waypoints]
waypoint_y = [point[1] for point in waypoints]

waypoint_scatter = ax.scatter(
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
    0.97,
    "",
    transform=ax.transAxes,
    verticalalignment="top",
    fontsize=9,
    bbox=dict(facecolor="white", alpha=0.8)
)

# Huong dan dieu khien mo phong
control_text = ax.text(
    0.98,
    0.97,
    "SPACE: Pause / Resume\n"
    "Click: Change destination (when paused)\n"
    "+ / -: Change speed\n"
    "R: Reset",
    transform=ax.transAxes,
    horizontalalignment="right",
    verticalalignment="top",
    fontsize=9,
    bbox=dict(facecolor="white", alpha=0.8)
)

ax.legend(loc="lower right")


# Ham cap nhat tung khung hinh
def update(frame):
    global agv_x, agv_y
    global current_target, current_target_index
    global total_distance, elapsed_time
    global mission_completed, last_direction
    global message

    # Di chuyen qua tung waypoint
    if not is_paused and not mission_completed:

        target_x, target_y = current_target

        # Tinh khoang cach den diem dich
        dx = target_x - agv_x
        dy = target_y - agv_y

        distance = math.sqrt(dx**2 + dy**2)

        # Kiem tra AGV da den diem dich chua
        step_distance = speed * time_step

        if distance <= step_distance or distance < 0.05:
            old_x = agv_x
            old_y = agv_y

            agv_x = target_x
            agv_y = target_y

            # Luu vi tri moi
            moved_distance = math.sqrt(
                (agv_x - old_x)**2 + (agv_y - old_y)**2
            )

            if moved_distance > 0:
                path_x.append(agv_x)
                path_y.append(agv_y)

                #Tinh quang duong AGV vua di duoc
                total_distance += moved_distance
                elapsed_time += moved_distance / speed

                direction_x = agv_x - old_x
                direction_y = agv_y - old_y

                direction_length = math.sqrt(
                    direction_x**2 + direction_y**2
                )

                last_direction = (
                    direction_x / direction_length,
                    direction_y / direction_length
                )

            print(f"Da den waypoint: {current_target}")

            current_target_index += 1

            if current_target_index < len(waypoints):
                current_target = waypoints[current_target_index]
            else:
                mission_completed = True
                message = "Da hoan thanh hanh trinh"

                print("\nAGV da hoan thanh hanh trinh!")
                print(f"Tong quang duong: {total_distance:.2f} m")
                print(f"Thoi gian di chuyen: {elapsed_time:.2f} s")

        else:
            # Quang duong di duoc trong mot buoc
            old_x = agv_x
            old_y = agv_y

            # Cap nhat vi tri AGV
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
        f"Destination: ({current_target[0]:.2f}, "
        f"{current_target[1]:.2f}) m\n"
        f"Speed: {speed:.1f} m/s\n"
        f"Total Distance: {total_distance:.2f} m\n"
        f"Elapsed Time: {elapsed_time:.1f} s\n"
        f"Message: {message}"
    )

    return (
        path_line,
        agv_arrow,
        status_text,
        destination_marker,
        waypoint_scatter
    )


# Xu ly su kien ban phim
def on_key_press(event):
    global is_paused, speed, message

    if event.key in (" ", "space"):
        if is_paused:
            is_paused = False
            ani.event_source.start()
            message = "Tiep tuc mo phong AGV"
            print("Tiep tuc mo phong AGV")
        else:
            is_paused = True
            ani.event_source.stop()
            message = "Da tam dung mo phong"
            update(0)
            fig.canvas.draw_idle()
            print("Da tam dung mo phong AGV")

    elif event.key in ("+", "="):
        speed = min(1.5, round(speed + 0.1, 2))
        message = f"Tang toc do: {speed:.1f} m/s"
        update(0)
        fig.canvas.draw_idle()
        print(message)

    elif event.key == "-":
        speed = max(0.1, round(speed - 0.1, 2))
        message = f"Giam toc do: {speed:.1f} m/s"
        update(0)
        fig.canvas.draw_idle()
        print(message)

    elif event.key == "r":
        reset_simulation()


# Xu ly su kien chuot
def on_mouse_click(event):
    global current_target
    global current_target_index
    global waypoints
    global mission_completed
    global message

    # Chi chon diem dich khi AGV dang tam dung
    if not is_paused:
        return

    if event.inaxes != ax:
        return

    if event.xdata is None or event.ydata is None:
        return

    # Cap nhat diem dich moi
    new_target = (float(event.xdata), float(event.ydata))

    is_valid, reason = kiem_tra_diem_dich(
        new_target[0],
        new_target[1]
    )

    if not is_valid:
        message = reason
        print(f"Khong the chon diem dich: {reason}")
        update(0)
        fig.canvas.draw_idle()
        return

    current_target = new_target
    waypoints = [new_target]
    current_target_index = 0
    mission_completed = False
    message = "Da cap nhat diem dich"

    destination_marker.set_offsets([new_target])
    waypoint_scatter.set_offsets([new_target])

    print(
        f"Da chon diem dich moi: "
        f"({new_target[0]:.2f}, {new_target[1]:.2f})"
    )

    update(0)
    fig.canvas.draw_idle()


# Dat lai mo phong ve trang thai ban dau
def reset_simulation():
    global agv_x, agv_y
    global path_x, path_y
    global total_distance, elapsed_time
    global waypoints, current_target
    global current_target_index, mission_completed
    global is_paused, last_direction
    global speed, message

    ani.event_source.stop()

    agv_x = 0.0
    agv_y = 0.0

    path_x = [agv_x]
    path_y = [agv_y]

    total_distance = 0.0
    elapsed_time = 0.0

    waypoints = default_waypoints.copy()
    current_target_index = 0
    current_target = waypoints[0]

    mission_completed = False
    is_paused = True
    last_direction = (1.0, 0.0)
    speed = default_speed

    message = "Da reset, nhan SPACE de chay lai"

    destination_marker.set_offsets([current_target])
    waypoint_scatter.set_offsets(waypoints)

    update(0)
    fig.canvas.draw_idle()

    print("Da reset mo phong AGV")


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
