import pandas as pd
import random
from datetime import datetime, timedelta
import math
import warnings
import openai
import traceback
# Import the required module for text 
# to speech conversion
from gtts import gTTS
from playsound import playsound  
# This module is imported so that we can 
# play the converted audio
import os
from os.path import exists



APIFile='ChatGPTAPI.txt'
GPT_API_RETRIAL_TIME=3
if exists(APIFile):
    with open(APIFile) as f:
        lines = f.readlines()
    openai.api_key = lines[0]
else:
    API = input('Input Your ChatGPI API: ')
    openai.api_key=API
    with open(APIFile, 'w') as f:
        f.write(API)

warnings.filterwarnings("ignore")
df = pd.read_excel(r'Vocabulary.xlsx')
df = df.fillna('')
dfToBerestudy=df.iloc[0:0] #empty DF

playSoundMode=True
keymMapping={'a':2,'s':3,'d':4,'w':1}
reverseMapping={1:'w',2:'a',3:'s',4:'d'}
def genMCQuestion(df,QuestionType='ALL',Q=-1):

    random.seed()
    questionPara=Q
    global dfToBerestudy
    global playSoundMode
    if QuestionType !='ALL':
         
        if(QuestionType=='ThisWeek'):
            df= df[df['Date']> datetime.today()- timedelta(days=7)]
        elif(QuestionType=='Latest'):
            df= df[df['Date']==df.iloc[-1]['Date']]
    if questionPara <0:
         
        if(QuestionType=='ALL'):
            questionPara=int(math.sqrt(len(df)))
        elif(QuestionType=='ThisWeek'):
            questionPara=int(len(df)*1/5)
        elif(QuestionType=='Latest'):
            questionPara=int(len(df))
        else:
            questionPara=int(len(df)/4)
    for Q in range(questionPara):
        random.seed()
        rowNo=random.randrange(len(df))
        selectedRow=df.iloc[rowNo]
        vocabulary=selectedRow['vocabulary']
        meaning=selectedRow['meaning']
        sentence=str(selectedRow['sentence'])
        Question='meaning: '+meaning+'\n'
        vocabularyA=df.iloc[getNeighbourNum(rowNo,10,len(df)) ]['vocabulary']
        vocabularyB=df.iloc[getNeighbourNum(rowNo,10,len(df))]['vocabulary']
        vocabularyC=df.iloc[getNeighbourNum(rowNo,10,len(df))]['vocabulary']
        answerBag=(vocabulary,vocabularyA,vocabularyB,vocabularyC)
        while(len(set(answerBag) )<4):
            vocabularyA=df.iloc[getNeighbourNum(rowNo,10,len(df))]['vocabulary']
            vocabularyB=df.iloc[getNeighbourNum(rowNo,10,len(df))]['vocabulary']
            vocabularyC=df.iloc[getNeighbourNum(rowNo,10,len(df))]['vocabulary']
            answerBag=(vocabulary,vocabularyA,vocabularyB,vocabularyC)

        answerList=[vocabulary,vocabularyA,vocabularyB,vocabularyC]
        number_list=random.shuffle(answerList)
        optionString=""
        for i in range(len(answerList)):
            optionString=optionString+str(i+1)+f'({reverseMapping[i+1]}):'+'\n'+answerList[i]+'\n'
        exampleFromChatGPT=generateExampleFromChatGPT(vocabulary,meaning)
        print(Question)
        print('Sentence:\n'+str(exampleFromChatGPT.replace(vocabulary, "________"))+'\n\n\n')
        print(optionString)
        variable=''
        while True:
        
            variable = input('Your Answer: ')
            if variable in ['w','a','s','d']:
                break
            elif variable =='p':
                playSoundMode= not playSoundMode
        inputAanswer=-1
        if variable in keymMapping:
            inputAanswer=keymMapping[variable]
        else:
            inputAanswer=-1
        print(inputAanswer)
        answer=-1
        for i in range(len(answerList)):
            if vocabulary==answerList[i]:
                answer=i+1
        print(sentence)
        if str(inputAanswer)==str(answer):
            print('correct')
            print('\n')
        else:
            print('INCORRECT!!!!!!!!!!!!!!!!')
            print('answer:'+str(answer))
            print('\n')
            dfToBerestudy=dfToBerestudy.append(df.iloc[rowNo])
        if playSoundMode:
            filename=generateSentenceSpeaking(exampleFromChatGPT,vocabulary)
            while True:
                
                # Playing the converted file
                playsound(filename)
                if input('Any enter for next')=='':
                    break
        
        
            
