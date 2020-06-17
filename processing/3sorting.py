# -*- coding: utf-8 -*-

import json
import requests
import os
from subprocess import call
import shutil
import ast
import re
import time
from collections import OrderedDict
from operator import getitem
from azure.storage.file.fileservice import FileService


# Declare variables to connect to the Cognitive Search endpoint
endpoint = 'https://sephora.search.windows.net/'
api_version = '?api-version=2019-05-06'
headers = {'Content-Type': 'application/json',
        'api-key': 'A54DE9E994C977D6C43EA04DFE1BD845' }

# Declare variables to connect to the Azure Blob Storage endpoint
AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=puppeteerscrapingresults;AccountKey=QsaFrqTErlHV6+tnoy1OhfYWMEshAUUnPq/lgY8t/oe6rCHxTuA7IgtlrbQRsSS4Il7olLAR0PQ+NxaIYqfgjw==;EndpointSuffix=core.windows.net"

# Query cognitive search
def cognitive_search(scoringProfile, brand):
    if brand != "":
        searchstring = "&search=*&$count=true&$top=1000&$scoringProfile=" + scoringProfile + "&$filter=brand eq '" + brand +"'"
    else:
        searchstring = "&search=*&$count=true&$top=1000&$scoringProfile=" + scoringProfile
    url = endpoint + "indexes/sephora/docs" + api_version + searchstring
    response  = requests.get(url, headers=headers, json=searchstring)
    query = response.json()
    while "@odata.nextLink" in query:
        if brand != "":
            searchstring = "&search=*&$count=true&$top=1000&$skip=1000&$scoringProfile=" + scoringProfile + "&$filter=brand eq '" + brand +"'"
        else:
            searchstring = "&search=*&$count=true&$top=1000&$skip=1000&$scoringProfile=" + scoringProfile
        url = endpoint + "indexes/sephora/docs" + api_version + searchstring
        response  = requests.get(url, headers=headers, json=searchstring)
        if "@odata.nextLink" not in response.json():
            del query["@odata.nextLink"]
        query['value'] = query['value'] + response.json()['value']
    return query

# Get the products of a specific brand
def sort_by_brand(results, brand):
    brand_products = {}
    brand_products['value'] = []
    for product in range(len(results['value'])):
        if (results['value'][product]['brand'] == brand):
            brand_products['value'].append(results['value'][product])
    return brand_products

