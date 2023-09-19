# Confluence_And_Jira_Secret_Scanner
Scan your Confluence and/or Jira environment for credentials or secrets using your credentials (username and API Token).

This python script supports 'some' REGEX and finds keywords you provide in the .txt file. (JQL and CQL is fking weird)
The output file (.csv format) gives you the Created date, URL, Title, PageID, and the CommentID (if the finding is found under comments) of the finding.

Prerequisites:
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens and create a API Token. (Keep a note of it)
2. Download the "chromedriver" from this website; select the one that's compatible with your OS version.
- https://googlechromelabs.github.io/chrome-for-testing/#stable
3. Unzip it
3. Add the "Chrome_Selenium.py" to the folder from step 3
4. In the "Chrome_Selenium.py", edit the "chrome_driver_path" to match the path of chromedriver.exe
(So something like this)
chrome_driver_path = 'C:\Users\<username>\Desktop\Jira_Secret_Scanner-main\chromedriver-win64\chromedriver.exe'

Note:
1. Download/install python ( https://www.python.org/downloads/ )
2. Download/install any extensitions if it splits out any errors about extenstions/imports

=======================================================================================================================================

JIRA Scan:
1. Open up command prompt & cd to the directory
2. Run the following command:
python JiraScanner.py -j <https://yourcompanyname.atlassian.net/> -u <username or email> -p <Your API Token> -d ./dictionaries/keywordlist.txt
3. Results should go to the "loot" directory

=======================================================================================================================================

CONFLUENCE Scan:
1. Open up command prompt & cd to the directory
2. Run the following command:
python ConfluenceScanner.py -c <https://yourcompanyname.atlassian.net/> -u <username or email> -p <Your API Token> -d ./dictionaries/keywordlist.txt
3. Results should go to the "loot" directory
