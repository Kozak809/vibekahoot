import time
from openai import OpenAI
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import re
from colorama import init, Fore, Style

init(autoreset=True)

# --- ВСТАВЬ КЛЮЧ ---
client = OpenAI(api_key="ВСТАВЬ КЛЮЧ") 

def ask_gpt_html(question, options):
    prompt = f"""
    Kahoot bot.
    Q: "{question}"
    Ops:
    1: "{options[0]}"
    2: "{options[1]}"
    3: "{options[2]}"
    4: "{options[3]}"
    Answer integer (1-4) ONLY.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        reply = response.choices[0].message.content.strip()
        match = re.search(r'[1-4]', reply)
        return int(match.group()) - 1 if match else 0
    except Exception as e:
        print(f"{Fore.RED}GPT Error: {e}")
        return 0

def print_colored_options(question, options):
    print(f"\n{Style.BRIGHT}{Fore.WHITE}┌──────────────────────────────────────────────┐")
    print(f"{Fore.WHITE}  ВОПРОС: {question}")
    print(f"{Fore.WHITE}└──────────────────────────────────────────────┘")
    colors = [Fore.RED, Fore.BLUE, Fore.YELLOW, Fore.GREEN]
    shapes = ["▲", "◆", "●", "■"]
    for i in range(4):
        opt = options[i] if i < len(options) else "Empty"
        print(f"{colors[i]}  {shapes[i]}: {opt}")
    print(Style.RESET_ALL)

def main():
    pin = input("PIN: ")
    nick = input("Nick: ")
    
    print(f"{Fore.CYAN}Запуск Kahoot Solver (by Kozak)...")
    options = webdriver.ChromeOptions()
    options.add_argument("--log-level=3")  
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.page_load_strategy = 'eager' 
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://kahoot.it")

    # Быстрый логин
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "gameId"))).send_keys(pin)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "nickname"))).send_keys(nick)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    
    print(f"{Fore.GREEN}Бот готов! Режим: Turbo.{Style.RESET_ALL}")
    
    last_question_text = ""

    while True:
        try:
            try:
                WebDriverWait(driver, 0.05).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-functional-selector='question-block-title']"))
                )
            except:
                continue

            q_elem = driver.find_element(By.CSS_SELECTOR, "[data-functional-selector='question-block-title']")
            current_question = q_elem.text.strip()

            if current_question == last_question_text or not current_question:
                time.sleep(0.05) 
                continue

            buttons = WebDriverWait(driver, 2).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-functional-selector^='answer-']"))
            )
            
            options_text = [btn.text for btn in buttons]
            while len(options_text) < 4: options_text.append("Empty")

            print_colored_options(current_question, options_text)
            
            # 5. GPT
            idx = ask_gpt_html(current_question, options_text)
            
            try:
                # Клик
                buttons[idx].click()
                print(f"{Fore.WHITE}>>> КЛИК: Вариант {idx + 1}")
                
                last_question_text = current_question
                # В теории этот код должен был работать, но мне лень
                print(f"{Fore.CYAN}Жду итоги...{Style.RESET_ALL}")
                WebDriverWait(driver, 60).until(
                    lambda d: "result" in d.current_url or "ranking" in d.current_url or "scoreboard" in d.current_url
                )
                print(f"{Fore.MAGENTA}Раунд всё.{Style.RESET_ALL}")

            except Exception as e:
                print(f"{Fore.RED}Fail: {e}")

        except Exception:
            pass
        
        time.sleep(0.05)

if __name__ == "__main__":
    main()