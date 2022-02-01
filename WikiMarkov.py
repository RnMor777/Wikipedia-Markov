import sys
import re
import random
import requests
import numpy as np
from bs4 import BeautifulSoup as bs

depth = 2
maxLink = 12
rootAddress = "https://en.wikipedia.org"

def createConnection (website):
    web = requests.get(website)
    web.close()
    return web

def cleanResponse (resp):
    tArr = []
    parsed = bs(resp.text, 'html.parser')
    for obj in parsed.find_all('p'):
        # remove all html tags
        tmp = re.sub(r'<\s*[a-z]*?[^>]*>|<\s*/\s*[a-z]*?>', '', str(obj))
        # remove all reference
        tmp = re.sub(r'\[\d*\]', '', tmp)
        # remove all punctuation
        tmp = re.sub(r'[\(\)\[\],\!\?\*\"\'”“;]', '', tmp)
        # remove new line
        tmp = tmp.strip()

        for line in list(tmp.split('. ')):
            if (re.search("refer to:", line)):
                return []
                # # need to pick the first link
                # # print ("Page does not exist, taking first hyperlink...")
                # newAddress = parsed.li.a.get('href')
                # webresp = createConnection("https://en.wikipedia.org" + newAddress)
                # return cleanResponse(webresp)

            # clean up the words further
            line = line.lower()
            line = line.replace('\xa0', '')
            line = re.sub(r'(\.(?!\d))', '', line)
            words = [word for word in line.split(' ') if word != '']
            tArr += words

    return tArr

def mixLinks (linkArr):
    outArr = []
    for possibleLink in linkArr:
        tmpStr = str(possibleLink.get('href'))
        if (re.match(r"^\/wiki\/[a-zA-Z_]*$",tmpStr) and tmpStr!="/wiki/Main_Page"):
            outArr.append(tmpStr)
    np.random.shuffle(outArr)
    return outArr

def make_markov (words, ngram=2):
    markovModel = {}
    for i in range(len(words)-ngram-1):
        currState, nextState = "", ""
        for j in range(ngram):
            currState += words[i+j] + " "
            nextState += words[i+j+ngram] + " "
        currState = currState[:-1]
        nextState = nextState[:-1]
        if (currState not in markovModel):
            markovModel[currState] = {}
            markovModel[currState][nextState] = 1
        else:
            if (nextState in markovModel[currState]):
                markovModel[currState][nextState] += 1
            else:
                markovModel[currState][nextState] = 1
    for currState, transition in markovModel.items():
        total = sum(transition.values())
        for state, count in transition.items():
            markovModel[currState][state] = count/total

    return markovModel

def generateStory (markovModel, start, limit):
    n = 0
    currState = start
    nextState= None
    story = ""
    story += currState + " "
    while n<limit:
        nextState = random.choices (list(markovModel[currState].keys()),
                                    list(markovModel[currState].values()))
        currState = nextState[0]
        story += currState + " "
        n += 1
    return story


def main ():
    address = rootAddress + "/wiki/" + input("Enter Search Term: ")
    webresp = createConnection (address)
    print ("\n" + address)
    print ("Searching...", end='')

    if (not webresp.ok):
        print ("\nFailed to Create Connection")
        print ("Exiting...")
        sys.exit(1)

    textArray = cleanResponse (webresp)
    linkArr = mixLinks(bs(webresp.text, 'html.parser').find_all('a'))

    for _ in range(1, depth):
        for j in range(maxLink):
            print ("\b"*12, end='')
            print ("\r  ->", linkArr[j])
            print ("Searching...", end='\r', flush=True)

            webresp = createConnection(rootAddress+linkArr[j])
            textArray += cleanResponse (webresp)

    markov = make_markov(textArray)
    x = random.randint(0, len(textArray)-1)

    print (" "*12)
    print ("Markov Generated Sentence: ")
    print ("Words:", len(markov))
    print (generateStory(markov, ' '.join(textArray[x:x+2]), 20))

if __name__ == "__main__":
    main()
