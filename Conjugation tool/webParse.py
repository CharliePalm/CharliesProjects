from bs4 import BeautifulSoup
import requests
import urllib
import json
import csv
import unidecode


first = 1

def getDef(verb):
    r = requests.get('https://www.wordreference.com/fren/' + verb)
    soup = BeautifulSoup(r.content, 'html5lib')
    soup = str(soup)
    j = 0
    definitions = []
    for i in range(len(soup)):
        if soup[i:i+7] == '=\"ToWrd':
            print(i)
            if len(definitions) == 3:
                break
            i += 7

            while soup[i] != '<':
                if  soup[i] == '>':
                    i += 1
                    j = i
                i += 1
            definitions.append(soup[j:i])
    return definitions[1:3]

#TODO: use user inputted file as well as expand format acceptance

#This version uses the included file, but the json was created using the 'french top.txt' file
def parse():
    with open("french-verb-conjugation.csv") as file:
        reader = csv.reader(file, delimiter=',')
        for row in reader:
            if first == 1:
                first += 1
                continue
            wordList.append(row[0])

def generateJson(wordList):
    word = {}

    # iterate for each verb in the list
    for currVerb in wordList:
        print(currVerb) #DEBUG: ensure code is operating correctly

        currVerb = unidecode.unidecode(currVerb) #Web urls don't recognize accents
        # Define dictionary of dictonary of dictionaries
        word[currVerb] = {}
        word[currVerb]['Present'] = {}
        word[currVerb]['Simple Past'] = {}
        word[currVerb]['Past Perfect'] = {}

        # all credit for conjugations to conjugation-fr.com
        # all credit for definitions to wordreference.com

        word[currVerb]['Definition'] = getDef(currVerb)

        website = "http://www.conjugation-fr.com/conjugate.php?verb=" +currVerb
        r = requests.get(website)
        soup = BeautifulSoup(r.content, 'html5lib')
        soup = str(soup)
        infin = currVerb

        j = 0
        k = 0
        base = ''
        tenses = ['Present', 'Simple Past', 'Past Perfect']
        #Now loop over the webpage until we find our conjugations
        for i in range(len(soup)):
            if soup[i:i+3] == 'je ' or soup[i:i+2] == 'j\'':
                # keep iterating until we reach the other side of the html block
                while (soup[i+1:i+3] != '</'):
                    i += 1
                    # now update j and keep iterating
                    if (soup [i] == '>'):
                        j = i + 1
                word[currVerb][tenses[k]]['je'] = soup[j:i+1]
                continue

            if soup[i:i+3] == 'tu ':
                while (soup[i+1:i+3] != '</'):
                    i += 1
                    if (soup [i] == '>'):
                        j = i + 1
                word[currVerb][tenses[k]]['tu'] = soup[j:i+1]
                continue

            if soup[i:i+3] == 'il ':
                while (soup[i+1:i+3] != '</'):
                    if (soup[i]=='\n'):
                        j = i
                        i -= 3
                        break
                    i += 1
                    if (soup [i] == '>'):
                        j = i + 1
                word[currVerb][tenses[k]]['il'] = soup[j:i + 1]
                continue

            if soup[i:i+5] == 'nous ':
                i += 4
                while(soup[i + 1] != '<'):
                    i += 1
                    if soup[i] != ' ':
                        base += soup[i]
                    else:
                        base = ''

                word[currVerb][tenses[k]]['base'] = base
                base = ''

                while (soup[i+1:i+3] != '</'):
                    i += 1
                    if (soup [i] == '>'):
                        j = i + 1
                word[currVerb][tenses[k]]['nous'] = soup[j:i+1]
                continue

            if soup[i:i+5] == 'vous ':
                while (soup[i+1:i+3] != '</'):
                    i += 1
                    if (soup [i] == '>'):
                        j = i + 1
                word[currVerb][tenses[k]]['vous'] = soup[j:i+1]
                continue

            if soup[i:i+4] == 'ils ':

                while (soup[i+1:i+3] != '</'):
                    i += 1
                    if (soup [i] == '>'):
                        j = i + 1
                word[currVerb][tenses[k]]['ils'] = soup[j:i+1]
                #ils will be the last to be found, update the k:
                k += 1
                if (k == 3):
                    break

        with open("/Users/chuckpalm/Documents/Atom projects/Conjugation tool/bigWordFile.json", 'w') as jsonOut:
            json.dump(word, jsonOut, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    ## TODO: add user prompt for file name
    wordList = parse()
    generateJson(wordList)
