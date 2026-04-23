import requests
import re
import urllib.request
import urllib.error
import urllib.parse
import os

header = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}

# Size:     Any (None), large, medium, icon
# Color:    Any (None), color, gray, trans
# Type:     Any (None), face, photo, clipart, lineart

CLIENT_ID = "463291698813-feu7uujf39986hmbq37m9k1fv9js6b2e.apps.googleusercontent.com"
API_KEY = "AIzaSyCQV7ZgJYmqs50OpjFPeSHwfy3U8K3czJI"
PROJECT_ID = "project=white-rune-147815"
CX = "012131163717407201601:uikkqitby9c"
CLIENT_ID = "463291698813-nbpkrfdunojp2g1g0u578r24m1u9vnsf.apps.googleusercontent.com"
CLIENT_ID = "361169336202-fkc96ihd7063h8j0a2bhhci0lrqb8opq.apps.googleusercontent.com"
API_KEY = "AIzaSyB8X3xEwwNwA7OWx88571tsvfjrSd-bAlU"
PROJECT_NUMBER = "361169336202"
PROJECT_ID = "sandtable-493918"
API_KEY = "AIzaSyBDkoJhyp_pwewYWr5YsshfSun_fxKB6Ag"
API_KEY = "AIzaSyB7cskNuztzp9GZrUvZBYYkY9ZH8U3ibqE"

def gis(query):
    from google_images_search import GoogleImagesSearch
    giss = GoogleImagesSearch(API_KEY, CX)

    params = {
            'q': query,
            'num': 10,
    }
    giss.search(search_params=params)
    for image in gis.results():
        print(image.url)

print(gis("puppies"))

def googleImages(query, size=None, color=None, ty=None):
    t = []
    if size:
        t.append('isz:%.1s' % size.lower())
    if color:
        t.append('ic:%.5s' % color.lower())
    if ty:
        t.append('itp:%s' % ty.lower())
    tbs = '&tbs=' + ','.join(t) if len(t) else ''

    query = '+'.join(query.split())
    url = "https://www.google.com/search?q="+query+"&source=lnms&tbm=isch"+tbs+"&sa=X&biw=1200&bih=357"

    content = requests.get(url, headers=header).content
    fileNames = re.findall('\\["(http.?://.*?)",(\d+),(\d+)]', content.decode())

    imageInfo = []
    pat = re.compile('(\\\\u[0-9a-fA-F]{4})')
    for fn in fileNames:
        imageInfo.append(fn[0])
    return imageInfo


def fetchImage(url, directory, fileName):
    req = urllib.request.Request(url, headers=header)
    raw_img = urllib.request.urlopen(req).read()

    with open(os.path.join(directory, fileName), 'wb') as f:
        f.truncate()
        f.write(raw_img)


def fetchImages(imageInfo, directory, fileName, counter=0):
    for url in imageInfo:
        try:
            fetchImage(url, directory, "%s%04d" % (fileName, counter))
            counter += 1
        except Exception:
            pass
    return counter


if __name__ == '__main__':
    DIR = "Pictures"
    query = input("Query image:")
    imageInfo = googleImages(query)
    print(imageInfo)

    if not os.path.exists(DIR):
        os.mkdir(DIR)
    DIR = os.path.join(DIR, query.split()[0])
    if not os.path.exists(DIR):
        os.mkdir(DIR)

    print("Downloaded %d images" % fetchImages(imageInfo, DIR, query))
