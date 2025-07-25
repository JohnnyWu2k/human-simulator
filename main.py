import json
import tkinter as tk
from tkinter import simpledialog, messagebox
from difflib import get_close_matches
import socket
import threading


def start_server(host='0.0.0.0', port=5000):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen()
    clients = []

    def broadcast(msg, exclude=None):
        for client in clients:
            if client is not exclude:
                try:
                    client.sendall(msg)
                except OSError:
                    pass

    def handle_client(conn, addr):
        with conn:
            clients.append(conn)
            try:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    broadcast(data, exclude=conn)
            finally:
                clients.remove(conn)

    def _accept_loop():
        while True:
            conn, addr = server.accept()
            threading.Thread(
                target=handle_client,
                args=(conn, addr),
                daemon=True,
            ).start()

    threading.Thread(target=_accept_loop, daemon=True).start()

    return server


def connect(host='localhost', port=5000, on_message=None):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    def listen():
        while True:
            data = client.recv(1024)
            if not data:
                break
            if on_message:
                on_message(data.decode('utf-8'))

    threading.Thread(target=listen, daemon=True).start()
    return client


# Initial person settings
person = {
    'name': '',
    'energy': 100,
    'hunger': 0,
    'sleep': 100,
    'mood': 50,
    'hygiene': 100,
    'social': 50,
    'location': '',
    'tasks': []
}

# Define the tasks available in different locations
tasks = {}
action_stories = {}
action_energy = {}
action_hunger = {}
action_sleep = {}
action_mood = {}
action_hygiene = {}
action_social = {}
combo_stories = {
    ("起床", "刷牙", "吃早餐"): "你開始了一個充滿活力的一天。",
    ("跑步", "洗臉", "喝咖啡"): "你保持了健康的生活方式。",
}

# Drag-and-drop support
drag_data = {"widget": None, "x": 0, "y": 0}


def drag_start(event):
    widget = event.widget
    drag_data["widget"] = widget
    drag_data["x"] = event.x
    drag_data["y"] = event.y
    widget.orig_row = widget.grid_info().get("row", 0)
    widget.orig_col = widget.grid_info().get("column", 0)
    widget.lift()
    widget.place(in_=scrollable_frame, x=widget.winfo_x(), y=widget.winfo_y())


def drag_motion(event):
    widget = drag_data.get("widget")
    if widget:
        x = widget.winfo_x() + event.x - drag_data["x"]
        y = widget.winfo_y() + event.y - drag_data["y"]
        widget.place(x=x, y=y)


def drag_stop(event):
    widget = drag_data.get("widget")
    if widget:
        if root.winfo_containing(event.x_root, event.y_root) == drop_area:
            handle_task(widget["text"], widget)
        widget.place_forget()
        widget.grid(row=widget.orig_row, column=widget.orig_col, sticky="nsew")
        drag_data["widget"] = None


# Basic button style for a cooler look
BUTTON_STYLE = {
    "bg": "#444",
    "fg": "white",
    "activebackground": "#666",
    "font": ("Arial", 12),
}


# Function to load tasks and stories from a file
def load_tasks_from_file(filename):
    global tasks, action_stories, action_energy, action_hunger
    global action_sleep, action_mood, action_hygiene, action_social
    tasks = {}
    action_stories = {}
    action_energy = {}
    action_hunger = {}
    action_sleep = {}
    action_mood = {}
    action_hygiene = {}
    action_social = {}
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for location, actions in data.items():
        tasks[location] = []
        for action, info in actions.items():
            tasks[location].append(action)
            action_stories[action] = info.get('story', '')
            action_energy[action] = info.get('energy', 0)
            action_hunger[action] = info.get('hunger', 0)
            action_sleep[action] = info.get('sleep', 0)
            action_mood[action] = info.get('mood', 0)
            action_hygiene[action] = info.get('hygiene', 0)
            action_social[action] = info.get('social', 0)


# Load tasks from tasks.json
load_tasks_from_file('tasks.json')


def generate_extra_tasks(count=5000):
    """Generate additional tasks to reach the desired count."""
    verbs = [
        "閱讀",
        "撰寫",
        "整理",
        "研究",
        "清潔",
        "烹飪",
        "運動",
        "學習",
        "觀察",
        "修理",
    ]
    nouns = [
        "文件",
        "書籍",
        "報告",
        "設備",
        "房間",
        "電腦",
        "廚房",
        "浴室",
        "客廳",
        "花園",
    ]
    existing = sum(len(v) for v in tasks.values())
    extras_needed = max(0, count - existing)
    tasks["extra"] = []
    for i in range(extras_needed):
        verb = verbs[i % len(verbs)]
        noun = nouns[i % len(nouns)]
        action = f"{verb}{noun}{i+1}"
        tasks["extra"].append(action)
        action_stories[action] = f"你{verb}{noun}。"
        action_energy[action] = (i % 7) - 3
        action_hunger[action] = (i % 5) - 2
        action_sleep[action] = (i % 5) - 2
        action_mood[action] = (i % 7) - 3
        action_hygiene[action] = (i % 5) - 2
        action_social[action] = (i % 5) - 2


