import tkinter as tk
from tkinter import simpledialog, messagebox
from difflib import get_close_matches

# Initial person settings
person = {
    'name': '',
    'energy': 100,
    'hunger': 0,
    'location': '',
    'tasks': []
}

# Define the tasks available in different locations
tasks = {}
action_stories = {}
action_energy = {}

# Function to load tasks and stories from a file
def load_tasks_from_file(filename):
    global tasks, action_stories, action_energy
    tasks = {}
    action_stories = {}
    action_energy = {}
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            location, actions = line.strip().split(':', 1)
            task_list = []
            for action_story in actions.split(','):
                action, story, energy = action_story.strip().split(':', 2)
                task_list.append(action.strip())
                action_stories[action.strip()] = story.strip()
                action_energy[action.strip()] = int(energy.strip())
            tasks[location.strip()] = task_list

# Load tasks from tasks.txt
load_tasks_from_file('tasks.txt')

# Function to display current status
def show_status():
    status_text = f"目前狀態: 名字: {person['name']}, 能量: {person['energy']}, 飢餓: {person['hunger']}, 位置: {person['location']}"
    status_label.config(text=status_text)

# Function to handle tasks
def handle_task(task):
    if task in tasks[person['location']]:
        story = action_stories.get(task, "你完成了這個動作。")
        energy_change = action_energy.get(task, 0)
        person['energy'] += energy_change
        messagebox.showinfo("結果", f"你選擇了{task}: {story}\n能量變化: {energy_change}")
        
        person['tasks'].append(task)
        check_story()

    else:
        messagebox.showinfo("無效動作", "這個動作在當前位置不可用。")
    
    update_tasks()
    show_status()

# Function to check if a specific story is triggered
def check_story():
    # Add story checking logic here if needed
    pass

# Function to update the task buttons based on the current location
def update_tasks():
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    num_tasks = len(tasks[person['location']])
    num_columns = 3  # Define number of columns
    num_rows = (num_tasks + num_columns - 1) // num_columns  # Calculate number of rows needed

    for idx, task in enumerate(tasks[person['location']]):
        btn = tk.Button(scrollable_frame, text=task, command=lambda t=task: handle_task(t))
        btn.grid(row=idx // num_columns, column=idx % num_columns, sticky="nsew")

    leave_btn = tk.Button(scrollable_frame, text="離開房間", command=leave_room)
    leave_btn.grid(row=num_rows, column=0, columnspan=num_columns, sticky="nsew")

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
    num_rows = (num_rooms + num_columns - 1) // num_columns  # Calculate number of rows needed

    for idx, room in enumerate(tasks.keys()):
        btn = tk.Button(scrollable_frame, text=room, command=lambda r=room: select_room(r))
        btn.grid(row=idx // num_columns, column=idx % num_columns, sticky="nsew")

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
        close_matches = get_close_matches(query, [task for loc_tasks in tasks.values() for task in loc_tasks], n=5, cutoff=0.1)
        if close_matches:
            result = tk.Toplevel(root)
            result.title("搜索結果")
            result.geometry("300x200")
            result_label = tk.Label(result, text="選擇一個動作:")
            result_label.pack(pady=10)
            for match in close_matches:
                btn = tk.Button(result, text=match, command=lambda m=match: [handle_task(m), result.destroy()])
                btn.pack(fill=tk.X, padx=10, pady=2)
        else:
            messagebox.showinfo("搜索結果", "未找到相近的選項。")

# Initialize the main window
root = tk.Tk()
root.title("人模擬器")
root.geometry("800x600")  # Set window size

welcome_label = tk.Label(root, text="歡迎來到人模擬器!", font=("Arial", 18))
welcome_label.pack(pady=10)

status_label = tk.Label(root, text="", font=("Arial", 14))
status_label.pack(pady=10)

task_buttons_frame = tk.Frame(root)
task_buttons_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

# Add a scrollbar for the task buttons frame
canvas = tk.Canvas(task_buttons_frame)
scrollbar = tk.Scrollbar(task_buttons_frame, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas)

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

search_frame = tk.Frame(root)
search_frame.pack(pady=10)
search_label = tk.Label(search_frame, text="搜索任務:")
search_label.pack(side=tk.LEFT)
search_entry = tk.Entry(search_frame)
search_entry.pack(side=tk.LEFT, padx=5)
search_button = tk.Button(search_frame, text="搜索", command=search_tasks)
search_button.pack(side=tk.LEFT)
search_entry.bind("<Return>", search_tasks)

start_simulation()

root.mainloop()
