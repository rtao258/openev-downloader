# Automatically downloads files from OpenEv website
# and sorts them according to their tags
# by Raymond

from bs4 import BeautifulSoup as bs

from typing import Sequence

import os
import shutil
import argparse

import util

DEFAULT_OUTPUT_DIRECTORY = 'output'


class File:
    """
    Represents one file uploaded to OpenEv
    """

    def __init__(self, name, url, camp, tags):
        self.name = name
        self.url = url
        self.camp = camp
        self.tags = tags

    def __repr__(self):
        return f"File('{self.name}', '{self.url}', '{self.camp}', {self.tags})"

    def download(self, path, name=None):
        """
        Downloads the file from self.url
        :param path: the path to save the file to
        :param name: (optional) rename the file
        :return: None
        """
        if name is None:
            name = self.name
        r = util.get_or_stop(self.url)
        path_to_file = os.path.join(path, f'{name}.docx')
        with open(path_to_file, 'wb') as output_file:
            output_file.write(r.content)


def get_url(year: int, category="") -> str:
    base_url = 'https://openev.debatecoaches.org'

    if category != "":
        category = category.title()

    return f'{base_url}/{year}/{category}'


def get_output_path(root=os.getcwd()):
    return os.path.join(root, DEFAULT_OUTPUT_DIRECTORY, util.current_time())


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
        file = File(name, url, camp, tags)
        files.append(file)
    print(f"Found {len(files)} files")

    return files


def make_dirs(path, tags):
    paths = {}

    os.makedirs(path, exist_ok=True)

    # make paths from tags
    for tag in tags:
        paths[tag] = os.path.join(path, tag)

    # create directories at paths
    for p in paths.values():
        os.makedirs(p, exist_ok=True)

    return paths


def download_files(path: str, files: Sequence[File]) -> None:
    # aggregate the tags of all files
    tags = set()
    for file in files:
        tags |= set(file.tags)

    paths = make_dirs(path, tags)

    for i in range(len(files)):
        file = files[i]

        # print progress
        numerator = str(i).zfill(3)
        denominator = str(len(files)).zfill(3)
        percentage = str(round(100 * i / len(files), 3)).zfill(7)  # TODO: Fix formatting
        print(f"*** PROGRESS: {numerator}/{denominator} = {percentage}% ***")

        # download file
        print(f"DOWNLOADING\t{file.name}")
        for tag in file.tags:
            file.download(paths[tag])

    print("*** DOWNLOAD COMPLETE ***")


# define as separate function so it shows up in my Structure view in PyCharm yaaay
def main():
    # parse command line arguments
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        'year',
        type=int,
        help="specify which year's files to download",
    )
    argparser.add_argument(
        '-d', '--debug',
        action='store_true',
        help="run the program in debug mode",
    )
    argparser.add_argument(
        '-o', '--output', default=DEFAULT_OUTPUT_DIRECTORY,
        help="change the name of the output directory",
    )
    args = argparser.parse_args()

    # run code
    url = get_url(args.year)
    table = get_table(url)
    files = get_files(table)
    download_files(args.output, files)


# if directly run (not called as library)
if __name__ == '__main__':
    main()
