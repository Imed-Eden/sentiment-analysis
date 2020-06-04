# -*- coding: utf-8 -*-

key = "f9a2d00149784f57b55f1ed8db0d970a"
endpoint = "https://sentimentanalysis-cognitive.cognitiveservices.azure.com/"

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

# function that transform the string in float
def transform_sephora_marks_to_floats(score):
    mark = ""
    try: 
        for letter in score:
            if (letter == " " ):
                break
            mark += letter
        return (float(mark))
    except:
        pass

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
    products = {}
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
            "price": product['price'], \
            "number_reviews": product['number_reviews'], \
            "number_likes": product['number_likes'], \
            "positive" : pos, \
            "neutral" : neu, \
            "negative" : neg, \
            "mark": transform_sephora_marks_to_floats(product['mark']), \
            "type": product['type'], \
            "family": product['family'], \
            "gender": product['gender'] \
        }
        products[product['product']] = dictionary

    return products

# function that formats the results of the text analysis to something that can be used by Cognitive Search
def format_results(results):
    results_formatted = {}
    for product in results.keys():
        results[product] = results_formatted[product] 
    return results_formatted

# function that writes cognitive text analysis to a file that will be used by Cognitive Search
def write_results_to_file(results):
    with open('products_analysis.json', 'w+') as file:
        file.write(str(results))
        file.close()

client = authenticate_client()
data = get_comments()
results = sephora_analysis(client, data)
write_results_to_file(results)
print(results)
