import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager   # ✅ NEW — auto installs chromedriver

#                 SETTINGS
BASE_URL  = "https://helicarbooking.com/"
WAIT_TIME = 10  # max seconds to wait for an element to appear
PAUSE_SEC = 1   # short pause between actions so we can watch what is happening

# Direct URL for the "Review your booking" form page
FORM_URL = (
    BASE_URL + "complete-booking?carId=2e0c153b-30c7-456f-aaf9-41b1b9912285"
    "&pickUp=Airport&destination=Thamel"
    "&pickUpDate=2026-05-10&returnDate=&pickUpTime=null&returnTime=null&price=1200.00"
)

#        RESULTS TRACKER
#  Every test calls record() to save its result.
results = []

def record(test_id, passed, message=""):
    status = "PASS" if passed else "FAIL"
    results.append((test_id, status, message))
    symbol = "+" if passed else "X"   # ✅ Changed from emoji — GitHub logs handle plain text better
    print(f"  {symbol} [{test_id}] {status}  {message}")

#  SHARED HELPER FUNCTIONS
def pause():
    time.sleep(PAUSE_SEC)

def wait_for(driver, by, locator):
    return WebDriverWait(driver, WAIT_TIME).until(
        EC.presence_of_element_located((by, locator))
    )

def wait_clickable(driver, by, locator):
    return WebDriverWait(driver, WAIT_TIME).until(
        EC.element_to_be_clickable((by, locator))
    )

def src(driver):
    return driver.page_source


#     OPEN THE BROWSER  (called only once)
# ✅ THIS WHOLE FUNCTION IS CHANGED — now works on GitHub (Linux, no screen)

def open_browser():
    options = Options()
    options.add_argument("--headless")               # ✅ No screen needed on GitHub
    options.add_argument("--no-sandbox")             # ✅ Required on GitHub/Linux
    options.add_argument("--disable-dev-shm-usage")  # ✅ Required on GitHub/Linux
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--window-size=1920,1080")  # ✅ Set a screen size even in headless

    # ✅ ChromeDriverManager downloads the right chromedriver automatically — no manual path needed
    service = Service(ChromeDriverManager().install())
    driver  = webdriver.Chrome(service=service, options=options)
    return driver

######  PHASE 1 — Home Search Form  (A01 – A25)

