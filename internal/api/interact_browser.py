import os
import time
from common.logger import log
# Selenium 4
from selenium_stealth import stealth
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromiumService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


def tweet_with_media(filename, title, link, comment):
    # Tweet status with media
    options = Options()
    options.add_argument("--incognito")
    options.add_argument("--headless")
    # Disable DevTools
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=ChromiumService("/usr/bin/chromedriver"), options=options)
    driver.set_window_size("800", "1600")
    stealth(
            driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
    )
    driver.get("https://twitter.com/i/flow/login")

    try:
        twitter_connect_selenium(driver)
        status = f'{title}\nLink: {link}\n\nBuy me a coffee ☕️: https://www.buymeacoffee.com/bot_unixporn'
        twitter_post_media_selenium(driver, status, filename)
        # waiting to upload media
        time.sleep(10)
        if comment is not None:
            twitter_post_comment(driver, comment)
            # waiting to upload comment
            time.sleep(10)
    except Exception as e:
        driver.save_screenshot("screenshot/error.png")
        log.error("[twitter_connect_selenium] Error while connect in twitter with selenium: {}".format(e))
    finally:
        driver.quit()


def twitter_connect_selenium(driver):
    # Fill username and click on "next" button
    time.sleep(10)
    driver.find_element(By.TAG_NAME, "input").send_keys(os.environ["TWITTER_USERNAME"])
    driver.save_screenshot("screenshot/login.png")
    driver.find_elements(By.XPATH, "//button[@role='button']")[-3].click()

    # Fill password and click on "connect" button
    WebDriverWait(driver, int(os.environ["DRIVER_TIMEOUT"])).until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='password']")))
    driver.find_element(By.XPATH, "//input[@type='password']").send_keys(os.environ["TWITTER_PASSWORD"])
    driver.save_screenshot("screenshot/login_password.png")
    driver.find_element(By.XPATH, "//button[@data-testid='LoginForm_Login_Button']").click()
    log.info("[twitter_connect_selenium] Connect successfull")

def twitter_post_media_selenium(driver, status, filename):
    # Wait for block to write comment
    WebDriverWait(driver, int(os.environ["DRIVER_TIMEOUT"])).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'public-DraftStyleDefault-block')]")))
    driver.find_element(By.XPATH, "//div[contains(@class, 'public-DraftStyleDefault-block')]").send_keys(status)
    if isinstance(filename, (list, tuple)):
        files = "\n".join(filename)
        driver.find_element(By.XPATH, "//input[@data-testid='fileInput']").send_keys(files)
    else:
        driver.find_element(By.XPATH, "//input[@data-testid='fileInput']").send_keys(filename)
    driver.save_screenshot("screenshot/status_post.png")

    # Wait for media to be uploaded
    time.sleep(5) 
     
    # Wait for post button to be accessible with aria-disabled="false"
    WebDriverWait(driver, int(os.environ["DRIVER_TIMEOUT"])).until(
        lambda d: d.find_element(By.XPATH, "//button[@data-testid='tweetButtonInline']").get_attribute("aria-disabled") != "true")
    driver.save_screenshot("screenshot/last_media_upload.png")
    driver.find_element(By.XPATH, "//button[@data-testid='tweetButtonInline']").click()
    log.info("[twitter_post_media_selenium] post media successfull")


def twitter_post_comment(driver, comment):
    # Click on Reply button
    WebDriverWait(driver, int(os.environ["DRIVER_TIMEOUT"])).until(
        EC.presence_of_element_located((By.XPATH, "//button[@data-testid='reply']")))
    driver.find_elements(By.XPATH, "//button[@data-testid='reply']")[0].click()

    # Write comment
    WebDriverWait(driver, int(os.environ["DRIVER_TIMEOUT"])).until(
        EC.presence_of_element_located((By.XPATH, "//div[@data-testid='tweetTextarea_0']")))
    driver.find_element(By.XPATH, "//div[@data-testid='tweetTextarea_0']").send_keys(comment)
    driver.save_screenshot("screenshot/last_comment_upload.png")

    # Post comment
    WebDriverWait(driver, int(os.environ["DRIVER_TIMEOUT"])).until(
        EC.presence_of_element_located((By.XPATH, "//button[@data-testid='tweetButton']")))
    driver.find_element(By.XPATH, "//button[@data-testid='tweetButton']").click()
    log.info("[twitter_post_comment] post comment successfull")
