#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import numpy as np
import cv2 
import os
import requests
from PIL import Image
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from trueSolver import get_points
from trueSolver2 import PuzleSolver
from selenium.common.exceptions import TimeoutException


def load_website():
    from selenium.webdriver.chrome.options import Options
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    
    chrome_options.add_argument("--window-size=200,1440")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options =chrome_options)
    #driver.maximize_window()

    url = "https://avas.mfa.gov.cn/qzyyCoCommonController.do?yypersoninfo&status=continue&1686142874790&locale=ru_RU"
    driver.get(url)
    print("loaded")
    return driver, url


def enter_form_data(driver):
    fio = "Belkina Tatiana"
    phone = "79058323393"
    email = "miheeva-291980@mail.ru"
    number = "2023053061423288300"

    fio_input = driver.find_element(By.XPATH, "//input[@id='linkname']")
    phone_input = driver.find_element(By.XPATH, "//input[@id='linkphone']")
    email_input = driver.find_element(By.XPATH, "//input[@id='mail']")
    number_input = driver.find_element(By.XPATH, "//input[@id='applyid1']")
    time.sleep(1)
    fio_input.send_keys(fio)
    time.sleep(1)
    phone_input.send_keys(phone)
    time.sleep(1)
    email_input.send_keys(email)
    time.sleep(1)
    number_input.send_keys(number)
    time.sleep(1)
    print("Form data entered successfully")


def submit_form(driver):
    submit_button = driver.find_element(
        By.XPATH, "//div[@class='title_right']/button"
    )
    submit_button.click()
    print("form sent")

def solve(driver):
    iframe = driver.find_element(By.XPATH,"//iframe")
    #print(iframe)
    driver.switch_to.frame(iframe)
    x = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "#slideBg"))
        ).get_attribute("style")

    driver.execute_script(open("script.js").read())
    #driver.execute_script('document.body.innerHTML="hello"')
    #print(driver.page_source)
    print('tut')
    #url = driver.execute_script('return document.querySelector("#slideBg").style.backgroundImage')
    url = driver.execute_script('return document.querySelector("#slideBg").style.backgroundImage')
    print(url)
    divs = driver.find_elements(By.CSS_SELECTOR, "div.unselectable")
    dir(divs)
    url = divs[0].value_of_css_property("background-image").split('"')[1]
    w = divs[0].value_of_css_property("width").replace("px",'')
    h = divs[0].value_of_css_property("height").replace("px",'')
    res = requests.get(url,stream=True)
    #dimensions = res.shape
    im = Image.open(res.raw)
    width, height = im.size
    
    print(width,height)
    #resized = cv2.resize(im, (w,h), interpolation = cv2.INTER_AREA)

    #image = cv2.rectangle(res, width, height)
    #cv2.imshow("ser", image)
    #im.show() 
    part2(driver,w,h)
    #f_css_property("background-image").split('"')[1])
    #body = driver.find_element(By.XPATH,"//body")
    #bgdiv = driver.find_element(By.XPATH,"//div[@id='slideBg']")
    #print(body)
def serSolver(im,w,h):
    print(w,h)
    img = cv2.imread(im, cv2.IMREAD_GRAYSCALE)
    edges = cv2.Canny(img,600,1000,apertureSize = 3)
    dsize = (int(float(w)), int(float(h)))
    
    resized = cv2.resize(edges, dsize, interpolation = cv2.INTER_AREA)
    
    cv2.imwrite('edges-1050___.jpg',resized)
    new_img = cv2.imread('edges-1050___.jpg', cv2.IMREAD_UNCHANGED)
    positions = np.nonzero(new_img)
    #print(positions)

    top = positions[0].min()
    bottom = positions[0].max()
    left = positions[1].min()
    right = positions[1].max()   
    print(right)
    print(right-(right-left))
    return right-(right-left) 

def part2(driver,w,h):
    global distance
    global right
    global left
    print('part2')
    time.sleep(2)
    network_requests = driver.execute_script(
        "return window.performance.getEntries()"
        )
    for request in network_requests:
            if "cap_union_new_getcapbysig?img_index=1" in request["name"]:
                print("Скачиваем задний фон")
                background_image = request["name"]
            elif "cap_union_new_getcapbysig?img_index=0" in request["name"]:
                print("Скачиваем пазл")
                piece_image = request["name"]
                break
    try:
            if background_image:
                response_back = requests.get(background_image)
                response_piece = requests.get(piece_image)
                with open("background.png", "wb") as file:
                    file.write(response_back.content)
                with open("piece.png", "wb") as file:
                    file.write(response_piece.content)
                right = int(serSolver("background.png",w,h))
                #distance = int(get_points("background.png") / 2.6) 
                #solution = solver2.get_position()
                print(f"Нужно передвинуть на {right} пикселей")
                #print(f"Нужно передвинуть на {distance} пикселей")
            else:
                raise ValueError("Отсутствуют ссылки на изображения")
    except Exception as e:
            print("Капча не решаема")
            print(e)
            #os.remove("background1.png")
            #os.remove("piece1.png")
            driver.execute_script('$("#reload").click();') 
            #part2(driver)
            
            #return False

    #slider = wait.until(
    #        EC.presence_of_element_located((By.CSS_SELECTOR, "img[alt='slider']"))
    #    )
    slider = driver.find_elements(By.CSS_SELECTOR, "div.tc-slider-normal")[0]
    offset= int(float(slider.value_of_css_property("left").replace("px",'')))
    print("offset")
    print(offset)
    actions = webdriver.ActionChains(driver)
    actions.click_and_hold(slider).perform()
    #actions.move_by_offset(-offset, 0).perform()
    #time.sleep(1)
    actions.move_by_offset(right-offset-10, 0).perform()
    actions.release(slider).perform()     
    #os.remove("background.png")
    #os.remove("piece.png")
    time.sleep(10)
    #er = driver.execute_script('ext_js + "\n" + "return get_errors()')
    er = driver.execute_script('return document.body.classList.contains("ser")')
    loctest = driver.execute_script('return window.location.href')
    print(loctest)
    print(er)
    if er: 
        time.sleep(2)
        right-=10
        #driver.execute_script('$("#reload").click();') 
        actions.click_and_hold(slider).perform()
        actions.move_by_offset(right, 0).perform()
        actions.release(slider).perform()  
        print('podvinul')
    else: print(er)
    time.sleep(3)       
            
def main():
    # # Initialize ChromeDriver
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    # driver.maximize_window()
    #
    # # Load the website
    # url = "https://avas.mfa.gov.cn/qzyyCoCommonController.do?yypersoninfo&status=continue&1686142874790&locale=ru_RU"
    # driver.get(url)
    # print("Браузер загружен")

    driver, _ = load_website()

    enter_form_data(driver)
    submit_form(driver)
    solve(driver)
    # Reload the page
    print("Перезагружаем страницу")
    #driver.refresh()

    # Close the browser
    #driver.quit()
    #print("Закрываем браузер")


if __name__ == "__main__":
    main()
