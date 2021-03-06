#!/usr/bin/env python3
import mwparserfromhell
import re
import pywikibot as pb
import time
from random import randint
import argparse

MIN_YEAR = 1800

months = {
    "sv" : ["januari", "februari", "mars", "april", "maj", "juni", "juli", "augusti", "september", "oktober", "november", "december"],
    "no" : ["januar", "februar", "mars", "april", "mai", "juni", "juli", "august", "september", "oktober", "november", "desember"],
    "da" : ["januar", "februar", "marts", "april", "maj", "juni", "juli", "august", "september", "oktober", "november", "december"],
    "pl" : ["stycznia", "lutego", "marca", "kwietnia", "maja", "czerwca", "lipca", "sierpnia", "września", "października", "listopada", "grudnia"]
}

wikis = {
    "sv" : "Q169514",
    "no" : "Q191769",
    "da" : "Q181163",
    "pl" : "Q1551807"
}

props = {
    "born" : "P569",
    "dead" : "P570"
}

def itemIsHuman(wdItem):
    item_dict = wdItem.get()
    clm_dict = item_dict["claims"]
    clm_list = clm_dict["P31"]
    for clm in clm_list:
        clm_trgt = clm.getTarget()
        if clm_trgt.getID() == "Q5":
            return True

def findBornSection(language, text):
    if language == "sv":
        patternShort = re.compile("född [0-9]{4}")
        patternLong = re.compile("född [0-9]{1,2} [a-z]+ [0-9]{4}")
    elif language == "no" or language == "da":
        patternShort = re.compile("født [0-9]{4}")
        patternLong = re.compile("født [0-9]{1,2}\. [a-z]+ [0-9]{4}")
    elif language == "pl":
        patternShort = re.compile("ur\. [0-9]{4}")
        patternLong = re.compile("ur\. [0-9]{1,2} \D+ [0-9]{4}")
    resultLong = patternLong.findall(text)
    if len(resultLong) == 0:
        resultShort = patternShort.findall(text)
        if len(resultShort) == 0:
            return None
        else:
            return resultShort[0]
    else:
        return resultLong[0]

def findDeadSection(language, text):
    if language == "sv":
        patternShort = re.compile("död [0-9]{4}")
        patternLong = re.compile("död [0-9]{1,2} [a-z]+ [0-9]{4}")
    elif language == "no" or language == "da":
        patternShort = re.compile("død [0-9]{4}")
        pattern = re.compile("død [0-9]{1,2}\. [a-z]+ [0-9]{4}")
    elif language == "pl":
        patternShort = re.compile("zm\. [0-9]{4}")
        patternLong = re.compile("zm\. [0-9]{1,2} \D+ [0-9]{4}")
    resultLong = patternLong.findall(text)
    if len(resultLong) == 0:
        resultShort = patternShort.findall(text)
        if len(resultShort) == 0:
            return None
        else:
            return resultShort[0]
    else:
            return resultLong[0]

def get_date_string(language, text):
    if language == "sv":
        patternShort = re.compile("[0-9]{4}")
        patternLong = re.compile("[0-9]{1,2} [a-z]+ [0-9]{4}")
    elif language == "no" or language == "da":
        patternShort = re.compile("[0-9]{4}")
        patternLong = re.compile("[0-9]{1,2}\. [a-z]+ [0-9]{4}")
    elif language == "pl":
        patternShort = re.compile("[0-9]{4}")
        patternLong = re.compile("[0-9]{1,2} \D+ [0-9]{4}")
    resultLong = patternLong.findall(text)
    if len(resultLong) == 0:
        resultShort = patternShort.findall(text)
        if len(resultShort) == 0:
            return None
        else:
            return resultShort[0]
    else:
            return resultLong[0]

def objectify_date(language, string):
    string = string.replace(".", "")
    if len(string) == 4:
        year = int(string)
        return [year]
    else :
        parts = string.split(" ")
        day = int(parts[0])
        year = int(parts[2])
        month_list = months[language]
        monthNumber = month_list.index(parts[1]) + 1
        return [day, monthNumber, year]

def addDate(what, date, item, language):
    if what == "b":
        prop = props["born"]
    elif what == "d":
        prop = props["dead"]
    claim = pb.Claim(repo, prop)
    if len(date) == 1:
        if date[0] < MIN_YEAR:
            return
        timestamp = pb.WbTime(year=date[0])
    else:
        if date[2] < MIN_YEAR:
            return
        timestamp = pb.WbTime(year=date[2], month=date[1], day=date[0])
    claim.setTarget(timestamp)
    item.addClaim(claim)
    print("Set date on " + title + " (" + what + ")")
    addReference(language, claim)

def addReference(language, claim):
    retrieved = pb.Claim(repo, u'P143')
    wikipedia = pb.ItemPage(repo, wikis[language])
    retrieved.setTarget(wikipedia)
    claim.addSources([retrieved])
    print("Added reference (" + language + ")")

def sleepytime():
    sleepTime = (randint(13,65))
    print("Sleeping for " + str(sleepTime))
    time.sleep(sleepTime)

if __name__ == '__main__':
    i = 0
    parser = argparse.ArgumentParser()
    parser.add_argument("language")
    parser.add_argument("list")
    parser.parse_args()

    language = parser.parse_args().language
    pagepile = parser.parse_args().list

    siteWp = pb.Site(language, "wikipedia")

    with open(pagepile, "r") as f:
        titles = []
        for line in f:
            line = line.rstrip('\n')
            titles.append(line)
        noItems = len(titles)

    for title in titles:
        try:
            print("--------------")
            i = i + 1
            page = pb.Page(siteWp, title)
            wikitext = page.text
            parsed = mwparserfromhell.parse(wikitext).strip_code()
            print("Processing line " + str(i) + "/" + str(noItems) + " (" + str(round(100*float(i)/float(noItems), 3)) + " %)")
            try:
                bornSection = findBornSection(language, parsed)
                date_birth = objectify_date(language, get_date_string(language, bornSection))
            except Exception as e:
                date_birth = None
                pass
            try:
                deadSection = findDeadSection(language, parsed)
                date_death = objectify_date(language, get_date_string(language, deadSection))
            except Exception as e:
                date_death = None
                pass
            repo = siteWp.data_repository()
            page = pb.Page(siteWp, title)
            item = pb.ItemPage.fromPage(page)
            if itemIsHuman(item):
                if not props["born"] in item.claims and date_birth is not None:
                    addDate("b", date_birth, item, language)
                    print()
                else:
                    print(title, "already has born.")
                if not props["dead"] in item.claims and date_death is not None:
                    addDate("d", date_death, item, language)
                    print()
                else:
                    print(title, "already has death")
            else:
                print(title, "is not marked as human...")
        except Exception as e:
            print(e)
            print(title, " - processing went wrong...")
            pass
