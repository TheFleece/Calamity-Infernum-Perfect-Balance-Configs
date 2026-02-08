import os
import time
import zipfile
import requests
import webbrowser
import psutil
import winreg
import sys
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, NoSuchWindowException

# --- КОНФИГУРАЦИЯ ---
COLLECTION_URL = "https://steamcommunity.com/sharedfiles/filedetails/?id=3662508581"
CONFIGS_URL = "https://github.com/TheFleece/Calamity-Infernum-Perfect-Balance-Configs/releases/download/v1.0.0/ModConfigs.zip"
ENABLED_JSON_URL = "https://raw.githubusercontent.com/TheFleece/Calamity-Infernum-Perfect-Balance-Configs/main/enabled.json"
TERRARIA_ID = "105600"
TMODLOADER_ID = "1281930"

def get_steam_path():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
        path, _ = winreg.QueryValueEx(key, "SteamPath")
        return Path(path)
    except: return None

def is_game_installed(app_id):
    steam_path = get_steam_path()
    if not steam_path: return False
    library_folders = [steam_path / "steamapps"]
    vdf_path = steam_path / "steamapps" / "libraryfolders.vdf"
    if vdf_path.exists():
        with open(vdf_path, "r") as f:
            for line in f:
                if '"path"' in line:
                    lib_path = Path(line.split('"')[3]) / "steamapps"
                    if lib_path not in library_folders: library_folders.append(lib_path)
    for folder in library_folders:
        manifest = folder / f"appmanifest_{app_id}.acf"
        if manifest.exists():
            with open(manifest, "r", encoding="utf-8") as f:
                if '"StateFlags"		"4"' in f.read(): return True
    return False

def is_process_running(name):
    return any(p.info['name'] and p.info['name'].lower() == name.lower() for p in psutil.process_iter(['name']))

def run_installer():
    print("="*60)
    print("🚀 TOTAL CALAMITY INSTALLER: PERFECT BALANCE [RU]")
    print("="*60)

    # 1. Подготовка Steam
    if not is_process_running("Steam.exe"):
        print("\n[1/6] Запуск Steam...")
        webbrowser.open("steam://open/main")
        while not is_process_running("Steam.exe"): time.sleep(3)
    
    webbrowser.open(f"steam://install/{TERRARIA_ID}")
    time.sleep(2)
    webbrowser.open(f"steam://install/{TMODLOADER_ID}")

    # 2. Selenium: Автоматизация
    print("\n[2/6] Настройка подписок на моды...")
    driver = webdriver.Chrome()
    driver.get(COLLECTION_URL)
    wait = WebDriverWait(driver, 10)

    print("👉 Пожалуйста, войдите в Steam. Скрипт ждет авторизации...")
    
    login_clicked = False
    subscribed = False

    while not subscribed:
        try:
            # ПРОВЕРКА: Не закрыто ли окно браузера?
            _ = driver.window_handles 

            # Если еще не нажимали кнопку входа и мы не залогинены
            if not login_clicked:
                try:
                    login_btn = driver.find_element(By.XPATH, "//a[contains(@class, 'global_action_link') and (contains(text(), 'sign in') or contains(text(), 'войти'))]")
                    login_btn.click()
                    login_clicked = True
                    print("🔗 Переход на страницу входа...")
                except: pass

            # Проверяем, появился ли аватар (значит вход выполнен)
            try:
                driver.find_element(By.ID, "account_pulldown")
                
                # Клик 1: Подписаться на все
                sub_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='subscribeCollection']//a[contains(@class, 'subscribe')]")))
                sub_btn.click()
                print("🎯 Кнопка 'Подписаться на все' нажата.")

                # Клик 2: Overwrite My Subscriptions
                ow_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Overwrite My Subscriptions') or contains(text(), 'Перезаписать')]/..")))
                ow_btn.click()
                
                # Клик 3: Yes, Overwrite My Subscriptions
                yes_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Yes, Overwrite My Subscriptions') or contains(text(), 'Да, перезаписать')]/..")))
                yes_btn.click()
                
                subscribed = True
                print("✅ Подписка подтверждена. Закрываю браузер...")
                driver.quit()
            except:
                # Если аватара нет, просто ждем входа пользователя
                time.sleep(2)

        except (NoSuchWindowException, WebDriverException):
            print("\n❌ ОШИБКА: Вы закрыли браузер! Запустите скрипт еще раз.")
            sys.exit()
        except Exception as e:
            time.sleep(2)

    # 3. Файлы
    print("\n[3/6] Установка конфигов и enabled.json...")
    tmod_path = Path.home() / "Documents" / "My Games" / "Terraria" / "tModLoader"
    config_dir = tmod_path / "ModConfigs"
    mods_dir = tmod_path / "Mods"
    config_dir.mkdir(parents=True, exist_ok=True)
    mods_dir.mkdir(parents=True, exist_ok=True)

    try:
        r_zip = requests.get(CONFIGS_URL)
        with open("temp.zip", "wb") as f: f.write(r_zip.content)
        with zipfile.ZipFile("temp.zip", "r") as z: z.extractall(config_dir)
        os.remove("temp.zip")
        print("✅ Конфиги установлены.")

        r_json = requests.get(ENABLED_JSON_URL)
        with open(mods_dir / "enabled.json", "wb") as f: f.write(r_json.content)
        print("✅ Файл enabled.json обновлен.")
    except Exception as e: print(f"❌ Ошибка загрузки: {e}")

    # 4. Завершение
    print("\n[4/6] Ожидание завершения загрузки в Steam...")
    while not (is_game_installed(TERRARIA_ID) and is_game_installed(TMODLOADER_ID)):
        time.sleep(15)
    
    print("\n[5/6] Запуск игры...")
    webbrowser.open(f"steam://run/{TMODLOADER_ID}")
    print("\n✅ УСТАНОВКА ЗАВЕРШЕНА!")
    input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    run_installer()