# Automatically downloads files from OpenEv website
# and sorts them according to their tags
# by Raymond

from bs4 import BeautifulSoup as bs

import os
import shutil
import argparse

import util

OUTPUT_DIRECTORY = 'output'


def get_url(year: int, category="") -> str:
    base_url = 'https://openev.debatecoaches.org'

    if category != "":
        category = category.title()

    return f'{base_url}/{year}/{category}'


def get_output_path(root=os.getcwd()):
    return os.path.join(root, OUTPUT_DIRECTORY, util.current_time())


def get_table(url: str):
    """Get table with files as BeautifulSoup table"""
    print(f"Connecting to: {url}")
    r = util.get_or_stop(url)
    soup = bs(r.text, 'html.parser')
    return soup.select('#FileTable')[0]


def get_files(table):
    """Parse BeautifulSoup table into files"""

    print("Extracting files from website")

    files = []

    # remove column names
    table.select('.sortHeader')[0].extract()

    for file in table.children:
        tds = list(file.children)
        name = tds[0].get_text(strip=True)
        url = tds[0].div.p.span.a['href']
        camp = tds[1].get_text(strip=True)
        tags = tds[2].get_text(strip=True).split(',')
        for tag in tags:
            tags.add(tag)
        file = File(name, url, camp, tags)
        files.append(file)
    print(f"Found {len(files)} files")

    return files


def make_dirs(path, tags):
    paths = {}

    os.makedirs(path, exist_ok=True)

    # make paths from tags
    for tag in tags:
        paths[tag] = path + f'\\{tag}'
    paths['.temp'] = path + '\\.temp'

    # create directories at paths
    for p in paths.values():
        os.makedirs(p, exist_ok=True)

    return paths


def download_table(path, paths, files):
    tags = set([file.tag for file in files])

    make_dirs(path, tags)
    os.chdir(path)

    for i in range(len(files)):
        file = files[i]

        # print progress
        numerator = str(i).zfill(3)
        denominator = str(len(files)).zfill(3)
        percentage = str(round(100 * i / len(files), 3)).zfill(7)  # TODO: Fix formatting
        print(f"*** PROGRESS: {numerator}/{denominator} = {percentage}% ***")

        # download file
        print(f"DOWNLOADING\t{file.name}")
        file.download(paths['.temp'])

        # copy file
        print(f"COPYING\t\t{file.name}")
        for tag in file.tags:
            src = paths['.temp'] + f'\\{file.name}.docx'
            dst = paths[tag] + f'\\{file.name}.docx'
            shutil.copy2(src, dst)

    # delete the temp folder
    shutil.rmtree(paths['.temp'])


class File:
    """
    Represents one file uploaded to OpenEv
    """

    def __init__(self, name, url, camp, tags):
        self.name = name
        self.url = url
        self.camp = camp
        self.tags = tags

    def download(self, path, name=None):
        """
        Downloads the file from self.url
        :param path: the path to save the file to
        :param name: (optional) rename the file
        :return: None
        """
        if name is None:
            name = self.name
        os.chdir(path)
        r = util.get_or_stop(self.url)
        open(f'{name}.docx', 'wb').write(r.content)


# directly run (not called as library)
if __name__ == '__main__':
    # parse command line arguments
    argparser = argparse.ArgumentParser()
    argparser.add_argument("year", help="specify which year's files to download", type=int)
    argparser.add_argument("-d", "--debug", action="store_true", help="run the program in debug mode")
    args = argparser.parse_args()

    # run code
    url = get_url(args.year)
    table = get_table(url)
