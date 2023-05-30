import io
from pathlib import Path
from time import sleep

import PIL.Image
import undetected_chromedriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.common.action_chains import ActionChains
from ultralytics import YOLO

script_dir = Path(__file__).parent
model_path = script_dir.joinpath('unfair_lane.pt')


def main():
    model = YOLO(model_path)
    driver = undetected_chromedriver.Chrome()
    while True:
        driver.get('https://www.pararius.nl/huurwoningen/amsterdam/1300-2000')

        captcha_div = WebDriverWait(
            driver, 20
        ).until(
            presence_of_element_located((By.XPATH, "//div[@id='_csnl_cp']/div"))
        )

        driver.execute_script(draw_cursor())

        captcha_div_png = captcha_div.screenshot_as_png
        image = PIL.Image.open(io.BytesIO(captcha_div_png))
        results = model.predict(image)

        if len(results) == 0:
            print("Couldn't find a solution")

        # Fetch the best solution
        x, y, _, _ = sorted(results, key=lambda result: result.boxes.conf)[0].boxes[0].xywh[0]

        ActionChains(driver).move_to_element_with_offset(
            captcha_div, (-(captcha_div.size['width'] / 2) + x), (-(captcha_div.size['height'] / 2) + y)
        ).click().perform()
        driver.find_element(By.XPATH, "//button[@id='submit_csnl_cp']").click()

        sleep(2)

        driver.delete_all_cookies()
        driver.get('about:blank')


def draw_cursor():
    return '''
function enableCursor() {
  var seleniumFollowerImg = document.createElement("img");
  seleniumFollowerImg.setAttribute('src', 'data:image/png;base64,'
    + 'iVBORw0KGgoAAAANSUhEUgAAABQAAAAeCAQAAACGG/bgAAAAAmJLR0QA/4ePzL8AAAAJcEhZcwAA'
    + 'HsYAAB7GAZEt8iwAAAAHdElNRQfgAwgMIwdxU/i7AAABZklEQVQ4y43TsU4UURSH8W+XmYwkS2I0'
    + '9CRKpKGhsvIJjG9giQmliHFZlkUIGnEF7KTiCagpsYHWhoTQaiUUxLixYZb5KAAZZhbunu7O/PKf'
    + 'e+fcA+/pqwb4DuximEqXhT4iI8dMpBWEsWsuGYdpZFttiLSSgTvhZ1W/SvfO1CvYdV1kPghV68a3'
    + '0zzUWZH5pBqEui7dnqlFmLoq0gxC1XfGZdoLal2kea8ahLoqKXNAJQBT2yJzwUTVt0bS6ANqy1ga'
    + 'VCEq/oVTtjji4hQVhhnlYBH4WIJV9vlkXLm+10R8oJb79Jl1j9UdazJRGpkrmNkSF9SOz2T71s7M'
    + 'SIfD2lmmfjGSRz3hK8l4w1P+bah/HJLN0sys2JSMZQB+jKo6KSc8vLlLn5ikzF4268Wg2+pPOWW6'
    + 'ONcpr3PrXy9VfS473M/D7H+TLmrqsXtOGctvxvMv2oVNP+Av0uHbzbxyJaywyUjx8TlnPY2YxqkD'
    + 'dAAAAABJRU5ErkJggg==');
  seleniumFollowerImg.setAttribute('id', 'selenium_mouse_follower');
  seleniumFollowerImg.setAttribute('style', 'position: absolute; z-index: 99999999999; pointer-events: none; left:0; top:0');
  document.body.appendChild(seleniumFollowerImg);
  document.onmousemove = function (e) {
    document.getElementById("selenium_mouse_follower").style.left = e.pageX + 'px';
    document.getElementById("selenium_mouse_follower").style.top = e.pageY + 'px';
  };
};

enableCursor();
'''


if __name__ == '__main__':
    main()
