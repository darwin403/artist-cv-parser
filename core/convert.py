import base64
import json
import sys

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


# Devtools handler
def send_devtools(driver, cmd, params={}):
    resource = "/session/%s/chromium/send_command_and_get_result" % driver.session_id
    url = driver.command_executor._url + resource
    body = json.dumps({"cmd": cmd, "params": params})
    response = driver.command_executor._request("POST", url, body)

    if response.get("status"):
        raise Exception(response.get("value"))

    return response.get("value")


# Convert html to pdf
def html2pdf(url, path):
    webdriver_options = Options()
    webdriver_options.add_argument("--headless")
    webdriver_options.add_argument("--disable-gpu")
    browser = webdriver.Chrome(
        ChromeDriverManager().install(), options=webdriver_options
    )

    # load url
    browser.get(url)

    print_options = {
        "landscape": False,
        "displayHeaderFooter": False,
        "printBackground": True,
        "preferCSSPageSize": True,
    }

    result = send_devtools(browser, "Page.printToPDF", print_options)
    browser.quit()

    # save file
    with open(path, "wb") as f:
        f.write(base64.b64decode(result.get("data")))

    return path


if __name__ == "__main__":
    html2pdf(sys.argv[1], sys.argv[2])