# Sort all the products by family
def sort_by_family(results):
    families = {}
    men_perfumes = {}
    men_colognes = {}
    women_perfumes = {}
    body_sprays = {}
    body_mist = {}
    lotions = {}
    cologne_sets = {}
    perfume_sets = {}
    men_bath_shower = {}
    women_bath_shower = {}
    men_deodorant = {}
    rollerballs = {}
    for product in range(len(results['value'])):
        if (results['value'][product]['gender'] == "Women" and results['value'][product]['type'] == "Perfume") :
            women_perfumes[results['value'][product]['id']] = results['value'][product]
        elif (results['value'][product]['gender'] == "Men" and results['value'][product]['type'] == "Cologne") :
            men_colognes[results['value'][product]['id']] = results['value'][product]
        elif (results['value'][product]['gender'] == "Men" and results['value'][product]['type'] == "Perfume") :
            men_perfumes[results['value'][product]['id']] = results['value'][product]
        elif (results['value'][product]['gender'] == "Men" and results['value'][product]['type'] == "Body Sprays & Deodorant") :
            body_sprays[results['value'][product]['id']] = results['value'][product]
        elif (results['value'][product]['gender'] == "Women" and results['value'][product]['type'] == "Body Mist & Hair Mist") :
            body_mist[results['value'][product]['id']] = results['value'][product]
        elif (results['value'][product]['gender'] == "Women" and results['value'][product]['type'] == "Lotions & Oils") :
            lotions[results['value'][product]['id']] = results['value'][product]
        elif (results['value'][product]['gender'] == "Value & Gift Sets" and results['value'][product]['type'] == "Cologne Gift Sets") :
            cologne_sets[results['value'][product]['id']] = results['value'][product]
        elif (results['value'][product]['gender'] == "Value & Gift Sets" and results['value'][product]['type'] == "Perfume Gift Sets") :
            perfume_sets[results['value'][product]['id']] = results['value'][product]
        elif (results['value'][product]['gender'] == "Men" and results['value'][product]['type'] == "Bath & Shower") :
            men_bath_shower[results['value'][product]['id']] = results['value'][product]
        elif (results['value'][product]['gender'] == "Women" and results['value'][product]['type'] == "Bath & Shower") :
            women_bath_shower[results['value'][product]['id']] = results['value'][product]
        elif (results['value'][product]['gender'] == "Fragrance" and results['value'][product]['type'] == "Deodorant for Men") :
            men_deodorant[results['value'][product]['id']] = results['value'][product]
        elif (results['value'][product]['gender'] == "Women" and results['value'][product]['type'] == "Rollerballs & Travel Size") :
            rollerballs[results['value'][product]['id']] = results['value'][product]
    families['women_perfumes'] = women_perfumes
    families['men_perfumes'] = men_perfumes
    families['men_colognes'] = men_colognes
    families['body_sprays'] = body_sprays
    families['body_mist'] = body_mist
    families['lotions'] = lotions
    families['cologne_sets'] = cologne_sets
    families['perfume_sets'] = perfume_sets
    families['men_bath_shower'] = men_bath_shower
    families['women_bath_shower'] = women_bath_shower
    families['men_deodorant'] = men_deodorant
    families['rollerballs'] = rollerballs
    fams = {}
    for family in families.keys():
        if families[family] != {}:
            fams[family] = families[family]
    return fams

# Get the mean of one metric for each brand of products of a specific family
def mean_by_brand_one_metric(family, metric):
    family_mean = {}
    for product in family.keys():
        brand = family[product]['brand']
        if brand not in family_mean:
            family_mean[brand] = []
        family_mean[brand].append(family[product])
    for brand in list(family_mean):
        sum_metric = 0
        number_products_brand = 0
        for product in range(len(family_mean[brand])):
            if family_mean[brand][product][metric] != None:
                if family_mean[brand][product]["mark"] != None:
                    if (family_mean[brand][product]["number_likes"] == 0 or family_mean[brand][product]["number_reviews"] == 0 or family_mean[brand][product]["wilson_score"] < 0 or family_mean[brand][product]["wilson_score"] > 1 or family_mean[brand][product]["mark"] <= 0 or family_mean[brand][product]["mark"] == None or family_mean[brand][product]["price"] == 0): 
                        pass
                    else:
                        sum_metric += family_mean[brand][product][metric]
                        number_products_brand += 1
        family_mean[brand] = {}
        if number_products_brand != 0:
            family_mean[brand][metric] = sum_metric / number_products_brand
        else:
            family_mean.pop(brand)
    return family_mean

# Get the mean of two metrics for each brand of products of a specific family
def mean_by_brand_two_metrics(family, metric1, metric2):
    family_mean = {}
    for product in family.keys():
        brand = family[product]['brand']
        if brand not in family_mean:
            family_mean[brand] = []
        family_mean[brand].append(family[product])
    for brand in list(family_mean):
        sum_metric1 = 0
        sum_metric2 = 0
        number_products_brand = 0
        for product in range(len(family_mean[brand])):
            if family_mean[brand][product][metric1] != None and family_mean[brand][product][metric2] != None:
                if family_mean[brand][product]["mark"] != None :
                    if (family_mean[brand][product]["number_likes"] == 0 or family_mean[brand][product]["number_reviews"] == 0 or family_mean[brand][product]["wilson_score"] < 0 or family_mean[brand][product]["wilson_score"] > 1 or family_mean[brand][product]["mark"] <= 0 or family_mean[brand][product]["price"] == 0): 
                        pass
                    else:
                        sum_metric1 += family_mean[brand][product][metric1]
                        sum_metric2 += family_mean[brand][product][metric2]
                        number_products_brand += 1
        family_mean[brand] = {}
        if number_products_brand != 0:
            family_mean[brand][metric1] = sum_metric1 / number_products_brand
            family_mean[brand][metric2] = sum_metric2 / number_products_brand
        else:
            family_mean.pop(brand)
    return family_mean

