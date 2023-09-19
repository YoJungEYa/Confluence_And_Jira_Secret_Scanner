from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Set the path to the ChromeDriver executable
chrome_driver_path = 'PATH_TO_CHROMEDRIVER'

if not chrome_driver_path:
    raise ValueError("PATH_TO_CHROMEDRIVER environment variable not set")

# Configure Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# Initialize the ChromeDriver with the specified options
driver = webdriver.Chrome(options=chrome_options)
