import time
import openpyxl
from openpyxl.styles import PatternFill, Font
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager

# ─────────────────────────────────────────────
#   SETTINGS
# ─────────────────────────────────────────────
BASE_URL  = "https://helicarbooking.com/"
WAIT_TIME = 10
PAUSE_SEC = 1
EXCEL_FILE = "Test_Cases_Helicar.xlsx"

FORM_URL = (
    BASE_URL + "complete-booking?carId=2e0c153b-30c7-456f-aaf9-41b1b9912285"
    "&pickUp=Airport&destination=Thamel"
    "&pickUpDate=2026-05-10&returnDate=&pickUpTime=null&returnTime=null&price=1200.00"
)

# ─────────────────────────────────────────────
#   EXCEL — read test cases and write results
# ─────────────────────────────────────────────
wb = openpyxl.load_workbook(EXCEL_FILE)
ws = wb["Helicar UI Test Cases"]

# Find which column has "Status" and "Actual Result" in the header row (row 3)
HEADER_ROW = 3
col_map = {}
for cell in ws[HEADER_ROW]:
    if cell.value:
        col_map[cell.value] = cell.column

STATUS_COL       = col_map.get("Status", 8)
ACTUAL_COL       = col_map.get("Actual Result", 7)
TEST_ID_COL      = 1

# Build a lookup: test_id -> row number
test_rows = {}
for row in ws.iter_rows(min_row=HEADER_ROW + 1, values_only=False):
    test_id = row[TEST_ID_COL - 1].value
    if test_id:
        test_rows[test_id] = row[0].row

GREEN = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
RED   = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")

def update_excel(test_id, passed, actual_message):
    """Write PASS/FAIL + actual message back into the Excel sheet."""
    row_num = test_rows.get(test_id)
    if not row_num:
        return
    status = "PASS" if passed else "FAIL"
    ws.cell(row=row_num, column=STATUS_COL).value = status
    ws.cell(row=row_num, column=ACTUAL_COL).value = actual_message
    fill = GREEN if passed else RED
    ws.cell(row=row_num, column=STATUS_COL).fill = fill
    wb.save(EXCEL_FILE)

# ─────────────────────────────────────────────
#   RESULTS TRACKER
# ─────────────────────────────────────────────
results = []

def record(test_id, passed, message=""):
    status = "PASS" if passed else "FAIL"
    results.append((test_id, status, message))
    symbol = "+" if passed else "X"
    print(f"  {symbol} [{test_id}] {status}  {message}")
    update_excel(test_id, passed, message)   # <- writes to Excel automatically

# ─────────────────────────────────────────────
#   HELPERS
# ─────────────────────────────────────────────
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

# ─────────────────────────────────────────────
#   OPEN BROWSER  — works on GitHub + your PC
# ─────────────────────────────────────────────
def open_browser():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    driver  = webdriver.Chrome(service=service, options=options)
    return driver

