import math
import heapq
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import FancyArrowPatch, Rectangle

# Vi tri ban dau cua AGV
agv_x = 1.0
agv_y = 1.0

path_x = [agv_x]
path_y = [agv_y]

total_distance = 0.0
elapsed_time = 0.0

# Thong so mo phong
default_speed = 0.5
speed = default_speed
time_step = 0.1

# Gioi han ban do
x_min = 0.0
x_max = 10.0
y_min = 0.0
y_max = 7.0

# Cac vung cam tren ban do
no_go_zones = [
    (3.0, 1.0, 1.2, 3.5),
    (5.5, 3.5, 1.0, 2.5),
    (7.5, 0.5, 1.0, 2.5)
]

robot_radius = 0.2
safety_margin = 0.1
grid_size = 0.25

default_target = (9.0, 6.0)
current_target = default_target

is_paused = True
mission_completed = False
last_direction = (1.0, 0.0)
message = "Nhan SPACE de bat dau"

planned_path = []
route_index = 1

print("Bat dau mo phong AGV")
print(f"Vi tri ban dau: ({agv_x}, {agv_y})")


# mo rong vung cam theo kich thuoc AGV
def get_inflated_zones():
    zones = []
    margin = robot_radius + safety_margin

    for x, y, width, height in no_go_zones:
        zones.append((
            x - margin,
            y - margin,
            width + 2 * margin,
            height + 2 * margin
        ))

    return zones


inflated_zones = get_inflated_zones()


# Kiem tra mot diem co nam trong vung cam khong
def diem_trong_vung_cam(x, y, zone):
    zone_x, zone_y, width, height = zone

    return (
        zone_x <= x <= zone_x + width
        and zone_y <= y <= zone_y + height
    )


# Kiem tra diem co nam trong ban do va vung di duoc khong
def vi_tri_hop_le(x, y):
    margin = robot_radius + safety_margin

    if not (
        x_min + margin <= x <= x_max - margin
        and y_min + margin <= y <= y_max - margin
    ):
        return False

    for zone in inflated_zones:
        if diem_trong_vung_cam(x, y, zone):
            return False

    return True


# doi toa do thanh o tren luoi
def toa_do_sang_o(x, y):
    col = round((x - x_min) / grid_size)
    row = round((y - y_min) / grid_size)
    return col, row


def o_sang_toa_do(cell):
    x = x_min + cell[0] * grid_size
    y = y_min + cell[1] * grid_size
    return x, y


# check o co nam trong ban do ko
def o_hop_le(cell):
    x, y = o_sang_toa_do(cell)
    return vi_tri_hop_le(x, y)


def heuristic(a, b):
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    return max(dx, dy) + (math.sqrt(2) - 1) * min(dx, dy)


# lay cac o xung quanh de tim duong
def lay_o_ke(cell):
    neighbors = [
        (-1, 0, 1), (1, 0, 1),
        (0, -1, 1), (0, 1, 1),
        (-1, -1, math.sqrt(2)), (-1, 1, math.sqrt(2)),
        (1, -1, math.sqrt(2)), (1, 1, math.sqrt(2))
    ]

    result = []

    for dx, dy, cost in neighbors:
        next_cell = (cell[0] + dx, cell[1] + dy)

        if not o_hop_le(next_cell):
            continue

        # tranh cat cheo qua goc vat can
        if dx != 0 and dy != 0:
            side_1 = (cell[0] + dx, cell[1])
            side_2 = (cell[0], cell[1] + dy)

            if not o_hop_le(side_1) or not o_hop_le(side_2):
                continue

        result.append((next_cell, cost))

    return result


# tim duong bang A*
def tim_duong(start, goal):
    open_list = []
    heapq.heappush(open_list, (0, start))

    came_from = {}
    g_score = {start: 0}
    closed_set = set()

    while open_list:
        _, current = heapq.heappop(open_list)

        if current in closed_set:
            continue

        if current == goal:
            route = [current]

            while current in came_from:
                current = came_from[current]
                route.append(current)

            route.reverse()
            return route

        closed_set.add(current)

        for neighbor, move_cost in lay_o_ke(current):
            new_cost = g_score[current] + move_cost

            if new_cost < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = new_cost
                priority = new_cost + heuristic(neighbor, goal)
                heapq.heappush(open_list, (priority, neighbor))

    return None


