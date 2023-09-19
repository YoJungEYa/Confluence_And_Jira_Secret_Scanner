import os
import requests
import sys
import getopt
import time
import csv
import datetime
import re

def search_confluence_for_keywords(confluence_url, username, access_token, keywords):
    content_set = set()

    print("[*] Searching for Confluence content for keywords: {}".format(keywords))

    # Combine the keywords into a single search phrase
    search_phrase = " ".join(keywords)

    search_query = {
        'cql': 'text ~ "{}"'.format(search_phrase),
        'start': 0,
        'limit': 50
    }

    try:
        response = requests.get(
            confluence_url + "/wiki/rest/api/search",
            auth=(username, access_token),
            headers={'Accept': 'application/json'},
            params=search_query
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("[*] Failed to search for the combined phrase")
        print("Status code: %d" % response.status_code)
        print("Response: %s" % response.text)
        sys.exit(2)

    json_resp = response.json()
    total_size = json_resp.get("size", 0)

    if total_size:
        print("[*] Found %d result(s) for the combined phrase" % total_size)

        for result in json_resp.get("results", []):
            content_id = result.get("content", {}).get("id")
            page_title = result.get("title")
            last_modified = result.get("lastModified")
            content_type = result.get("content", {}).get("type")
            url_comment = result.get("url")

            if content_type == "page":
                content_id = result.get("content", {}).get("id")
                comment_id = ""

            elif content_type == "comment":
                comment_id = content_id
                match_obj = re.search(r"/pages/(\d+)/", url_comment)
                if match_obj:
                    zzz = match_obj.group(1)
                else:
                    zzz = ""  # Set a default value if no match is found
                content_id = zzz
                
            else:
                comment_id = ""

            content_set.add((content_id, page_title, last_modified, search_phrase, comment_id))
            #print("result: ", (result))
            #print("content_type", (content_type))
            #print("content_id: ", (content_id))

        print("[*] %d unique page(s) added to the set for the combined phrase" % len(content_set))

    return content_set

def save_content(confluence_url, username, access_token, confluence_content):
    timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
    filename = "Confluence-Findings-Comment_{}.csv".format(timestamp)
    directory = "loot"

    # Create the "loot" directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    filepath = os.path.join(directory, filename)

    print("[*] Saving content to file: {}".format(filepath))

    try:
        with open(filepath, "w", newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            # Write Confluence content to the CSV file
            writer.writerow(["Confluence Results"])
            writer.writerow(['LastModified', 'Keyword', 'URL', 'PageId', 'CommentId', 'Title'])
            for content_id, page_title, last_modified, keyword, comment_id in confluence_content:
                url = confluence_url + "/wiki/pages/viewpage.action?pageId=%s" % content_id
                writer.writerow([last_modified, keyword, url, content_id, comment_id, page_title])

    except Exception as e:
        print("[*] An error occurred while saving content to file: %s" % str(e))
        return

    print("[*] Saved content to '{}' file".format(filepath))


def main():
    confluence_url = ""
    username = ""
    access_token = ""
    dictionary_path = ""

    # Usage
    usage = '\nUsage: python3 combined_search.py -c <CONFLUENCE URL> -u <USERNAME> -p <API ACCESS TOKEN> -d <DICTIONARY FILE>'

    # Try parsing options and arguments
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hj:c:u:p:d:", ["help", "confluenceurl=", "user=", "accesstoken=", "dict="])
    except getopt.GetoptError as err:
        print(str(err))
        print(usage)
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(usage)
            sys.exit()
        if opt in ("-c", "--confluenceurl"):
            confluence_url = arg
        if opt in ("-u", "--user"):
            username = arg
        if opt in ("-p", "--accesstoken"):
            access_token = arg
        if opt in ("-d", "--dict"):
            dictionary_path = arg

    # Check for mandatory arguments
    if not confluence_url:
        print("\nConfluence URL (-c, --confluenceurl) is a mandatory argument\n")
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
    if confluence_url.endswith('/'):
        confluence_url = confluence_url[:-1]

    try:
        with open(dictionary_path, "r") as file:
            lines = file.read().splitlines()
            keywords_list = [line.lower().split() for line in lines]
    except Exception as e:
        print("[*] An error occurred while opening the dictionary file: %s" % str(e))
        sys.exit(2)

    confluence_content = set()

    for keywords in keywords_list:
        content_for_keywords = search_confluence_for_keywords(confluence_url, username, access_token, keywords)
        confluence_content.update(content_for_keywords)

    save_content(confluence_url, username, access_token, confluence_content)

if __name__ == "__main__":
    main()
