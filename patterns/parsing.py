from selenium import webdriver
from selenium.webdriver.common.by import By
import time





# Настройка браузера (Chrome)
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # без графического интерфейса

# Selenium 4.6+ автоматически найдет и использует ChromeDriver
driver = webdriver.Chrome(options=options)
class parser:
    def check_teck(symbols):
        try:
            driver.get(f"https://ru.tradingview.com/symbols/{symbols}.P/technicals/")
            driver.find_element(By.XPATH, '/html/body/div[3]/div[4]/div[2]/div[2]/div/section/div/div[2]/div/div/button[5]/span[1]/span').click()
            time.sleep(2)
            rsishort = driver.find_element(By.XPATH, "/html/body/div[3]/div[4]/div[2]/div[2]/div/section/div/div[4]/div[2]/div[2]/div[1]/span[2]").text
            rsilong = driver.find_element(By.XPATH, "/html/body/div[3]/div[4]/div[2]/div[2]/div/section/div/div[4]/div[2]/div[2]/div[3]/span[2]").text
            rsishort = int(rsishort)
            rsilong = int(rsilong)

            if rsilong >10:
                return 1
            elif rsishort >10:
                return 2
            else:
                return 3

        finally:
            driver.quit()