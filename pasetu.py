import os
import re
import requests
import warnings
from requests.packages import urllib3
from hashlib import sha256

urllib3.disable_warnings()
warnings.filterwarnings("ignore")


def calculate_hash(filepath, block_size=8092):
    hash_obj = sha256()
    with open(filepath, "rb") as file:
        while True:
            data = file.read(block_size)
            if not data:
                break
            hash_obj.update(data)
    return hash_obj.hexdigest()


def find_duplicate_images(_directory):
    image_hashes = {}
    duplicates = []

    for root, _, files in os.walk(_directory):
        for file in files:
            if file.lower().endswith(".jpg"):
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


def download_image(image_url, _directory):
    for tries in range(3):
        try:
            image_get = requests.get(image_url, headers=headers)
            image_get.raise_for_status()
        except Exception as ex:
            print(ex)
            pass
        else:
            if len(image_get.content) > 10000:
                cnt = get_next_file_number(_directory, r'(\d+)\.jpg$')
                with open(r'%s\%s.jpg' % (_directory, cnt), 'wb') as file:
                    file.write(image_get.content)
                    print(r'%s\%s.jpg is ok' % (_directory, cnt))
                    return True
    return False


def get_next_file_number(_directory, pattern):
    cnt = 0
    for filename in os.listdir(_directory):
        match = re.match(pattern, filename)
        if match:
            number = int(match.group(1))
            if number >= cnt:
                cnt = number + 1
    return cnt


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

directory = '.\\'
log_file = '.\\'


def write_log(log):
    with open(log_file, 'a') as file:
        file.write(log + '\n')


def read_log():
    if not os.path.exists(log_file):
        return None
    with open(log_file, 'r') as file:
        return file.read()


log_lines = read_log()
if log_lines:
    last_page = int(re.findall(r'page:(\d+)', log_lines)[-1]) + 1
else:
    last_page = 1

for page in range(last_page, 100):

    main_url = f'https://meirentu.top/hots/{page}.html'

    try:
        main_get = requests.get(main_url, headers=headers)
        main_get.raise_for_status()

        main_html = main_get.content.decode('utf-8')

        print('page %s' % page)
        write_log(f'page:{page}')

        urls = ['https://meirentu.top' + url for url in re.findall(r'<a href="(/pic/\d+?).html"', main_html)]

        urls_len = len(urls)

        for _url in urls:
            urls_len -= 1

            delete_duplicates(find_duplicate_images(directory))
            try:
                for i in range(1, 100):
                    url = '%s-%d.html' % (_url, i)
                    write_log(f'url:{url}')
                    print('getting')
                    html_get = requests.get(url, headers=headers)
                    html_get.raise_for_status()

                    html = html_get.content.decode('utf-8')
                    print('re')
                    pics_urls = re.findall(r'<img alt=".+?" src="(https://cdn\d+?.mmdb.cc/file/\d+?/\d+?/\d+?.jpg)"',
                                           html)

                    # print(url, pics_urls)
                    print('%s get ok' % url)

                    download_num = 0

                    for pic_url in pics_urls:
                        download_num += int(download_image(pic_url, directory))

                    print('%s of %s downloads ok' % (download_num, len(pics_urls)))

            except Exception as e:
                print(e)
                print(f'{len(urls) - urls_len} of page {page} downloads ok')
                pass

        print(f'{urls_len} of {len(urls)} pics ok')

    except KeyboardInterrupt:
        pass
