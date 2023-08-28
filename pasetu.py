import os
import re
import requests
import time
import warnings
from requests.packages import urllib3
from hashlib import sha256

urllib3.disable_warnings()
warnings.filterwarnings("ignore")


def calculate_hash(filepath, block_size=65536):
    hash_obj = sha256()
    with open(filepath, "rb") as f:
        while True:
            data = f.read(block_size)
            if not data:
                break
            hash_obj.update(data)
    return hash_obj.hexdigest()


def find_duplicate_images(path):
    image_hashes = {}
    duplicates = []

    for root, _, files in os.walk(path):
        for file in files:
            if file.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
                file_path = os.path.join(root, file)
                hash_value = calculate_hash(file_path)
                if hash_value in image_hashes:
                    duplicates.append((file_path, image_hashes[hash_value]))
                else:
                    image_hashes[hash_value] = file_path

    return duplicates


def delete_duplicates(duplicates):
    for duplicate_pair in duplicates:
        print(f"Deleting duplicate: {duplicate_pair[0]}")
        os.remove(duplicate_pair[0])


for page in range(1, 100):
    print('page %s' % page)

    main_url = f'https://meirentu.top/index/{page}.html'
    path = './'

    headers = {
        'authority': 'cdn2.mmdb.cc',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.7',
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
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 '
                      'Safari/537.36 Edg/111.0.1661.41',
    }

    try:
        main_get = requests.get(main_url, headers=headers)
        main_get.raise_for_status()

        main_html = main_get.content.decode('utf-8')

        print('init ok')

        urls = ['https://meirentu.top' + url for url in re.findall(r'<a href="(/pic/\d+?).html"', main_html)]

        for _url in urls:
            delete_duplicates(find_duplicate_images(path))
            try:
                for i in range(1, 100):
                    url = '%s-%d.html' % (_url, i)
                    html_get = requests.get(url, headers=headers)
                    html_get.raise_for_status()

                    html = html_get.content.decode('utf-8')
                    pics_urls = re.findall(r'src="(https://cdn\d+?.mmdb.cc/file/\d+?/\d+?/\d+?.jpg)"', html)

                    # print(url, pics_urls)
                    print('%s get ok' % url)

                    for pic_url in pics_urls:
                        for times in range(5):
                            try:
                                pic_get = requests.get(pic_url, headers=headers)
                                pic_get.raise_for_status()
                            except Exception as e:
                                print(e)
                                pass
                            else:
                                time.sleep(1)
                                if len(pic_get.content) > 50000:
                                    cnt = 0
                                    for filename in os.listdir(path):
                                        target_pattern = r'(\d+)\.jpg$'
                                        match = re.match(target_pattern, filename)
                                        if match:
                                            number = int(match.group(1))
                                            if number >= cnt:
                                                cnt = number + 1
                                    with open('%s/%s.jpg' % (path, cnt), 'wb') as f:
                                        f.write(pic_get.content)
                                        print('%s/%s.jpg is ok' % (path, cnt))
                                        cnt += 1
                                        # raise KeyboardInterrupt
                                        break
                                elif len(pic_get.content) > 10000:
                                    cnt = 0
                                    for filename in os.listdir(path):
                                        target_pattern = r'small_(\d+)\.jpg$'
                                        match = re.match(target_pattern, filename)
                                        if match:
                                            number = int(match.group(1))
                                            if number >= cnt:
                                                cnt = number + 1
                                    with open('%s/small_%s.jpg' % (path, cnt), 'wb') as f:
                                        f.write(pic_get.content)
                                        print('%s/small_%s.jpg is ok' % (path, cnt))
                                        cnt += 1
                                        # raise KeyboardInterrupt
                                        break
            except Exception as e:
                delete_duplicates(find_duplicate_images(path))
                print(e)
                pass
    except KeyboardInterrupt:
        pass
