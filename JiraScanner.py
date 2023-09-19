import os
import requests
import sys
import getopt
import time
import csv
import re

def search_jira_recursive(jira_url, username, access_token, dictionary_path):
    content_set = set()

    try:
        with open(dictionary_path, "r") as file:
            phrases = file.read().splitlines()  # Read phrases directly
    except Exception as e:
        print("[*] An error occurred while opening the dictionary file: %s" % str(e))
        sys.exit(2)

    print("[*] Searching for Jira issues for phrases and compiling a list of pages")

    max_results = 50  # Maximum number of results to fetch per request

    for phrase in phrases:
        keywords = phrase.split()  # Split phrase into keywords

        start_at = 0

        while True:
            keyword_conditions = [
                '(summary ~ "%s" OR comment ~ "%s")' % (keyword.lower(), keyword.lower()) for keyword in keywords
            ]

            combined_condition = ' AND '.join(keyword_conditions)

            search_query = {
                'jql': combined_condition,
                'startAt': start_at,
                'maxResults': max_results,
                'fields': 'summary,comment'
            }

            try:
                response = requests.get(
                    jira_url + "/rest/api/2/search",
                    auth=(username, access_token),
                    headers={'Accept': 'application/json'},
                    params=search_query
                )
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print("[*] Failed to search for phrase '%s'" % phrase)
                print("Status code: %d" % response.status_code)
                print("Response: %s" % response.text)
                break

            json_resp = response.json()
            #print(json_resp)  # Add this line to print the response
            total_size = json_resp.get("total", 0)

            if total_size:
                print("[*] Found %d result(s) for search phrase: %s" % (total_size, phrase))

                for result in json_resp.get("issues", []):
                    issue_key = result.get("key")
                    issue_summary = result.get("fields", {}).get("summary")
                    comments = result.get("fields", {}).get("comment", {}).get("comments", [])
                    
                    for comment in comments:
                        created_time = comment.get("created")  # Extract created time from comment
                        comment_id = comment.get("id")
                        
                        if any(keyword.lower() in comment.get("body", "").lower() for keyword in keywords):
                            comment_ids_with_keyword = tuple([comment_id])
                            content_set.add((created_time, issue_key, issue_summary, phrase, comment_ids_with_keyword))
                            
                print("[*] %d unique issue(s) added to the set for search phrase: %s" % (len(content_set), phrase))

            if total_size <= (start_at + max_results):
                break  # All results have been fetched
            else:
                start_at += max_results

    print("[*] Compiled set of %d unique issue(s) with matching phrases" % len(content_set))
    return content_set

def save_content(jira_url, username, access_token, jira_content):
    timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
    filename = "JIRA_findings_{}.csv".format(timestamp)
    directory = "loot"

    # Create the "loot" directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    filepath = os.path.join(directory, filename)

    print("[*] Saving content to file: {}".format(filepath))

    try:
        with open(filepath, "w", newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            # Write column headers to the CSV file
            writer.writerow(["Jira Results"])
            writer.writerow(['Created', 'Keyword', 'URL', 'Summary', 'Comment IDs'])  # Add 'Comment IDs' column

            for created_time, issue_key, issue_summary, keyword, comment_ids in jira_content:  # Include comment_ids
                url = jira_url + "/browse/%s" % issue_key
                comment_ids_str = ", ".join(comment_ids) if comment_ids else "N/A"
                writer.writerow([created_time, keyword, url, issue_summary, comment_ids_str])  # Include comment_ids

    except Exception as e:
        print("[*] An error occurred while saving content to file: %s" % str(e))
        return

    print("[*] Saved content to '{}' file".format(filepath))

def main():
    jira_url = ""
    username = ""
    access_token = ""
    dictionary_path = ""

    # Usage
    usage = '\nUsage: python3 JIRA_search.py -j <JIRA URL> -u <USERNAME> -p <API ACCESS TOKEN> -d <DICTIONARY FILE>'

    # Try parsing options and arguments
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hj:c:u:p:d:", ["help", "jiraurl=", "user=", "accesstoken=", "dict="])
    except getopt.GetoptError as err:
        print(str(err))
        print(usage)
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(usage)
            sys.exit()
        if opt in ("-j", "--jiraurl"):
            jira_url = arg
        if opt in ("-u", "--user"):
            username = arg
        if opt in ("-p", "--accesstoken"):
            access_token = arg
        if opt in ("-d", "--dict"):
            dictionary_path = arg

    # Check for mandatory arguments
    if not jira_url:
        print("\nJira URL (-j, --jiraurl) is a mandatory argument\n")
        print(usage)
        sys.exit(2)

    if not username:
        print("\nUsername (-u, --user) is a mandatory argument\n")
        print(usage)
        sys.exit(2)

    if not access_token:
        print("\nAccess Token (-p, --accesstoken) is a mandatory argument\n")
        print(usage)
        sys.exit(2)

    if not dictionary_path:
        print("\nDictionary Path (-d, --dict) is a mandatory argument\n")
        print(usage)
        sys.exit(2)

    # Strip trailing / from URLs if they have one
    if jira_url.endswith('/'):
        jira_url = jira_url[:-1]

    jira_content = search_jira_recursive(jira_url, username, access_token, dictionary_path)  # <-- Updated function name
    save_content(jira_url, username, access_token, jira_content)

if __name__ == "__main__":
    main()