def genMeaningMCQuestion(df,QuestionType='ALL',Q=-1):
    random.seed()
    questionPara=Q
    global dfToBerestudy
    global playSoundMode
    if QuestionType !='ALL':
         
        if(QuestionType=='ThisWeek'):
            df= df[df['Date']> datetime.today()- timedelta(days=7)]
        elif(QuestionType=='Latest'):
            df= df[df['Date']==df.iloc[-1]['Date']]
    if questionPara <0:
         
        if(QuestionType=='ALL'):
            questionPara=int(math.sqrt(len(df))*1.5)
        elif(QuestionType=='ThisWeek'):
            questionPara=int(len(df)*1/5)
        elif(QuestionType=='Latest'):
            questionPara=int(len(df))
        else:
            questionPara=int(len(df)/4)
    for Q in range(questionPara):
        rowNo=random.randrange(len(df))
        selectedRow=df.iloc[rowNo]
        vocabulary=selectedRow['vocabulary']
        meaning=selectedRow['meaning']
        sentence=selectedRow['sentence']
        sentence=generateExampleFromChatGPT(vocabulary,meaning)
        Question='vocabulary: '+vocabulary+'\n'+'Sentence:\n'+str(sentence)+'\n'
        vocabularyA=df.iloc[getNeighbourNum(rowNo,10,len(df)) ]['meaning']
        vocabularyB=df.iloc[getNeighbourNum(rowNo,10,len(df))]['meaning']
        vocabularyC=df.iloc[getNeighbourNum(rowNo,10,len(df))]['meaning']
        answerBag=(meaning,vocabularyA,vocabularyB,vocabularyC)
        while(len(set(answerBag) )<4):
            vocabularyA=df.iloc[getNeighbourNum(rowNo,10,len(df))]['meaning']
            vocabularyB=df.iloc[getNeighbourNum(rowNo,10,len(df))]['meaning']
            vocabularyC=df.iloc[getNeighbourNum(rowNo,10,len(df))]['meaning']
            answerBag=(meaning,vocabularyA,vocabularyB,vocabularyC)

        answerList=[meaning,vocabularyA,vocabularyB,vocabularyC]
        number_list=random.shuffle(answerList)
        optionString=""
        for i in range(len(answerList)):
            optionString=optionString+str(i+1)+f'({reverseMapping[i+1]}):'+'\n'+answerList[i]+'\n'
        print(Question)
        print(optionString)
        
        filename=generateSentenceSpeaking(sentence,vocabulary)
        while True:
            if playSoundMode:
                
                # Playing the converted file
                playsound(filename)
            
            variable=input('w,a,s,d for answer;r for generating antoher sentence; p for switch the speech mode;\n')
            if variable=='p':
                
                
                # Playing the converted file
                playSoundMode= not playSoundMode
            elif variable=='r':
                sentence=generateExampleFromChatGPT(vocabulary,meaning)
                print(sentence)
                filename=generateSentenceSpeaking(sentence,vocabulary)
            elif variable in ['w','a','s','d']:
                break
            
            
        inputAanswer=-1
        if variable in keymMapping:
            inputAanswer=keymMapping[variable]
        else:
            inputAanswer=-1
        print(inputAanswer)
        answer=-1
        for i in range(len(answerList)):
            if meaning==answerList[i]:
                answer=i+1
        if str(inputAanswer)==str(answer):
            print('correct')
            print('\n')
        else:
            print('INCORRECT!!!!!!!!!!!!!!!!')
            print('answer:'+str(answer))
            print('\n')
            dfToBerestudy=dfToBerestudy.append(df.iloc[rowNo])
            input('Any key for next')
        	
def getNeighbourNum(rowNo,neighbourRange,Cap):
    global result
    result=rowNo+random.randint(0-neighbourRange, neighbourRange)
    while(result<0 or result>Cap-2):
        result=rowNo+random.randint(0-neighbourRange, neighbourRange)
    try:
        _=df.iloc[result]['meaning']
    except:
        print('result')
        print(result)
        print('Cap')
        print(Cap)
        print('rowNo')
        print(rowNo)
    return result
result=0
def generateSentenceSpeaking(sentence,vocab):
    # Language in which you want to convert
    language = 'en'
      
    # Passing the text and language to the engine, 
    # here we have marked slow=False. Which tells 
    # the module that the converted audio should 
    # have a high speed
    myobj = gTTS(text=sentence, lang=language, slow=True)
      
    # Saving the converted audio in a mp3 file named
    # welcome 
    directory = os.getcwd()
    filename=vocab+'_'+datetime.now().strftime("%Y%m%d%H%M%S")+'sentence'
    filename="".join(letter for letter in filename if letter.isalnum())
    filename=os.path.join(directory,'SampleSentence', filename+'.mp3')
    myobj.save(filename)
      
    return filename
lastPlace='Dummy'
def generateExampleFromChatGPT(vocab,meaning):

    placeList=["School",
        "War zone",
        "Job interview",
        "Hospital",
        "Police station",
        "Courtroom",
        "Coffee shop",
        "Science laboratory",
        "Art gallery",
        "Music studio",
        "Cruise ship",
        "Detective's office",
        "Theater backstage",
        "Beach resort",
        "Office",
        "Supermarket",
        "School",
        "Space station",
        "Body check"]
        
    global lastPlace
    random.seed()
    while (True):

        place=placeList[random.randrange(len(placeList))]
        if lastPlace!=place:
            break
    user_message = f"""
I am preparing vocab practice. 
I will tell you what the vocab and its meaning are.

Now, give me an example sentence with vocab '{vocab}'  that the reader can guess the meaning of it. 
Here the '{vocab}' words means '{meaning}'.
It should be not more than 1 sentence and not more than 30 words.
The example should be related to {place}
"""

    for i in range(GPT_API_RETRIAL_TIME):
        try:
            completion = openai.ChatCompletion.create(
              model = 'gpt-3.5-turbo',
              messages = [
                {'role': 'user', 'content': user_message}
              ],
              temperature =0.9,
            max_tokens=100,
            timeout=5
            )
            break
        
        except Exception as e:
            pass
    lastPlace=place
    return completion['choices'][0]['message']['content']

try:
    genMeaningMCQuestion(df,'Latest')
        

    input('Any key for next part:This week Vocab')
    genMCQuestion(df,'Latest')

    input('Any key for next part:This week meaning')

    genMeaningMCQuestion(df,'ThisWeek')
    input('Any key for next part:This week Vocab')
    genMCQuestion(df,'ThisWeek')

    input('Any key for next part:ALL meaning')

    genMeaningMCQuestion(df,'ALL')
    
except Exception as e: 
    print(e)
    
    traceback.print_exc()
    print("Something went wrong")
finally:
    dfToBerestudy.to_excel('ReStudy/'+datetime.now().strftime("%Y%m%d%H%M")+'.xlsx',index=False)