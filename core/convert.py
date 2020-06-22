import base64
import json
import os
import sys

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

import pdfkit


# Devtools handler
def send_devtools(driver, cmd, params={}):
    resource = "/session/%s/chromium/send_command_and_get_result" % driver.session_id
    url = driver.command_executor._url + resource
    body = json.dumps({"cmd": cmd, "params": params})
    response = driver.command_executor._request("POST", url, body)

    if response.get("status"):
        raise Exception(response.get("value"))

    return response.get("value")


# Convert webpage to pdf
def web2pdf(url, path):
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


# Convert html to pdf
def html2pdf(html, path):
    WKHTMLTOPDF_PATH = os.environ.get("WKHTMLTOPDF_PATH")

    # decide wkhtmltopdf path
    if WKHTMLTOPDF_PATH:
        configuration = pdfkit.configuration(wkhtmltopdf="/opt/bin/wkhtmltopdf")
    else:
        configuration = pdfkit.configuration()

    pdfkit.from_string(html, path, configuration=configuration)
    return path


# convert parsed data to html
def data2pdf(data, path):
    # render template
    template = """
    <div style="text-align:center; margin-bottom: 5rem">
        <h1>{input_name} - CV</h1>
        <h3 style="color:#b7b7b7">
            Parsed with <a href="https://artbiogs.com">https://artbiogs.com</a>
        </h3>
    </div>
    <table>
        <tbody>
            <tr>
                <td><b>Reference ID</b></td>
                <td>{hash}</td>
            </tr>
            <tr>
                <td><b>Name</b></td>
                <td>{name}</td>
            </tr>
            <tr>
                <td><b>DOB</b></td>
                <td>{dob}</td>
            </tr>
            <tr>
                <td colspan="2" style="padding-bottom: 1rem;"><b>Solo Exhibitions:</b></td>
            </tr>
            {solo_exhibitions}
            <tr>
                <td colspan="2" style="padding-bottom: 1rem;padding-top: 1rem;"><b>Group Exhibitions:</b></td>
            </tr>
            {group_exhibitions}
                  
        </tbody>
        <tfoot>
            <tr>
                <td colspan="2" style="padding-top: 4rem;">
                    Your reference id is: "{hash}". Contact <a href="mailto:martin.shub@gmail.com">martin.shub@gmail.com</a> for any enquiries.
                </td>
            </tr>
        </tfoot>
    </table>
    <div style="position:absolute;bottom:0;width:100%;text-align:center">
        
    </div>
    """

    # convert exhibitions to html bullets
    for t in ["solo_exhibitions", "group_exhibitions"]:
        for index, exhibition in enumerate(data.get(t, [])):
            # no title
            if not exhibition.get("title"):
                data[t][index] = ""
                continue

            # bullet template
            li = "<tr><td colspan='2' style='padding-left: 3rem'>{year}: <span style='background-color:yellow;'>{title}</span>{remaining}</td></tr>"

            # convert json to html
            data[t][index] = li.format(
                year=exhibition.get("year"),
                title=exhibition.get("title"),
                remaining=exhibition.get("original").replace(
                    exhibition.get("title"), ""
                ),
            )

    # populate template
    html = template.format(
        hash=data.get("meta", {}).get("hash") or "Not provided.",
        name=data.get("name") or "Not detected.",
        dob=data.get("dob") or "Not Detected.",
        solo_exhibitions="".join(data.get("solo_exhibitions", []))
        or "<tr><td>Not detected.</td></tr>",
        group_exhibitions="".join(data.get("group_exhibitions", []))
        or "<tr><td>Not detected.</td></tr>",
        input_name=data.get("meta", {}).get("input", {}).get("name") or "Not provided.",
    )

    html2pdf(html, path)

    return path


if __name__ == "__main__":
    # html2pdf(sys.argv[1], sys.argv[2])

    data = {}
    data2pdf(data, "cv-parsed.pdf")