# Get the mean of one metric for each family of products of a specific brand
def mean_by_family_one_metric(sorted_brand_products, metric):
    families_mean = {}
    for family in sorted_brand_products.keys():
        families_mean[family] = {}
        sum_metric = 0
        number_products_family = 0
        for product in sorted_brand_products[family]:
            if sorted_brand_products[family][product][metric] != None:
                if sorted_brand_products[family][product]["mark"] != None:
                    if (sorted_brand_products[family][product]["number_likes"] == 0 or sorted_brand_products[family][product]["number_reviews"] == 0 or sorted_brand_products[family][product]["wilson_score"] < 0 or sorted_brand_products[family][product]["wilson_score"] > 1 or sorted_brand_products[family][product]["mark"] <= 0 or sorted_brand_products[family][product]["price"] == 0): 
                        pass
                    else:
                        sum_metric += sorted_brand_products[family][product][metric]
                        number_products_family += 1
        if sorted_brand_products[family] == {}:
            families_mean.pop(family)
        else:
            if number_products_family != 0:
                families_mean[family][metric] = sum_metric / number_products_family
            else:
                families_mean.pop(family)
    return families_mean

# Get the mean of two metrics for each family of products of a specific brand
def mean_by_family_two_metrics(sorted_brand_products, metric1, metric2):
    families_mean = {}
    for family in sorted_brand_products.keys():
        families_mean[family] = {}
        sum_metric1 = 0
        sum_metric2 = 0
        number_products_family = 0
        for product in sorted_brand_products[family]:
            if sorted_brand_products[family][product][metric1] != None and sorted_brand_products[family][product][metric2] != None:
                if sorted_brand_products[family][product]["mark"] != None:
                    if (sorted_brand_products[family][product]["number_likes"] == 0 or sorted_brand_products[family][product]["number_reviews"] == 0 or sorted_brand_products[family][product]["wilson_score"] < 0 or sorted_brand_products[family][product]["wilson_score"] > 1 or sorted_brand_products[family][product]["mark"] <= 0 or sorted_brand_products[family][product]["price"] == 0): 
                        pass
                    else:
                        sum_metric1 += sorted_brand_products[family][product][metric1]
                        sum_metric2 += sorted_brand_products[family][product][metric2]
                        number_products_family += 1
        if sorted_brand_products[family] == {}:
            families_mean.pop(family)
        else:
            if number_products_family != 0:
                families_mean[family][metric1] = sum_metric1 / number_products_family
                families_mean[family][metric2] = sum_metric2 / number_products_family
            else:
                families_mean.pop(family)
    return families_mean

# Format the file to remove special characters
def format(toFormat):
    toFormat = str(toFormat)
    toFormat = re.sub("([A-z])'([A-z])", '\\1 \\2', toFormat)
    toFormat = toFormat.replace("'", '"')
    toFormat = toFormat.replace("‘", " ")
    toFormat = re.sub('\"([A-Za-z0-9 \\-]*)\"([A-Za-z0-9 \\-]*)\"([A-Za-z0-9 \\-]*)\"', '\"\\1\\2\\3\"', toFormat)
    toFormat = re.sub('\"([A-Za-z0-9 \\-]*)\"([A-Za-z0-9 \\-]*)\"', '\"\\1\\2\"', toFormat)
    toFormat = re.sub('\"([A-Za-z0-9 \\-]*)\"([A-Za-z0-9 \\-]*)\,([A-Za-z0-9 \\-]*)\,([A-Za-z0-9 ,\\-]*)\"', '\"\\1\\2,\\3,\\4\"', toFormat)
    toFormat = ast.literal_eval(toFormat)
    return toFormat