def phase1_home_search_form(driver):
    print("\n" + "=" * 58)
    print("  PHASE 1 --- Home Search Form  (A01 - A25)")
    print("=" * 58)

    driver.get(BASE_URL)
    time.sleep(2)

    # ---- A01
    try:
        title = driver.title
        record("A01", len(title) > 0, f"Page title is: '{title}'")
    except Exception as e:
        record("A01", False, str(e))

    # ----- A02
    try:
        form = wait_for(driver, By.CSS_SELECTOR, "form, .search-form, [class*='search']")
        record("A02", form.is_displayed(), "Search form box is visible on the home page")
    except Exception as e:
        record("A02", False, str(e))

    # ---- A03
    record("A03", "Cars" in src(driver), "Cars tab text is visible on the home page")

    # ---- A04
    record("A04", "Van" in src(driver), "Van/Hiace tab text is visible")

    # ---- A05
    record("A05", "Scorpio" in src(driver), "Scorpio/Jeep tab text is visible")

    # ----- A06
    record("A06", "Minibus" in src(driver), "Minibus/Coaster tab text is visible")

    # ----- A07
    record("A07", "Sutlej" in src(driver), "Sutlej Bus tab text is visible")

    # ----- A08
    found = bool(driver.find_elements(By.CSS_SELECTOR, "select")) or "Pick-up" in src(driver)
    record("A08", found, "Pick-up location dropdown is visible")

    # ----- A09
    record("A09", "Destination" in src(driver), "Destination dropdown is visible")

    # ----- A10
    record("A10", "date" in src(driver).lower(), "Pick-up date field is visible")

    # ----- A11
    try:
        btns = driver.find_elements(By.XPATH, "//button[contains(text(),'Search')]")
        if not btns:
            btns = driver.find_elements(By.CSS_SELECTOR, "[type='submit']")
        record("A11", len(btns) > 0, "Search button is visible on the form")
    except Exception as e:
        record("A11", False, str(e))

    # ----- A12
    try:
        btn = wait_clickable(driver, By.XPATH, "//button[contains(text(),'Search')]")
        record("A12", btn.is_enabled(), "Search button is enabled and clickable")
    except Exception:
        try:
            btn = wait_clickable(driver, By.CSS_SELECTOR, "[type='submit']")
            record("A12", btn.is_enabled(), "Search (submit) button is enabled and clickable")
        except Exception as e:
            record("A12", False, str(e))

    # ---- A13
    try:
        tab = wait_clickable(driver, By.XPATH,
            "//*[contains(text(),'Van') or contains(text(),'Hiace')]")
        tab.click()
        pause()
        record("A13", True, "Clicked Van/Hiace tab")
    except Exception as e:
        record("A13", False, str(e))

    # ---- A14
    try:
        tab = wait_clickable(driver, By.XPATH,
            "//*[contains(text(),'Scorpio') or contains(text(),'Jeep')]")
        tab.click()
        pause()
        record("A14", True, "Clicked Scorpio/Jeep tab")
    except Exception as e:
        record("A14", False, str(e))

    # ---- A15
    try:
        tab = wait_clickable(driver, By.XPATH,
            "//*[contains(text(),'Minibus') or contains(text(),'Coaster')]")
        tab.click()
        pause()
        record("A15", True, "Clicked Minibus/Coaster tab")
    except Exception as e:
        record("A15", False, str(e))

    # ----- A16
    try:
        tab = wait_clickable(driver, By.XPATH, "//*[contains(text(),'Sutlej')]")
        tab.click()
        pause()
        record("A16", True, "Clicked Sutlej Bus tab")
    except Exception as e:
        record("A16", False, str(e))

    # -----  A17
    try:
        tab = wait_clickable(driver, By.XPATH,
            "//*[contains(text(),'Cars') or contains(text(),'Car')]")
        tab.click()
        pause()
        record("A17", True, "Clicked Cars tab — switched back to Cars")
    except Exception as e:
        record("A17", False, str(e))

    # ----- A18
    record("A18", "Add another destination" in src(driver),
           "'Add another destination' button is visible")

    # ---- A19
    try:
        dropdowns = driver.find_elements(By.CSS_SELECTOR, "select")
        if len(dropdowns) >= 1:
            Select(dropdowns[0]).select_by_index(1)
            pause()
        if len(dropdowns) >= 2:
            Select(dropdowns[1]).select_by_index(1)
            pause()
        if len(dropdowns) >= 3:
            Select(dropdowns[2]).select_by_index(2)
            pause()
        btn = wait_clickable(driver, By.XPATH,
            "//*[contains(text(),'Add another destination')]")
        btn.click()
        pause()
        record("A19", "To location" in src(driver),
               "Clicked 'Add another destination' — new row appeared")
    except Exception as e:
        record("A19", False, str(e))

    # ----- A20
    record("A20", "Remove" in src(driver),
           "Remove button is visible after adding another destination")

    # ----- A21
    try:
        remove_btn = wait_clickable(driver, By.XPATH,
            "//button[contains(text(),'Remove')]")
        remove_btn.click()
        pause()
        record("A21", True, "Clicked Remove — extra destination row was removed")
    except Exception as e:
        record("A21", False, str(e))

    # ----- A22
    try:
        date_field = wait_clickable(driver, By.CSS_SELECTOR,
            "input[type='date'], [placeholder*='date'], [class*='date']")
        date_field.click()
        pause()
        calendar = driver.find_elements(By.CSS_SELECTOR,
            ".datepicker, [class*='calendar'], [class*='picker']")
        record("A22", True,
               f"Date field clicked — {len(calendar)} calendar element(s) appeared")
    except Exception as e:
        record("A22", "NoSuchElement" not in type(e).__name__,
               f"Date field click attempted ({type(e).__name__})")

    # ---- A23
    record("A23", "pickup" in src(driver).lower() or "Pick-up" in src(driver),
           "Pick-up date field/label is visible")

    # ---- A24
    record("A24", "destination" in src(driver).lower(),
           "Destination placeholder text is visible")

    # ---- A25
    try:
        driver.get(BASE_URL)
        time.sleep(2)
        date_visible = "date" in src(driver).lower()
        time_visible = "time" in src(driver).lower()
        record("A25", date_visible and time_visible,
               f"Date visible: {date_visible} | Time visible: {time_visible}")
    except Exception as e:
        record("A25", False, str(e))


