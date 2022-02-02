import re
import random
import requests
from bs4 import BeautifulSoup as bs

depth = 3
maxLink = 4
rootAddress = "https://www.gutenberg.org/files"

def createConnection (website):
    web = requests.get(website)
    web.close()
    return web

def cleanResponse (resp):
    tArr = []
    parsed = bs(resp.text, 'html.parser')
    for div in parsed.find_all('div', {"class":"chapter"}):
        for p in div.find_all('p'):
            if (p.get("class") is not None):
                continue

            tmp = p.text
            # remove all punctuation
            tmp = re.sub(r'[\.\(\)\[\],\!\?\*\"\'”“;]', '', tmp)
            # remove new line
            tmp = re.sub(r'[\n\r]', ' ', tmp)

            tArr += [word for word in list(tmp.split(' ')) if word!='']

    return tArr

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

def main ():
    startAddress = "/84/84-h/84-h.htm"
    print ("\n"+rootAddress+startAddress)
    webResponse = createConnection(rootAddress + startAddress)
    textArray = cleanResponse(webResponse)

    markov = make_markov(textArray)

    print (" "*12)
    print ("Markov Generated Sentence: ")
    print ("Words:", len(markov))
    print ()
    x = random.randint(0, len(textArray)-1)
    print (generateStory(markov, ' '.join(textArray[x:x+2]), 20))
    print ()
    x = random.randint(0, len(textArray)-1)
    print (generateStory(markov, ' '.join(textArray[x:x+2]), 20))

if __name__ == "__main__":
    main()
