# Jira_Secret_Scanner
Scan your Jira environment to scan for credentials or secrets using your credentials (username &amp; API Token).

This python script supports some REGEX and finds keywords you provide in the .txt file.
The output file (.csv format) gives you the Created date, URL, Title, and the CommentID (if the finding is found under comments) of the finding.


1. Go to https://id.atlassian.com/manage-profile/security/api-tokens and create a API Token. (Keep a note of it)

2. Download the Chrome Selenium Webdriver from this website; select the one that's compatible with your OS version.
- https://chromedriver.chromium.org/downloads/version-selection
- https://googlechromelabs.github.io/chrome-for-testing/

3. Add the chromedriver.exe to the "chromedrive_win32" folder.

3. In the "Chrome_Selenium.py" from chromedriver_win32 folder, edit the "chrome_driver_path"

4. Open up command prompt & cd to the directory

6. Run the following command:
python JiraScanner.py -j https://<yourcompanyname.atlassian.net/ -u <username or email> -p <Your API Token> -d ./dictionaries/keywordlist.txt

7. Make sure to install/import any extensitions if splits out any errors.