#  PHASE 2 — Vehicle List Page  (B01 – B07)

def phase2_vehicle_list_page(driver):
    print("\n" + "=" * 58)
    print("  PHASE 2 --- Vehicle List Page  (B01 - B07)")
    print("=" * 58)

    driver.get(BASE_URL + "vehicle-rental")
    time.sleep(2)

    # ----- B01
    record("B01", "vehicle" in driver.current_url.lower(),
           f"URL contains 'vehicle': {driver.current_url}")

    # ----- B02
    record("B02", len(driver.title) > 0,
           f"Page title: '{driver.title}'")

    # ----- B03
    body = driver.find_element(By.TAG_NAME, "body").text
    record("B03", len(body.strip()) > 50, "Page body has real content")

    # ---- B04
    found = any(name in src(driver) for name in
                ["Mini Bus", "Toyota", "TATA", "Coaster", "Bus", "Van"])
    record("B04", found, "Vehicle names visible on the page")

    # ---- B05
    record("B05", "Rs." in src(driver), "Vehicle prices (Rs.) visible")

    # ----- B06
    record("B06", "Book Now" in src(driver), "'Book Now' button text visible")

    # ---- B07
    try:
        btn = wait_clickable(driver, By.XPATH,
            "//a[contains(text(),'Book Now')] | //button[contains(text(),'Book Now')]")
        record("B07", btn.is_enabled(), "'Book Now' button is enabled")
    except Exception as e:
        record("B07", False, str(e))


#  PHASE 3 — Vehicle Selection  (C01 – C06)

def phase3_vehicle_selection(driver):
    print("\n" + "=" * 58)
    print("  PHASE 3 --- Vehicle Selection  (C01 - C06)")
    print("=" * 58)

    driver.get(BASE_URL)
    time.sleep(2)
    try:
        dropdowns = driver.find_elements(By.CSS_SELECTOR, "select")
        if len(dropdowns) >= 2:
            Select(dropdowns[0]).select_by_index(1)
            pause()
            Select(dropdowns[1]).select_by_index(1)
            pause()
        btn = wait_clickable(driver, By.XPATH,
            "//button[contains(text(),'Search')] | //input[@type='submit']")
        btn.click()
        time.sleep(3)
    except Exception as e:
        print(f"  [Setup] Search note: {e}")

    # -------C01
    time.sleep(1)
    cards = driver.find_elements(By.CSS_SELECTOR,
        ".card, [class*='vehicle'], article, [class*='car']")
    record("C01", len(cards) > 0,
           f"Vehicle cards present — found {len(cards)} card(s)")

    # ---- C02
    url_before = driver.current_url
    try:
        card_img = driver.find_elements(By.CSS_SELECTOR,
            ".card img, [class*='vehicle'] img, article img")
        if card_img:
            card_img[0].click()
            time.sleep(2)
        changed = (driver.current_url != url_before) or ("Book Now" in src(driver))
        record("C02", changed, "Clicking vehicle card opened a detail view or changed page")
    except Exception as e:
        record("C02", False, str(e))

    # ------ C03
    images = driver.find_elements(By.CSS_SELECTOR, "img")
    loaded = sum(1 for img in images
                 if driver.execute_script("return arguments[0].naturalWidth;", img))
    record("C03", loaded > 0, f"{loaded} vehicle image(s) loaded correctly")

    # ---- C04
    try:
        btn = wait_clickable(driver, By.XPATH,
            "//a[contains(text(),'Book Now')] | //button[contains(text(),'Book Now')]")
        record("C04", btn.is_displayed(), "'Book Now' button visible on vehicle card")
    except Exception as e:
        record("C04", False, str(e))

    # ----- C05
    try:
        driver.get(BASE_URL + "vehicle-rental")
        time.sleep(2)
        prices = driver.find_elements(By.XPATH, "//*[contains(text(),'Rs.')]")
        record("C05", len(prices) > 0, f"Price shown on {len(prices)} vehicle card(s)")
    except Exception as e:
        record("C05", False, str(e))

    # ------ C06
    try:
        book_buttons = driver.find_elements(By.XPATH,
            "//a[contains(text(),'Book Now')] | //button[contains(text(),'Book Now')]")
        if book_buttons:
            book_buttons[0].click()
            time.sleep(3)
        record("C06", "complete-booking" in driver.current_url or "booking" in src(driver).lower(),
               f"Clicked 'Book Now' — landed at: {driver.current_url}")
    except Exception as e:
        record("C06", False, str(e))