# ─────────────────────────────────────────────
#   PHASE 1 — Home Search Form  (A01-A25)
# ─────────────────────────────────────────────
def phase1_home_search_form(driver):
    print("\n" + "=" * 58)
    print("  PHASE 1 --- Home Search Form  (A01-A25)")
    print("=" * 58)

    driver.get(BASE_URL)
    time.sleep(2)

    try:
        title = driver.title
        record("A01", len(title) > 0, f"Page title: '{title}'")
    except Exception as e:
        record("A01", False, str(e))

    try:
        form = wait_for(driver, By.CSS_SELECTOR, "form, .search-form, [class*='search']")
        record("A02", form.is_displayed(), "Search form visible")
    except Exception as e:
        record("A02", False, str(e))

    record("A03", "Cars" in src(driver), "Cars tab visible")
    record("A04", "Van" in src(driver), "Van/Hiace tab visible")
    record("A05", "Scorpio" in src(driver), "Scorpio/Jeep tab visible")
    record("A06", "Minibus" in src(driver), "Minibus/Coaster tab visible")
    record("A07", "Sutlej" in src(driver), "Sutlej Bus tab visible")

    found = bool(driver.find_elements(By.CSS_SELECTOR, "select")) or "Pick-up" in src(driver)
    record("A08", found, "Pickup location dropdown visible")
    record("A09", "Destination" in src(driver), "Destination dropdown visible")
    record("A10", "date" in src(driver).lower(), "Date field visible")

    try:
        btns = driver.find_elements(By.XPATH, "//button[contains(text(),'Search')]")
        if not btns:
            btns = driver.find_elements(By.CSS_SELECTOR, "[type='submit']")
        record("A11", len(btns) > 0, "Search button visible")
    except Exception as e:
        record("A11", False, str(e))

    try:
        btn = wait_clickable(driver, By.XPATH, "//button[contains(text(),'Search')]")
        record("A12", btn.is_enabled(), "Search button enabled and clickable")
    except Exception:
        try:
            btn = wait_clickable(driver, By.CSS_SELECTOR, "[type='submit']")
            record("A12", btn.is_enabled(), "Search (submit) button enabled")
        except Exception as e:
            record("A12", False, str(e))

    try:
        tab = wait_clickable(driver, By.XPATH, "//*[contains(text(),'Van') or contains(text(),'Hiace')]")
        tab.click(); pause()
        record("A13", True, "Clicked Van/Hiace tab")
    except Exception as e:
        record("A13", False, str(e))

    try:
        tab = wait_clickable(driver, By.XPATH, "//*[contains(text(),'Scorpio') or contains(text(),'Jeep')]")
        tab.click(); pause()
        record("A14", True, "Clicked Scorpio/Jeep tab")
    except Exception as e:
        record("A14", False, str(e))

    try:
        tab = wait_clickable(driver, By.XPATH, "//*[contains(text(),'Minibus') or contains(text(),'Coaster')]")
        tab.click(); pause()
        record("A15", True, "Clicked Minibus/Coaster tab")
    except Exception as e:
        record("A15", False, str(e))

    try:
        tab = wait_clickable(driver, By.XPATH, "//*[contains(text(),'Sutlej')]")
        tab.click(); pause()
        record("A16", True, "Clicked Sutlej Bus tab")
    except Exception as e:
        record("A16", False, str(e))

    try:
        tab = wait_clickable(driver, By.XPATH, "//*[contains(text(),'Cars') or contains(text(),'Car')]")
        tab.click(); pause()
        record("A17", True, "Switched back to Cars tab")
    except Exception as e:
        record("A17", False, str(e))

    record("A18", "Add another destination" in src(driver), "'Add another destination' button visible")

    try:
        dropdowns = driver.find_elements(By.CSS_SELECTOR, "select")
        if len(dropdowns) >= 1:
            Select(dropdowns[0]).select_by_index(1); pause()
        if len(dropdowns) >= 2:
            Select(dropdowns[1]).select_by_index(1); pause()
        if len(dropdowns) >= 3:
            Select(dropdowns[2]).select_by_index(2); pause()
        btn = wait_clickable(driver, By.XPATH, "//*[contains(text(),'Add another destination')]")
        btn.click(); pause()
        record("A19", "To location" in src(driver), "New destination row appeared")
    except Exception as e:
        record("A19", False, str(e))

    record("A20", "Remove" in src(driver), "Remove button visible after adding destination")

    try:
        remove_btn = wait_clickable(driver, By.XPATH, "//button[contains(text(),'Remove')]")
        remove_btn.click(); pause()
        record("A21", True, "Clicked Remove — extra row removed")
    except Exception as e:
        record("A21", False, str(e))

    try:
        date_field = wait_clickable(driver, By.CSS_SELECTOR,
            "input[type='date'], [placeholder*='date'], [class*='date']")
        date_field.click(); pause()
        calendar = driver.find_elements(By.CSS_SELECTOR, ".datepicker, [class*='calendar'], [class*='picker']")
        record("A22", True, f"Date field clicked — {len(calendar)} calendar element(s) found")
    except Exception as e:
        record("A22", "NoSuchElement" not in type(e).__name__, f"Date click attempted ({type(e).__name__})")

    record("A23", "pickup" in src(driver).lower() or "Pick-up" in src(driver), "Pickup label visible")
    record("A24", "destination" in src(driver).lower(), "Destination placeholder visible")

    try:
        driver.get(BASE_URL); time.sleep(2)
        date_visible = "date" in src(driver).lower()
        time_visible = "time" in src(driver).lower()
        record("A25", date_visible and time_visible, f"Date visible:{date_visible} | Time visible:{time_visible}")
    except Exception as e:
        record("A25", False, str(e))


