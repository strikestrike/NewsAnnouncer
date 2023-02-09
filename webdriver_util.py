import constants

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def get_chrome_webdriver():
    """
    Builds and returns the Chrome webdriver that we will use to automate interactions with Chrome.
    :return:    Chrome Webdriver that automates interactions with Chrome.
    """
    options = Options()
    # options.headless = True  # hide GUI
    options.add_argument("--window-size=1920,1080")
    options.add_argument("start-maximized")
    options.add_argument("--mute-audio")

    return webdriver.Chrome(options=options)