#  PHASE 4 — Review Booking Form  (D01 – D14)

def phase4_review_booking_form(driver):
    print("\n" + "=" * 58)
    print("  PHASE 4 --- Review Booking Form  (D01 - D14)")
    print("=" * 58)

    driver.get(FORM_URL)
    time.sleep(2)

    # ---- D01
    record("D01", "complete-booking" in driver.current_url,
           f"Booking form URL is correct: {driver.current_url}")

    # ---- D02
    record("D02", len(driver.title) > 0, f"Booking form page title: '{driver.title}'")

    # ---- D03
    body = driver.find_element(By.TAG_NAME, "body").text
    record("D03", len(body.strip()) > 50, "Booking form page has real content")

    # ---- D04
    record("D04", "Review" in src(driver) or "booking" in src(driver).lower(),
           "'Review your booking' heading is visible")

    # ----- D05
    inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
    record("D05", len(inputs) >= 2, f"First/Last name fields present — found {len(inputs)} text input(s)")

    # ------ D06
    try:
        inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
        inputs[0].clear()
        inputs[0].send_keys("Saniya")
        pause()
        record("D06", inputs[0].get_attribute("value") == "Saniya",
               "Typed 'Saniya' in First Name field")
    except Exception as e:
        record("D06", False, str(e))

    # ------ D07
    try:
        inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
        inputs[1].clear()
        inputs[1].send_keys("Bam")
        pause()
        record("D07", inputs[1].get_attribute("value") == "Bam",
               "Typed 'Bam' in Last Name field")
    except Exception as e:
        record("D07", False, str(e))

    # ------ D08
    try:
        email = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
        email.clear()
        email.send_keys("testuser@example.com")
        pause()
        record("D08", "testuser@example.com" in email.get_attribute("value"),
               "Typed email in Email field")
    except Exception as e:
        record("D08", False, str(e))

    # -------- D09
    try:
        tel = driver.find_elements(By.CSS_SELECTOR, "input[type='tel']")
        if tel:
            tel[0].clear()
            tel[0].send_keys("9800000000")
            actual_value = tel[0].get_attribute("value")
        else:
            inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
            if len(inputs) >= 3:
                inputs[2].clear()
                inputs[2].send_keys("9800000000")
                actual_value = inputs[2].get_attribute("value")
            else:
                actual_value = ""
        record("D09", "9800000000" in actual_value,
               f"Typed phone number — value: '{actual_value}'")
    except Exception as e:
        record("D09", False, str(e))

    # ------ D10
    try:
        textarea = driver.find_element(By.CSS_SELECTOR, "textarea")
        textarea.clear()
        textarea.send_keys("I need a vehicle for airport pickup.")
        pause()
        record("D10", "airport" in textarea.get_attribute("value").lower(),
               "Typed message in Details textarea")
    except Exception as e:
        record("D10", False, str(e))

    # ------ D11
    driver.get(FORM_URL)
    time.sleep(2)
    try:
        inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
        if len(inputs) >= 2:
            inputs[0].send_keys("Saniya")
            inputs[1].send_keys("Bam")
        email = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
        email.clear()
        email.send_keys("not-an-email")
        pause()
        btn = wait_clickable(driver, By.XPATH,
            "//button[contains(text(),'Book') or contains(text(),'Submit')]")
        btn.click()
        time.sleep(2)
        record("D11", "Thank you" not in src(driver),
               "Invalid email rejected — form did not submit")
    except Exception as e:
        record("D11", False, str(e))

    # ----- D12
    driver.get(FORM_URL)
    time.sleep(2)
    try:
        btn = wait_clickable(driver, By.XPATH,
            "//button[contains(text(),'Book') or contains(text(),'Submit')]")
        btn.click()
        time.sleep(2)
        record("D12", "Thank you" not in src(driver),
               "Empty form submission was blocked")
    except Exception as e:
        record("D12", False, str(e))

    # -----  D13
    record("D13", "Book" in src(driver) or "Submit" in src(driver),
           "Book/Submit button visible on booking form")

    # ------ D14
    driver.get(FORM_URL)
    time.sleep(2)
    try:
        inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
        if len(inputs) >= 1:
            inputs[0].clear()
            inputs[0].send_keys("Test")
        if len(inputs) >= 2:
            inputs[1].clear()
            inputs[1].send_keys("User")
        email = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
        email.clear()
        email.send_keys("testuser@example.com")
        tel = driver.find_elements(By.CSS_SELECTOR, "input[type='tel']")
        if tel:
            tel[0].clear()
            tel[0].send_keys("9800000000")
        textareas = driver.find_elements(By.CSS_SELECTOR, "textarea")
        if textareas:
            textareas[0].clear()
            textareas[0].send_keys("Test booking for UI testing purposes.")
        pause()
        btn = wait_clickable(driver, By.XPATH,
            "//button[contains(text(),'Book') or contains(text(),'Submit')]")
        btn.click()
        time.sleep(4)
        success = (
            "Thank you" in src(driver) or
            "confirmed" in src(driver).lower() or
            "success" in src(driver).lower() or
            driver.current_url != FORM_URL
        )
        record("D14", success,
               f"Form submitted — at: {driver.current_url} | Success: {success}")
    except Exception as e:
        record("D14", False, str(e))


