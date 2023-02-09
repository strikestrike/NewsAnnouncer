import time
import constants

import webdriver_util


def start_sending_news() -> None:
    """
    Entry function for program. This function calls all necessary functions to automatically
    send lives in Candy Crush.
    :return: None.
    """
    driver = webdriver_util.get_chrome_webdriver()
    driver.get(constants.SITE_URL)


if __name__ == '__main__':
    start_sending_news()
