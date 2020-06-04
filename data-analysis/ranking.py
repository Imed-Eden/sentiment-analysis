# -*- coding: utf-8 -*-

import json
import requests
import string
import random
import math
from sklearn import preprocessing
from pprint import pprint


# Declare variables to connect to the Cognitive Search endpoint
endpoint = 'https://sephora.search.windows.net/'
api_version = '?api-version=2019-05-06'
headers = {'Content-Type': 'application/json',
        'api-key': 'A54DE9E994C977D6C43EA04DFE1BD845' }

# GET indexes collection of the search service and selects the name property of existing indexes
# Use to test connection
url = endpoint + "indexes" + api_version + "&$select=name"
response  = requests.get(url, headers=headers)
index_list = response.json()
pprint(index_list)

# Declare index before creation
index_schema = {
    "name": "sephora",
    "fields": [
        {"name": "id", "type": "Edm.String", "key": "true", "filterable": "true"},
        {"name": "product_name", "type": "Edm.String", "searchable": "true", "filterable": "true", "sortable": "true", "facetable": "true"},
        {"name": "positive", "type": "Edm.Double", "filterable": "true", "sortable": "true", "facetable": "false"},
        {"name": "neutral", "type": "Edm.Double", "filterable": "true", "sortable": "true", "facetable": "false"},
        {"name": "negative", "type": "Edm.Double", "filterable": "true", "sortable": "true", "facetable": "false"},
        {"name": "family", "type": "Edm.String", "searchable": "true", "filterable": "true", "sortable": "true", "facetable": "true"},
        {"name": "gender", "type": "Edm.String", "searchable": "true", "filterable": "true", "sortable": "false", "facetable": "true"},
        {"name": "brand", "type": "Edm.String", "searchable" : "true", "filterable": "true", "sortable": "true", "facetable": "true"},
        {"name": "mark", "type": "Edm.Double", "filterable": "true", "sortable": "true", "facetable": "true"},
        {"name": "type", "type": "Edm.String", "searchable" : "true", "filterable": "true", "sortable": "true", "facetable": "true"},
        {"name": "price", "type": "Edm.Double", "filterable": "true", "sortable": "true", "facetable": "true"},
        {"name": "number_likes", "type": "Edm.Double", "filterable": "true", "sortable": "true", "facetable": "true"},
        {"name": "number_reviews", "type": "Edm.Int32", "filterable": "true", "sortable": "true", "facetable": "true"},
        {"name": "wilson_score", "type": "Edm.Double", "filterable": "true", "sortable": "true", "facetable": "true"},
        {"name": "standardized_number_likes", "type": "Edm.Double", "filterable": "true", "sortable": "true", "facetable": "true"},
        {"name": "standardized_price", "type": "Edm.Double", "filterable": "true", "sortable": "true", "facetable": "true"}
    ],
    "scoringProfiles": [
        {
        "name": "reviewsAndLikes",
        "functions": [
            {
                "type": "magnitude",
                "boost": 2,
                "fieldName": "standardized_number_likes",
                "interpolation": "linear",
                "magnitude": {
                    "boostingRangeStart": -5,
                    "boostingRangeEnd": 5,
                    "constantBoostBeyondRange": True
                }               
            },
            {
                "type": "magnitude",
                "boost": 3,
                "fieldName": "wilson_score",
                "interpolation": "linear",
                "magnitude": {
                    "boostingRangeStart": 0,
                    "boostingRangeEnd": 1,
                    "constantBoostBeyondRange": False
                }
            }
        ]
        },
        {
        "name": "reviewsPriceLikes",
        "functions": [
            {
                "type": "magnitude",
                "boost": 4,
                "fieldName": "wilson_score",
                "interpolation": "linear",
                "magnitude": {
                    "boostingRangeStart": 0,
                    "boostingRangeEnd": 1,
                    'constantBoostBeyondRange': False
                }
            },
            {
                "type": "magnitude",
                "boost": 2,
                "fieldName": "standardized_number_likes",
                "interpolation": "linear",
                "magnitude": {
                    "boostingRangeStart": -5,
                    "boostingRangeEnd": 5,
                    "constantBoostBeyondRange": True
                }               
            },
            {
                "type": "magnitude",
                "boost": 3,
                "fieldName": "standardized_price",
                "interpolation": "linear",
                "magnitude": {
                    "boostingRangeStart": -3,
                    "boostingRangeEnd": 3,
                    "constantBoostBeyondRange": True
                }               
            }
        ]
        },
        {
        "name": "wilsonScore",
        "functions": [
            {
                "type": "magnitude",
                "boost": 10,
                "fieldName": "wilson_score",
                "interpolation": "linear",
                "magnitude": {
                    "boostingRangeStart": 0,
                    "boostingRangeEnd": 1,
                    'constantBoostBeyondRange': False
                }
            }
        ]
        }
        # {
        # "name": "reviewsOnly",
        # # "text": {
        # #     "weights": {
        # #     }
        # # },
        # "functions": [
        #     {
        #         "type": "magnitude",
        #         "boost": 4,
        #         "fieldName": "positive",
        #         "interpolation": "quadratic", # Car la plupart des produits sont entre 75 et 100% de positivité, ça nous permet de mieux séparer selon le critère de positivité
        #         "magnitude": {
        #             "boostingRangeStart": 0,
        #             "boostingRangeEnd": 100,
        #             'constantBoostBeyondRange': False
        #         }
        #     },
        #     {
        #         "type": "magnitude",
        #         "boost": 2,
        #         "fieldName": "negative",
        #         "interpolation": "logarithmic",
        #         "magnitude": {
        #             "boostingRangeStart": -100, # Car la plupart des produits sont entre 0 et 25% de négativité
        #             "boostingRangeEnd": 0,
        #             'constantBoostBeyondRange': False
        #         }
        #     }
        # ]
        # },
    ]
}

