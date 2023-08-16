import requests
import multidict as multidict
import pandas
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import json
import numpy as np
from PIL import Image
import os


fileName=''
def initialize():
    userid = input("Enter UserID")
    #userid = "1305881"
    apikey = input("Enter apikey")
    #apikey = "7df702f142b0fc7a44996a826b57c88bb8137609e560d7cbacdfc48b0f9599e1"
    return userid,apikey

## Captures tag input and searches site, search is always sorted by largest score first
def tag(userid,apikey):
    user = userid
    api = apikey
    #tag = "catgirl"
    tag = input("Enter tag to be searched: ")
    numberOfResults= input("Enter desired number of results: ")
    request_formed = "https://gelbooru.com/index.php?page=dapi&s=post&q=index&api_key={}&user_id={}&tags={}+sort:score&limit={}&json=1".format(api,user,tag,numberOfResults)
    response = requests.get(request_formed)

    #print(request_formed)
    return response

## Generates CSV based on tag input
def createCSV(response):
    json_resp = response.json()
    json_text = json.dumps(json_resp)
    json_text = json_text.replace(';','~')
    json_resp = json.loads(json_text)
    parsed_text = pandas.json_normalize(json_resp, 'post')

    #val = "hi"
    if not os.path.exists('./results/'):
        os.makedirs('./results/')
    global fileName    # Needed to modify global copy of fileName
    fileName = input("Enter file name where to save results: ")
    parsed_text.to_csv('./results/'+fileName+'.csv',sep=',',index=False)

    #Generate Tag only CSV
    parsed_text_t = parsed_text.filter(items=['tags'])
    #print(parsed_text_t)
    json_tags= parsed_text_t.to_json(orient="split")
    json_text_t = json.dumps(json_tags)
    #print(json_text_t)
    json_text_t = json_text_t.replace(' ',',')
    parsed_text_t.to_csv('./results/'+fileName+'2.csv',sep=' ',index=False)
    # Return tag only CSV to create wordcloud
    df = pandas.read_csv('./results/'+fileName+'2.csv', delimiter=r"\s+")
    df = df.to_string()
    df= df.replace('\n', ' ')
    return df

########################################### Plot the img ###


#Order by frequency of words in Tag only CSV
def getFrequencyDictForText(sentence):
    fullTermsDict = multidict.MultiDict()
    tmpDict = {}

    # making dict for counting frequencies
    for text in sentence.split(" "):
        
        val = tmpDict.get(text, 0)
        tmpDict[text.lower()] = val + 1
    
    for key in tmpDict:
        if key !=  '': 
            fullTermsDict.add(key + '~'+str(tmpDict[key]), tmpDict[key])
#Prints results from tag only CSV
    print (fullTermsDict)
    dk = pandas.DataFrame(fullTermsDict)
    dk.to_csv ('./results/'+fileName+'3.csv',index=False, sep=' ')
    return fullTermsDict

# Plots wordcloud based on Tag frequency
def plotImage(fullTermsDict):
    comment_words = ''
    stopwords = set(STOPWORDS)

     
    wordcloud = WordCloud(width = 800, height = 800,
                    background_color ='white',
                    stopwords = stopwords,
                    min_font_size = 10,max_words=1000)

    wordcloud.generate_from_frequencies(fullTermsDict)
     


    # plot the WordCloud image                      
    plt.figure(figsize = (8, 8), facecolor = None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad = 0)
     
    plt.show()


#Initialize aplication, sets ApiKey and UserID to allow GET operation   
credentialsApi,credentialsUser= initialize()

#Requests input to search and plot Wordcloud
while True:
    df= createCSV(tag(credentialsApi,credentialsUser))

    fullTermsDict = getFrequencyDictForText(df)


    plotImage(fullTermsDict)
    #Ask for input to allow multiple search
    out = input("Enter 1 to search again: ")
    if out  != "1":
        
        break
