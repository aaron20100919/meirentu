import requests, warnings, re, time, os
from requests.packages import urllib3

urllib3.disable_warnings()
warnings.filterwarnings("ignore")

# 自己指定 url 和 path
main_url = 'https://meirentu.top/model/%E5%B9%BC%E5%B9%BC.html'
path = './'

target_pattern = r'^(\d+)\.jpg$'

cnt = 0
for filename in os.listdir(path):
    match = re.match(target_pattern, filename)
    if match:
        number = int(match.group(1))
        if number > cnt:
            cnt = number
cnt += 1


headers = {
    'authority': 'cdn2.mmdb.cc',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'cache-control': 'max-age=0',
    'if-modified-since': 'Fri, 25 Aug 2023 10:44:14 GMT',
    'if-none-match': '"64e885fe-1d84c"',
    'referer': 'https://meirentu.top/',
    'sec-ch-ua': '"Microsoft Edge";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.41',
}

while True:
    try:
        main_get = requests.get(main_url, headers=headers)
        main_get.raise_for_status()
    except Exception as e:
        print(e)
        pass
    else:
        time.sleep(1)
        break
main_html = main_get.content.decode('utf-8')

print('init ok')

urls = ['https://meirentu.top' + url for url in re.findall(r'<a href="(/pic/\d+?).html"', main_html)]

try:
    for _url in urls:
        for i in range(1, 100):
            url = '%s-%d.html' % (_url, i)
            while True:
                try:
                    html_get = requests.get(url, headers=headers)
                    html_get.raise_for_status()
                except Exception as e:
                    print(e)
                    pass
                else:
                    time.sleep(1)
                    break

            html = html_get.content.decode('utf-8')
            pics_urls = re.findall(r'src="(https://cdn\d+?.mmdb.cc/file/\d+?/\d+?/\d+?.jpg)"', html)

            # print(url, pics_urls)
            print('%s get ok' % url)

            for pic_url in pics_urls:
                while True:
                    try:
                        pic_get = requests.get(pic_url, headers=headers)
                        pic_get.raise_for_status()
                    except Exception as e:
                        print(e)
                        pass
                    else:
                        time.sleep(1)
                        break

                if len(pic_get.content) > 10000:
                    with open('%s/%s.jpg' % (path, cnt), 'wb') as f:
                        f.write(pic_get.content)
                        print('%s/%s.jpg id ok' % (path, cnt))
                        cnt += 1
                        # raise KeyboardInterrupt



except KeyboardInterrupt:
    pass