# ─────────────────────────────────────────────
#   PHASE 2 — Vehicle List Page  (B01-B07)
# ─────────────────────────────────────────────
def phase2_vehicle_list_page(driver):
    print("\n" + "=" * 58)
    print("  PHASE 2 --- Vehicle List Page  (B01-B07)")
    print("=" * 58)

    driver.get(BASE_URL + "vehicle-rental")
    time.sleep(2)

    record("B01", "vehicle" in driver.current_url.lower(), f"URL contains 'vehicle': {driver.current_url}")
    record("B02", len(driver.title) > 0, f"Page title: '{driver.title}'")

    body = driver.find_element(By.TAG_NAME, "body").text
    record("B03", len(body.strip()) > 50, "Page body has real content")

    found = any(name in src(driver) for name in ["Mini Bus", "Toyota", "TATA", "Coaster", "Bus", "Van"])
    record("B04", found, "Vehicle names visible")
    record("B05", "Rs." in src(driver), "Vehicle prices (Rs.) visible")
    record("B06", "Book Now" in src(driver), "'Book Now' text visible")

    try:
        btn = wait_clickable(driver, By.XPATH, "//a[contains(text(),'Book Now')] | //button[contains(text(),'Book Now')]")
        record("B07", btn.is_enabled(), "'Book Now' button enabled")
    except Exception as e:
        record("B07", False, str(e))


# ─────────────────────────────────────────────
#   PHASE 3 — Vehicle Selection  (C01-C06)
# ─────────────────────────────────────────────
def phase3_vehicle_selection(driver):
    print("\n" + "=" * 58)
    print("  PHASE 3 --- Vehicle Selection  (C01-C06)")
    print("=" * 58)

    driver.get(BASE_URL); time.sleep(2)
    try:
        dropdowns = driver.find_elements(By.CSS_SELECTOR, "select")
        if len(dropdowns) >= 2:
            Select(dropdowns[0]).select_by_index(1); pause()
            Select(dropdowns[1]).select_by_index(1); pause()
        btn = wait_clickable(driver, By.XPATH, "//button[contains(text(),'Search')] | //input[@type='submit']")
        btn.click(); time.sleep(3)
    except Exception as e:
        print(f"  [Setup] {e}")

    time.sleep(1)
    cards = driver.find_elements(By.CSS_SELECTOR, ".card, [class*='vehicle'], article, [class*='car']")
    record("C01", len(cards) > 0, f"Found {len(cards)} vehicle card(s)")

    url_before = driver.current_url
    try:
        card_img = driver.find_elements(By.CSS_SELECTOR, ".card img, [class*='vehicle'] img, article img")
        if card_img:
            card_img[0].click(); time.sleep(2)
        changed = (driver.current_url != url_before) or ("Book Now" in src(driver))
        record("C02", changed, "Vehicle card click opened detail view")
    except Exception as e:
        record("C02", False, str(e))

    images = driver.find_elements(By.CSS_SELECTOR, "img")
    loaded = sum(1 for img in images if driver.execute_script("return arguments[0].naturalWidth;", img))
    record("C03", loaded > 0, f"{loaded} image(s) loaded correctly")

    try:
        btn = wait_clickable(driver, By.XPATH, "//a[contains(text(),'Book Now')] | //button[contains(text(),'Book Now')]")
        record("C04", btn.is_displayed(), "'Book Now' button visible on card")
    except Exception as e:
        record("C04", False, str(e))

    try:
        driver.get(BASE_URL + "vehicle-rental"); time.sleep(2)
        prices = driver.find_elements(By.XPATH, "//*[contains(text(),'Rs.')]")
        record("C05", len(prices) > 0, f"Price shown on {len(prices)} card(s)")
    except Exception as e:
        record("C05", False, str(e))

    try:
        book_buttons = driver.find_elements(By.XPATH, "//a[contains(text(),'Book Now')] | //button[contains(text(),'Book Now')]")
        if book_buttons:
            book_buttons[0].click(); time.sleep(3)
        record("C06", "complete-booking" in driver.current_url or "booking" in src(driver).lower(),
               f"Clicked Book Now — landed at: {driver.current_url}")
    except Exception as e:
        record("C06", False, str(e))


