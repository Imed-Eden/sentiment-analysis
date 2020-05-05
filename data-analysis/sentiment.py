key = <Key of the Text Analytic Service>
endpoint = <Endpoint URL of the Text Analytic Service>

from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
import os
import json

# function that helps to run the exec shell script file
def get_data_products():
    os.system('./getDataScript.sh')

# function that helps to authenticate to the right cognitive service text analytics api
def authenticate_client():
    ta_credential = AzureKeyCredential(key)
    text_analytics_client = TextAnalyticsClient(
            endpoint=endpoint, credential=ta_credential)
    return text_analytics_client

# function that opens and read json file and its data
def get_comments():
    with open('products.json', 'r') as file:
        data = json.loads(file.read())
        return data

# function that requests and uses text analytics azure api
def sentiment_analysis(client, documents):

    response = client.analyze_sentiment(documents = documents)[0]
    comment_sentiment = response.sentiment
    comment_positive = response.confidence_scores.positive
    comment_neutral = response.confidence_scores.neutral
    comment_negative = response.confidence_scores.negative
    return [comment_sentiment, comment_positive, comment_neutral, comment_negative]

def sephora_analysis(client, data):
    products = []
    for product in data:

        feedback=[]
        for comment in product['comments']:
            documents = [comment]
            try:
                feedback.append(sentiment_analysis(client, documents))
            except:
                pass

        pos = 0
        neu = 0
        neg = 0
        for i in feedback:
            pos += i[1]
            neu += i[2]
            neg += i[3]
        try:
            pos /= len(feedback)
            pos = round(pos, 3)
            neu /= len(feedback)
            neu = round(neu, 3)
            neg /= len(feedback)
            neg = round(neg, 3)
        except:
            pass

        pos = str(pos*100)+'%'
        neu = str(neu*100)+'%'
        neg = str(neg*100)+'%'

        dictionary = { \
            "brand" : product['brand'], \
            "product": product['product'], \
            "price": product['price'], \
            "number_reviews": product['number_reviews'], \
            "number_likes": product['number_likes'], \
            "feedback": { \
                'positive' : pos, \
                'neutral' : neu, \
                'negative' : neg \
                }, \
            "mark": product['mark'], \
            "type": product['type'], \
            "family": product['family'], \
            "gender": product['gender'] \
            }
        products.append(dictionary)

    print(json.dumps(products, indent=4))



get_data_products()
client = authenticate_client()
data = get_comments()
results = sephora_analysis(client, data)
