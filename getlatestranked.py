import requests
import json
import os
import itertools
import operator
import re
import time
import sys
import pickle
from operator import itemgetter
from multiprocessing import Queue
    
result = []
todownload = []
numbers = set()

# Checks if directory exists and create one
# Not everyone has osu! installed on default folder
# Please, make a function to open files when download is finished, since it's easier this way.
def createdir():
    # Checks if dir exists
    if os.path.exists("./DownloadedSongs"):
        #Print message to user confirming that it exists
        print("Found Song Downloads folder")
        return 1
    else:
        # If not exists, print message to user and creates and changes to that
        print("Download folder not found, creating one in local directory")
        os.mkdir("./DownloadedSongs")
        os.chdir("./DownloadedSongs")

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

# This detects the operating system and clears the window
def clearconsole():
    # Windows
    if os.name == "nt":
        os.system("cls")
    # Linux/Other
    else:
        os.system("clear")


def dotitlebar():
    clearconsole()
    print("-----[Super Ultimate Ranked Maps Downloader V1 by karstenes]-----\n")

def loadlogin():
    try:
        with open('data.pydata', 'rb') as f:
            login = pickle.load(f)
            f.close()
            return login
    except Exception as e:
        return {}

dotitlebar()

login = loadlogin()

if login:
    yes = input("Use saved login? (Y/n): ")
    if yes.lower() == "y" or yes == "":
        pass
    else:
        login = {}
        print()

if not login:
    login["username"] = input("osu username: ")
    print()
    login["password"] = input("osu password: ")
    print()
    login["apikey"] = input("api key (https://osu.ppy.sh/p/api): ")
    print()
    save = input("Save login? (Y/n): ")
    if save.lower() == "y" or save == "":
        with open('data.pydata', 'wb+') as f:
            pickle.dump(login, f)
            f.close()


apikey = login["apikey"]


files = os.listdir()

for i, v in enumerate(files):
    files[i] = v.split( )

for v in files:
    if RepresentsInt(v[0]):
        numbers.add(int(v[0]))

final = sorted(numbers)[-1]

def querymaps(date):
    r = requests.post("https://osu.ppy.sh/api/get_beatmaps", data={"k":apikey, "since":date})
    return json.loads(r.content)
date = json.loads(requests.post("https://osu.ppy.sh/api/get_beatmaps", data={"k":apikey, "s":str(final)}).content)[0]["approved_date"]

q = querymaps(date)

for i,v in enumerate(q):
    if v["mode"] != "0":
        del q[i]
    if v["approved"] != "1":
        del q[i]

getvals = operator.itemgetter('beatmapset_id')
q.sort(key=getvals)
for k, g in itertools.groupby(q, getvals):
    result.append(g.__next__())

songs = os.listdir(".")

for v in result:
    v['artist'] = re.sub("[\*.\":?\\\/\|]", "", v['artist'])
    v['title'] = re.sub("[\*.\":\\\/\|?]", "", v['title'])
    if "{} {} - {}".format(v["beatmapset_id"], v["artist"], v["title"]) not in songs:
        todownload.append({"id":v["beatmapset_id"], "fullname":"{} {} - {}".format(v["beatmapset_id"], v["artist"], v["title"])})

dotitlebar()

if not todownload:
    print("No maps to download!")
    time.sleep(2)
    sys.exit()

print("About to download:\n")

for v in todownload:
    print(v["fullname"])
print()
print(str(len(todownload)), "beatmaps")

qu = input("\nContinue? (Y/n): ") 
if qu.lower() == "y" or qu == "":
    pass
else:
    print("Closing application...")
    time.sleep(2)
    sys.exit()


session = requests.Session()

r = session.get("https://osu.ppy.sh/home")

headers = {
    'Origin': "https://osu.ppy.sh",
    'Referer': "https://osu.ppy.sh/home",
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134",
    'X-CSRF-Token': session.cookies.get_dict()['XSRF-TOKEN'],
    'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8",
    'Accept': "*/*;q=0.5, text/javascript, application/javascript, application/ecmascript, application/x-ecmascript",
    'X-Requested-With': "XMLHttpRequest",
    'Accept-Language': "en-US",
    'Accept-Encoding': "gzip, deflate, br",
    'Host': "osu.ppy.sh",
    'Content-Length': "85",
    'Connection': "Keep-Alive",
    'Cache-Control': "no-cache"
    }


print()

r = session.post("https://osu.ppy.sh/session", headers=headers, data="_token={}&username={}&password={}".format(session.cookies.get_dict()['XSRF-TOKEN'], login["username"], login["password"]))

dotitlebar()

for i,v in enumerate(todownload):
    dotitlebar()
    print("Downloading: "+v["fullname"]+" "+str(i+1)+"\\"+str(len(todownload))+"\n")
    retries = 3
    while retries != 0:
        with open(v["fullname"]+".osz", "wb+") as f:
            response = session.get("https://osu.ppy.sh/beatmapsets/{}/download".format(v["id"]), stream=True)
            if r.status_code == requests.codes.ok:
                retries = 0
                total_length = response.headers.get('content-length')
                if total_length is None: # no content length header
                    f.write(response.content)
                else:
                    dl = 0
                    total_length = int(total_length)
                    for data in response.iter_content(chunk_size=4096):
                        dl += len(data)
                        f.write(data)
                        done = int(50 * dl / total_length)
                        sys.stdout.write("\r{}% [{}{}]".format(round(dl / total_length * 100), '=' * done, ' ' * (50-done)))    
                        sys.stdout.flush()
                print("\n")
            else:
                retries -= 1
                print("Failed to get map, retrying")
                time.sleep(1)
