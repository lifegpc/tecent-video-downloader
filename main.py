# (C) 2020 lifegpc
# This file is part of tecent-video-downloader.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import common
from regex import search, I
import pickle
from time import sleep
from os.path import exists, abspath
from json import loads
from requests import Session
from filemod import mkdir, filterd, filtern
from ffmpegmod import FFMpegOption, FFMpeg


class main:
    def __confirm_download(self):
        self.__driver.execute_script('alert("请在控制台窗口进行确认。")')
        while True:
            inp = input('确认要开始下载了吗？（下载开始后请不要调整画质，以免造成BUG。）(y/n)')
            if len(inp) > 0:
                if inp[0].lower() == 'y':
                    return True
                elif inp[0].lower() == 'n':
                    return False

    def __detail_loop(self):
        try:
            url = self.__driver.current_url
        except:
            self.__driver = None
            return True
        if self.__videoType == 0:
            self.__metadata = {'title': '',
                               'desc': '', 'username': '', 'tags': []}
        da = self.__metadata
        try:
            title = self.__driver.find_elements_by_class_name(
                'video_title._video_title')
            if len(title) != 0:
                if 'title' not in da or da['title'] == '':
                    da['title'] = title[0].text
                if self.__videoType == 1:
                    da['subTitle'] = title[0].text
            summary = self.__driver.find_elements_by_class_name('summary')
            if len(summary) != 0:
                if 'desc' not in da or da['desc'] == '':
                    if summary[0].text != '':
                        da['desc'] = summary[0].text
                    else:
                        button = self.__driver.find_elements_by_class_name(
                            'icon_sm.icon_arrow_down_sm.icon_rotate_down')
                        if len(button) != 0:
                            button[0].click()
                        return False
            userName = self.__driver.find_elements_by_class_name('user_name')
            if len(userName) != 0:
                if 'username' not in da or da['username'] == '':
                    for username in userName:
                        if username.text != '':
                            da['username'] = username.text
                            break
            tagListE = self.__driver.find_elements_by_class_name('video_tags')
            if len(tagListE) != 0:
                tagList = tagListE[0].find_elements_by_tag_name('a')
                if 'tags' not in da:
                    da['tags'] = []
                for tag in tagList:
                    tagName = tag.text
                    if tagName not in da['tags']:
                        da['tags'].append(tagName)
        except common.exceptions.NoSuchElementException:
            return False
        except:
            self.__driver = None
            return True
        return True

    def __detail_page_loop(self):
        try:
            url = self.__driver.current_url
        except:
            self.__driver = None
            return True
        da = {'title': '', 'area': '', 'lang': '',
              'date': '', 'tags': [], 'desc': '', 'alias': ''}
        try:
            title = self.__driver.find_elements_by_class_name('video_title_cn')
            if len(title) != 0:
                titleA = title[0].find_element_by_tag_name('a')
                da['title'] = titleA.text
            typeItems = self.__driver.find_elements_by_class_name('type_item')
            if len(typeItems) != 0:
                for i in range(len(typeItems)):
                    typeItem = typeItems[i]
                    try:
                        typeDetail = typeItem.find_elements_by_tag_name('span')
                    except common.exceptions.NoSuchElementException:
                        pass
                    except:
                        self.__driver = None
                        return True
                    if len(typeDetail) == 2:
                        typeTitle = typeDetail[0].text
                        typeContent = typeDetail[1].text
                        if typeTitle == '地\u3000区:':
                            da['area'] = typeContent
                        elif typeTitle == '语\u3000言:':
                            da['lang'] = typeContent
                        elif typeTitle == '上映时间:':
                            da['date'] = typeContent
                        elif typeTitle == '别\u3000名:':
                            da['alias'] = typeContent
            tagListE = self.__driver.find_elements_by_class_name('tag_list')
            if len(tagListE) > 0:
                tagList = tagListE[0].find_elements_by_class_name('tag')
                for tag in tagList:
                    da['tags'].append(tag.text)
            descTxt = self.__driver.find_elements_by_class_name('desc_txt')
            if len(descTxt) != 0:
                da['desc'] = descTxt[0].text
            self.__metadata = da
        except common.exceptions.NoSuchElementException:
            return False
        except:
            self.__driver = None
            return True
        return True

    def __filter_logs(self, logs: list):
        for log in logs:
            message = loads(log['message'])['message']
            if 'method' in message and message['method'] == 'Network.requestWillBeSent':
                request_url: str = message['params']['request']['url']
                if request_url == 'https://vd.l.qq.com/proxyhttp':
                    if message['params']['request']['hasPostData']:
                        try:
                            obj = loads(message['params']
                                        ['request']['postData'])
                            if 'vinfoparam' in obj:
                                self.__httpproxy_logs.append(message)
                        except:
                            pass

    def __getInput(self):
        inp = input('请输入您想要下载的视频：')
        r = search(
            r'v\.qq\.com/(x/(?P<type>\w+))?(?P<type>detail/[a-z0-9])?/(?P<videoId>[a-z0-9]+)(/(?P<videoSubId>[a-z0-9]+))?', inp, I)
        if r == None:
            print('输入有误，请重试')
            return self.__getInput()
        ree = r.groupdict()
        self.__videoType = 0
        if ree['type'] and (ree['type'] == 'cover' or ree['type'][0:7] == 'detail/'):
            self.__videoType = 1
        self.__videoId = ree['videoId']
        self.__videoSubId = ree['videoSubId']

    def __getVideoPath(self) -> str:
        dire = self.__output_dir
        if self.__videoType == 1:
            if self.__meta('title'):
                dire = filterd(f"{dire}{self.__metadata['title']}")
        if not exists(dire):
            mkdir(dire)
        self.__output_dir = dire
        if self.__meta('subTitle'):
            fileName = f"{self.__metadata['subTitle']}.mp4"
        elif self.__meta('title'):
            fileName = f"{self.__metadata['title']}.mp4"
        elif self.__videoSubId is None:
            fileName = f"{self.__videoId}.mp4"
        else:
            fileName = f"{self.__videoId}-{self.__videoSubId}.mp4"
        return filtern(fileName)

    def __init__(self):
        self.__r = Session()
        self.__r.trust_env = False
        self.__output_dir = 'Download/'

    def __loop(self):
        if self.__downloadComplete:
            return True
        try:
            url = self.__driver.current_url
        except:
            self.__driver = None
            return True
        try:
            logs = self.__driver.get_log('performance')
            self.__logs = self.__logs + logs
            self.__filter_logs(logs)
        except:
            self.__driver = None
            return True
        if len(self.__httpproxy_logs) > 0:
            if self.__request_proxyhttp():
                if self.__vinfo['dltype'] == 8:
                    return True  # 有vinfo信息足以
        return False

    def __meta(self, key: str):
        try:
            return False if key not in self.__metadata or (type(self.__metadata[key]) == str and self.__metadata[key] == '') or (type(self.__metadata[key]) == list and len(self.__metadata[key]) == 0) else True
        except:
            return False

    def __openWebDriver(self):
        try:
            if not exists('Chrome Data'):
                mkdir('Chrome Data')
            cap = DesiredCapabilities.CHROME
            cap["loggingPrefs"] = {"performance": "ALL"}
            cap["goog:loggingPrefs"] = {"performance": "ALL"}
            option = webdriver.ChromeOptions()
            option.add_argument(f"user-data-dir={abspath('Chrome Data')}")
            option.add_argument("disable-logging")
            option.add_argument('log-level=3')
            self.__driver = webdriver.Chrome(
                options=option, desired_capabilities=cap)
            self.__driver.set_page_load_timeout(10)
            self.__driverType = 'Chrome'
        except:
            return False
        return True

    def __openWebPage(self, url: str):
        try:
            self.__driver.get(url)
        except common.exceptions.TimeoutException:
            pass

    def __request_proxyhttp(self):
        found = False
        for message in self.__httpproxy_logs:
            try:
                re = self.__r.post(message['params']['request']['url'], data=message['params']
                                   ['request']['postData'], headers=message['params']['request']['headers'])
                if re.status_code == 200:
                    re = re.json()
                    if re['errCode'] == 0:
                        self.__vinfo = loads(re['vinfo'])
                        if 'ad' in re:
                            self.__ad = loads(re['ad'])
                        found = True
            except:
                pass
        self.__httpproxy_logs.clear()
        return found

    def start(self):
        self.__getInput()
        if not self.__openWebDriver():
            return
        self.__downloadComplete = False
        self.__metadata = {}
        if self.__videoType == 1:
            self.__url = f"https://v.qq.com/detail/m/{self.__videoId}.html"
            self.__openWebPage(self.__url)
            while True:
                if self.__detail_page_loop():
                    break
                sleep(1)
            if self.__driver is None:
                return
            self.__driver.set_page_load_timeout(15)
            if self.__videoSubId is not None:
                self.__openWebPage(
                    f"https://v.qq.com/x/cover/{self.__videoId}/{self.__videoSubId}.html")
            else:
                self.__openWebPage(
                    f"https://v.qq.com/x/cover/{self.__videoId}.html")
        elif self.__videoType == 0:
            self.__driver.set_page_load_timeout(15)
            self.__openWebPage(
                f"https://v.qq.com/x/page/{self.__videoId}.html")
        while True:
            if self.__detail_loop():
                break
            sleep(1)
        if self.__driver is None:
            return
        if not self.__confirm_download():
            return
        self.__logs = []
        self.__httpproxy_logs = []
        while not self.__downloadComplete:
            if self.__loop():
                break
            sleep(1)
        if self.__driver is not None and not self.__downloadComplete:
            try:
                if self.__vinfo['dltype'] == 8:
                    try:
                        if len(self.__vinfo['vl']['vi'][0]['ul']['ui']) > 0:
                            play_url = self.__driver.current_url
                            url = self.__vinfo['vl']['vi'][0]['ul']['ui'][0]['url']
                            videoName = self.__getVideoPath()
                            ffmpeg_option = FFMpegOption()
                            self.__metadata['playUrl'] = play_url
                            ffmpeg_option.metadata = self.__metadata
                            ffmpeg_option.output_dir = self.__output_dir
                            ffmpeg_option.file_name = videoName
                            ffmpeg_option.input_file_name = url
                            ffmpeg_option.m3u8 = True
                            self.__driver.quit()
                            ffmpeg = FFMpeg(ffmpeg_option)
                            ffmpeg.start()
                    except:
                        raise Exception('未知错误。请提交BUG。dltype：8。')
            except AttributeError:
                pass


if __name__ == "__main__":
    m = main()
    m.start()
