import requests
import multiprocessing
import threading
from urllib.parse import urlparse

def get_user_agents():
    with open("ua.conf", "r") as ua_file:
        return [line.strip() for line in ua_file]

def get_paths():
    with open("paths.conf", "r") as paths_file:
        return [line.strip() for line in paths_file]

def choose_user_agent(user_agents):
    print("请选择一个用户代理：")
    for i, ua in enumerate(user_agents, 1):
        print(f"{i}. {ua}")

    choice = input("输入选项编号：")
    try:
        choice_index = int(choice) - 1
        if 0 <= choice_index < len(user_agents):
            return user_agents[choice_index]
        else:
            print("选择无效，请重新输入。")
            return choose_user_agent(user_agents)
    except ValueError:
        print("输入无效，请输入一个数字。")
        return choose_user_agent(user_agents)

def process_url(url, user_agent):
    try:
        headers = {"User-Agent": user_agent}
        response = requests.get(url, headers=headers)
        status_code = response.status_code
        print(f"{url} (User-Agent: {user_agent}): {status_code}")
    except requests.exceptions.RequestException as e:
        print(f"{url} (User-Agent: {user_agent}): 请求失败 ({e})")

def main():
    base_url = input("请输入站点URL: ")
    parsed_url = urlparse(base_url)
    if not parsed_url.scheme:
        base_url = "http://" + base_url
    elif not parsed_url.netloc:
        print("无效的URL。")
        return

    if not base_url.endswith("/"):
        base_url += "/"

    user_agents = get_user_agents()
    paths = get_paths()
    selected_user_agent = choose_user_agent(user_agents)
    concurrent_method = input("请选择并发处理方式 (p=多进程, t=多线程): ")

    if concurrent_method.lower() == 'p':
        num_processes = int(input("请输入进程数量："))
        with multiprocessing.Pool(processes=num_processes) as pool:
            pool.starmap(process_url, [(base_url + path, selected_user_agent) for path in paths])
    elif concurrent_method.lower() == 't':
        num_threads = int(input("请输入线程数量："))
        threads = []
        for path in paths:
            thread = threading.Thread(target=process_url, args=(base_url + path, selected_user_agent))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()
    else:
        print("无效选择。")
        return

if __name__ == "__main__":
    main()