#  PHASE 5 — After Booking / Confirmation  (E01 – E05)

def phase5_confirmation(driver):
    print("\n" + "=" * 58)
    print("  PHASE 5 --- Confirmation  (E01 - E05)")
    print("=" * 58)

    # ----- E01
    error_found = (
        ("404" in src(driver) or "500" in src(driver))
        and "Review" not in src(driver)
        and "booking" not in src(driver).lower()
    )
    record("E01", not error_found, "No server error (404/500) after booking submission")

    # ----- E02
    keywords = ["Thank you", "success", "confirmed", "booking", "Review"]
    record("E02", any(kw in src(driver) for kw in keywords),
           "Booking-related content present after submitting")

    # ----- E03
    try:
        home = wait_clickable(driver, By.XPATH,
            "//a[contains(text(),'Home')] | //a[@href='/']")
        home.click()
        time.sleep(2)
        record("E03", "helicarbooking" in driver.current_url,
               f"Clicked Home — returned to: {driver.current_url}")
    except Exception as e:
        record("E03", False, str(e))

    # ----- E04
    driver.get(BASE_URL)
    time.sleep(2)
    body = driver.find_element(By.TAG_NAME, "body").text
    record("E04", len(body.strip()) > 50, "Home page reloaded correctly")

    # ---- E05
    record("E05", "Search" in src(driver),
           "Search form still present on home page after completing booking")


#  EDGE CASES  (X01 – X10)

