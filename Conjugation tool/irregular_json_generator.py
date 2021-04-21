import json
import os
irrWords = {}
words = None
with open(os.getcwd() + '/bigWordFile.json', 'r') as file:
    words = json.load(file)
    print(len(words))

for word in words:
    length = len(word)
    try:
        if word[(length-2):(length)] == 'er':
            if words[word]['Present']['je'] != 'e':
                irrWords[word] = words[word]

        elif word[(length-2):(length)] == 'ir':
            if words[word]['Present']['je'] != 'is':
                irrWords[word] = words[word]

        elif word[(length-2):(length)] == 're':
            if words[word]['Present']['je'] != 's':
                irrWords[word] = words[word]
    except:
        print(word)
        continue

with open(os.getcwd() + "/irregulars.json", 'w') as jsonOut:
    json.dump(irrWords, jsonOut, indent=4, ensure_ascii=False)
