from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import  json
import time

with open("account.json", 'r') as f:
    data = json.load(f)

username = data["username"]
password = data["password"]


def find_input_username(driver):
    try:
        inputname = driver.find_element(By.NAME, "username")
        return True

    except Exception:
            return False

def find_buttons(driver, button_labels):
    results = []

    # Access main page and frames
    frames = [driver] + driver.find_elements(By.TAG_NAME, "iframe")
    print(frames)

    # Search each frame
    for index, frame in enumerate(frames):
        # Switch to each frame; if it's the main document, no switch is necessary
        if frame is not driver:
            driver.switch_to.frame(frame)

        # Search for buttons by iterating over the labels
        for label in button_labels:
            try:
                # Look for elements with visible text matching any of the button labels
                # Convert label to lowercase for case insensitive matching
                buttons = WebDriverWait(frame, 0.5).until(
                    EC.presence_of_all_elements_located((By.XPATH, f"//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{label.lower()}')]"))
                )
                # Check each button if it is visible and add to results
                for button in buttons:
                    if button.is_displayed():
                        results.append(button)
            except TimeoutException:
                # Timeout implies no buttons found in the current frame with the current label
                continue
            except NoSuchElementException:
                # If no such element exists, skip to next label
                continue

        # Switch back to the main document to reset the frame
        if frame is not driver:
            driver.switch_to.default_content()

    # Return the list of buttons found
    return results

def find_buttons_main(driver, button_labels):
    results = []  # List to store found buttons

    # Iterate over each label to find buttons on the main page
    for label in button_labels:
        try:
            # Convert label to lowercase for case insensitive matching
            # Use XPath to match the text of button elements
            buttons = WebDriverWait(driver, 0.5).until(
                EC.presence_of_all_elements_located((By.XPATH,
            f"//button[contains(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{label.lower()}')]|"
            f"//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{label.lower()}')]|"
            f"//div[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{label.lower()}')]|"
            f"//span[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{label.lower()}')]"))
            )
            # Add visible buttons to results
            for button in buttons:
                if button.is_displayed() and button.is_enabled():  # Check if button is visible
                    results.append(button)
        except TimeoutException:
            # Handle timeout if no buttons are found within the given time
            print(f"No buttons found with label: {label}")
        except NoSuchElementException:
            # Handle case where no such button exists
            print(f"No element found for label: {label}")

    return results

def save_page(driver, name):
    try:
        html_content = driver.page_source
        with open(f'{name}.html', 'w', encoding='utf-8') as f:
            f.write(html_content)

    except StaleElementReferenceException:
        print("StaleElementReferenceException: Element is not attached to the page document.")
    except TimeoutException:
        print("TimeoutException: The page did not load within the expected time.")


def main():

    url = "https://app.grammarly.com/"
    # Set up Chrome WebDriver
    service = Service('D:\Aqualab\chromedriver-win64\chromedriver-win64\chromedriver.exe')
    driver = webdriver.Chrome(service=service)


    try:
        driver.get(url)
        time.sleep(2)

        # Usage example (assuming 'driver' is already defined and configured)
        button_labels = ["log in", "sign in", "account", "my account"]
        auth_buttons = ["Sign up with Google", "Sign in with Google", "Continue with Google", "Log in with Google", "Login with Google", "Register with Google"]


        print("Try to find login buttons")
        found_buttons = find_buttons_main(driver, button_labels)
        print(found_buttons)
        i = 0
        for btn in found_buttons:

                btn.click()
                time.sleep(2)
                save_page(driver, f"output-{i}.html")
                cur_url = driver.current_url


                oauthbuttons = find_buttons_main(driver, auth_buttons)

                if len(oauthbuttons)>0:
                    print("Find SSO login: ",  oauthbuttons)
                    main_window = driver.current_window_handle


                    for b in oauthbuttons:
                        b.click()
                        try:
                            WebDriverWait(driver,10).until(EC.number_of_windows_to_be(2))
                            print("Redirect to a separate SSO page")
                            print(driver.window_handles)
                            for handle in driver.window_handles:
                                if handle != main_window:
                                    driver.switch_to.window(handle)
                                    sso_url = driver.current_url
                                    save_page(driver, "aha")
                                    print("the redirect SSO url: ", sso_url)



                        except Exception as e:
                            print(e)


                # print(f"Found button with text: {btn.text}")
                i += 1

            # except StaleElementReferenceException:
            #     print("StaleElementReferenceException: Element is not attached to the page document.")
            #
            # except Exception:
            #     print(Exception)


        #
        # # search_box = driver.find_element("name", "q")
        # sign_in_button = driver.find_element(By.LINK_TEXT, "Sign In")
        # sign_in_button.click()
        # time.sleep(3)
        # # Type the search term and submit
        #
        # google_sso_button = driver.find_element(By.XPATH, '//button[contains(@aria-label, "Google")]')
        # google_sso_button.click()
        # time.sleep(5)
        #
        # # Output the title of the page
        # print("Page title:", driver.title)

    except Exception as e:
        print(e)

    finally:
        # Close the browser
        # print(sso_url)
        driver.quit()

if __name__ == "__main__":
    main()
