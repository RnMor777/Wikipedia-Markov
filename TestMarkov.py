import sys
import re
import random
import time
import argparse
import requests
import numpy as np
from bs4 import BeautifulSoup as bs

rootWikipedia = "https://en.wikipedia.org"

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
        for _, count in transition.items():
            transition = count/total

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

def depthLinks (maxDepth, maxTot, startPage):
    links = [startPage]
    responses = []

    while len(responses) < maxDepth:
        newResponses = []
        newLinks = []
        for page in links:
            conn = createConnection (rootWikipedia + page)

            print (f"Contacting {rootWikipedia + page}:")
            if not conn.ok:
                print (f"Failed to Connect - {conn.status_code}")
            else:
                print ("Success")

            newResponses.append(conn)
            newLinks += mixLinks(bs(conn.text, 'html.parser').find_all('a'))[:maxTot]
        responses.append(newResponses)
        links = newLinks

    print (responses)
    return responses

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create a markov chain based on text extracted from Wikipedia')
    parser.add_argument('-t', '--term', dest='term', type=str, required=True,
            help='The search text to start with')
    parser.add_argument('-d', '--depth', dest='depth', type=int, required=True,
            help='The depth of sublinks to search')
    parser.add_argument('-m', '--max', dest='max', type=int, required=True,
            help='The maximum number of links to scan at each level')

    args = parser.parse_args()
    startTime = time.time()

    if not createConnection(rootWikipedia + '/wiki/' + args.term).ok:
        print ("Error: Page Not Found")
        print ("Exiting...")
        sys.exit(1)

    textArray = depthLinks (args.depth, args.max, '/wiki/' + args.term)
    endTime = time.time()

    markov = make_markov(textArray)
    x = random.randint(0, len(textArray)-1)

    print (" "*12)
    print ("Markov Generated Sentence: ")
    print ("Words:", len(markov))
    print (f"Time Elapsed: {round(endTime-startTime, 3)} seconds")
    print ()
    print (generateStory(markov, ' '.join(textArray[x:x+2]), 20))
