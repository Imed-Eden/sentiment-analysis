key = <Key of the Text Analytic Service>
endpoint = <Endpoint URL of the Text Analytic Service>


###################################################################

from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
import os
import json
import matplotlib.pylab as plt
import pylab
import numpy as np
from pylab import figure, text, scatter, show, bar
import random
from matplotlib.offsetbox import TextArea, DrawingArea, OffsetImage, AnnotationBbox
import matplotlib.image as mpimg
###################################################################

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
            "product": product['product'], \
            "price": product['price'], \
            "number_reviews": product['number_reviews'], \
            "number_likes": product['number_likes'], \
            "feedback": { \
                'positive' : float(pos[:-1]), \
                'neutral' : float(neu[:-1]), \
                'negative' : float(neg[:-1]) \
                }, \
            "mark": transform_sephora_marks_to_floats(product['mark']), \
            "type": product['type'], \
            "family": product['family'], \
            "gender": product['gender'] \
        }
        products[product['product']] = dictionary
    return products


def classify_products(products):
    families = {}
    men_perfumes = {}
    men_colognes = {}
    women_perfumes = {}
    women_colognes = {}
    body_sprays = {}
    body_mist = {}
    lotions = {}
    cologne_sets = {}
    perfume_sets = {}
    men_bath_shower = {}
    women_bath_shower = {}
    for product in products.keys():
        if (products[product]['gender'] == "Men" and products[product]['type'] == "Perfume") :
          men_perfumes[product] = products[product]
        elif (products[product]['gender'] == "Men" and products[product]['type'] == "Cologne") :
          men_colognes[product] = products[product]
        elif (products[product]['gender'] == "Women" and products[product]['type'] == "Perfume") :
          women_perfumes[product] = products[product]
        elif (products[product]['gender'] == "Women" and products[product]['type'] == "Cologne") :
            women_colognes[product] = products[product]
        elif (products[product]['gender'] == "Men" and products[product]['type'] == "Body Sprays & Deodorant") :
            body_sprays[product] = products[product]
        elif (products[product]['gender'] == "Women" and products[product]['type'] == "Body Mist & Hair Mist") :
            body_mist[product] = products[product]
        elif (products[product]['gender'] == "Women" and products[product]['type'] == "Lotions & Oils") :
            lotions[product] = products[product]
        elif (products[product]['gender'] == "Value & Gift Sets" and products[product]['type'] == "Cologne Gift Sets") :
            cologne_sets[product] = products[product]
        elif (products[product]['gender'] == "Value & Gift Sets" and products[product]['type'] == "Perfume Gift Sets") :
            perfume_sets[product] = products[product]
        elif (products[product]['gender'] == "Men" and products[product]['type'] == "Bath & Shower") :
            men_bath_shower[product] = products[product]
        elif (products[product]['gender'] == "Women" and products[product]['type'] == "Bath & Shower") :
            women_bath_shower[product] = products[product]
    families['men_perfumes'] = men_perfumes
    families['men_colognes'] = men_colognes
    families['women_perfumes'] = women_perfumes
    families['women_colognes'] = women_colognes
    families['body_sprays'] = body_sprays
    families['body_mist'] = body_mist
    families['lotions'] = lotions
    families['cologne_sets'] = cologne_sets
    families['perfume_sets'] = perfume_sets
    families['men_bath_shower'] = men_bath_shower
    families['women_bath_shower'] = women_bath_shower
    return families


def transform_sephora_marks_to_floats(score):
    mark = ""
    if(score == ""):
      return ""
    for letter in score:
        if (letter == " " ):
          break
        mark += letter
    return (float(mark))


def sort_products(products, metric):
    dictionnaire = {}
    if(metric=="neutral" or metric=="positive" or metric=="negative"):
      for elem in sorted(products.items(),key=lambda x: x[1]['feedback'][metric],reverse=True) :
        dictionnaire[elem[0]] = elem[1]
      return dictionnaire

    else :
      for elem in sorted(products.items(),key=lambda x: x[1][metric],reverse=True) :
        dictionnaire[elem[0]] = elem[1]
      return dictionnaire


def filter_similar_products(products, product):
    results = {}
    typee = products[product]["type"]
    family = products[product]["family"]
    gender = products[product]["gender"]
    for produit in products.keys():
        if (products[produit]["type"] == typee) or (products[produit]["family"] == family) or (products[produit]["gender"] == gender):
            results[produit]= products[produit]
    return results

def add_values_based_on_a_metric(data, metric1, metric2):
  dictionnaire = {}
  for x, y in data.items():
    if(y[metric2]==''):
      continue
    total = y[metric2]
    for z, w in data.items():
      if(y[metric2]==''):
        continue
      if(y[metric1]==w[metric1] and y['product']!=w['product']):
        total += w[metric2]
    dictionnaire[y[metric1]] = total
  return dictionnaire


