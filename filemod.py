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
from os.path import exists
from platform import system
from os import mkdir as mkdir2
from regex import search


def filtern(filen: str):
    "对文件名进行去除不应该字符"
    filen = str(filen)
    re = search(r'[^[:print:]]', filen)
    while re is not None:
        filen = filen.replace(re.group(), '_')
        re = search(r'[^[:print:]]', filen)
    filen = filen.replace('/', '_')
    filen = filen.replace('\\', '_')
    filen = filen.replace(':', '_')
    filen = filen.replace('*', '_')
    filen = filen.replace('?', '_')
    filen = filen.replace('"', '_')
    filen = filen.replace('<', '_')
    filen = filen.replace('>', '_')
    filen = filen.replace('|', '_')
    filen = filen.replace('\t', '_')
    while len(filen) > 0 and filen[0] == ' ':
        filen = filen[1:]
    return filen


def filterd(dir: str) -> str:
    "对文件夹去除不应该出现的字符"
    p = system()
    if p == "Windows":
        f = ""
        r = search(r'^[A-Z]:[\\/]?', dir)
        if r != None:
            f = r.group()
            dir = dir[len(f):]
            if f[-1] != "/" and f[-1] != '\\':
                f = f+'/'
            if dir == "":
                return f
    if dir[-1] != '/' and dir[-1] != '\\':
        dir = dir+'/'
    re = search(r'[^[:print:]]', dir)
    while re is not None:
        dir = dir.replace(re.group(), '_')
        re = search(r'[^[:print:]]', dir)
    dir = dir.replace(':', '_')
    dir = dir.replace('*', '_')
    dir = dir.replace('?', '_')
    dir = dir.replace('"', '_')
    dir = dir.replace('<', '_')
    dir = dir.replace('>', '_')
    dir = dir.replace('|', '_')
    if p == 'Windows':
        dir = f+dir
    return dir


def mkdir(dir: str):
    dir = filterd(dir)
    dl = dir.split('/')[:-1]
    if len(dl):
        s = ""
        f = True
        for i in dl:
            if f:
                f = False
                s = i
            else:
                s = s+"/"+i
            if s != "" and not exists(s):
                mkdir2(s)