# Rank by value (when one metric only)
def rank(toRank, metric):
    ranked = str({k: v for k, v in sorted(toRank.items(), key=lambda item: item[1][metric])})
    return ranked

# Create a directory in which to place the files that will be later uplaoded to File Storage
path = 'json_files'
if os.path.exists(path) == False:
    os.mkdir(path)

scoringProfiles = ['']
files_path = []
files_names = []
for scoringProfile in scoringProfiles:
    brand = ''
    # Get the results from Cognitive Search
    search_results = cognitive_search(scoringProfile, brand)

    # Creation of the files for each family of products
    sorted_products = sort_by_family(search_results)
    sorted_products = format(sorted_products)
    for family in sorted_products:
        price = mean_by_brand_one_metric(sorted_products[family], 'price')
        price = rank(price, 'price')
        file_name = path + "/" + family + "_price.json"
        f = open(file_name, "w")
        f.write(str(price))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        popularity = mean_by_brand_one_metric(sorted_products[family], 'wilson_score')
        popularity = rank(popularity, 'wilson_score')
        file_name = path + "/" + family + "_popularity.json"
        f = open(file_name, "w")
        f.write(str(popularity))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        mark = mean_by_brand_one_metric(sorted_products[family], 'mark')
        mark = rank(mark, 'mark')
        file_name = path + "/" + family + "_mark.json"
        f = open(file_name, "w")
        f.write(str(mark))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        number_likes = mean_by_brand_one_metric(sorted_products[family], 'number_likes')
        number_likes = rank(number_likes, 'number_likes')
        file_name = path + "/" + family + "_likes.json"
        f = open(file_name, "w")
        f.write(str(number_likes))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        positivity = mean_by_brand_one_metric(sorted_products[family], 'positive')
        positivity = rank(positivity, 'positive')
        file_name = path + "/" + family + "_positivity.json"
        f = open(file_name, "w")
        f.write(str(positivity))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        likes_and_positivity = mean_by_brand_two_metrics(sorted_products[family], 'number_likes', 'positive')
        file_name = path + "/" + family + "_likes_and_positivity.json"
        f = open(file_name, "w")
        f.write(str(likes_and_positivity))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        likes_and_popularity = mean_by_brand_two_metrics(sorted_products[family], 'number_likes', 'wilson_score')
        file_name = path + "/" + family + "_likes_and_popularity.json"
        f = open(file_name, "w")
        f.write(str(likes_and_popularity))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        likes_and_mark = mean_by_brand_two_metrics(sorted_products[family], 'number_likes', 'mark')
        file_name = path + "/" + family + "_likes_and_mark.json"
        f = open(file_name, "w")
        f.write(str(likes_and_mark))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        likes_and_price = mean_by_brand_two_metrics(sorted_products[family], 'number_likes', 'price')
        file_name = path + "/" + family + "_likes_and_price.json"
        f = open(file_name, "w")
        f.write(str(likes_and_price))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        positivity_and_likes = mean_by_brand_two_metrics(sorted_products[family], 'positive', 'number_likes')
        file_name = path + "/" + family + "_positivity_and_likes.json"
        f = open(file_name, "w")
        f.write(str(positivity_and_likes))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        positivity_and_popularity = mean_by_brand_two_metrics(sorted_products[family], 'positive', 'wilson_score')
        file_name = path + "/" + family + "_positivity_and_popularity.json"
        f = open(file_name, "w")
        f.write(str(positivity_and_popularity))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        positivity_and_price = mean_by_brand_two_metrics(sorted_products[family], 'positive', 'price')
        file_name = path + "/" + family + "_positivity_and_price.json"
        f = open(file_name, "w")
        f.write(str(positivity_and_price))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        positivity_and_mark = mean_by_brand_two_metrics(sorted_products[family], 'positive', 'mark')
        file_name = path + "/" + family + "_positivity_and_mark.json"
        f = open(file_name, "w")
        f.write(str(positivity_and_mark))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        mark_and_popularity = mean_by_brand_two_metrics(sorted_products[family], 'mark', 'wilson_score')
        file_name = path + "/" + family + "_mark_and_popularity.json"
        f = open(file_name, "w")
        f.write(str(mark_and_popularity))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        mark_and_likes = mean_by_brand_two_metrics(sorted_products[family], 'mark', 'number_likes')
        file_name = path + "/" + family + "_mark_and_likes.json"
        f = open(file_name, "w")
        f.write(str(mark_and_likes))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        mark_and_positivity = mean_by_brand_two_metrics(sorted_products[family], 'mark', 'positive')
        file_name = path + "/" + family + "_mark_and_positivity.json"
        f = open(file_name, "w")
        f.write(str(mark_and_positivity))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        mark_and_price = mean_by_brand_two_metrics(sorted_products[family], 'mark', 'price')
        file_name = path + "/" + family + "_mark_and_price.json"
        f = open(file_name, "w")
        f.write(str(mark_and_price))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        price_and_likes = mean_by_brand_two_metrics(sorted_products[family], 'price', 'number_likes')
        file_name = path + "/" + family + "_price_and_likes.json"
        f = open(file_name, "w")
        f.write(str(price_and_likes))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        price_and_positivity = mean_by_brand_two_metrics(sorted_products[family], 'price', 'positive')
        file_name = path + "/" + family + "_price_and_positivity.json"
        f = open(file_name, "w")
        f.write(str(price_and_positivity))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        price_and_popularity = mean_by_brand_two_metrics(sorted_products[family], 'price', 'wilson_score')
        file_name = path + "/" + family + "_price_and_popularity.json"
        f = open(file_name, "w")
        f.write(str(price_and_popularity))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        price_and_mark = mean_by_brand_two_metrics(sorted_products[family], 'price', 'mark')
        file_name = path + "/" + family + "_price_and_mark.json"
        f = open(file_name, "w")
        f.write(str(price_and_mark))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        popularity_and_mark = mean_by_brand_two_metrics(sorted_products[family], 'wilson_score', 'mark')
        file_name = path + "/" + family + "_popularity_and_mark.json"
        f = open(file_name, "w")
        f.write(str(popularity_and_mark))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        popularity_and_likes = mean_by_brand_two_metrics(sorted_products[family], 'wilson_score', 'number_likes')
        file_name = path + "/" + family + "_popularity_and_likes.json"
        f = open(file_name, "w")
        f.write(str(popularity_and_likes))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        popularity_and_price = mean_by_brand_two_metrics(sorted_products[family], 'wilson_score', 'price')
        file_name = path + "/" + family + "_popularity_and_price.json"
        f = open(file_name, "w")
        f.write(str(popularity_and_price))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        popularity_and_positivity = mean_by_brand_two_metrics(sorted_products[family], 'wilson_score', 'positive')
        file_name = path + "/" + family + "_popularity_and_positivity.json"
        f = open(file_name, "w")
        f.write(str(popularity_and_positivity))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
    print("Family Files done!")

    # Creation of the files for each brand
    brand_list = []
    for product in search_results['value']:
        brand_list.append(product['brand'])
        brand_list = list(set(brand_list))
    print("Brand list done!")

    for brand in range(len(brand_list)):
        if "'" in brand_list[brand]:
            brand_list[brand] = brand_list[brand].replace("'", "''") #In OData filters, single quotes are escaped by doubling
        if '&' in brand_list[brand]:
            brand_list[brand] = brand_list[brand].replace("&", "%26")

    for brand in brand_list:
        brand_results = cognitive_search(scoringProfile, brand)
        sorted_products = sort_by_family(brand_results)
        prices = mean_by_family_one_metric(sorted_products, 'price')
        prices = rank(prices, 'price')
        file_name = path + "/" + brand + "_price.json"
        f = open(file_name, "w")
        f.write(str(prices))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        popularity = mean_by_family_one_metric(sorted_products, 'wilson_score')
        popularity = rank(popularity, 'wilson_score')
        file_name = path + "/" + brand + "_popularity.json"
        f = open(file_name, "w")
        f.write(str(popularity))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        positivity = mean_by_family_one_metric(sorted_products, 'positive')
        positivity = rank(positivity, 'positive')
        file_name = path + "/" + brand + "_positivity.json"
        f = open(file_name, "w")
        f.write(str(positivity))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        number_likes = mean_by_family_one_metric(sorted_products, 'number_likes')
        number_likes = rank(number_likes, 'number_likes')
        file_name = path + "/" + brand + "_likes.json"
        f = open(file_name, "w")
        f.write(str(number_likes))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        marks = mean_by_family_one_metric(sorted_products, 'mark')
        marks = rank(marks, 'mark')
        file_name = path + "/" + brand + "_mark.json"
        f = open(file_name, "w")
        f.write(str(marks))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        likes_and_positivity = mean_by_family_two_metrics(sorted_products, 'number_likes', 'positive')
        file_name = path + "/" + brand + "_likes_and_positivity.json"
        f = open(file_name, "w")
        f.write(str(likes_and_positivity))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        likes_and_popularity = mean_by_family_two_metrics(sorted_products, 'number_likes', 'wilson_score')
        file_name = path + "/" + brand + "_likes_and_popularity.json"
        f = open(file_name, "w")
        f.write(str(likes_and_popularity))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        likes_and_price = mean_by_family_two_metrics(sorted_products, 'number_likes', 'price')
        file_name = path + "/" + brand + "_likes_and_price.json"
        f = open(file_name, "w")
        f.write(str(likes_and_price))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        likes_and_marks = mean_by_family_two_metrics(sorted_products, 'number_likes', 'mark')
        file_name = path + "/" + brand + "_likes_and_mark.json"
        f = open(file_name, "w")
        f.write(str(likes_and_marks))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        positivity_and_likes = mean_by_family_two_metrics(sorted_products, 'positive', 'number_likes')
        file_name = path + "/" + brand + "_positivity_and_likes.json"
        f = open(file_name, "w")
        f.write(str(positivity_and_likes))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        positivity_and_price = mean_by_family_two_metrics(sorted_products, 'positive', 'price')
        file_name = path + "/" + brand + "_positivity_and_price.json"
        f = open(file_name, "w")
        f.write(str(positivity_and_price))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        positivity_and_popularity = mean_by_family_two_metrics(sorted_products, 'positive', 'wilson_score')
        file_name = path + "/" + brand + "_positivity_and_popularity.json"
        f = open(file_name, "w")
        f.write(str(positivity_and_popularity))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        positivity_and_marks = mean_by_family_two_metrics(sorted_products, 'positive', 'mark')
        file_name = path + "/" + brand + "_positivity_and_mark.json"
        f = open(file_name, "w")
        f.write(str(positivity_and_marks))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        marks_and_likes = mean_by_family_two_metrics(sorted_products, 'mark', 'number_likes')
        file_name = path + "/" + brand + "_mark_and_likes.json"
        f = open(file_name, "w")
        f.write(str(marks_and_likes))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        marks_and_price = mean_by_family_two_metrics(sorted_products, 'mark', 'price')
        file_name = path + "/" + brand + "_mark_and_price.json"
        f = open(file_name, "w")
        f.write(str(marks_and_price))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        marks_and_positivity = mean_by_family_two_metrics(sorted_products, 'mark', 'positive')
        file_name = path + "/" + brand + "_mark_and_positivity.json"
        f = open(file_name, "w")
        f.write(str(marks_and_positivity))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        marks_and_popularity = mean_by_family_two_metrics(sorted_products, 'mark', 'wilson_score')
        file_name = path + "/" + brand + "_mark_and_popularity.json"
        f = open(file_name, "w")
        f.write(str(marks_and_popularity))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        price_and_likes = mean_by_family_two_metrics(sorted_products, 'price', 'number_likes')
        file_name = path + "/" + brand + "_price_and_likes.json"
        f = open(file_name, "w")
        f.write(str(price_and_likes))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        price_and_popularity = mean_by_family_two_metrics(sorted_products, 'price', 'wilson_score')
        file_name = path + "/" + brand + "_price_and_popularity.json"
        f = open(file_name, "w")
        f.write(str(price_and_popularity))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        price_and_positivity = mean_by_family_two_metrics(sorted_products, 'price', 'positive')
        file_name = path + "/" + brand + "_price_and_positivity.json"
        f = open(file_name, "w")
        f.write(str(price_and_positivity))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        price_and_marks = mean_by_family_two_metrics(sorted_products, 'price', 'mark')
        file_name = path + "/" + brand + "_price_and_mark.json"
        f = open(file_name, "w")
        f.write(str(price_and_marks))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        popularity_and_likes = mean_by_family_two_metrics(sorted_products, 'wilson_score', 'number_likes')
        file_name = path + "/" + brand + "_popularity_and_likes.json"
        f = open(file_name, "w")
        f.write(str(popularity_and_likes))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        popularity_and_price = mean_by_family_two_metrics(sorted_products, 'wilson_score', 'price')
        file_name = path + "/" + brand + "_popularity_and_price.json"
        f = open(file_name, "w")
        f.write(str(popularity_and_price))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        popularity_and_positivity = mean_by_family_two_metrics(sorted_products, 'wilson_score', 'positive')
        file_name = path + "/" + brand + "_popularity_and_positivity.json"
        f = open(file_name, "w")
        f.write(str(popularity_and_positivity))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
        popularity_and_mark = mean_by_family_two_metrics(sorted_products, 'wilson_score', 'mark')
        file_name = path + "/" + brand + "_popularity_and_mark.json"
        f = open(file_name, "w")
        f.write(str(popularity_and_mark))
        f.close()
        files_path.append(file_name)
        files_names.append(file_name.split('/')[1])
    print("Brand Files done!")