def mean_values_based_on_a_metric(data, metric1, metric2):
  dictionnaire = {}
  for x, y in data.items():
    if(y[metric2]=='' or y[metric1]==''):
      continue
    total = y[metric2]
    count = 1
    for z, w in data.items():
      if(w[metric2]==''):
        continue
      if(y[metric1]==w[metric1] and y['product']!=w['product']):
        total += w[metric2]
        count += 1
    dictionnaire[y[metric1]] = total/count                                                                              
  return dictionnaire

def mean_values_based_on_two_metric(data, metric1, metric2, metric3):
      dictionnaire = {}
      for x, y in data.items():
        if(y[metric3]==''):
          continue
        total = y[metric2]
        total2 = y[metric3]
        count = 1
        for z, w in data.items():
          if(w[metric3]==''):
                continue
          if(y[metric1]==w[metric1] and y['product']!=w['product']):
            total += w[metric2]
            total2 += w[metric3]
            count += 1
        dictionnaire[y[metric1]] = {metric2:total/count, metric3:total2/count}
      return dictionnaire

def plot_two_values(family, data, metric1, metric2, name_of_figure):
    dictionnaire = {}
    for x, y in data.items():
      if(y[metric2]==''):
        continue
      if(metric2=="neutral" or metric2=="positive" or metric2=="negative"):
        dictionnaire[y[metric1]] = (y['feedback'][metric2])
      else :
        dictionnaire[y[metric1]] = (y[metric2])
    w = 1
    x_axis = np.arange(0, len(dictionnaire.keys())*w, w)
    fig, ax = plt.subplots(1, figsize=(10, 6))
    ax.bar(x_axis, dictionnaire.values(), width = 0.5, color='g', align='center')
    #ax = plt.subplot(111)
    #ax.bar(x-0.2, y, width=0.2, color='b', align='center')
    #ax.scatter
    #ax.plot
    ax.set_xticks(x_axis)
    ax.set_xticklabels(dictionnaire.keys(), rotation=90)
    plt.savefig(name_of_figure ,dpi=300, bbox_inches = "tight", quality=95)



#get_data_products()

client = authenticate_client()

data = get_comments()

results = sephora_analysis(client, data)
print(json.dumps(results, indent=4))

#men_perfumes, men_colognes, women_perfumes, women_colognes, body_sprays, body_mist, lotions, cologne_sets, perfume_sets, men_bath_shower, women_bath_shower = classify_products(results)
families = classify_products(results)

'''
#sorted_results = sort_products(results, 'positive')
#print(filter_similar_products(results, 'BLEU DE CHANEL Eau de Parfum'))

print("***********\n\n men fragrances: \n")
print(json.dumps(men_perfumes, indent=4))
print("***********\n men colognes: \n")
print(json.dumps(men_colognes, indent=4))
print("***********\n women fragrances: \n")
print(json.dumps(women_perfumes, indent=4))
print("***********\n women colognes: \n")
print(json.dumps(women_colognes, indent=4))
print("***********\n body sprays: \n")
print(json.dumps(body_sprays, indent=4))
print("***********\n body mist: \n")
print(json.dumps(body_mist, indent=4))
print("***********\n lotions: \n")
print(json.dumps(lotions, indent=4))
print("***********\n cologne sets: \n")
print(json.dumps(cologne_sets, indent=4))
print("***********\n perfume sets: \n")
print(json.dumps(perfume_sets, indent=4))
print("***********\n men shower: \n")
print(json.dumps(men_bath_shower, indent=4))
print("***********\n women shower: \n")
print(json.dumps(women_bath_shower, indent=4))

plot_two_values(results, 'brand', 'number_reviews', 'comments.png')
plot_two_values(results, 'brand', 'number_likes', 'number_of_likes.png')
plot_two_values(results, 'product', 'mark', 'marks.png')

print(add_values_based_on_a_metric(results, 'brand', 'number_reviews'))
print(mean_values_based_on_a_metric(results, 'brand', 'number_reviews'))
print(add_values_based_on_a_metric(results, 'gender', 'number_reviews'))
values = mean_values_based_on_two_metric(results, 'brand', 'price', 'mark')
#results1 = mean_values_based_on_a_metric(results, 'brand', '')

'''



# preparing all the products families

#all_products_families = ["men_perfumes", "men_colognes", "women_perfumes", "women_colognes", "body_sprays", "body_mist", "lotions", "cologne_sets", "perfume_sets", "men_bath_shower", "women_bath_shower"]

#
print(families)
for family, products in families.items() :
  print("**********\n")
  results = mean_values_based_on_a_metric(products, 'brand', 'mark')
  plot_two_values(family, results, 'brand', 'marks', family+'-star-counts.png')
