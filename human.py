import tkinter as tk
from tkinter import simpledialog, messagebox
from difflib import get_close_matches

# Initial person settings
person = {
    'name': '',
    'energy': 100,
    'hunger': 0,
    'location': 'bedroom',
    'tasks': []
}

# Define the tasks available in different locations
tasks = {
    'bedroom': ['起床', '刷牙', '洗臉', '穿衣服', '整理床鋪', '做瑜伽', '冥想', '換床單', '打掃房間', '玩手機'],
    'kitchen': ['吃早餐', '喝咖啡', '吃午餐', '吃晚餐', '準備食材', '煮飯', '洗碗', '喝茶', '烤麵包', '喝牛奶'],
    'office': ['工作', '開會', '打電話', '發郵件', '寫報告', '讀文件', '喝水', '做筆記', '整理資料', '與同事聊天'],
    'living_room': ['看電視', '休息', '閱讀', '打掃', '玩遊戲', '練習樂器', '畫畫', '聽音樂', '種花', '與家人聊天'],
    'bathroom': ['洗澡', '如廁', '洗手', '洗臉', '刷牙', '擦乾', '洗衣服', '護膚', '換衣服', '整理浴室'],
    'outside': ['跑步', '散步', '購物', '拜訪朋友', '去公園', '騎自行車', '野餐', '遛狗', '打籃球', '爬山'],
    'gym': ['舉重', '跑步機', '瑜伽', '跳繩', '拉伸', '騎動感單車', '健身操', '做俯卧撑', '打拳擊', '做引體向上'],
    'library': ['借書', '還書', '讀書', '做筆記', '上網', '查資料', '安靜休息', '參加讀書會', '寫作', '與朋友學習'],
    'cafe': ['喝咖啡', '吃點心', '閱讀', '寫作', '與朋友聊天', '上網', '放鬆', '聽音樂', '觀察人群', '做筆記'],
    'park': ['散步', '跑步', '野餐', '遛狗', '拍照', '打籃球', '騎自行車', '放風箏', '做瑜伽', '與朋友聊天']
}

# Define possible stories based on combinations of actions
stories = {
    ('起床', '刷牙', '吃早餐'): "你開始了一個充滿活力的一天。",
    ('工作', '開會', '喝咖啡'): "你在工作中度過了一個忙碌的上午。",
    ('看電視', '休息', '吃晚餐'): "你度過了一個悠閒的晚上。",
    ('跑步', '洗澡', '吃午餐'): "你保持了健康的生活方式。",
    ('閱讀', '喝咖啡', '寫作'): "你在咖啡廳度過了一個富有創造力的下午。",
    # More combinations can be added here
}

