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
    men_fragrances_products = {}
    women_fragrances_products = {}
    men_colognes_products = {}
    women_colognes_products = {}

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
            "mark":transform_sephora_marks_to_floats(product['mark']), \
            "type": product['type'], \
            "family": product['family'], \
            "gender": product['gender'] \
        }

        if (product['gender'] == "Men" and product['type'] == "Perfume") :
          men_fragrances_products[product['product']] = dictionary
        elif (product['gender'] == "Men" and product['type'] == "Cologne") :
          men_colognes_products[product['product']] = dictionary
        elif (product['gender'] == "Women" and product['type'] == "Perfume") :
          women_colognes_products[product['product']] = dictionary
        elif (product['gender'] == "Men" and product['type'] == "Fragrance") :
          women_fragrances_products[product['product']] = dictionary

    return men_fragrances_products, men_colognes_products, women_colognes_products, women_fragrances_products
    #print(json.dumps(products, indent=4))


def transform_sephora_marks_to_floats(score):
    mark = ""
    for letter in score:
        if (letter == " " ):
          break
        mark += letter
    return (float(mark))

def sort_products(products, metric):
    if(metric=="neutral" or metric=="positive" or metric=="negative"):
      return(sorted(products.items(),key=lambda x: x[1]['feedback'][metric],reverse=True))
    else :
      return(sorted(products.items(),key=lambda x: x[1][metric],reverse=True))

#get_data_products()
client = authenticate_client()
data = get_comments()
perfumes_men, colognes_men, perfumes_women, colognes_women = sephora_analysis(client, data)

sorted_perfumes_men = sort_products(perfumes_men, 'positive')
sorted_perfumes_women = sort_products(perfumes_women, 'positive')
sorted_colognes_men = sort_products(colognes_men, 'positive')
sorted_colognes_women = sort_products(colognes_women, 'positive')

print("***********\n\n men perfumes: \n")
print(json.dumps(sorted_perfumes_men, indent=4))
print("***********\n women perfumes: \n")
print(json.dumps(sorted_perfumes_women, indent=4))
print("***********\n men colognes: \n")
print(json.dumps(sorted_colognes_men, indent=4))
print("***********\n women colognes: \n")
print(json.dumps(sorted_colognes_women, indent=4))