# Upload the files to Azure Storage Files
uploader = FileService(account_name="puppeteerscrapingresults", account_key="QsaFrqTErlHV6+tnoy1OhfYWMEshAUUnPq/lgY8t/oe6rCHxTuA7IgtlrbQRsSS4Il7olLAR0PQ+NxaIYqfgjw==", connection_string="DefaultEndpointsProtocol=https;AccountName=puppeteerscrapingresults;AccountKey=QsaFrqTErlHV6+tnoy1OhfYWMEshAUUnPq/lgY8t/oe6rCHxTuA7IgtlrbQRsSS4Il7olLAR0PQ+NxaIYqfgjw==;EndpointSuffix=core.windows.net", sas_token="?sv=2019-10-10&ss=bfqt&srt=sco&sp=rwdlacupx&se=2021-01-01T00:00:00Z&st=2020-05-20T14:13:30Z&sip=109.221.195.239&spr=https&sig=TRkMxEIRXtdz4HqQzpV4q2etl5F7lMC8%2BTM7Ahe7HHI%3D", protocol='https', endpoint_suffix='core.windows.net')
#uploader.create_directory("test", "json_files", fail_on_exist=False)
for file in range(len(files_names)):
    uploader.create_file_from_path("test", "json_files", files_names[file], files_path[file])
    print(files_names[file] + " uploaded!")
print("Files uploaded!")
