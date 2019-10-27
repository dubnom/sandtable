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
    url = "https://www.google.com/search?q="+query+"&source=lnms&tbm=isch"+tbs+"&sa=1&biw=1200&bih=357"

    content = requests.get(url, headers=header).content
    fileNames = re.findall('"ity":"(.*?)","oh":[0-9]*,"ou":"(.*?)"', content.decode())

    imageInfo = []
    pat = re.compile('(\\\\u[0-9a-fA-F]{4})')
    for ty, fn in fileNames:
        fn = pat.sub(lambda x: chr(int(x.group(1)[3:], 16)), fn)
        imageInfo.append((fn, ty.lower()))
    return imageInfo


def fetchImage(url, fileType, directory, fileName):
    req = urllib.request.Request(url, headers=header)
    raw_img = urllib.request.urlopen(req).read()

    if fileType not in ["jpg", "jpeg", "gif", "png"]:
        fileType = 'jpg'
    with open(os.path.join(directory, fileName+"."+fileType), 'wb') as f:
        f.truncate()
        f.write(raw_img)


def fetchImages(imageInfo, directory, fileName, counter=0):
    for url, fileType in imageInfo:
        try:
            fetchImage(url, fileType, directory, "%s%04d" % (fileName, counter))
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
