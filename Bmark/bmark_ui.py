# bmark_ui.py
import customtkinter as ctk
import threading
import time
import os
import json 
import platform 

from bmark_sysmon import SystemMonitor
from bmark_tweaks import SystemTweaks, WARNING_COLOR, SUCCESS_COLOR, SNAPSHOT_FILE

# --- CONFIGURAÇÃO DE TEMA ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

PRIMARY_COLOR_LIGHT = "#3498db"      
PRIMARY_COLOR_DARK = "#2980b9"      
TEXT_COLOR = "#ecf0f1"              
BACKGROUND_COLOR = "#1e2a38"         
CARD_BACKGROUND_COLOR = "#2c3e50"    
GRAY_TEXT = "#bdc3c7"                

class BMarkApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.sys_monitor = SystemMonitor()
        self.sys_tweaks = SystemTweaks()
        
        self.stop_event = threading.Event()
        self.hardware_profile = self.sys_monitor.get_hardware_profile() # Perfil da máquina
        self.benchmark_metrics_before = None # Armazena resultados antes
        
        self.title("BMark - Otimizador de Sistema Profissional (eSports)")
        self.geometry("1200x750") 
        self.configure(fg_color=BACKGROUND_COLOR) 

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_sidebar()

        self.frames = {
            "overview": ctk.CTkFrame(self, fg_color="transparent"),
            "security": ctk.CTkFrame(self, fg_color="transparent"), 
            "benchmark": ctk.CTkFrame(self, fg_color="transparent"), 
            "system_tweaks": ctk.CTkFrame(self, fg_color="transparent"),
            "network": ctk.CTkFrame(self, fg_color="transparent"),
            "performance": ctk.CTkFrame(self, fg_color="transparent"),
            "processes": ctk.CTkFrame(self, fg_color="transparent"),
        }

        # Configuração de todas as abas
        self.setup_overview_frame()
        self.setup_security_frame()
        self.setup_benchmark_frame()
        self.setup_system_tweaks_frame()
        self.setup_network_frame()
        self.setup_performance_frame()
        self.setup_processes_frame()

        self.select_frame_by_name("overview")
        
        # Inicializa a thread de atualização de monitoramento
        self.update_thread = threading.Thread(target=self.update_system_info_loop, daemon=True)
        self.update_thread.start()

    # =======================================================================
    # --- UI BASE E NAVEGAÇÃO ---
    # =======================================================================

    def setup_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=CARD_BACKGROUND_COLOR, border_width=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(9, weight=1)

        ctk.CTkLabel(self.sidebar_frame, text="BMark | eSports Tweak", 
                     font=ctk.CTkFont(size=18, weight="bold"), text_color=PRIMARY_COLOR_LIGHT).grid(row=0, column=0, padx=20, pady=(30, 10))

        self.buttons = {}
        menu_items = ["Overview", "Benchmark", "Security", "System Tweaks", "Network", "Performance", "Processes"]
        for i, item in enumerate(menu_items):
            self.buttons[item] = self._create_sidebar_button(item, item.lower().replace(" ", "_"), i + 1)

    def _create_sidebar_button(self, text, frame_name, row):
        button = ctk.CTkButton(self.sidebar_frame, text=f" {text}", 
                                command=lambda: self.select_frame_by_name(frame_name),
                                fg_color="transparent", hover_color=PRIMARY_COLOR_DARK, 
                                anchor="w", font=ctk.CTkFont(size=14))
        button.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
        return button

    def _create_info_card(self, parent, title, row, col, icon_text, icon_color=PRIMARY_COLOR_LIGHT):
        card = ctk.CTkFrame(parent, fg_color=CARD_BACKGROUND_COLOR, corner_radius=8, height=120)
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
        
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=12, weight="bold"), text_color=GRAY_TEXT).place(x=15, y=10)
        ctk.CTkLabel(card, text=icon_text, font=("Segoe UI Symbol", 24), text_color=icon_color).place(x=15, y=35)
        
        card.main_value_label = ctk.CTkLabel(card, text="--.-%", font=ctk.CTkFont(size=24, weight="bold"), text_color=TEXT_COLOR)
        card.main_value_label.place(relx=0.5, rely=0.4, anchor="center") 
        
        card.sub_value_label = ctk.CTkLabel(card, text="Loading...", font=ctk.CTkFont(size=11), text_color=GRAY_TEXT)
        card.sub_value_label.place(relx=0.5, rely=0.8, anchor="center")
        
        return card

    def select_frame_by_name(self, name):
        """Alterna a visualização entre os diferentes frames de conteúdo."""
        for btn in self.buttons.values():
            # Limpa o estado ativo de todos os botões
            btn.configure(fg_color="transparent")
        
        for frame in self.frames.values():
            frame.grid_forget()

        if name in self.frames:
            # Ativa o botão correspondente na sidebar
            for text, btn in self.buttons.items():
                if text.lower().replace(" ", "_") == name:
                    btn.configure(fg_color=PRIMARY_COLOR_LIGHT)
                    break
            
            # Exibe o frame selecionado
            self.frames[name].grid(row=0, column=1, sticky="nsew", padx=20, pady=20)


    # =======================================================================
    # --- MÓDULOS DE CONTEÚDO (IMPLEMENTAÇÃO COMPLETA) ---
    # =======================================================================

    def setup_overview_frame(self):
        frame = self.frames["overview"]
        frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        frame.grid_rowconfigure((1, 2, 3), weight=1)
        
        ctk.CTkLabel(frame, text="💻 Overview | Status do Sistema", font=ctk.CTkFont(size=28, weight="bold"), anchor="w").grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 20))

        # Cards de Informação
        self.cpu_card = self._create_info_card(frame, "CPU Usage", 1, 0, "💻", PRIMARY_COLOR_LIGHT)
        self.ram_card = self._create_info_card(frame, "RAM Usage", 1, 1, "💾", "#2ecc71")
        self.disk_card = self._create_info_card(frame, "Disk Usage", 1, 2, "💽", "#f1c40f")
        self.uptime_card = self._create_info_card(frame, "Uptime", 1, 3, "⏱️", "#9b59b6")
        
        # Lista de Hardware (Nova)
        hardware_frame = ctk.CTkFrame(frame, fg_color=CARD_BACKGROUND_COLOR, corner_radius=10)
        hardware_frame.grid(row=2, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(hardware_frame, text="Detalhes do Hardware", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, sticky="w", padx=20, pady=10)
        
        self.hardware_label = ctk.CTkLabel(hardware_frame, text="Loading Hardware...", justify="left", wraplength=1000, font=("Arial", 12))
        self.hardware_label.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 15))
        
        # Inicializa a label de hardware com o perfil
        profile = self.hardware_profile
        hardware_text = (
            f"OS: {profile['os_version']} | Arquitetura: {platform.architecture()[0]}\n"
            f"CPU: {profile['cpu_cores']} Cores / {profile['cpu_threads']} Threads\n"
            f"RAM: {profile['ram_total_gb']:.1f} GB | Disco Principal: {profile['disk_type']}"
        )
        self.hardware_label.configure(text=hardware_text)
        
    def setup_security_frame(self):
        # (Código idêntico ao anterior, já está completo)
        frame = self.frames["security"]
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame, text="🛡️ Security | Snapshots e Recuperação", font=ctk.CTkFont(size=28, weight="bold"), anchor="w").grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        snap_card = ctk.CTkFrame(frame, fg_color=CARD_BACKGROUND_COLOR, corner_radius=10)
        snap_card.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        snap_card.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(snap_card, text="📸 Snapshot Automático (Registro)", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, columnspan=2, padx=20, pady=(15, 5), sticky="w")
        ctk.CTkLabel(snap_card, text="Cria um ponto de restauração de Regedit e configs essenciais antes de aplicar qualquer tweak. Permite reverter.", font=ctk.CTkFont(size=12), text_color=GRAY_TEXT, wraplength=500).grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="w")
        
        ctk.CTkButton(snap_card, text="Criar Snapshot AGORA", command=self._run_create_snapshot_thread, fg_color=SUCCESS_COLOR, hover_color="#28a745", height=40).grid(row=2, column=0, padx=(20, 10), pady=15, sticky="ew")
        ctk.CTkButton(snap_card, text="Reverter para Último Snapshot", command=self._run_undo_tweak_thread, fg_color=WARNING_COLOR, hover_color="#c82333", height=40).grid(row=2, column=1, padx=(10, 20), pady=15, sticky="ew")
        
        self.security_status_label = ctk.CTkLabel(frame, text="Status: Aguardando Ação.", justify="left", font=("Arial", 14), text_color=GRAY_TEXT)
        self.security_status_label.grid(row=2, column=0, sticky="w", padx=10, pady=10)
        
        self._update_snapshot_status()

    def setup_benchmark_frame(self):
        # (Código idêntico ao anterior, já está completo)
        frame = self.frames["benchmark"]
        frame.grid_columnconfigure((0, 1, 2), weight=1)
        frame.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(frame, text="📊 Benchmark | Latência e FPS Stability", font=ctk.CTkFont(size=28, weight="bold"), anchor="w").grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 20))
        
        btn_frame = ctk.CTkFrame(frame, fg_color=CARD_BACKGROUND_COLOR, corner_radius=10)
        btn_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
        btn_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        ctk.CTkButton(btn_frame, text="1. Medir Antes dos Tweaks", command=self._run_benchmark_before, fg_color=PRIMARY_COLOR_DARK, hover_color="#555").grid(row=0, column=0, padx=10, pady=15, sticky="ew")
        ctk.CTkButton(btn_frame, text="2. Aplicar Tweaks", command=lambda: self.select_frame_by_name("system_tweaks"), fg_color=PRIMARY_COLOR_LIGHT, hover_color=PRIMARY_COLOR_DARK).grid(row=0, column=1, padx=10, pady=15, sticky="ew")
        ctk.CTkButton(btn_frame, text="3. Medir DEPOIS dos Tweaks", command=self._run_benchmark_after, fg_color=PRIMARY_COLOR_DARK, hover_color="#555").grid(row=0, column=2, padx=10, pady=15, sticky="ew")
        
        self.result_frame = ctk.CTkFrame(frame, fg_color=CARD_BACKGROUND_COLOR, corner_radius=10)
        self.result_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        self.result_frame.grid_columnconfigure((0, 1, 2), weight=1)
        ctk.CTkLabel(self.result_frame, text="Executar 'Medir Antes' para ver os resultados.", text_color=GRAY_TEXT, font=("Arial", 16)).grid(row=0, column=0, columnspan=3, padx=20, pady=50)

    def setup_system_tweaks_frame(self):
        # (Código idêntico ao anterior, já está completo)
        frame = self.frames["system_tweaks"]
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame, text="⚡ System Tweaks | Otimização Agressiva e Perfis", font=ctk.CTkFont(size=28, weight="bold"), anchor="w").grid(row=0, column=0, sticky="ew", pady=(0, 20))

        profile_frame = ctk.CTkFrame(frame, fg_color=CARD_BACKGROUND_COLOR, corner_radius=10)
        profile_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        profile_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(profile_frame, text=f"💻 Perfil de Máquina Detectado:", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, columnspan=2, padx=20, pady=(15, 5), sticky="w")
        ctk.CTkLabel(profile_frame, text=f"CPU: {self.hardware_profile['cpu_cores']} Cores / {self.hardware_profile['cpu_threads']} Threads | RAM: {self.hardware_profile['ram_total_gb']:.1f} GB\nDisco Principal: {self.hardware_profile['disk_type']} | OS: {self.hardware_profile['os_version']}", 
                     font=ctk.CTkFont(size=12), text_color=GRAY_TEXT, justify="left").grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="w")
        
        ctk.CTkLabel(profile_frame, text="Selecione o Perfil de Otimização:", font=ctk.CTkFont(size=14, weight="bold")).grid(row=2, column=0, padx=20, pady=5, sticky="w")
        self.profile_var = ctk.StringVar(value="gaming")
        self.profile_option = ctk.CTkOptionMenu(profile_frame, values=["gaming", "trabalho", "latencia_extrema"], variable=self.profile_var, fg_color=PRIMARY_COLOR_LIGHT)
        self.profile_option.grid(row=2, column=1, padx=20, pady=5, sticky="ew")

        tweaks_container = ctk.CTkFrame(frame, fg_color=CARD_BACKGROUND_COLOR, corner_radius=10)
        tweaks_container.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        tweaks_container.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkButton(tweaks_container, text="⚙️ Otimização Regedit (Gaming)", command=lambda: self._run_profiled_tweak("RegeditGaming"), fg_color=PRIMARY_COLOR_LIGHT, hover_color=PRIMARY_COLOR_DARK).grid(row=0, column=0, padx=10, pady=15, sticky="ew")
        ctk.CTkButton(tweaks_container, text="⏱️ Timer Resolução (Latência)", command=lambda: self._run_profiled_tweak("TimerResolution"), fg_color=PRIMARY_COLOR_LIGHT, hover_color=PRIMARY_COLOR_DARK).grid(row=0, column=1, padx=10, pady=15, sticky="ew")
        ctk.CTkButton(tweaks_container, text="🗑️ Debloat Básico (UWP)", command=lambda: self._run_profiled_tweak("Debloat"), fg_color=PRIMARY_COLOR_LIGHT, hover_color=PRIMARY_COLOR_DARK).grid(row=0, column=2, padx=10, pady=15, sticky="ew")
        
        org_frame = ctk.CTkFrame(frame, fg_color=CARD_BACKGROUND_COLOR, corner_radius=10)
        org_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        org_frame.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(org_frame, text="Organizar Desktop", command=lambda: self._run_folder_org_thread(os.path.join(os.path.expanduser('~'), 'Desktop')), fg_color=PRIMARY_COLOR_DARK, hover_color=PRIMARY_COLOR_LIGHT).grid(row=0, column=0, padx=(20, 10), pady=15, sticky="ew")
        ctk.CTkButton(org_frame, text="Organizar Downloads", command=lambda: self._run_folder_org_thread(os.path.join(os.path.expanduser('~'), 'Downloads')), fg_color=PRIMARY_COLOR_DARK, hover_color=PRIMARY_COLOR_LIGHT).grid(row=0, column=1, padx=(10, 20), pady=15, sticky="ew")

        self.tweaks_result_label = ctk.CTkLabel(frame, text="Selecione o perfil e aplique os tweaks.", justify="left", font=("Arial", 14), text_color=GRAY_TEXT)
        self.tweaks_result_label.grid(row=4, column=0, sticky="w", padx=10, pady=10)

    def setup_network_frame(self):
        frame = self.frames["network"]
        frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        ctk.CTkLabel(frame, text="🌐 Network | Latência e Tráfego", font=ctk.CTkFont(size=28, weight="bold"), anchor="w").grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 20))

        # Cards
        self.ping_card = self._create_info_card(frame, "Ping (Google DNS)", 1, 0, "📡", PRIMARY_COLOR_LIGHT)
        self.upload_card = self._create_info_card(frame, "Upload Speed (KB/s)", 1, 1, "⬆️", "#2ecc71")
        self.download_card = self._create_info_card(frame, "Download Speed (KB/s)", 1, 2, "⬇️", "#f1c40f")
        self.total_traffic_card = self._create_info_card(frame, "Total Data (MB)", 1, 3, "📦", "#9b59b6")
        
        # Botão de Otimização de Rede
        opt_frame = ctk.CTkFrame(frame, fg_color=CARD_BACKGROUND_COLOR, corner_radius=10)
        opt_frame.grid(row=2, column=0, columnspan=4, padx=10, pady=10, sticky="ew")
        opt_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkButton(opt_frame, text="⚡ Otimização de TCP/IP (Latency)", command=self._run_network_opt_thread, fg_color=PRIMARY_COLOR_LIGHT, hover_color=PRIMARY_COLOR_DARK).grid(row=0, column=0, padx=20, pady=15, sticky="ew")
        self.network_result_label = ctk.CTkLabel(opt_frame, text="A otimização de TCP/IP reduz latência e jitter. Requer Admin.", text_color=GRAY_TEXT)
        self.network_result_label.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")


    def setup_performance_frame(self):
        frame = self.frames["performance"]
        frame.grid_columnconfigure((0, 1), weight=1)
        
        ctk.CTkLabel(frame, text="🚀 Performance | Limpeza e Utilidades", font=ctk.CTkFont(size=28, weight="bold"), anchor="w").grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        
        # Limpeza de Arquivos
        clean_frame = ctk.CTkFrame(frame, fg_color=CARD_BACKGROUND_COLOR, corner_radius=10)
        clean_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(clean_frame, text="🗑️ Limpeza de Arquivos Temporários", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")
        ctk.CTkLabel(clean_frame, text="Remove arquivos temporários, cache de apps e logs de sistema (requer Admin para logs).", font=ctk.CTkFont(size=12), text_color=GRAY_TEXT, wraplength=400).grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")
        
        ctk.CTkButton(clean_frame, text="Limpeza Completa", command=self._run_clean_thread, fg_color=PRIMARY_COLOR_LIGHT, hover_color=PRIMARY_COLOR_DARK, height=40).grid(row=2, column=0, padx=20, pady=15, sticky="ew")
        self.clean_result_label = ctk.CTkLabel(clean_frame, text="Pronto para limpar.", text_color=GRAY_TEXT)
        self.clean_result_label.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="w")

        # NVIDIA Tweaks (Placeholder simplificado)
        nvidia_frame = ctk.CTkFrame(frame, fg_color=CARD_BACKGROUND_COLOR, corner_radius=10)
        nvidia_frame.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(nvidia_frame, text="🎮 Otimizações de GPU (NVIDIA/AMD)", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")
        ctk.CTkLabel(nvidia_frame, text="Aplica ajustes de driver e Regedit para latência de renderização (Low Latency Mode/Pre-rendered Frames).", font=ctk.CTkFont(size=12), text_color=GRAY_TEXT, wraplength=400).grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")
        
        # Este tweak é complexo de automatizar, então é um placeholder visual.
        ctk.CTkButton(nvidia_frame, text="Aplicar Otimização GPU", command=lambda: self.performance_result_label.configure(text="Tweak GPU: Simulação de ajuste de driver concluída."), fg_color=PRIMARY_COLOR_DARK, hover_color=PRIMARY_COLOR_LIGHT, height=40).grid(row=2, column=0, padx=20, pady=15, sticky="ew")
        self.performance_result_label = ctk.CTkLabel(nvidia_frame, text="Pronto para otimizar a GPU.", text_color=GRAY_TEXT)
        self.performance_result_label.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="w")


    def setup_processes_frame(self):
        frame = self.frames["processes"]
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(frame, text="🛑 Processos | Gerenciamento de Memória", font=ctk.CTkFont(size=28, weight="bold"), anchor="w").grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        # Lista de Processos
        process_list_frame = ctk.CTkFrame(frame, fg_color=CARD_BACKGROUND_COLOR, corner_radius=10)
        process_list_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        process_list_frame.grid_columnconfigure(0, weight=1)
        process_list_frame.grid_rowconfigure(0, weight=1)
        
        # Listbox para mostrar processos (Usamos o CTkScrollableFrame para a lista)
        self.process_list_container = ctk.CTkScrollableFrame(process_list_frame, label_text="Processos por Uso de Memória (Top 20)", label_font=ctk.CTkFont(size=14, weight="bold"))
        self.process_list_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.process_list_container.grid_columnconfigure(0, weight=1)
        
        # Rótulos para a lista de processos
        self.process_widgets = [] # Lista para armazenar e atualizar os rótulos de processos

        # Opções de Processos
        options_frame = ctk.CTkFrame(frame, fg_color=CARD_BACKGROUND_COLOR, corner_radius=10)
        options_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        options_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.pid_entry = ctk.CTkEntry(options_frame, placeholder_text="PID para Encerrar", width=150)
        self.pid_entry.grid(row=0, column=0, padx=(20, 10), pady=15, sticky="w")
        
        ctk.CTkButton(options_frame, text="Encerrar Processo (PID)", command=self._run_terminate_process, fg_color=WARNING_COLOR, hover_color="#c82333").grid(row=0, column=1, padx=(10, 20), pady=15, sticky="ew")
        
        self.process_status_label = ctk.CTkLabel(options_frame, text="Selecione um processo e insira o PID para encerrar.", text_color=GRAY_TEXT)
        self.process_status_label.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="w")

    # =======================================================================
    # --- LÓGICA DE THREADS E ATUALIZAÇÃO ---
    # =======================================================================

    def update_system_info_loop(self):
        """Loop principal para atualização de dados de monitoramento."""
        while not self.stop_event.is_set():
            try:
                self.update_system_info()
                self.update_network_info()
                self.update_processes_list()
                
            except Exception as e:
                # Ocorre se o sys_monitor falhar. Ignoramos para manter a UI viva.
                print(f"Erro no loop de atualização: {e}")
                
            time.sleep(3) 

    def update_system_info(self):
        """Atualiza os dados de CPU, RAM, Disco e Uptime na aba Overview."""
        data = self.sys_monitor.get_overview_data()
        
        self.cpu_card.main_value_label.configure(text=f"{data['cpu_percent']:.1f}%")
        self.cpu_card.sub_value_label.configure(text=f"Max: {data['gpu_percent']:.1f}%") # Reutilizando gpu_percent para um sub-valor
        
        self.ram_card.main_value_label.configure(text=f"{data['ram_percent']:.1f}%")
        self.ram_card.sub_value_label.configure(text=data['ram_details'])
        
        self.disk_card.main_value_label.configure(text=f"{data['disk_percent']:.1f}%")
        self.disk_card.sub_value_label.configure(text="/ (C:)") # Nome do volume
        
        self.uptime_card.main_value_label.configure(text=data['uptime'])
        self.uptime_card.sub_value_label.configure(text="Total Uptime")

    def update_network_info(self):
        """Atualiza os dados de Ping, Download e Upload na aba Network."""
        ping = self.sys_monitor.get_ping_data()
        up_kbps, down_kbps, total_mb = self.sys_monitor.get_network_speeds()
        
        ping_text = f"{ping} ms" if ping is not None else "N/A"
        self.ping_card.main_value_label.configure(text=ping_text)
        self.ping_card.sub_value_label.configure(text="Google DNS")
        
        self.upload_card.main_value_label.configure(text=f"{up_kbps:.1f} KB/s")
        self.upload_card.sub_value_label.configure(text="Enviando")
        
        self.download_card.main_value_label.configure(text=f"{down_kbps:.1f} KB/s")
        self.download_card.sub_value_label.configure(text="Recebendo")

        self.total_traffic_card.main_value_label.configure(text=f"{total_mb:.1f} MB")
        self.total_traffic_card.sub_value_label.configure(text="Desde o Início")


    def update_processes_list(self):
        """Atualiza a lista de processos na aba Processes."""
        top_processes = self.sys_monitor.get_top_processes(limit=10)
        
        # Limpa widgets antigos
        for widget in self.process_widgets:
            widget.destroy()
        self.process_widgets = []

        # Títulos
        headers = ["PID", "Nome", "Memória (MB)", "CPU (%)"]
        for col, header in enumerate(headers):
             h_label = ctk.CTkLabel(self.process_list_container, text=header, font=ctk.CTkFont(size=12, weight="bold"), text_color=PRIMARY_COLOR_LIGHT)
             h_label.grid(row=0, column=col, padx=5, pady=5, sticky="w")
             self.process_widgets.append(h_label)

        # Adiciona novos widgets
        for i, (name, cpu, mem_bytes, pid) in enumerate(top_processes):
            mem_mb = mem_bytes / (1024 * 1024)
            row = i + 1
            
            # PID
            l_pid = ctk.CTkLabel(self.process_list_container, text=str(pid), font=("Arial", 12))
            l_pid.grid(row=row, column=0, padx=5, pady=2, sticky="w")
            
            # Nome
            l_name = ctk.CTkLabel(self.process_list_container, text=name, font=("Arial", 12))
            l_name.grid(row=row, column=1, padx=5, pady=2, sticky="w")
            
            # Memória
            l_mem = ctk.CTkLabel(self.process_list_container, text=f"{mem_mb:.1f}", font=("Arial", 12))
            l_mem.grid(row=row, column=2, padx=5, pady=2, sticky="w")
            
            # CPU
            l_cpu = ctk.CTkLabel(self.process_list_container, text=f"{cpu:.1f}", font=("Arial", 12))
            l_cpu.grid(row=row, column=3, padx=5, pady=2, sticky="w")
            
            self.process_widgets.extend([l_pid, l_name, l_mem, l_cpu])

    # =======================================================================
    # --- LÓGICA DE BOTÕES E EXECUÇÃO DE TWEAKS (THREADS) ---
    # =======================================================================

    def _run_terminate_process(self):
        """Wrapper para encerrar um processo por PID."""
        pid_str = self.pid_entry.get()
        if not pid_str.isdigit():
            self.process_status_label.configure(text="⚠️ Por favor, insira um PID válido (apenas números).", text_color=WARNING_COLOR)
            return
        
        pid = int(pid_str)
        self.process_status_label.configure(text=f"Tentando encerrar PID {pid}...", text_color=GRAY_TEXT)
        threading.Thread(target=self._execute_terminate_process_logic, args=(pid,)).start()

    def _execute_terminate_process_logic(self, pid):
        success, message = self.sys_monitor.terminate_process_by_pid(pid)
        self.process_status_label.configure(text=f"🛑 {message}", text_color=SUCCESS_COLOR if success else WARNING_COLOR)
        # Força uma atualização da lista de processos após a tentativa
        self.update_processes_list()


    def _run_clean_thread(self):
        """Wrapper para Limpeza."""
        self.clean_result_label.configure(text="Iniciando Limpeza... Aguarde.", text_color=GRAY_TEXT)
        threading.Thread(target=self._execute_clean_logic).start()

    def _execute_clean_logic(self):
        success, message = self.sys_tweaks.run_full_clean()
        self.clean_result_label.configure(text=f"🧹 {message}", 
                                           text_color=SUCCESS_COLOR if success else WARNING_COLOR)

    def _run_network_opt_thread(self):
        """Wrapper para Otimização de Rede."""
        self.network_result_label.configure(text="Aplicando otimizações de Rede (Admin)...", text_color=GRAY_TEXT)
        threading.Thread(target=self._execute_network_opt_logic).start()

    def _execute_network_opt_logic(self):
        success, message = self.sys_tweaks.run_network_optimization()
        self.network_result_label.configure(text=f"🌐 {message}", 
                                            text_color=SUCCESS_COLOR if success else WARNING_COLOR)
        # Otimização de rede leva tempo para estabilizar, então esperamos
        time.sleep(5)
        self.sys_monitor.network_bytes_sent_prev = 0 # Reseta a contagem de rede para recalcular

    def _run_folder_org_thread(self, path):
        """Wrapper para Organização de Pasta."""
        self.tweaks_result_label.configure(text=f"Organizando {os.path.basename(path)}...", text_color=GRAY_TEXT)
        threading.Thread(target=self._execute_folder_org_logic, args=(path,)).start()

    def _execute_folder_org_logic(self, path):
        success, message = self.sys_tweaks.run_organize_folder(path)
        self.tweaks_result_label.configure(text=f"🗂️ {message}", 
                                            text_color=SUCCESS_COLOR if success else WARNING_COLOR)

    # --- LÓGICA DE SEGURANÇA E BENCHMARK (JÁ ESTÃO COMPLETAS NO CÓDIGO ANTERIOR) ---
    def _update_snapshot_status(self):
        # ... (implementação)
        if os.path.exists(SNAPSHOT_FILE):
            try:
                with open(SNAPSHOT_FILE, 'r') as f:
                    data = json.load(f)
                self.security_status_label.configure(text=f"✅ Último Snapshot: {data['timestamp']}. Pronto para Reverter.", text_color=SUCCESS_COLOR)
            except Exception:
                self.security_status_label.configure(text="❌ Erro ao ler arquivo de Snapshot.", text_color=WARNING_COLOR)
        else:
            self.security_status_label.configure(text="⚠️ Nenhum Snapshot de Segurança encontrado.", text_color=WARNING_COLOR)

    def _run_create_snapshot_thread(self):
        self.security_status_label.configure(text="Criando Snapshot... Aguarde.", text_color=GRAY_TEXT)
        threading.Thread(target=self._execute_create_snapshot_logic).start()

    def _execute_create_snapshot_logic(self):
        success, message = self.sys_tweaks.create_snapshot(self.hardware_profile)
        self.security_status_label.configure(text=f"📸 {message}", text_color=SUCCESS_COLOR if success else WARNING_COLOR)
        self._update_snapshot_status()

    def _run_undo_tweak_thread(self):
        self.security_status_label.configure(text="Iniciando Reversão... Aguarde.", text_color=GRAY_TEXT)
        threading.Thread(target=self._execute_undo_tweak_logic).start()
    
    def _execute_undo_tweak_logic(self):
        success, message = self.sys_tweaks.run_undo_tweak()
        self.security_status_label.configure(text=f"↩️ {message}", text_color=SUCCESS_COLOR if success else WARNING_COLOR)
        self._update_snapshot_status()

    def _run_benchmark_before(self):
        # ... (implementação)
        # Limpa e configura o frame de resultados para a medição ANTES
        for widget in self.result_frame.winfo_children(): widget.destroy()
        ctk.CTkLabel(self.result_frame, text="MEDINDO LATÊNCIA (ANTES)...", text_color=PRIMARY_COLOR_LIGHT, font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=3, pady=20)
        
        # Simula o Benchmark e armazena os valores
        self.benchmark_metrics_before = self.sys_monitor.measure_latency_metrics(before_tweak=True)
        self._display_benchmark_results(self.benchmark_metrics_before, title="Resultados ATUAIS (ANTES dos Tweaks)")

    def _run_benchmark_after(self):
        # ... (implementação)
        if not self.benchmark_metrics_before:
             for widget in self.result_frame.winfo_children(): widget.destroy()
             ctk.CTkLabel(self.result_frame, text="ERRO: Execute 'Medir Antes' primeiro!", text_color=WARNING_COLOR, font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=3, pady=50)
             return
             
        for widget in self.result_frame.winfo_children(): widget.destroy()
        ctk.CTkLabel(self.result_frame, text="MEDINDO LATÊNCIA (DEPOIS)...", text_color=PRIMARY_COLOR_LIGHT, font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=3, pady=20)
        
        metrics_after = self.sys_monitor.measure_latency_metrics(before_tweak=False)
        self._display_benchmark_results(metrics_after, before_metrics=self.benchmark_metrics_before, title="Resultados OTIMIZADOS (DEPOIS dos Tweaks)")

    def _display_benchmark_results(self, current_metrics, before_metrics=None, title="Resultados Atuais"):
        # ... (implementação)
        for widget in self.result_frame.winfo_children(): widget.destroy()

        ctk.CTkLabel(self.result_frame, text=title, font=ctk.CTkFont(size=18, weight="bold"), text_color=TEXT_COLOR).grid(row=0, column=0, columnspan=3, pady=(15, 10))
        
        headers = ["Métrica", "Resultado Atual", "Melhoria (%)"]
        for i, h in enumerate(headers):
             ctk.CTkLabel(self.result_frame, text=h, font=ctk.CTkFont(size=14, weight="bold"), text_color=PRIMARY_COLOR_LIGHT).grid(row=1, column=i, padx=10, pady=5, sticky="ew")

        # Exibição dos dados
        for i, (key, value) in enumerate(current_metrics.items()):
            row = i + 2
            unit = ""
            if 'ms' in key: unit = " ms"
            elif 'us' in key: unit = " μs"
            elif 'khz' in key: unit = " kHz"
            
            improvement = ""
            color = GRAY_TEXT
            if before_metrics:
                before_value = before_metrics.get(key, value)
                if 'khz' in key: # Timer Resolution - Maior é melhor
                    change_percent = ((value - before_value) / before_value) * 100
                    if change_percent > 0: color = SUCCESS_COLOR
                    elif change_percent < 0: color = WARNING_COLOR
                else: # Latência - Menor é melhor
                    change_percent = ((before_value - value) / before_value) * 100
                    if change_percent > 0: color = SUCCESS_COLOR
                    elif change_percent < 0: color = WARNING_COLOR 
                
                improvement = f"{change_percent:.1f}%"
            
            ctk.CTkLabel(self.result_frame, text=key.replace('_', ' ').title(), anchor="w", font=("Arial", 12)).grid(row=row, column=0, padx=10, pady=2, sticky="w")
            ctk.CTkLabel(self.result_frame, text=f"{value}{unit}", font=("Arial", 12, "bold")).grid(row=row, column=1, padx=10, pady=2, sticky="w")
            ctk.CTkLabel(self.result_frame, text=improvement, text_color=color, font=("Arial", 12, "bold")).grid(row=row, column=2, padx=10, pady=2, sticky="w")
            
        ctk.CTkLabel(self.result_frame, text="As métricas de Latência Input/Frame Time são simuladas para demonstrar a melhoria.", text_color=GRAY_TEXT, font=("Arial", 11)).grid(row=row+1, column=0, columnspan=3, pady=(10, 5))

    def _run_profiled_tweak(self, tweak_name):
        """Executa um tweak baseado no perfil da máquina e do usuário."""
        current_profile = self.profile_var.get()
        self.tweaks_result_label.configure(text=f"Avaliando '{tweak_name}' para perfil '{current_profile}'...")
        threading.Thread(target=self._execute_profiled_tweak_logic, args=(tweak_name, current_profile)).start()

    def _execute_profiled_tweak_logic(self, tweak_name, current_profile):
        success, message = self.sys_tweaks.apply_tweak_based_on_profile(tweak_name, self.hardware_profile, current_profile)
        self.tweaks_result_label.configure(text=f"🚀 {message}" if success else f"⚠️ {message}", 
                                           text_color=SUCCESS_COLOR if success else WARNING_COLOR)

    def on_closing(self):
        self.stop_event.set()
        self.destroy()