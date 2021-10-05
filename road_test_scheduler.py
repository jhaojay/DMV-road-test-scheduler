from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import os
import datetime
import gmail_sender
import gmail_receiver


class road_test_scheduler:
    schedule_page = "https://nyrtspublicsite.azurewebsites.net/"
    loading_icon_id = "divLoading"

    def __init__(self, head=None):
        chromedriver_path = os.getcwd() + r"\chrome\chromedriver.exe"
        if head == "headless":
            options = Options()
            options.binary_location = os.getcwd() + r'\chrome\chrome.exe'
            options.add_argument('--headless')
            self.browser = webdriver.Chrome(chromedriver_path, chrome_options=options)
        else:
            self.browser = webdriver.Chrome(chromedriver_path)

    def quit(self):
        self.browser.quit()

    def login(self):
        self.browser.get(self.schedule_page)

    def loading(self):
        try:
            WebDriverWait(self.browser, 600).until(
                ec.invisibility_of_element_located((By.ID, self.loading_icon_id))
            )
            return True
        except TimeoutException:
            print("[!]TimeoutException")
            return False

rts = road_test_scheduler()
rts.login()

#scrolling down to the end of the page
time.sleep(2)
rts.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

# click reCAPTCHA by offsetting
time.sleep(10)
el = rts.browser.find_element_by_id("dayDropdown")
action = ActionChains(rts.browser)
action.move_to_element_with_offset(el, 30,70)
action.click()
action.perform()

# input DOB to the dropdown manual
time.sleep(1)
select = Select(rts.browser.find_element_by_id('monthDropdown'))
select.select_by_visible_text('month')
select = Select(rts.browser.find_element_by_id('dayDropdown'))
select.select_by_visible_text('day')
select = Select(rts.browser.find_element_by_id('yearDropDown'))
select.select_by_visible_text('year')

#inputing my DMVID and hit ENTER
time.sleep(1)
inputElement = rts.browser.find_element_by_id("ClientId")
inputElement.send_keys('your_permit_ID', Keys.ENTER)

#click on New Appointment
rts.browser.find_element_by_xpath("//input[@value='New or Reschedule Appointment']").click()

#bypass "Already have an appointment"
element = rts.browser.find_element_by_xpath("//input[@id='btnContinueSelectTest']")
time.sleep(1)
action = ActionChains(rts.browser)
action.move_to_element_with_offset(element, -3,-3)
action.click()
action.perform()

#entering zip code
time.sleep(1)
inputElement = rts.browser.find_element_by_xpath("//input[@id='Zip']")
inputElement.clear()
inputElement.send_keys('zip_code')

#hit next
time.sleep(2)
el = rts.browser.find_element_by_xpath("//input[@id='btnContinueSelectTest']")
action = ActionChains(rts.browser)
action.move_to_element_with_offset(el, 30,30)
action.click()
action.perform()

#entering contact info
time.sleep(2)
inputElements = rts.browser.find_element_by_xpath("//input[@id='phone1']")
for c in "phone_number":
    time.sleep(0.1)
    inputElements.send_keys(c)
inputElements = rts.browser.find_element_by_xpath("//input[@id='phone2']")
for c in "phone_number":
    time.sleep(0.1)
    inputElements.send_keys(c)
inputElement = rts.browser.find_element_by_xpath("//input[@id='email1']")
inputElement.send_keys('gmail.username@gmail.com')
inputElement = rts.browser.find_element_by_xpath("//input[@id='VerifyEmail']")
inputElement.send_keys('gmail.username@gmail.com')
inputElement.send_keys(Keys.ENTER)

rts.loading()

count = 0
while(1):
    #obtain location info
    location_names = []
    location_dates = []

    target_locations = rts.browser.find_element_by_id("target")
    all_sub_children_by_xpath = target_locations.find_elements_by_xpath("./*")
    location_info = all_sub_children_by_xpath[1].text
    location_names.append(location_info.split('(')[0].strip())
    location_dates.append(location_info.split('map')[-1].strip())

    suggested_locations = rts.browser.find_element_by_id("suggestedCentres")
    all_sub_children_by_xpath = suggested_locations.find_elements_by_xpath("./*")
    for i in range(1, len(all_sub_children_by_xpath)):
        child = all_sub_children_by_xpath[i]
        location_info = child.text
        location_names.append(location_info.split('(')[0].strip())
        location_dates.append(location_info.split('map')[-1].strip())

    print(str(count) + ": " + str(datetime.datetime.now().time()))
    for i in range(len(location_dates)):
        print(location_names[i] + "\t" + location_dates[i])
    print('\n')
    count = count + 1

    #conditions for notification it is super messy!!!
    for i in range(len(location_dates)):
        if(location_names[i] == "Red Hook"):
            month = location_dates[i].split(' ')[1].strip()

            if(month == "Oct" or month == "Sep"):
                day = location_dates[i].split(' ')[2].strip()
                if(int(day)) < 30:
                    msg = "Red Hook is avaliable on  "+ month + day + " !"
                    msg = msg + "\nGO TO REGISTER!!!\n\nDid you get it?"
                    gmail_sender.send_email("gmail.username@gmail.com", msg)
                    notification_time = 10000*datetime.datetime.now().time().hour +\
                                        100*datetime.datetime.now().time().minute +\
                                        datetime.datetime.now().time().second
                    time.sleep(1)
                    while(1):
                        time_now = 10000*datetime.datetime.now().time().hour + \
                                   100*datetime.datetime.now().time().minute + \
                                   datetime.datetime.now().time().second
                        mailtime, subject = gmail_receiver.read_email_from_gmail()

                        if(mailtime > notification_time):
                            if(subject.lower() == 'no'):
                                print("didn't register, continue monitoring DMV")
                                break
                            elif(subject.lower() == 'yes'):
                                print("registered, stop monitoring DMV")
                                rts.quit()
                                quit()

                        if(time_now - notification_time > 500):
                            print("no email response for 5 min, continue monitoring DMV")
                            break
                        else:
                            print(time_now - notification_time)

    time.sleep(10)
    rts.browser.refresh()