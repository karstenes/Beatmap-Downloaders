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
platform  = os.name

def dotitlebar():
    if platform == "nt":
    	os.system("cls")
    else:
	os.system("clear")
    print("-----[Super Ultimate Sotarks Downloader V1 by karstenes]-----\n")

def loadlogin():
    try:
        with open('data.pydata', 'rb') as f:
            login = pickle.load(f)
            f.close()
            return login
    except Exception as e:
        return {}

def queryuser(userid):
	r = requests.post("https://osu.ppy.sh/api/get_beatmaps", data={"k":apikey, "u":userid})
	return json.loads(r.content)

custom = input("Use a custom songs folder (default is in localappdata/osu!/Songs)? (Y/n): ")
if custom.lower() == "y" or custom == "":
    print()
    folder = input("Custom songs folder: ")
    os.chdir(folder)
else:
    os.chdir(os.getenv('localappdata')+"\\osu!\\Songs")


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



q = queryuser("sotarks")

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
qu = input("\nContinue? (Y/n): ") 
if qu.lower() == "y" or qu == "":
    pass
else:
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

for v in  todownload:
    print("Downloading: "+v["fullname"]+"\n")
    with open(v["fullname"]+".osz", "wb+") as f:
        response = session.get("https://osu.ppy.sh/beatmapsets/{}/download".format(v["id"]), stream=True)
        total_length = response.headers.get('content-length')
        if total_length is None:
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