# lap hanh trinh moi tu vi tri hien tai
def lap_hanh_trinh(target):
    global planned_path, route_index
    global current_target, mission_completed, message

    if not vi_tri_hop_le(target[0], target[1]):
        message = "Diem dich khong hop le"
        return False

    start_cell = toa_do_sang_o(agv_x, agv_y)
    goal_cell = toa_do_sang_o(target[0], target[1])

    if not o_hop_le(start_cell) or not o_hop_le(goal_cell):
        message = "Khong the tao duong di"
        return False

    cells = tim_duong(start_cell, goal_cell)

    if cells is None:
        message = "Khong tim thay duong di"
        return False

    new_path = [o_sang_toa_do(cell) for cell in cells]

    # giu dung vi tri AGV tai dau hanh trinh
    new_path[0] = (agv_x, agv_y)
    new_path[-1] = target

    planned_path = new_path
    route_index = 1
    current_target = target
    mission_completed = len(planned_path) <= 1
    message = "Da tim thay duong di"

    return True


lap_hanh_trinh(default_target)

# Tao giao dien mo phong 2D
fig, ax = plt.subplots(figsize=(10, 7))

# Cau hinh khu vuc hien thi
ax.set_xlim(x_min - 0.3, x_max + 0.3)
ax.set_ylim(y_min - 0.3, y_max + 0.3)
ax.set_xlabel("X (m)")
ax.set_ylabel("Y (m)")
ax.set_title("AGV 2D Path Planning")
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

# hien thi khoang an toan quanh vung cam
for zone in inflated_zones:
    zone_x, zone_y, width, height = zone
    safe_zone = Rectangle(
        (zone_x, zone_y),
        width,
        height,
        fill=False,
        edgecolor="orange",
        linestyle="--",
        linewidth=1
    )
    ax.add_patch(safe_zone)

# Hien thi vi tri bat dau
ax.scatter(agv_x, agv_y, color="green", s=90, label="Start")

# ve duong di du kien va duong AGV da di
planned_line, = ax.plot([], [], "g--", linewidth=1.5, label="Planned Path")
path_line, = ax.plot([], [], "b-", linewidth=2, label="AGV Path")

agv_arrow = FancyArrowPatch(
    (agv_x, agv_y),
    (agv_x + 0.4, agv_y),
    arrowstyle="-|>",
    mutation_scale=18,
    color="orange",
    linewidth=3
)
ax.add_patch(agv_arrow)

destination_marker = ax.scatter(
    [current_target[0]],
    [current_target[1]],
    color="purple",
    marker="*",
    s=180,
    label="Destination"
)

status_text = ax.text(
    0.02,
    0.97,
    "",
    transform=ax.transAxes,
    verticalalignment="top",
    fontsize=9,
    bbox=dict(facecolor="white", alpha=0.8)
)

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


# cap nhat vi tri AGV theo tung buoc
def update(frame):
    global agv_x, agv_y, route_index
    global total_distance, elapsed_time
    global mission_completed, last_direction, message

    if not is_paused and not mission_completed:
        if route_index < len(planned_path):
            target_x, target_y = planned_path[route_index]

            dx = target_x - agv_x
            dy = target_y - agv_y
            distance = math.sqrt(dx**2 + dy**2)
            step_distance = speed * time_step

            if distance <= step_distance:
                new_x = target_x
                new_y = target_y
                route_index += 1
            else:
                new_x = agv_x + dx / distance * step_distance
                new_y = agv_y + dy / distance * step_distance

            moved_distance = math.sqrt(
                (new_x - agv_x)**2 + (new_y - agv_y)**2
            )

            if moved_distance > 0:
                last_direction = (
                    (new_x - agv_x) / moved_distance,
                    (new_y - agv_y) / moved_distance
                )

                agv_x = new_x
                agv_y = new_y
                path_x.append(agv_x)
                path_y.append(agv_y)

                total_distance += moved_distance
                elapsed_time += moved_distance / speed

            if route_index >= len(planned_path):
                mission_completed = True
                message = "Da hoan thanh hanh trinh"
                print("AGV da den dich")
                print(f"Tong quang duong: {total_distance:.2f} m")
                print(f"Thoi gian di chuyen: {elapsed_time:.2f} s")

    path_line.set_data(path_x, path_y)

    if planned_path:
        route_x = [point[0] for point in planned_path]
        route_y = [point[1] for point in planned_path]
        planned_line.set_data(route_x, route_y)

    arrow_length = 0.4
    agv_arrow.set_positions(
        (agv_x, agv_y),
        (
            agv_x + last_direction[0] * arrow_length,
            agv_y + last_direction[1] * arrow_length
        )
    )

    if mission_completed:
        status = "Hoan thanh"
    elif is_paused:
        status = "Tam dung"
    else:
        status = "Dang di chuyen"

    status_text.set_text(
        f"AGV Position: ({agv_x:.2f}, {agv_y:.2f}) m\n"
        f"Status: {status}\n"
        f"Destination: ({current_target[0]:.2f}, {current_target[1]:.2f}) m\n"
        f"Speed: {speed:.1f} m/s\n"
        f"Total Distance: {total_distance:.2f} m\n"
        f"Elapsed Time: {elapsed_time:.1f} s\n"
        f"Route points: {len(planned_path)}\n"
        f"Message: {message}"
    )

    return (
        planned_line,
        path_line,
        agv_arrow,
        status_text,
        destination_marker
    )


