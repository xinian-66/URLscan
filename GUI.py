import requests
import random
import tkinter as tk
from tkinter import simpledialog, messagebox

def get_user_agents():
    with open("ua.conf", "r") as ua_file:
        return [line.strip() for line in ua_file]

def get_paths():
    with open("paths.conf", "r") as paths_file:
        return [line.strip() for line in paths_file]

def process_url(url, user_agents):
    user_agent = random.choice(user_agents)
    try:
        headers = {"User-Agent": user_agent}
        response = requests.get(url, headers=headers)
        status_code = response.status_code
        result_text.insert(tk.END, f"{url} (User-Agent: {user_agent}): {status_code}\n")
    except requests.exceptions.RequestException as e:
        result_text.insert(tk.END, f"{url} (User-Agent: {user_agent}): 请求失败 ({e})\n")

def run_task():
    base_url = base_url_entry.get()
    parsed_url = urlparse(base_url)
    if not parsed_url.scheme:
        base_url = "http://" + base_url
    elif not parsed_url.netloc:
        messagebox.showerror("错误", "无效的URL。")
        return

    if not base_url.endswith("/"):
        base_url += "/"

    user_agents = get_user_agents()
    paths = get_paths()
    concurrent_method = concurrent_method_var.get()

    result_text.delete(1.0, tk.END)

    if concurrent_method == 'p':
        num_processes = int(num_workers_entry.get())
        with multiprocessing.Pool(processes=num_processes) as pool:
            pool.starmap(process_url, [(base_url + path, user_agents) for path in paths])
    elif concurrent_method == 't':
        num_threads = int(num_workers_entry.get())
        for path in paths:
            app.after(0, process_url, base_url + path, user_agents)
    else:
        messagebox.showerror("错误", "无效选择。")

app = tk.Tk()
app.title("Web扫描工具")

base_url_label = tk.Label(app, text="站点URL：")
base_url_label.grid(row=0, column=0, sticky="w")
base_url_entry = tk.Entry(app)
base_url_entry.grid(row=0, column=1)

num_workers_label = tk.Label(app, text="并发数量：")
num_workers_label.grid(row=1, column=0, sticky="w")
num_workers_entry = tk.Entry(app)
num_workers_entry.grid(row=1, column=1)

concurrent_method_var = tk.StringVar()
concurrent_method_label = tk.Label(app, text="并发处理方式：")
concurrent_method_label.grid(row=2, column=0, sticky="w")
concurrent_method_radio_p = tk.Radiobutton(app, text="多进程", variable=concurrent_method_var, value="p")
concurrent_method_radio_p.grid(row=2, column=1, sticky="w")
concurrent_method_radio_t = tk.Radiobutton(app, text="多线程", variable=concurrent_method_var, value="t")
concurrent_method_radio_t.grid(row=2, column=1, sticky="e")

run_button = tk.Button(app, text="运行", command=run_task)
run_button.grid(row=3, column=0, columnspan=2)

result_text = tk.Text(app, height=10, width=50)
result_text.grid(row=4, column=0, columnspan=2)

app.mainloop()
