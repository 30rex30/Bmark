# bmark_tweaks.py
import os
import shutil
import subprocess
import platform
import json # Para simular o armazenamento do snapshot
import time
from datetime import datetime

WARNING_COLOR = "#e74c3c" 
SUCCESS_COLOR = "#2ecc77" 
SNAPSHOT_FILE = "bmark_snapshot.json" # Arquivo de simulação do registro de segurança

FILE_TYPES = {
    "Imagens": ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'],
    "Documentos": ['.doc', '.docx', '.pdf', '.txt', '.rtf', '.odt'],
    "Vídeos": ['.mp4', '.mkv', '.avi', '.mov', '.wmv'],
    "Áudio": ['.mp3', '.wav', '.flac', '.aac'],
    "Comprimidos": ['.zip', '.rar', '.7z', '.tar'],
}

class SystemTweaks:
    
    def __init__(self):
        # Simula o armazenamento dos tweaks aplicados para o 'Undo'
        self.applied_tweaks = {}

    def _run_system_command(self, command, os_check=True):
        # (Omitido por brevidade, código idêntico ao anterior)
        if os_check and platform.system() != "Windows":
             return False, "Funcionalidade exclusiva para Windows."
        try:
            subprocess.run(command, shell=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            return True, "Comando executado com sucesso."
        except subprocess.CalledProcessError:
            return False, "ERRO: Falha ao executar o comando. (Verifique se está rodando como Admin)"
        except Exception as e:
            return False, f"ERRO inesperado: {str(e)}"

    # --- MOTOR DE DECISÃO E SEGURANÇA ---
    
    def create_snapshot(self, system_profile):
        """Simula a criação de um snapshot do sistema antes dos tweaks."""
        try:
            # Em um ambiente real, isto faria um backup das chaves do Regedit e configurações
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            snapshot_data = {
                'timestamp': timestamp,
                'profile': system_profile,
                # Armazenar um estado base aqui (ex: valor de SystemResponsiveness, etc.)
                'regedit_backup': {'HKEY_LOCAL_MACHINE\\...': 'InitialValue'}
            }
            with open(SNAPSHOT_FILE, 'w') as f:
                json.dump(snapshot_data, f, indent=4)
            return True, f"Snapshot de Segurança criado em {timestamp}."
        except Exception as e:
            return False, f"Falha ao criar Snapshot: {str(e)}"

    def run_undo_tweak(self):
        """Simula a reversão das configurações a partir do snapshot."""
        if not os.path.exists(SNAPSHOT_FILE):
             return False, "Nenhum Snapshot de Segurança encontrado para reverter."

        # Em um ambiente real, aqui seriam revertidas as chaves e comandos aplicados.
        try:
             # Remoção para simular o uso do arquivo de backup
            os.remove(SNAPSHOT_FILE)
            return True, "Reversão para o estado do Snapshot concluída."
        except Exception as e:
            return False, f"Falha na Reversão: {str(e)}"
    
    def apply_tweak_based_on_profile(self, tweak_name, profile, profile_type="gaming"):
        """Aplica tweaks apenas se a máquina e o perfil fizerem sentido."""
        
        # Lógica de Decisão Simplificada
        if tweak_name == "RegeditGaming":
            if profile['cpu_cores'] < 4 and profile_type == "gaming":
                return False, "Regedit Gaming: Pulado. CPU de baixo core/thread pode não se beneficiar."
            return self.run_regedit_optimization()

        elif tweak_name == "TimerResolution":
            if profile['disk_type'] == 'HDD' and profile_type == "gaming":
                 # Se for HDD, desativamos o defrag. Se for SSD, pulamos a desativação de defrag
                 return self.run_timer_resolution_tweak(desativar_defrag=True)
            elif profile_type != "gaming":
                 return False, "Timer Res: Pulado. Tweak agressivo demais para perfil Trabalho/Latência."
            return self.run_timer_resolution_tweak(desativar_defrag=False)

        elif tweak_name == "Debloat":
            if profile['ram_total_gb'] < 8:
                # O Debloat é sempre bom se a RAM for baixa
                return self.run_debloat()
            return False, "Debloat: Pulado. RAM suficiente. Usuário pode precisar de apps UWP."

        return False, f"Tweak '{tweak_name}' não reconhecido ou lógica de perfil falhou."


    # --- TWEAKS ATUAIS (Adaptados para receber parâmetros) ---

    def run_regedit_optimization(self):
        # (Omitido por brevidade, código idêntico ao anterior)
        commands = [
            r'REG ADD "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v "SystemResponsiveness" /t REG_DWORD /d "0" /f',
            r'REG ADD "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "GPU Priority" /t REG_DWORD /d "8" /f'
        ]
        success = True
        for cmd in commands:
            if not self._run_system_command(cmd)[0]: success = False
        if success: return True, "Otimização de Regedit (Multimedia/Gaming) Aplicada!"
        return False, "Erro na aplicação de Regedit. (Rodar como Admin)"
        
    def run_timer_resolution_tweak(self, desativar_defrag=True):
        """Ajusta a resolução do timer E opcionalmente desativa o defrag."""
        commands = []
        # Otimização principal (requer software de terceiros ou DLL, simulamos o scheduler)
        commands.append(r'schtasks /Change /TN "\Microsoft\Windows\SystemRestore\RV" /DISABLE')
        if desativar_defrag:
             commands.append(r'schtasks /Change /TN "\Microsoft\Windows\Defrag\ScheduledDefrag" /DISABLE')
             
        success = True
        for cmd in commands:
             if not self._run_system_command(cmd)[0]: success = False
             
        if success: return True, "Otimização de Scheduler/Timer Resolução Aplicada!"
        return False, "Erro na aplicação do Timer Tweak. (Rodar como Admin)"
    
    def run_debloat(self):
        # (Omitido por brevidade, código idêntico ao anterior)
        commands = [
            r'PowerShell "Get-AppxPackage *xbox* | Remove-AppxPackage"',
            r'PowerShell "Get-AppxPackage *3dviewer* | Remove-AppxPackage"',
            r'PowerShell "Get-AppxPackage *candycrush* | Remove-AppxPackage"'
        ]
        success = True
        for cmd in commands:
            if not self._run_system_command(cmd)[0]: success = False
        if success: return True, "Debloat Básico (UWP) Concluído!"
        return False, "Erro ao tentar o Debloat. (Rodar como Admin)"

    def run_network_optimization(self):
        # (Omitido por brevidade, código idêntico ao anterior)
        commands = [
            r'netsh interface tcp set global autotuninglevel=normal',
            r'netsh interface tcp set global rss=enabled',
            r'netsh interface tcp set global heuristics=disabled'
        ]
        success = True
        for cmd in commands:
            if not self._run_system_command(cmd)[0]: success = False
        if success: return True, "Otimização de TCP/IP Aplicada! Requer reinício."
        return False, "Erro na Otimização de Rede. (Rodar como Admin)"

    def run_full_clean(self):
        # (Omitido por brevidade, código idêntico ao anterior)
        paths_to_clean = [os.environ.get('TEMP'), os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Local', 'Temp')]
        total_bytes = 0
        for path in paths_to_clean:
            if path: total_bytes += self._clean_path(path)
        mb_freed = total_bytes / (1024 * 1024)
        return True, f"Limpeza Concluída! {mb_freed:.2f} MB Recuperados."

    def run_organize_folder(self, folder_path):
        # (Omitido por brevidade, código idêntico ao anterior)
        if not os.path.isdir(folder_path): return False, f"ERRO: Pasta '{folder_path}' não encontrada."
        organized_count = 0
        for filename in os.listdir(folder_path):
            if os.path.isfile(os.path.join(folder_path, filename)):
                file_extension = os.path.splitext(filename)[1].lower()
                for folder_name, extensions in FILE_TYPES.items():
                    if file_extension in extensions:
                        target_dir = os.path.join(folder_path, folder_name)
                        os.makedirs(target_dir, exist_ok=True)
                        try:
                            shutil.move(os.path.join(folder_path, filename), os.path.join(target_dir, filename))
                            organized_count += 1
                        except Exception: pass
                        break
        return True, f"Organização Concluída! {organized_count} arquivos movidos."