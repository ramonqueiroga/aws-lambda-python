import json
import requests
import boto3
import os
from googletrans import Translator

SQS_URL = os.getenv('SQS_URL')
NA_SQS_URL = os.getenv('NA_SQS_URL')
JOKE_ENDPOINT = os.getenv('JOKE_ENPOINT')
SECURITY_ENDPOINT = os.getenv('SECURITY_ENDPOINT')
client = boto3.client('sqs')

def lambda_handler(event, context):
    headers = {'Accept':'application/json'}
    jokeResp = requests.get(JOKE_ENDPOINT, headers = headers)

    joke = json.loads(jokeResp.text)
    
    translator = Translator()
    questionEnglish = translator.translate(joke["pergunta"], src='pt', dest='en').text
    answerEnglish = translator.translate(joke["resposta"], src='pt', dest='en').text
    #http://wdylike.appspot.com/?q=
    profanityQuestion = requests.get(SECURITY_ENDPOINT + questionEnglish, headers=headers).text
    profanityAnswer = requests.get(SECURITY_ENDPOINT + answerEnglish, headers=headers).text
    if(profanityQuestion == "false" and profanityAnswer == "false"):
        print("it is allowed")
        client.send_message(QueueUrl=SQS_URL, MessageBody=jokeResp.text)
        return responseObj(jokeResp.text, 200)
    else:
        print("its not allowed")
        client.send_message(QueueUrl=NA_SQS_URL, MessageBody=jokeResp.text)
        return responseObj("content not allowed", 200)
    
def responseObj(message, statusCode):
    return {
        'statuscode': statusCode,
        'body': message
    }
