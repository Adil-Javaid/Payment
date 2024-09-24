import os
import time
import json
import re
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from twocaptcha import TwoCaptcha
import sys

# Load parameters from command-line argument
data = json.loads(sys.argv[1])

# Example: Access user information
sign_up_username = data['username']
sign_up_password = data['password']

# CONFIGURATION
url = "https://admin.pinkrose.uno/users.php"
apikey = "8ce373d9940e907e325cca294bc7e0b7"



intercept_script = """ 
    console.clear = () => console.log('Console was cleared')
    const i = setInterval(()=>{
        if (window.turnstile) {
            console.log('success!!');
            clearInterval(i);
            window.turnstile.render = (a,b) => {
                let params = {
                    sitekey: b.sitekey,
                    pageurl: window.location.href,
                    data: b.cData,
                    pagedata: b.chlPageData,
                    action: b.action,
                    userAgent: navigator.userAgent,
                };
                console.log('intercepted-params:' + JSON.stringify(params));
                window.cfCallback = b.callback;
                return;
            };
        }
    }, 50);   
"""

# LOCATORS
success_message_locator = "//p[contains(@class,'successMessage')]"
username_locator = "user"
password_locator = "passwd"
submit_button_locator = "dologin"
close_modal_button_locator = "//button[@type='button' and @data-dismiss='modal']"
users_menu_locator = "//a[@href='users.php' and contains(@class,'collapsible-header')]"
new_user_button_locator = "//button[@id='NewUserButton']"
register_user_button_locator = "//button[@id='ModalNewUserPlayerSubmit']"
register_username_textFeild_locator = "NewUserPlayerUsername"
register_userpassword_textFeild_locator = "NewUserPlayerPassword"

# GETTERS
def get_element(locator):
    """Waits for an element to be clickable and returns it."""
    return WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.XPATH, locator)))

# ACTIONS
def get_captcha_params(script):
    """Refreshes the page, injects a script to intercept Turnstile parameters, and retrieves them."""
    browser.refresh()
    browser.execute_script(script)
    time.sleep(5)
    logs = browser.get_log("browser")
    params = None
    for log in logs:
        if "intercepted-params:" in log['message']:
            log_entry = log['message'].encode('utf-8').decode('unicode_escape')
            match = re.search(r'intercepted-params:({.*?})', log_entry)
            if match:
                json_string = match.group(1)
                params = json.loads(json_string)
                break
    print("Parameters received")
    return params

def solver_captcha(apikey, params):
    """Solves the Turnstile captcha using the 2Captcha service."""
    solver = TwoCaptcha(apikey)
    try:
        result = solver.turnstile(
            sitekey=params["sitekey"],
            url=params["pageurl"],
            action=params["action"],
            data=params["data"],
            pagedata=params["pagedata"],
            useragent=params["userAgent"]
        )
        print(f"Captcha solved")
        return result['code']
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def send_token_callback(token):
    """Executes the callback function with the given token."""
    script = f"cfCallback('{token}')"
    browser.execute_script(script)
    print("The token is sent to the callback function")

def final_message(locator):
    """Retrieves and prints the final success message."""
    message = get_element(locator).text
    print(message)

def wait_for_login_screen():
    """Waits for the login screen elements to be visible and interactable."""
    try:
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.ID, username_locator)))
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.ID, password_locator)))
        WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.ID, submit_button_locator)))
        print("Login screen is ready.")
    except Exception as e:
        print(f"Login screen did not appear in the expected time: {e}")

def login(username, password):
    """Logs into the admin site using provided credentials."""
    try:
        WebDriverWait(browser, 15).until(EC.visibility_of_element_located((By.ID, username_locator)))
        username_field = browser.find_element(By.ID, username_locator)
        WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, password_locator)))
        password_field = browser.find_element(By.ID, password_locator)
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.ID, submit_button_locator)))
        submit_button = browser.find_element(By.ID, submit_button_locator)

        username_field.clear()
        password_field.clear()

        username_field.send_keys(username)
        password_field.send_keys(password)
        submit_button.click()
        print(f"User '{username}' logged in successfully.")
        time.sleep(3)

        if WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, success_message_locator))):
            final_message(success_message_locator)
        else:
            print("Success message not found. Verify login success manually.")

    except Exception as e:
        print(f"Login failed: {e}")

def close_modal_if_present():
    """Closes the modal if the close button is present."""
    try:
        close_button = WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.XPATH, close_modal_button_locator)))
        close_button.click()
        print("Modal closed.")
    except Exception as e:
        print(f"Modal close button not found or already closed: {e}")

def navigate_to_users_and_create_new_user():
    """Clicks on the 'Users' menu and then the 'New User' button."""
    try:
        # Close modal if present
        close_modal_if_present()
        time.sleep(5)
        # Click on the "Users" menu
        users_menu = WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, users_menu_locator)))
        users_menu.click()
        time.sleep(5)
        print("Clicked on the 'Users' menu.")
        # Close modal if present
        close_modal_if_present()
        time.sleep(5)
        # Wait for the "New User" button to be visible and click it
        new_user_button = WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, new_user_button_locator)))
        new_user_button.click()
        print("Clicked on the 'New User' button.")
        time.sleep(5)
        WebDriverWait(browser, 15).until(EC.visibility_of_element_located((By.ID, register_username_textFeild_locator)))
        username_field = browser.find_element(By.ID, register_username_textFeild_locator)
        WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, register_userpassword_textFeild_locator)))
        password_field = browser.find_element(By.ID, register_userpassword_textFeild_locator)

        username_field.clear()
        password_field.clear()

        username_field.send_keys(sign_up_username)
        password_field.send_keys(sign_up_password)
        time.sleep(5)
        # Wait for the "New User" to be a register
        new_user_button = WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, register_user_button_locator)))
        new_user_button.click()
        print("Clicked on the 'New User' button.")
    except Exception as e:
        print(f"Failed to navigate and click on elements: {e}")

# MAIN LOGIC
chrome_options = Options()
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
chrome_options.set_capability("goog:loggingPrefs", {"browser": "INFO"})

with webdriver.Chrome(service=Service(), options=chrome_options) as browser:
    browser.get(url)
    print("Started")

    params = get_captcha_params(intercept_script)

    if params:
        token = solver_captcha(apikey, params)
        if token:
            send_token_callback(token)
            wait_for_login_screen()
            login('botmarley1', 'aa123aa')  # Replace with your actual credentials
            time.sleep(5)
            
            # Navigate to "Users" and click "New User"
            navigate_to_users_and_create_new_user()
            time.sleep(15)
            print("Finished")
        else:
            print("Failed to solve captcha")
    else:
        print("Failed to intercept parameters")