# Create index
url = endpoint + "indexes" + api_version
response  = requests.post(url, headers=headers, json=index_schema)
index = response.json()
pprint(index)

# Generate a document that can be added to our Cognitive Search index from the content of the file containing the text analysis results
def generate_document(results_file):
    # Read the text analysis results from file
    with open(results_file, 'r') as file:
        results = file.read()
    results = eval(results)
    # Formats the results of the text analysis to something that can be used by Cognitive Search
    results_formatted = {}
    max_number_likes = 0
    max_price = 0
    number_likes_values = []
    price_values = []

    for product in results.keys():
        produit = product.encode('utf-8')
        results_formatted[produit] = results[product]
        
        # Get max values that will be used for normalization
        if results_formatted[produit]["number_likes"] > max_number_likes:
            max_number_likes = results_formatted[produit]["number_likes"]
        if results_formatted[produit]["price"] > max_price:
            max_price = results_formatted[produit]["price"]
        # Get value that will be used for standardization
        number_likes_values.append(results_formatted[produit]["number_likes"])
        price_values.append(results_formatted[produit]["price"])

    for produit in results_formatted.keys(): 
        for characteristic in results_formatted[produit]:
            if isinstance(results_formatted[produit][characteristic], int) == False and isinstance(results_formatted[produit][characteristic], float) == False and results_formatted[produit][characteristic] is not None:
                results_formatted[produit][characteristic] = results_formatted[produit][characteristic].encode('utf-8')
            if (characteristic == 'positive' or characteristic == 'neutral' or characteristic == 'negative') and results_formatted[produit][characteristic] is not None:
                results_formatted[produit][characteristic] = float(results_formatted[produit][characteristic].split('%')[0])
            # Normalize the price to values in range 0-1:
            # if characteristic == 'price':
            #     results_formatted[produit][characteristic] = results_formatted[produit][characteristic]*100/max_price

    # Standardize the number_likes and the price
    standardized_number_likes = preprocessing.scale(number_likes_values)
    standardized_price = preprocessing.scale(price_values)
    standardized_price = [i*(-1) for i in standardized_price]

    # Function to generate a random 16-characters-long string that will serve as product id
    def generate_random_string():
        lettersAndDigits = string.ascii_letters + string.digits
        randomstring = ''
        for i in range(16):
            randomstring = randomstring+random.choice(lettersAndDigits)
        return randomstring
    
    # Function to compute the wilson score
    def compute_wilson_score(positivity, number_of_reviews):
        positivity = positivity/100
        z = 1.96
        denominator = 1 + z**2/number_of_reviews
        centre_adjusted_probability = positivity + z*z / (2*number_of_reviews)
        adjusted_standard_deviation = math.sqrt((positivity*(1 - positivity) + z*z / (4*number_of_reviews)) / number_of_reviews)
        lower_bound = (centre_adjusted_probability - z*adjusted_standard_deviation) / denominator
        upper_bound = (centre_adjusted_probability + z*adjusted_standard_deviation) / denominator
        return lower_bound

    documents = {}
    documents["value"] = []
    for product in results_formatted.keys():
        # Generate the id of the product
        id = generate_random_string()
        # Get the standardized value for number_likes and price
        for index in range(len(number_likes_values)):
            if results_formatted[product]["number_likes"] == number_likes_values[index]:
                number_like = standardized_number_likes[index]
        for index in range(len(price_values)):
            if results_formatted[product]["price"] == price_values[index]:
                prix = standardized_price[index]
        # Get the Wilson score of the product
        if results_formatted[product]['number_reviews'] != 0:
            wilson_score = compute_wilson_score(results_formatted[product]['positive'], results_formatted[product]['number_reviews'])
        # Create dictionary of the product
        product_dict = {
            "@search.action": "upload",
            "id": id,
            "product_name": product,
            "positive": results_formatted[product]['positive'],
            "neutral": results_formatted[product]['neutral'],
            "negative": results_formatted[product]['negative']*(-1),
            "family": results_formatted[product]['family'],
            "gender": results_formatted[product]['gender'],
            "brand": results_formatted[product]['brand'],
            "mark": results_formatted[product]['mark'],
            "type": results_formatted[product]['type'],
            "price": results_formatted[product]['price'],
            "number_likes": results_formatted[product]['number_likes'],
            "number_reviews": results_formatted[product]['number_reviews'],
            "wilson_score": wilson_score,
            "standardized_number_likes": number_like,
            "standardized_price": prix
        }
        documents["value"].append(product_dict)
    return documents

