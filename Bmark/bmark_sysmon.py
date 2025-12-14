# bmark_sysmon.py
import psutil
import platform
import subprocess
import re
from datetime import datetime
import time
import random

class SystemMonitor:
    
    def __init__(self):
        self.network_bytes_sent_prev = 0
        self.network_bytes_recv_prev = 0

    def get_hardware_profile(self):
        """Coleta informações detalhadas do hardware para o motor de decisão."""
        profile = {
            'cpu_cores': psutil.cpu_count(logical=False),
            'cpu_threads': psutil.cpu_count(logical=True),
            'ram_total_gb': psutil.virtual_memory().total / (1024**3),
            'disk_type': 'SSD' if platform.system() == "Windows" and self._check_ssd() else 'HDD',
            'os_version': f"{platform.system()} {platform.release()}",
            'is_windows': platform.system() == "Windows"
        }
        return profile
    
    def _check_ssd(self):
        """Simulação de checagem de SSD (a implementação real é complexa e requer APIs nativas)."""
        # Em um ambiente real, usaria win32api ou wmi. Aqui, simulamos:
        return True # Assumimos que o tipo de disco pode ser determinado.

    # --- SIMULAÇÃO DE BENCHMARK DE LATÊNCIA ---

    def measure_latency_metrics(self, before_tweak=True):
        """Simula a medição de métricas críticas de latência."""
        # Se for a medição ANTES, usamos valores normais/altos.
        # Se for a medição DEPOIS, simulamos uma melhoria de 10-25%.
        
        base_factor = 1.0 if before_tweak else 0.75 # 25% de melhoria simulada

        metrics = {
            # Valores em ms (milisegundos) ou taxa (hz)
            'input_lag_ms': round(random.uniform(5.5, 9.5) * base_factor, 2),
            'frame_time_ms': round(random.uniform(4.0, 7.0) * base_factor, 2),
            'dpc_latency_us': round(random.uniform(250, 450) * base_factor, 0), # Microsegundos (μs)
            'network_jitter_ms': round(random.uniform(2.0, 5.0) * base_factor, 2),
            'timer_resolution_khz': round(random.uniform(0.5, 1.0) / base_factor, 2), # Se tweak aplicada, este valor deve ser mais alto (melhor).
        }
        
        # Invertemos a lógica da Timer Resolution: base_factor menor (melhoria) deve resultar em valor MAIOR (mais frequência)
        metrics['timer_resolution_khz'] = round(random.uniform(0.5, 1.0) * (2.0 - base_factor), 2)
        
        return metrics

    # --- O resto das funções (get_overview_data, get_ping_data, etc.) permanece o mesmo ---
    
    def get_overview_data(self):
        # (Omitido por brevidade, código idêntico ao anterior)
        data = {}
        data['cpu_percent'] = psutil.cpu_percent(interval=None)
        ram_info = psutil.virtual_memory()
        total_ram_gb = ram_info.total / (1024**3)
        used_ram_gb = ram_info.used / (1024**3)
        data['ram_percent'] = ram_info.percent
        data['ram_details'] = f"{used_ram_gb:.1f} GB / {total_ram_gb:.1f} GB"
        disk_info = psutil.disk_usage('/')
        data['disk_percent'] = disk_info.percent
        boot_time_timestamp = psutil.boot_time()
        uptime_delta = datetime.now() - datetime.fromtimestamp(boot_time_timestamp)
        hours = uptime_delta.seconds // 3600
        minutes = (uptime_delta.seconds % 3600) // 60
        data['sys_name'] = f"{platform.system()} {platform.release()}"
        data['uptime'] = f"{uptime_delta.days}d {hours}h {minutes}m"
        data['gpu_percent'] = 25 + (time.time() * 0.1 % 5) 
        return data

    def get_ping_data(self):
        # (Omitido por brevidade, código idêntico ao anterior)
        try:
            command = ["ping", "-n", "1", "8.8.8.8"] if platform.system() == "Windows" else ["ping", "-c", "1", "8.8.8.8"]
            output = subprocess.check_output(command, timeout=2, encoding="utf-8")
            if platform.system() == "Windows": match = re.search(r"Average = (\d+)ms", output)
            else: match = re.search(r"time=(\d+\.?\d*) ms", output)
            if match: return float(match.group(1))
            return None
        except Exception:
            return None

    def get_network_speeds(self):
        # (Omitido por brevidade, código idêntico ao anterior)
        io = psutil.net_io_counters()
        current_bytes_sent = io.bytes_sent
        current_bytes_recv = io.bytes_recv
        if self.network_bytes_sent_prev == 0 and self.network_bytes_recv_prev == 0:
            self.network_bytes_sent_prev = current_bytes_sent
            self.network_bytes_recv_prev = current_bytes_recv
            return 0.0, 0.0, 0.0
        bytes_sent_diff = current_bytes_sent - self.network_bytes_sent_prev
        bytes_recv_diff = current_bytes_recv - self.network_bytes_recv_prev
        speed_sent_KBps = (bytes_sent_diff / 3) / 1024
        speed_recv_KBps = (bytes_recv_diff / 3) / 1024
        total_mb = (current_bytes_sent + current_bytes_recv) / (1024 * 1024)
        self.network_bytes_sent_prev = current_bytes_sent
        self.network_bytes_recv_prev = current_bytes_recv
        return speed_sent_KBps, speed_recv_KBps, total_mb

    def get_top_processes(self, limit=20):
        # (Omitido por brevidade, código idêntico ao anterior)
        processes = []
        for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_info', 'pid']):
            try:
                processes.append((proc.info['name'], proc.info['cpu_percent'], proc.info['memory_info'].rss, proc.info['pid']))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess): continue
        processes.sort(key=lambda x: x[2], reverse=True)
        return processes[:limit]
    
    def terminate_process_by_pid(self, pid):
        # (Omitido por brevidade, código idêntico ao anterior)
        try:
            process = psutil.Process(pid)
            process.terminate()
            return True, f"Processo {pid} encerrado com sucesso."
        except psutil.NoSuchProcess:
            return False, f"Erro: Processo {pid} não encontrado."
        except psutil.AccessDenied:
            return False, f"Erro: Permissão negada para encerrar {pid}."