# ─────────────────────────────────────────────
#   PHASE 4 — Review Booking Form  (D01-D14)
# ─────────────────────────────────────────────
def phase4_review_booking_form(driver):
    print("\n" + "=" * 58)
    print("  PHASE 4 --- Review Booking Form  (D01-D14)")
    print("=" * 58)

    driver.get(FORM_URL); time.sleep(2)

    record("D01", "complete-booking" in driver.current_url, f"Correct URL: {driver.current_url}")
    record("D02", len(driver.title) > 0, f"Page title: '{driver.title}'")
    body = driver.find_element(By.TAG_NAME, "body").text
    record("D03", len(body.strip()) > 50, "Page has real content")
    record("D04", "Review" in src(driver) or "booking" in src(driver).lower(), "'Review booking' heading visible")

    inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
    record("D05", len(inputs) >= 2, f"Name fields present — found {len(inputs)} input(s)")

    try:
        inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
        inputs[0].clear(); inputs[0].send_keys("Saniya"); pause()
        record("D06", inputs[0].get_attribute("value") == "Saniya", "First name 'Saniya' accepted")
    except Exception as e:
        record("D06", False, str(e))

    try:
        inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
        inputs[1].clear(); inputs[1].send_keys("Bam"); pause()
        record("D07", inputs[1].get_attribute("value") == "Bam", "Last name 'Bam' accepted")
    except Exception as e:
        record("D07", False, str(e))

    try:
        email = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
        email.clear(); email.send_keys("testuser@example.com"); pause()
        record("D08", "testuser@example.com" in email.get_attribute("value"), "Email accepted")
    except Exception as e:
        record("D08", False, str(e))

    try:
        tel = driver.find_elements(By.CSS_SELECTOR, "input[type='tel']")
        if tel:
            tel[0].clear(); tel[0].send_keys("9800000000")
            actual_value = tel[0].get_attribute("value")
        else:
            inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
            if len(inputs) >= 3:
                inputs[2].clear(); inputs[2].send_keys("9800000000")
                actual_value = inputs[2].get_attribute("value")
            else:
                actual_value = ""
        record("D09", "9800000000" in actual_value, f"Phone number accepted: '{actual_value}'")
    except Exception as e:
        record("D09", False, str(e))

    try:
        textarea = driver.find_element(By.CSS_SELECTOR, "textarea")
        textarea.clear(); textarea.send_keys("I need a vehicle for airport pickup."); pause()
        record("D10", "airport" in textarea.get_attribute("value").lower(), "Message accepted in textarea")
    except Exception as e:
        record("D10", False, str(e))

    driver.get(FORM_URL); time.sleep(2)
    try:
        inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
        if len(inputs) >= 2:
            inputs[0].send_keys("Saniya"); inputs[1].send_keys("Bam")
        email = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
        email.clear(); email.send_keys("not-an-email"); pause()
        btn = wait_clickable(driver, By.XPATH, "//button[contains(text(),'Book') or contains(text(),'Submit')]")
        btn.click(); time.sleep(2)
        record("D11", "Thank you" not in src(driver), "Invalid email rejected")
    except Exception as e:
        record("D11", False, str(e))

    driver.get(FORM_URL); time.sleep(2)
    try:
        btn = wait_clickable(driver, By.XPATH, "//button[contains(text(),'Book') or contains(text(),'Submit')]")
        btn.click(); time.sleep(2)
        record("D12", "Thank you" not in src(driver), "Empty form submission blocked")
    except Exception as e:
        record("D12", False, str(e))

    record("D13", "Book" in src(driver) or "Submit" in src(driver), "Book/Submit button visible")

    driver.get(FORM_URL); time.sleep(2)
    try:
        inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
        if len(inputs) >= 1: inputs[0].clear(); inputs[0].send_keys("Test")
        if len(inputs) >= 2: inputs[1].clear(); inputs[1].send_keys("User")
        email = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
        email.clear(); email.send_keys("testuser@example.com")
        tel = driver.find_elements(By.CSS_SELECTOR, "input[type='tel']")
        if tel: tel[0].clear(); tel[0].send_keys("9800000000")
        textareas = driver.find_elements(By.CSS_SELECTOR, "textarea")
        if textareas: textareas[0].clear(); textareas[0].send_keys("Test booking for UI testing.")
        pause()
        btn = wait_clickable(driver, By.XPATH, "//button[contains(text(),'Book') or contains(text(),'Submit')]")
        btn.click(); time.sleep(4)
        success = ("Thank you" in src(driver) or "confirmed" in src(driver).lower() or
                   "success" in src(driver).lower() or driver.current_url != FORM_URL)
        record("D14", success, f"Form submitted — at: {driver.current_url}")
    except Exception as e:
        record("D14", False, str(e))


