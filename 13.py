import winreg
import ctypes


def get_autologon_creds():
    print("=== АНАЛИЗ ПАРАМЕТРОВ СИСТЕМНОГО ВХОДА (AutoLogon) ===")

    # Путь к настройкам Winlogon
    path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"

    try:
        # Открываем ключ реестра
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)

        # Список параметров, которые мы ищем
        params = {
            "AutoAdminLogon": "Статус AutoLogon",
            "DefaultDomainName": "Домен",
            "DefaultUserName": "Пользователь",
            "DefaultPassword": "ПАРОЛЬ (PLAIN TEXT)"
        }

        found_anything = False
        results = {}

        for param, description in params.items():
            try:
                value, reg_type = winreg.QueryValueEx(key, param)
                results[description] = value
                found_anything = True
            except FileNotFoundError:
                continue

        if found_anything:
            print("[+] Данные обнаружены в реестре:\n")
            for desc, val in results.items():
                print(f"    {desc.ljust(20)}: {val}")

            if "ПАРОЛЬ (PLAIN TEXT)" in results:
                print("\n[!!!] КРИТИЧЕСКАЯ УЯЗВИМОСТЬ: Пароль найден в открытом виде.")
                print(f"[!] Используй эти данные для входа (RDP/Локально).")
            else:
                print("\n[-] Автологин настроен, но пароль скрыт или отсутствует.")
        else:
            print("[-] Параметры AutoLogon не найдены в этой ветке реестра.")

        winreg.CloseKey(key)

    except Exception as e:
        print(f"[-] Ошибка доступа к реестру: {e}")
        print("[!] Попробуй запустить скрипт от имени Администратора (если возможно).")


if __name__ == "__main__":
    # Маскируем окно
    ctypes.windll.kernel32.SetConsoleTitleW("System Login Configuration Audit")
    get_autologon_creds()