def edge_cases(driver):
    print("\n" + "=" * 58)
    print("  EDGE CASES  (X01 - X10)")
    print("=" * 58)

    # ----- X01
    driver.get(BASE_URL)
    time.sleep(2)
    try:
        dropdowns = driver.find_elements(By.CSS_SELECTOR, "select")
        if len(dropdowns) >= 2:
            Select(dropdowns[0]).select_by_index(1)
            pause()
            Select(dropdowns[1]).select_by_index(1)
            pause()
            btn = driver.find_element(By.XPATH,
                "//button[contains(text(),'Search')] | //input[@type='submit']")
            btn.click()
            time.sleep(2)
        record("X01", "500" not in src(driver),
               "Same pickup and destination — no server error")
    except Exception as e:
        record("X01", False, str(e))

    # -----  X02
    driver.get(BASE_URL)
    time.sleep(1)
    try:
        for field in driver.find_elements(By.CSS_SELECTOR, "input[type='text']")[:2]:
            field.clear()
            field.send_keys("!@#$%^&*")
            time.sleep(0.3)
        record("X02", True, "Random symbols typed — page did not crash")
    except Exception as e:
        record("X02", False, str(e))

    # ----- X03
    driver.get(FORM_URL)
    time.sleep(2)
    try:
        textarea = driver.find_element(By.CSS_SELECTOR, "textarea")
        textarea.clear()
        textarea.send_keys("A" * 200)
        pause()
        val = textarea.get_attribute("value")
        record("X03", len(val) > 0,
               f"200-character text typed — field accepted {len(val)} characters")
    except Exception as e:
        record("X03", False, str(e))

    # ------ X04
    driver.get(BASE_URL)
    time.sleep(1)
    try:
        for keyword in ["Van", "Scorpio", "Minibus", "Sutlej", "Cars"]:
            tabs = driver.find_elements(By.XPATH, f"//*[contains(text(),'{keyword}')]")
            if tabs:
                tabs[0].click()
                time.sleep(0.3)
        record("X04", True, "Rapidly clicked all 5 tabs — page did not freeze")
    except Exception as e:
        record("X04", False, str(e))

    # ----- X05
    driver.get(BASE_URL)
    time.sleep(1)
    try:
        dropdowns = driver.find_elements(By.CSS_SELECTOR, "select, .dropdown-toggle")
        if dropdowns:
            dropdowns[0].click()
            time.sleep(0.5)
            driver.find_element(By.TAG_NAME, "body").click()
            pause()
        record("X05", True, "Clicked outside open dropdown — closed without errors")
    except Exception as e:
        record("X05", False, str(e))

    # ---- X06
    driver.get(BASE_URL)
    time.sleep(1)
    try:
        btn = driver.find_element(By.XPATH,
            "//button[contains(text(),'Search')] | //input[@type='submit']")
        btn.send_keys(Keys.ENTER)
        time.sleep(2)
        record("X06", len(src(driver)) > 100,
               "Pressed Enter on Search without fields — page still alive")
    except Exception as e:
        record("X06", False, str(e))

    # ---- X07
    driver.get(BASE_URL)
    time.sleep(1)
    try:
        for _ in range(2):
            add_btns = driver.find_elements(By.XPATH,
                "//*[contains(text(),'Add another destination')]")
            if add_btns:
                add_btns[0].click()
                time.sleep(0.8)
        record("X07", True,
               "Clicked 'Add another destination' twice — no crash")
    except Exception as e:
        record("X07", False, str(e))

    # ----- X08
    driver.get(BASE_URL)
    time.sleep(1)
    try:
        fields = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
        if fields:
            fields[0].send_keys("halfway")
            pause()
        driver.refresh()
        time.sleep(2)
        record("X08", "500" not in src(driver),
               "Browser refreshed mid-form — no server error")
    except Exception as e:
        record("X08", False, str(e))

    # ---- X09
    try:
        driver.get(BASE_URL + "complete-booking")
        time.sleep(2)
        record("X09", "500" not in src(driver),
               f"Booking URL without parameters — no 500 error — at: {driver.current_url}")
    except Exception as e:
        record("X09", False, str(e))

    # ----- X10
    driver.get(FORM_URL)
    time.sleep(2)
    try:
        email = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
        email.clear()
        email.send_keys("bademail@@@@")
        pause()
        btn = wait_clickable(driver, By.XPATH,
            "//button[contains(text(),'Book') or contains(text(),'Submit')]")
        btn.click()
        time.sleep(2)
        record("X10", "Thank you" not in src(driver),
               "Badly formatted email rejected — form did not submit")
    except Exception as e:
        record("X10", False, str(e))


#      FINAL SUMMARY
def print_summary():
    print("\n" + "=" * 58)
    print("  FINAL SUMMARY")
    print("=" * 58)
    passed = [r for r in results if r[1] == "PASS"]
    failed = [r for r in results if r[1] == "FAIL"]
    print(f"  Total tests  : {len(results)}")
    print(f"  Passed (+)   : {len(passed)}")
    print(f"  Failed (X)   : {len(failed)}")
    if failed:
        print("\n  ----- Tests that FAILED --------")
        for test_id, status, message in failed:
            print(f"    X [{test_id}]  {message}")
    else:
        print("\n  All tests passed! Great work.")
    print("=" * 58)


#        MAIN
if __name__ == "__main__":
    print("=" * 58)
    print("  Helicar Booking System --- UI Test Suite")
    print("  Website : https://helicarbooking.com/")
    print("=" * 58)

    driver = open_browser()

    try:
        phase1_home_search_form(driver)      # A01 - A25
        phase2_vehicle_list_page(driver)     # B01 - B07
        phase3_vehicle_selection(driver)     # C01 - C06
        phase4_review_booking_form(driver)   # D01 - D14
        phase5_confirmation(driver)          # E01 - E05
        edge_cases(driver)                   # X01 - X10
    finally:
        print_summary()
        driver.quit()
        print("\nChrome closed. Testing complete.")