# Xu ly su kien ban phim
def on_key_press(event):
    global is_paused, speed, message

    if event.key in (" ", "space"):
        is_paused = not is_paused

        if is_paused:
            ani.event_source.stop()
            message = "Da tam dung mo phong"
            update(0)
            fig.canvas.draw_idle()
            print("Da tam dung mo phong AGV")
        else:
            message = "Tiep tuc mo phong AGV"
            ani.event_source.start()
            print("Tiep tuc mo phong AGV")

    elif event.key in ("+", "=", "plus"):
        speed = min(1.5, round(speed + 0.1, 2))
        message = f"Tang toc do: {speed:.1f} m/s"
        update(0)
        fig.canvas.draw_idle()

    elif event.key in ("-", "minus"):
        speed = max(0.1, round(speed - 0.1, 2))
        message = f"Giam toc do: {speed:.1f} m/s"
        update(0)
        fig.canvas.draw_idle()

    elif event.key in ("r", "R"):
        reset_simulation()


# Xu ly su kien chuot
def on_mouse_click(event):
    global message, is_paused

    if not is_paused:
        return

    if event.inaxes != ax:
        return

    if event.xdata is None or event.ydata is None:
        return

    new_target = (float(event.xdata), float(event.ydata))

    if not vi_tri_hop_le(new_target[0], new_target[1]):
        message = "Diem dich nam trong vung khong the di"
        print(message)
        update(0)
        fig.canvas.draw_idle()
        return

    if lap_hanh_trinh(new_target):
        destination_marker.set_offsets([new_target])
        message = "Da cap nhat diem dich"
        print(f"Da chon diem dich moi: ({new_target[0]:.2f}, {new_target[1]:.2f})")
    else:
        print(message)

    update(0)
    fig.canvas.draw_idle()


# Dat lai mo phong ve trang thai ban dau
def reset_simulation():
    global agv_x, agv_y, path_x, path_y
    global total_distance, elapsed_time
    global current_target, mission_completed
    global is_paused, last_direction, speed
    global message

    ani.event_source.stop()

    agv_x = 1.0
    agv_y = 1.0
    path_x = [agv_x]
    path_y = [agv_y]
    total_distance = 0.0
    elapsed_time = 0.0
    speed = default_speed
    last_direction = (1.0, 0.0)
    is_paused = True

    lap_hanh_trinh(default_target)
    current_target = default_target
    mission_completed = False
    message = "Da reset, nhan SPACE de chay lai"

    destination_marker.set_offsets([current_target])
    update(0)
    fig.canvas.draw_idle()

    print("Da reset mo phong AGV")


# Tao hoat anh
ani = FuncAnimation(
    fig,
    update,
    frames=None,
    interval=50,
    repeat=False,
    blit=False,
    cache_frame_data=False
)

# Lang nghe su kien ban phim va chuot
fig.canvas.mpl_connect("key_press_event", on_key_press)
fig.canvas.mpl_connect("button_press_event", on_mouse_click)

plt.show()