# Define individual action stories
action_stories = {
    '起床': "你醒來了，開始新的一天。",
    '刷牙': "你刷了牙，口氣清新。",
    '洗臉': "你洗了臉，感覺精神抖擻。",
    '穿衣服': "你穿好了衣服，準備開始一天的活動。",
    '整理床鋪': "你整理了床鋪，房間看起來更整潔了。",
    '做瑜伽': "你做了一些瑜伽，感覺身心舒暢。",
    '冥想': "你冥想了片刻，感覺平靜。",
    '換床單': "你換了床單，床鋪變得乾淨舒適。",
    '打掃房間': "你打掃了房間，整個房間焕然一新。",
    '玩手機': "你玩了會手機，放鬆了一下。",
    '吃早餐': "你吃了早餐，補充了能量。",
    '喝咖啡': "你喝了一杯咖啡，提神醒腦。",
    '吃午餐': "你吃了午餐，感覺飽滿。",
    '吃晚餐': "你吃了晚餐，感覺滿足。",
    '準備食材': "你準備好了食材，開始做飯。",
    '煮飯': "你煮了一頓美味的飯菜。",
    '洗碗': "你洗了碗，廚房變得乾淨了。",
    '喝茶': "你喝了一杯茶，感覺很放鬆。",
    '烤麵包': "你烤了一片香噴噴的麵包。",
    '喝牛奶': "你喝了一杯牛奶，補充了營養。",
    '工作': "你開始了一天的工作。",
    '開會': "你參加了一個會議，討論了很多重要的事情。",
    '打電話': "你打了一個電話，解決了一些工作上的問題。",
    '發郵件': "你發了幾封郵件，處理了日常的工作。",
    '寫報告': "你寫了一份報告，總結了最近的工作成果。",
    '讀文件': "你讀了一些文件，獲取了重要的信息。",
    '喝水': "你喝了一杯水，補充了水分。",
    '做筆記': "你做了一些筆記，記錄了重要的信息。",
    '整理資料': "你整理了資料，工作變得更有條理。",
    '與同事聊天': "你和同事聊了聊，放鬆了一下。",
    '看電視': "你看了一會電視，放鬆了心情。",
    '休息': "你休息了一會，恢復了體力。",
    '閱讀': "你讀了一本書，獲取了新的知識。",
    '打掃': "你打掃了客廳，房間變得乾淨了。",
    '玩遊戲': "你玩了一會遊戲，感覺很開心。",
    '練習樂器': "你練習了樂器，提高了技巧。",
    '畫畫': "你畫了一幅畫，感覺很有成就感。",
    '聽音樂': "你聽了一些音樂，感覺很放鬆。",
    '種花': "你給花澆了水，花園變得更美麗了。",
    '與家人聊天': "你和家人聊了聊，增進了感情。",
    '洗澡': "你洗了個澡，感覺很清爽。",
    '如廁': "你去了一趟廁所，解決了生理問題。",
    '洗手': "你洗了手，保持了清潔。",
    '擦乾': "你擦乾了自己，感覺很舒服。",
    '洗衣服': "你洗了衣服，衣服變得乾淨了。",
    '護膚': "你做了護膚，感覺皮膚變得更好了。",
    '換衣服': "你換了衣服，感覺更舒適。",
    '整理浴室': "你整理了浴室，變得更加乾淨了。",
    '跑步': "你跑了一段路，感覺身體很健康。",
    '散步': "你散了一會步，感覺很放鬆。",
    '購物': "你購物了一些東西，感覺很滿足。",
    '拜訪朋友': "你拜訪了朋友，增進了感情。",
    '去公園': "你去了公園，享受了大自然。",
    '騎自行車': "你騎了一段自行車，感覺很開心。",
    '野餐': "你在公園裡野餐，享受了美食。",
    '遛狗': "你遛了狗，狗狗也很開心。",
    '打籃球': "你打了一會籃球，感覺很運動。",
    '爬山': "你爬了一座山，享受了美景。",
    '舉重': "你舉了一些重物，鍛鍊了肌肉。",
    '跑步機': "你在跑步機上跑了一段，感覺很累。",
    '瑜伽': "你做了一些瑜伽，放鬆了身心。",
    '跳繩': "你跳了一會繩，鍛鍊了體能。",
    '拉伸': "你做了一些拉伸，感覺很舒服。",
    '騎動感單車': "你騎了一段動感單車，感覺很累。",
    '健身操': "你做了一些健身操，感覺很有活力。",
    '做俯卧撑': "你做了一些俯卧撑，鍛鍊了上肢力量。",
    '打拳擊': "你打了一會拳擊，發洩了壓力。",
    '做引體向上': "你做了一些引體向上，鍛鍊了背部肌肉。",
    '借書': "你借了一本書，準備閱讀。",
    '還書': "你還了一本書，感覺很有責任心。",
    '讀書': "你讀了一本書，獲取了新的知識。",
    '做筆記': "你做了一些筆記，記錄了重要的信息。",
    '上網': "你上網查了一些資料，獲取了新的信息。",
    '查資料': "你查了一些資料，幫助了工作。",
    '安靜休息': "你在圖書館安靜地休息了一會。",
    '參加讀書會': "你參加了一個讀書會，交流了讀書心得。",
    '寫作': "你寫了一些文章，感覺很有成就感。",
    '與朋友學習': "你和朋友一起學習，感覺很充實。",
    '喝咖啡': "你喝了一杯咖啡，提神醒腦。",
    '吃點心': "你吃了一些點心，感覺很滿足。",
    '閱讀': "你讀了一本書，獲取了新的知識。",
    '寫作': "你寫了一些文章，感覺很有成就感。",
    '與朋友聊天': "你和朋友聊了聊，增進了感情。",
    '上網': "你上網查了一些資料，獲取了新的信息。",
    '放鬆': "你放鬆了一會，感覺很舒服。",
    '聽音樂': "你聽了一些音樂，感覺很放鬆。",
    '觀察人群': "你觀察了一下周圍的人群，感覺很有趣。",
    '做筆記': "你做了一些筆記，記錄了重要的信息。",
    '散步': "你散了一會步，感覺很放鬆。",
    '跑步': "你跑了一段路，感覺身體很健康。",
    '野餐': "你在公園裡野餐，享受了美食。",
    '遛狗': "你遛了狗，狗狗也很開心。",
    '拍照': "你拍了一些照片，紀錄了美好時刻。",
    '打籃球': "你打了一會籃球，感覺很運動。",
    '騎自行車': "你騎了一段自行車，感覺很開心。",
    '放風箏': "你放了一個風箏，享受了戶外的樂趣。",
    '做瑜伽': "你做了一些瑜伽，放鬆了身心。",
    '與朋友聊天': "你和朋友聊了聊，增進了感情。"
}

