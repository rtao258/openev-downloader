# this code is actually really disgusting
# and I'm ashamed to say that I wrote it
# Raymond

import os
import re
import argparse
import requests
from bs4 import BeautifulSoup as bs

# for those epic gamer moments
from epic_gamer_moment import get_epic_gamer_moment

OUTPUT_DIR = os.path.join('output', 'wiki')


class Wiki:
    def __init__(self, url):
        self.url = url


HS_WIKI = Wiki('https://hspolicy.debatecoaches.org')
COLLEGE_WIKI = Wiki('https://opencaselist.paperlessdebate.com')


def get_table_by_id(soup, id):
    """
    Gets all the td, excluding th, from a table with a given id in a given soup.
    :param soup: BeautifulSoup of all tags in which to search for id
    :param id: id of the desired <table> element from which to extract td
    :return: a 2D array of td
    """
    # dont include .tbody after the find() for some reason
    rows = soup.find(id=id).find_all('tr')[1:]
    table = [row.contents for row in rows]
    return table


class School:
    def __init__(self, wiki, name, state, school_url_part):
        self.wiki = wiki
        self.name = name
        self.state = state
        self.school_url_part = school_url_part

    @property
    def url(self):
        return self.wiki.url + self.school_url_part


def get_schools(wiki):
    schools = []
    soup = bs(requests.get(wiki.url).text, features='html.parser')
    anchors = soup.find(class_='Schools').div.contents[1].p.find_all('a')
    for anchor in anchors:
        name = anchor.text[:-5]
        state = anchor.text[-3:-1]
        school_url_part = anchor['href'][:-1]
        schools.append(School(wiki, name, state, school_url_part))
    return schools


class Debater:
    def __init__(self, first, last):
        self.first = first
        self.last = last

    @property
    def full(self):
        return self.first + ' ' + self.last


class Team:
    def __init__(self, school, debater1, debater2, aff_url_part, neg_url_part):
        self.school = school
        self.debater1 = debater1
        self.debater2 = debater2
        self.aff_url_part = aff_url_part
        self.neg_url_part = neg_url_part

    @property
    def wiki(self):
        # what kind of sick person would ever write this
        return self.school.wiki

    @property
    def full_names(self):
        return self.debater1.full + ' - ' + self.debater2.full

    @property
    def last_names(self):
        return self.debater1.last + '-' + self.debater2.last

    @property
    def aff_url(self):
        return self.wiki.url + self.aff_url_part

    @property
    def neg_url(self):
        return self.wiki.url + self.neg_url_part


def parse_debater_names(names):
    debater1, debater2 = names.split(' - ')
    debater1 = debater1.split()
    debater2 = debater2.split()
    debater1 = Debater(debater1[0], debater1[-1])
    debater2 = Debater(debater2[0], debater2[-1])
    return debater1, debater2


def get_teams(school):
    teams = []
    soup = bs(requests.get(school.url).text, features='html.parser')
    table = get_table_by_id(soup, 'tblTeams')
    for row in table:
        debater1, debater2 = parse_debater_names(row[0].div.p.text[len(school.name) + 1:])
        aff_url_part = row[1].span.a['href']
        neg_url_part = row[2].span.a['href']
        teams.append(Team(school, debater1, debater2, aff_url_part, neg_url_part))
    return teams


class OpenSource:
    def __init__(self, team, side, filename, url, date, uploader):
        self.team = team
        self.side = side
        self.filename = filename
        self.url = url
        self.date = date
        self.uploader = uploader

    @property
    def school(self):
        return self.team.school

    @property
    def wiki(self):
        return self.team.wiki


def interpret_side(side):
    if side == 'both':
        return {'aff': True, 'neg': True}
    if side == 'aff':
        return {'aff': True, 'neg': False}
    if side == 'neg':
        return {'aff': False, 'neg': True}
    raise ValueError(f"invalid input {side} (must be 'aff', 'neg', or 'both')")


def get_open_source(team, aff=True, neg=True):
    open_sources = []
    if aff:
        soup = bs(requests.get(team.aff_url).text, features='html.parser')
        table = get_table_by_id(soup, 'tblOpenSource')
        for row in table:
            anchor = row[0].div.p.span.a
            filename = anchor.text
            url = anchor['href']
            date = row[1].div.p.text
            uploader = row[2].div.p.text
            open_source = OpenSource(team, "aff", filename, url, date, uploader)
            open_sources.append(open_source)
    if neg:
        soup = bs(requests.get(team.neg_url).text, features='html.parser')
        table = get_table_by_id(soup, 'tblOpenSource')
        for row in table:
            anchor = row[0].div.p.span.a
            filename = anchor.text
            url = anchor['href']
            date = row[1].div.p.text
            uploader = row[2].div.p.text
            open_sources.append(OpenSource(team, "neg", filename, url, date, uploader))

    return open_sources


def iterate(wiki, school_re, team_re, side, ignore_case=True, callback=None):
    open_sources = []

    # compile regular expressions
    re_flag = re.IGNORECASE if ignore_case else 0
    school_re = re.compile(school_re, re_flag)
    team_re = re.compile(team_re, re_flag)

    # make side kwarg
    side = interpret_side(side)

    for school in get_schools(wiki):
        if school_re.search(school.name) is None:
            continue
        print(4 * "*", school.name)
        for team in get_teams(school):
            if team_re.search(team.full_names) is None:
                continue
            print(8 * "*", team.last_names)
            for open_source in get_open_source(team, **side):
                print(12 * "*", open_source.filename)
                open_sources.append(open_source)
                if callback is not None:
                    callback(open_source)

    return open_sources


def download(open_source):
    path = os.path.join(OUTPUT_DIR, open_source.school.name,
                        open_source.team.last_names, open_source.side)
    os.makedirs(path, exist_ok=True)

    downloaded = requests.get(open_source.url).content

    path = os.path.join(path, open_source.filename)
    with open(path, 'wb') as file:
        file.write(downloaded)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()

    # filters
    argparser.add_argument("-w", "--wiki", default="hs", choices=["hs", "college"], help="hs or college wiki")
    argparser.add_argument("-s", "--school", default="",
                           help="regular expression to filter the list of schools")
    argparser.add_argument("-t", "--team", default="",
                           help="regular expression to filter the list of teams")
    argparser.add_argument("-i", "--side", default="both", choices=["aff", "neg", "both"],
                           help="filter for files from a particular side (i.e. aff or neg team page)")

    # flags
    argparser.add_argument("-g", "--epic-gamer-moment", choices=["fps", "minecraft", "random"],
                           help="ignoring everything else, returns a link to one of two pictures"
                                "of Aden Barton playing a video game while appearing as if he is debating")
    argparser.add_argument("-d", "--debug", action="store_true", help="run the program in debug mode")

    args = argparser.parse_args()
    if args.epic_gamer_moment is not None:
        print(get_epic_gamer_moment(args.epic_gamer_moment))
    else:
        iterate(HS_WIKI, args.school, args.team, args.side, callback=download)