generate_extra_tasks(5000)


# Function to display current status
def show_status():
    status_text = (
        f"名字: {person['name']}\n"
        f"能量: {person['energy']}  飢餓: {person['hunger']}  "
        f"睡眠: {person['sleep']}\n"
        f"心情: {person['mood']}  衛生: {person['hygiene']}  "
        f"社交: {person['social']}\n"
        f"位置: {person['location']}"
    )
    status_label.config(text=status_text)

    if person['energy'] < 20:
        messagebox.showinfo("提醒", "你感到疲倦，需要休息。")
    if person['hunger'] > 80:
        messagebox.showinfo("提醒", "你非常餓，該去吃點東西了。")
    if person['sleep'] < 20:
        messagebox.showinfo("提醒", "你非常困倦，需要睡眠。")
    if person['hygiene'] < 20:
        messagebox.showinfo("提醒", "你需要洗澡了。")
    if person['mood'] < 20:
        messagebox.showinfo("提醒", "你的心情很差，做些讓自己開心的事吧。")
    if person['social'] < 20:
        messagebox.showinfo("提醒", "你感到孤單，與他人互動一下。")


# Function to handle tasks

def handle_task(task, button=None):
    if task == "打電話":
        open_phone()
        return

    if task in tasks[person['location']]:
        story = action_stories.get(task, "你完成了這個動作。")
        energy_change = action_energy.get(task, 0)
        hunger_change = action_hunger.get(task, 0)
        sleep_change = action_sleep.get(task, 0)
        mood_change = action_mood.get(task, 0)
        hygiene_change = action_hygiene.get(task, 0)
        social_change = action_social.get(task, 0)

        intensity = simpledialog.askinteger(
            "強度",
            "請輸入強度(1-3)",
            minvalue=1,
            maxvalue=3,
        )
        if intensity is None:
            intensity = 1
        if button is not None:
            orig = button.cget("bg")
            button.config(bg="#888")
            root.after(200, lambda: button.config(bg=orig))
        energy_change *= intensity
        hunger_change *= intensity
        sleep_change *= intensity
        mood_change *= intensity
        hygiene_change *= intensity
        social_change *= intensity

        person['energy'] += energy_change
        person['hunger'] += hunger_change
        person['sleep'] += sleep_change
        person['mood'] += mood_change
        person['hygiene'] += hygiene_change
        person['social'] += social_change
        messagebox.showinfo(
            "結果",
            (
                f"你選擇了{task}: {story}\n強度: {intensity}\n"
                f"能量變化: {energy_change}, 飢餓變化: {hunger_change}\n"
                f"睡眠變化: {sleep_change} 心情變化: {mood_change}\n"
                f"衛生變化: {hygiene_change} 社交變化: {social_change}"
            ),
        )

        person['tasks'].append(task)
        check_story()

    else:
        messagebox.showinfo("無效動作", "這個動作在當前位置不可用。")

    update_tasks()
    show_status()


# Function to check if a specific story is triggered
def check_story():
    for combo, story in combo_stories.items():
        if all(action in person['tasks'] for action in combo):
            messagebox.showinfo("故事情節", story)
            person['tasks'].clear()
            break


# Function to update the task buttons based on the current location
def update_tasks():
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    num_tasks = len(tasks[person['location']])
    num_columns = 3  # Define number of columns
    num_rows = (num_tasks + num_columns - 1) // num_columns
    # Calculate number of rows needed

    for idx, task in enumerate(tasks[person['location']]):
        btn = tk.Button(
            scrollable_frame,
            text=task,
            **BUTTON_STYLE,
        )
        btn.configure(command=lambda t=task, b=btn: handle_task(t, b))
        btn.grid(
            row=idx // num_columns,
            column=idx % num_columns,
            sticky="nsew",
        )
        btn.bind("<ButtonPress-1>", drag_start)
        btn.bind("<B1-Motion>", drag_motion)
        btn.bind("<ButtonRelease-1>", drag_stop)

    leave_btn = tk.Button(
        scrollable_frame,
        text="離開房間",
        command=leave_room,
        **BUTTON_STYLE,
    )
    leave_btn.grid(
        row=num_rows,
        column=0,
        columnspan=num_columns,
        sticky="nsew",
    )

    # Make the buttons fill the frame
    for row in range(num_rows + 1):
        scrollable_frame.grid_rowconfigure(row, weight=1)
    for col in range(num_columns):
        scrollable_frame.grid_columnconfigure(col, weight=1)


# Function to update room buttons based on tasks
def update_rooms():
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    num_rooms = len(tasks.keys())
    num_columns = 3  # Define number of columns
    num_rows = (num_rooms + num_columns - 1) // num_columns
    # Calculate number of rows needed

    for idx, room in enumerate(tasks.keys()):
        btn = tk.Button(
            scrollable_frame,
            text=room,
            command=lambda r=room: select_room(r),
            **BUTTON_STYLE,
        )
        btn.grid(
            row=idx // num_columns,
            column=idx % num_columns,
            sticky="nsew",
        )

    # Make the buttons fill the frame
    for row in range(num_rows):
        scrollable_frame.grid_rowconfigure(row, weight=1)
    for col in range(num_columns):
        scrollable_frame.grid_columnconfigure(col, weight=1)