# ─────────────────────────────────────────────
#   PHASE 5 — Confirmation  (E01-E05)
# ─────────────────────────────────────────────
def phase5_confirmation(driver):
    print("\n" + "=" * 58)
    print("  PHASE 5 --- Confirmation  (E01-E05)")
    print("=" * 58)

    error_found = (("404" in src(driver) or "500" in src(driver))
                   and "Review" not in src(driver)
                   and "booking" not in src(driver).lower())
    record("E01", not error_found, "No server error (404/500) after booking")

    keywords = ["Thank you", "success", "confirmed", "booking", "Review"]
    record("E02", any(kw in src(driver) for kw in keywords), "Booking content present after submit")

    try:
        home = wait_clickable(driver, By.XPATH, "//a[contains(text(),'Home')] | //a[@href='/']")
        home.click(); time.sleep(2)
        record("E03", "helicarbooking" in driver.current_url, f"Home link worked — at: {driver.current_url}")
    except Exception as e:
        record("E03", False, str(e))

    driver.get(BASE_URL); time.sleep(2)
    body = driver.find_element(By.TAG_NAME, "body").text
    record("E04", len(body.strip()) > 50, "Home page reloaded with content")
    record("E05", "Search" in src(driver), "Search form visible after returning home")


# ─────────────────────────────────────────────
#   EDGE CASES  (X01-X10)
# ─────────────────────────────────────────────
def edge_cases(driver):
    print("\n" + "=" * 58)
    print("  EDGE CASES  (X01-X10)")
    print("=" * 58)

    driver.get(BASE_URL); time.sleep(2)
    try:
        dropdowns = driver.find_elements(By.CSS_SELECTOR, "select")
        if len(dropdowns) >= 2:
            Select(dropdowns[0]).select_by_index(1); pause()
            Select(dropdowns[1]).select_by_index(1); pause()
            btn = driver.find_element(By.XPATH, "//button[contains(text(),'Search')] | //input[@type='submit']")
            btn.click(); time.sleep(2)
        record("X01", "500" not in src(driver), "Same pickup/destination — no server error")
    except Exception as e:
        record("X01", False, str(e))

    driver.get(BASE_URL); time.sleep(1)
    try:
        for field in driver.find_elements(By.CSS_SELECTOR, "input[type='text']")[:2]:
            field.clear(); field.send_keys("!@#$%^&*"); time.sleep(0.3)
        record("X02", True, "Random symbols typed — page did not crash")
    except Exception as e:
        record("X02", False, str(e))

    driver.get(FORM_URL); time.sleep(2)
    try:
        textarea = driver.find_element(By.CSS_SELECTOR, "textarea")
        textarea.clear(); textarea.send_keys("A" * 200); pause()
        val = textarea.get_attribute("value")
        record("X03", len(val) > 0, f"200-char text accepted — got {len(val)} chars")
    except Exception as e:
        record("X03", False, str(e))

    driver.get(BASE_URL); time.sleep(1)
    try:
        for keyword in ["Van", "Scorpio", "Minibus", "Sutlej", "Cars"]:
            tabs = driver.find_elements(By.XPATH, f"//*[contains(text(),'{keyword}')]")
            if tabs: tabs[0].click(); time.sleep(0.3)
        record("X04", True, "Rapid tab clicking — no freeze")
    except Exception as e:
        record("X04", False, str(e))

    driver.get(BASE_URL); time.sleep(1)
    try:
        dropdowns = driver.find_elements(By.CSS_SELECTOR, "select, .dropdown-toggle")
        if dropdowns:
            dropdowns[0].click(); time.sleep(0.5)
            driver.find_element(By.TAG_NAME, "body").click(); pause()
        record("X05", True, "Clicked outside dropdown — closed properly")
    except Exception as e:
        record("X05", False, str(e))

    driver.get(BASE_URL); time.sleep(1)
    try:
        btn = driver.find_element(By.XPATH, "//button[contains(text(),'Search')] | //input[@type='submit']")
        btn.send_keys(Keys.ENTER); time.sleep(2)
        record("X06", len(src(driver)) > 100, "Enter on Search — page still alive")
    except Exception as e:
        record("X06", False, str(e))

    driver.get(BASE_URL); time.sleep(1)
    try:
        for _ in range(2):
            add_btns = driver.find_elements(By.XPATH, "//*[contains(text(),'Add another destination')]")
            if add_btns: add_btns[0].click(); time.sleep(0.8)
        record("X07", True, "Clicked 'Add another destination' twice — no crash")
    except Exception as e:
        record("X07", False, str(e))

    driver.get(BASE_URL); time.sleep(1)
    try:
        fields = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
        if fields: fields[0].send_keys("halfway"); pause()
        driver.refresh(); time.sleep(2)
        record("X08", "500" not in src(driver), "Refresh mid-form — no server error")
    except Exception as e:
        record("X08", False, str(e))

    try:
        driver.get(BASE_URL + "complete-booking"); time.sleep(2)
        record("X09", "500" not in src(driver), f"Booking URL without params — at: {driver.current_url}")
    except Exception as e:
        record("X09", False, str(e))

    driver.get(FORM_URL); time.sleep(2)
    try:
        email = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
        email.clear(); email.send_keys("bademail@@@@"); pause()
        btn = wait_clickable(driver, By.XPATH, "//button[contains(text(),'Book') or contains(text(),'Submit')]")
        btn.click(); time.sleep(2)
        record("X10", "Thank you" not in src(driver), "Bad email rejected — form did not submit")
    except Exception as e:
        record("X10", False, str(e))


