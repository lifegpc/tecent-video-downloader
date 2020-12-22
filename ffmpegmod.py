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
from filemod import mkdir, filterd, filtern
from os.path import exists
from time import time
from math import floor
from regex import search
from os import system, remove


class FFMpegOption:
    output_dir = 'Download/'
    file_name = 'cs.mp4'
    input_file_name = 'cs.temp.mp4'
    m3u8 = False
    metadata = {}

    def meta(self, key: str):
        try:
            return False if key not in self.metadata or (type(self.metadata[key]) == str and self.metadata[key] == '') or (type(self.metadata[key]) == list and len(self.metadata[key]) == 0) else True
        except:
            return False


class FFMpeg:
    def __dumps_metadata_file(self):
        if not exists('Temp'):
            mkdir('Temp')
        fileName = f"Temp/{floor(time() * 1000)}.txt"
        self.__tempName = fileName
        with open(fileName, 'w', encoding='utf8', newline='\n') as f:
            f.write(';FFMETADATA1\n')
            if self.__meta('subTitle'):
                if self.__meta('title'):
                    if self.__metadata['title'] != self.__metadata['subTitle']:
                        f.write(f"title={self.__filter(self.__metadata['title'])} - {self.__filter(self.__metadata['subTitle'])}\n")
                    else:
                        f.write(f"title={self.__filter(self.__metadata['title'])}\n")
                    f.write(f"album={self.__filter(self.__metadata['title'])}\n")
                else:
                    f.write(f"title={self.__filter(self.__metadata['subTitle'])}\n")
            elif self.__meta('title'):
                f.write(f"title={self.__filter(self.__metadata['title'])}\n")
            if self.__meta('desc'):
                f.write(f"comment={self.__filter(self.__metadata['desc'])}\n")
            if self.__meta('username'):
                f.write(f"artist={self.__filter(self.__metadata['username'])}\n")
            if self.__meta('date'):
                f.write(f"date={self.__filter(self.__metadata['date'])}\n")

    def __filter(self, i:str):
        s = str(i)
        re = search(r'[^[:print:]\r\n]', s)
        while re is not None:
            s = s.replace(re.group(), '_')
            re = search(r'[^[:print:]\r\n]', s)
        s = s.replace('#', '\\#')
        s = s.replace('\\', '\\\\')
        s = s.replace('=', '\\=')
        s = s.replace(';', '\\;')
        s = s.replace('\r', '')
        s = s.replace('\n', '\\\n')
        return s

    def __init__(self, Option: FFMpegOption = FFMpegOption()):
        self.__options = Option
        self.__options.output_dir = filterd(self.__options.output_dir)
        self.__options.file_name = filtern(self.__options.file_name)
        self.__metadata = self.__options.metadata
        self.__tempName = ''
    
    def __meta(self, key: str):
        return self.__options.meta(key)

    def start(self):
        if not exists(self.__options.output_dir):
            mkdir(self.__options.output_dir)
        self.__dumps_metadata_file()
        if self.__options.m3u8:
            commandLine = f"""ffmpeg -i "{self.__options.input_file_name}" -i "{self.__tempName}" -map 0 -map_metadata 1 -c copy "{self.__options.output_dir}{self.__options.file_name}" """
            re = system(commandLine)
            if exists(self.__tempName):
                remove(self.__tempName)
            if re != 0:
                raise Exception(f'调用ffmpeg可能失败。返回值：{re}。')