# Declare document before upload
documents = generate_document('products_analysis.json')

# Upload document to index
url = endpoint + "indexes/sephora/docs/index" + api_version
response  = requests.post(url, headers=headers, json=documents)
index_content = response.json()
pprint(index_content)

# &search=*&$count=true&scoringProfile=wilsonScore&$select=positive,number_reviews,wilson_score
# &search=*&$count=true&scoringProfile=reviewsAndLikes&$select=product_name,wilson_score,number_likes
# &search=*&$count=true&scoringProfile=reviewsPriceLikes&$select=product_name,positive,number_likes,price&$filter=brand eq 'CHANEL'

# # Search for CHANEL products, ranked using the scoring profile "reviewsOnly"
# searchstring = '&search=*&scoringProfile=wilsonScore&$count=true&$select=product_name,positive,negative&$filter=brand eq \'CHANEL\''

# url = endpoint + "indexes/sephora-test/docs" + api_version + searchstring
# response  = requests.get(url, headers=headers, json=searchstring)
# query = response.json()
# pprint(query)

# # Search for CHANEL products, ranked using the scoring profile "reviewsAndLikes" 
# searchstring = '&search=*&scoringProfile=reviewsandLikes&$count=true&$select=product_name,positive,negative,number_likes&$filter=brand eq \'CHANEL\''

# url = endpoint + "indexes/sephora-test/docs" + api_version + searchstring
# response  = requests.get(url, headers=headers, json=searchstring)
# query = response.json()
# pprint(query)

# # Search for CHANEL products, ranked using the scoring profile "reviewsAndLikes" 
# searchstring = '&search=*&scoringProfile=reviewsandLikes&$count=true&$select=product_name,positive,negative,number_likes&$filter=brand eq \'CHANEL\''

# url = endpoint + "indexes/sephora-test/docs" + api_version + searchstring
# response  = requests.get(url, headers=headers, json=searchstring)
# query = response.json()
# pprint(query)

# &search=*&$count=true&scoringProfile=wilsonScore&$select=positive,number_reviews,wilson_score
# &search=*&$count=true&scoringProfile=reviewsAndLikes&$select=product_name,wilson_score,number_likes
# &search=*&$count=true&scoringProfile=reviewsPriceLikes&$select=product_name,positive,number_likes,price&$filter=brand eq 'CHANEL'


##############################
## BELOW ARE SOME SEARCHES  ##
##############################

# # Empty search, returns all entries, $count=true renders the number of entries returned
# searchstring = '&search=*&$count=true'

# url = endpoint + "indexes/sephora-test/docs" + api_version + searchstring
# response  = requests.get(url, headers=headers, json=searchstring)
# query = response.json()
# pprint(query)

# # Search a String (here DIOR), $select allows to choose which values to return (here return only product_name and Price)
# searchstring = '&search=DIOR&$count=true&$select=product_name,price'

# url = endpoint + "indexes/sephora-test/docs" + api_version + searchstring
# response  = requests.get(url, headers=headers, json=searchstring)
# query = response.json()
# pprint(query)

# # Search for all the products with more than 3K likes
# searchstring = '&search=*&$filter=number_likes gt 3000&$select=product_name,number_likes'

# url = endpoint + "indexes/sephora-test/docs" + api_version + searchstring
# response  = requests.get(url, headers=headers, json=searchstring)
# query = response.json()
# pprint(query)

# # Search for the top 3 men products
# searchstring = '&search=Men&$top=3&$select=product_name'

# url = endpoint + "indexes/sephora-test/docs" + api_version + searchstring
# response  = requests.get(url, headers=headers, json=searchstring)
# query = response.json()
# pprint(query)
