import requests
from bs4 import BeautifulSoup

ids_to_check = []
id_homepage = {}
id_url_pages = {}
id_good_stats = {}
id_bad_stats = {}
banned_links = ["w3.org", "google.co"]
check_loop = True

BAD_HTML_LIST = ["br", "font", "center", "table", "style"]
GOOD_HTML_LIST = ["section", "nav", "header", "footer", "aside", "main", "figure", "div"]
#TAG_LIST = ["br", "font", "center", "table", "article", "section", "nav", "header", "footer", "aside", "main", "figure", "div"]
banned_formats = ["mp4", "jpg", "webm", "css"]


def homepage_grab(user_id):
    w = requests.get("http://{}.web1.rdfx.org".format(user_id), timeout=30)
    id_homepage[user_id] = {"content": w.content, "url": w.url}
    print("Done {} {}".format(user_id, w.status_code))


def doctype_checker(content, user_id, url):
    if "<!DOCTYPE>" in content.decode("utf-8"):
        return 1
        print("<!DOCTYPE> used in {} {}".format(user_id, repr(url)))
    elif "<!DOCTYPE html>" in content.decode("utf-8"):
        return 1
        print("<!DOCTYPE html> used in {} {}".format(user_id, repr(url)))
    elif "<!doctype html>" in content.decode("utf-8"):
        return 1
    else:
        return 0


def tag_usage_checker(soup, user_id, tag, url):
    amount = soup.find_all(tag)
    return len(amount)
    print("{} uses of <{}> in {} by {}".format(len(amount), tag, url, user_id))


def recursive_page_finder(soup, user_id):
    id_url_pages[user_id] = []
    links = soup.find_all("a")
    hyperlinks = [link["href"] for link in links]
    for link in hyperlinks:
        if link.startswith("/"):
            link = link[1:]
        if not any(disallowed_links in link for disallowed_links in banned_links):
            if link.startswith("#"):
                print("Didn't add {}".format("http://{}.web1.rdfx.org/{}".format(user_id, link)))
            elif any(link.endswith(format) for format in banned_formats):
                print("Didn't add {}".format("http://{}.web1.rdfx.org/{}".format(user_id, link)))
            elif "http://{}.web1.rdfx.org/{}".format(user_id, link) not in id_url_pages[user_id]:
                test = requests.get("http://{}.web1.rdfx.org/{}".format(user_id, link))
                if test.status_code == 200:
                    id_url_pages[user_id].append("http://{}.web1.rdfx.org/{}".format(user_id, link))
                    print("Added {}".format("http://{}.web1.rdfx.org/{}".format(user_id, link)))
                else:
                    print("Didn't add {}".format("http://{}.web1.rdfx.org/{}".format(user_id, link)))


while check_loop:
    raw_ids = input("What ID's do you want to check? Please input in a space separated list: ")
    id_list = raw_ids.split(" ")
    if len(id_list) > 10:
        print("At MAX you should have 10 ID's. Please try again.")
    else:
        ids_to_check = id_list
        print(", ".join(ids_to_check))
        check = input("Is this list correct for the IDs to check? ").upper()
        if check.startswith("Y"):
            check_loop = False

for user_id in ids_to_check:
    homepage_grab(user_id)

for user_id in ids_to_check:
    soup = BeautifulSoup(id_homepage[user_id]["content"], "html.parser")
    recursive_page_finder(soup, user_id)

print("\n")

#Init
for user_id in ids_to_check:
    id_good_stats[user_id] = {"page_amount": len(id_url_pages[user_id]), "doctype": 0, "tag": {}}
    id_bad_stats[user_id] = {"page_amount": len(id_url_pages[user_id]), "doctype": 0, "tag": {}}
    for tag in BAD_HTML_LIST:
        id_bad_stats[user_id]["tag"][tag] = 0
    for tag in GOOD_HTML_LIST:
        id_good_stats[user_id]["tag"][tag] = 0
        

for user_id in ids_to_check:
    print("Started {}".format(user_id))
    for link in id_url_pages[user_id]:
        content = requests.get(link).content
        id_good_stats[user_id]["doctype"] += doctype_checker(content, user_id, link)
        soup = BeautifulSoup(content, "html.parser")
        for tag in BAD_HTML_LIST:
            id_bad_stats[user_id]["tag"][tag] += tag_usage_checker(soup, user_id, tag, link)
        for tag in GOOD_HTML_LIST:
            id_good_stats[user_id]["tag"][tag] += tag_usage_checker(soup, user_id, tag, link)
    print("Completed {} {}".format(user_id, len(id_url_pages[user_id])))

#Print the stats
for user_id in ids_to_check:
    print("\n==================================================")
    print("\nStats on {}".format(user_id))
    print("\n==General HTML Used: ==")
    print("Amount of times DOCTYPE was used: {}".format(id_good_stats[user_id]["doctype"]))
    print("Amount of pages checked: {}".format(id_good_stats[user_id]["page_amount"]))
    #Final output
    print("\n== Bad HTML Used: ==")
    for tag in BAD_HTML_LIST:
        print("Amount of times <{}> was used: {}".format(tag, id_bad_stats[user_id]["tag"][tag]))
    print("\n== Good HTML Used: ==")
    for tag in GOOD_HTML_LIST:
        print("Amount of times <{}> was used: {}".format(tag, id_good_stats[user_id]["tag"][tag]))
        
        
        
        
        
        
        
        
        
        