# Function to display current status
def show_status():
    status_text = f"目前狀態: 名字: {person['name']}, 能量: {person['energy']}, 飢餓: {person['hunger']}, 位置: {person['location']}"
    status_label.config(text=status_text)

# Function to handle tasks
def handle_task(task):
    if task in tasks[person['location']]:
        story = action_stories.get(task, "你完成了這個動作。")
        messagebox.showinfo("結果", f"你選擇了{task}: {story}")
        
        # Update status based on task
        if task in ['起床', '刷牙', '洗臉', '穿衣服', '整理床鋪', '做瑜伽', '冥想', '換床單', '打掃房間', '玩手機']:
            person['energy'] += 5
        elif task in ['吃早餐', '吃午餐', '吃晚餐']:
            person['hunger'] -= 20
        elif task in ['工作', '開會', '打電話', '發郵件']:
            person['energy'] -= 10
        elif task in ['看電視', '休息', '閱讀']:
            person['energy'] += 10
        elif task在 ['洗澡', '如廁', '洗手']:
            person['energy'] += 5
        elif task in ['跑步', '散步', '購物', '拜訪朋友']:
            person['energy'] -= 15
            person['hunger'] += 10

        person['tasks'].append(task)
        check_story()

    else:
        messagebox.showinfo("無效動作", "這個動作在當前位置不可用。")
    
    update_tasks()
    show_status()

# Function to check if a specific story is triggered
def check_story():
    for key, story in stories.items():
        if all(task in person['tasks'] for task in key):
            messagebox.showinfo("故事情節", story)
            person['tasks'] = []  # Reset tasks after story is shown

# Function to update the task buttons based on the current location
def update_tasks():
    for widget in task_buttons_frame.winfo_children():
        widget.destroy()
    
    num_tasks = len(tasks[person['location']])
    num_columns = 3  # Define number of columns
    num_rows = (num_tasks + num_columns - 1) // num_columns  # Calculate number of rows needed

    for idx, task in enumerate(tasks[person['location']]):
        btn = tk.Button(task_buttons_frame, text=task, command=lambda t=task: handle_task(t))
        btn.grid(row=idx // num_columns, column=idx % num_columns, sticky="nsew")

    # Make the buttons fill the frame
    for row in range(num_rows):
        task_buttons_frame.grid_rowconfigure(row, weight=1)
    for col in range(num_columns):
        task_buttons_frame.grid_columnconfigure(col, weight=1)

# Function to start the simulation
def start_simulation():
    person['name'] = simpledialog.askstring("名字", "你的名字是?")
    if person['name']:
        welcome_label.config(text=f"歡迎 {person['name']} 開始你的一天!")
        show_status()
        update_tasks()
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