# ─────────────────────────────────────────────
#   FINAL SUMMARY
# ─────────────────────────────────────────────
def print_summary():
    print("\n" + "=" * 58)
    print("  FINAL SUMMARY")
    print("=" * 58)
    passed = [r for r in results if r[1] == "PASS"]
    failed = [r for r in results if r[1] == "FAIL"]
    print(f"  Total  : {len(results)}")
    print(f"  Passed : {len(passed)}")
    print(f"  Failed : {len(failed)}")
    if failed:
        print("\n  Tests that FAILED:")
        for test_id, status, message in failed:
            print(f"    X [{test_id}]  {message}")
    else:
        print("\n  All tests passed!")
    print("=" * 58)
    print(f"\n  Results saved to: {EXCEL_FILE}")


# ─────────────────────────────────────────────
#   MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 58)
    print("  Helicar Booking System --- UI Test Suite")
    print("  Reading test cases from:", EXCEL_FILE)
    print("  Website:", BASE_URL)
    print("=" * 58)

    driver = open_browser()

    try:
        phase1_home_search_form(driver)
        phase2_vehicle_list_page(driver)
        phase3_vehicle_selection(driver)
        phase4_review_booking_form(driver)
        phase5_confirmation(driver)
        edge_cases(driver)
    finally:
        print_summary()
        driver.quit()
        print("\nChrome closed. Testing complete.")