def select_room(room):
    person['location'] = room
    update_tasks()
    show_status()


def leave_room():
    person['location'] = ''
    update_rooms()
    show_status()


network_server = None
network_client = None
phone_log = None


def host_game():
    global network_server
    if not network_server:
        network_server = start_server()
        messagebox.showinfo("網路", "已啟動主機，等待其他玩家連線")


def join_game():
    global network_client
    host = simpledialog.askstring("連線", "輸入主機位址", initialvalue="localhost")
    if host:
        network_client = connect(host, on_message=receive_message)
        messagebox.showinfo("網路", "已連線到主機")


def receive_message(msg):
    if phone_log:
        phone_log.configure(state="normal")
        phone_log.insert(tk.END, f"\n{msg}")
        phone_log.configure(state="disabled")


def open_phone():
    global phone_log
    phone = tk.Toplevel(root)
    phone.title("手機")
    phone.geometry("300x400")
    phone_log = tk.Text(phone, state="disabled")
    phone_log.pack(expand=True, fill=tk.BOTH)
    entry = tk.Entry(phone)
    entry.pack(fill=tk.X)

    def send():
        if network_client:
            msg = entry.get()
            if msg:
                network_client.sendall(msg.encode("utf-8"))
                entry.delete(0, tk.END)

    send_btn = tk.Button(phone, text="發送", command=send)
    send_btn.pack()


# Function to start the simulation
def start_simulation():
    person['name'] = simpledialog.askstring("名字", "你的名字是?")
    if person['name']:
        welcome_label.config(text=f"歡迎 {person['name']} 開始你的一天!")
        show_status()
        update_rooms()
    else:
        root.destroy()


# Function to search for tasks
def search_tasks(event=None):
    query = search_entry.get()
    if query:
        close_matches = get_close_matches(
            query,
            [task for loc_tasks in tasks.values() for task in loc_tasks],
            n=5,
            cutoff=0.1,
        )
        if close_matches:
            result = tk.Toplevel(root)
            result.title("搜索結果")
            result.geometry("300x200")
            result.configure(bg="#1e1e1e")
            result_label = tk.Label(
                result,
                text="選擇一個動作:",
                bg="#1e1e1e",
                fg="white",
            )
            result_label.pack(pady=10)
            for match in close_matches:
                btn = tk.Button(
                    result,
                    text=match,
                    command=lambda m=match: [handle_task(m), result.destroy()],
                    **BUTTON_STYLE,
                )
                btn.pack(fill=tk.X, padx=10, pady=2)
        else:
            messagebox.showinfo("搜索結果", "未找到相近的選項。")


def decay_stats():
    person['energy'] -= 1
    person['hunger'] += 1
    person['sleep'] -= 1
    person['mood'] -= 1
    person['hygiene'] -= 0.5
    person['social'] -= 0.5
    show_status()
    root.after(10000, decay_stats)


# Initialize the main window
root = tk.Tk()
root.title("人模擬器")
root.geometry("800x600")  # Set window size
root.configure(bg="#1e1e1e")

welcome_label = tk.Label(
    root,
    text="歡迎來到人模擬器!",
    font=("Arial", 18),
    bg="#1e1e1e",
    fg="white",
)
welcome_label.pack(pady=10)

status_label = tk.Label(
    root,
    text="",
    font=("Arial", 14),
    bg="#1e1e1e",
    fg="white",
)
status_label.pack(pady=10)

task_buttons_frame = tk.Frame(root, bg="#1e1e1e")
task_buttons_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

# Add a scrollbar for the task buttons frame
canvas = tk.Canvas(task_buttons_frame, bg="#1e1e1e", highlightthickness=0)
scrollbar = tk.Scrollbar(
    task_buttons_frame,
    orient="vertical",
    command=canvas.yview,
)
scrollable_frame = tk.Frame(canvas, bg="#1e1e1e")

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

search_frame = tk.Frame(root, bg="#1e1e1e")
search_frame.pack(pady=10)
search_label = tk.Label(search_frame, text="搜索任務:", bg="#1e1e1e", fg="white")
search_label.pack(side=tk.LEFT)
search_entry = tk.Entry(search_frame)
search_entry.pack(side=tk.LEFT, padx=5)
search_button = tk.Button(
    search_frame,
    text="搜索",
    command=search_tasks,
    **BUTTON_STYLE,
)
search_button.pack(side=tk.LEFT)
search_entry.bind("<Return>", search_tasks)

drop_area = tk.Label(root, text="拖到此處執行", bg="#333", fg="white", height=2)
drop_area.pack(fill=tk.X, pady=(0, 10))

menubar = tk.Menu(root)
network_menu = tk.Menu(menubar, tearoff=0)
network_menu.add_command(label="主機", command=host_game)
network_menu.add_command(label="連接", command=join_game)
menubar.add_cascade(label="網路", menu=network_menu)
root.config(menu=menubar)

start_simulation()
decay_stats()

root.mainloop()
