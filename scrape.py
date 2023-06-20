from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd

driver = webdriver.Firefox()
wait = WebDriverWait(driver, 10)

# prompt log in
driver.get("https://account.baywheels.com/ride-history")

# enter phone number and submit button
phone_input = driver.find_element_by_id("phone")
phone_number = input("Enter phone number: ")
phone_input.send_keys(phone_number)
next_button = driver.find_element_by_css_selector("button[data-testid='formSubmit']")
next_button.click()

# enter auth code
auth_code = input("Enter the auth code: ")
auth_input = driver.find_element_by_name("phoneCode")
auth_input.send_keys(auth_code)

# click button to verify identity
confirm_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-aid='challenge']")))
confirm_button.click()

# enter email and submit button
email_input = driver.find_element_by_name("email")
email = input("Enter email: ")
email_input.send_keys(email)
final_button = driver.find_element_by_css_selector("button[data-testid='form-submit']")
final_button.click()

# go back to ride history
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-tracking-label='profile']")))
driver.get("https://account.baywheels.com/ride-history")

# keep clicking "show more" until all rides are displayed
show_more_selector = "button[data-testid='DATA_TESTID_SHOW_MORE'][aria-disabled='false']"
try:
    show_more = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, show_more_selector)))
    while show_more:
        driver.execute_script("return arguments[0].parentNode;", show_more).click()
        show_more = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, show_more_selector)))
except TimeoutException:
    pass

# go through every card and expand
ride_card_selector = "div[data-testid='DATA_TESTID_RIDE_OVERVIEW_CARD']"
ride_cards = driver.find_elements_by_css_selector(ride_card_selector)
for card in ride_cards:
    card.click()

# collect details about each ride
d = {'date': [], 'bike_id': [], 'price': [], 'start_time': [], 'end_time': []}

details_selector = "div[data-testid='DATA_TESTID_RIDE_DETAILS_INFO']"
for card, details in zip(driver.find_elements_by_css_selector(ride_card_selector), 
                driver.find_elements_by_css_selector(details_selector)):
    date, bike_id = [c.text for c in card.find_elements_by_xpath('./div/div')]

    price = card.find_element_by_xpath(".//*[contains(text(), 'Price')]/..").text
    price = price[7:]
    
    start, end = [d.text for d in details.find_elements_by_xpath('./div/div/div/div')]
    start, end = start[11:], end[9:]

    d['date'].append(date)
    d['bike_id'].append(bike_id)
    d['price'].append(price)
    d['start_time'].append(start)
    d['end_time'].append(end)

# save to dataframe, csv
df = pd.DataFrame(d)
df.to_csv('past_rides.csv')