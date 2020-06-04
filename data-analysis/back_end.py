# -*- coding: utf-8 -*-

import sys, getopt
import json
import requests


# Declare variables to connect to the Cognitive Search endpoint
endpoint = 'https://sephora.search.windows.net/'
api_version = '?api-version=2019-05-06'
headers = {'Content-Type': 'application/json',
        'api-key': 'A54DE9E994C977D6C43EA04DFE1BD845' }


def fetch_parameters():
    brand = ""
    scoringProfile = ""
    gender = ""
    typee = ""
    sort = ""
    try:
        opts, args = getopt.getopt(sys.argv[1:],"h:bsgtr",["help=","brand=","scoringProfile=","gender=","type=","sort="])
    except getopt.GetoptError:
        print 'Options not recognized'
        sys.exit(2)
    for o, a in opts:
        if o in ("-h", "--help"):
            print("Help")
        elif o in ("-b", "--brand"):
            brand = a
        elif o in ("-s", "--scoringProfile"):
            scoringProfile = a
            # sys.exit()
        elif o in ("-g", "--gender"):
            gender = a
        elif o in ("-t", "--type"):
            typee = a
        elif o in ("-r", "--sort"):
            sort = a
    return brand, scoringProfile, gender, typee, sort

def cognitive_search(scoringProfile, brand):
    #searchstring = "&search=*&$count=true&scoringProfile=reviewsPriceLikes&$select=product_name,positive,number_likes,price&$filter=brand eq 'CHANEL'"
    if brand != "":
        searchstring = "&search=*&$count=true&$top=1000&$scoringProfile=" + scoringProfile + "&$filter=brand eq '" + brand +"'"
    else:
        searchstring = "&search=*&$count=true&$top=10&$scoringProfile=" + scoringProfile
    url = endpoint + "indexes/sephora/docs" + api_version + searchstring
    response  = requests.get(url, headers=headers, json=searchstring)
    query = response.json()
    return query

def sort_by_brand(results, brand):
    brand_products = {}
    brand_products['value'] = []
    for product in range(len(results['value'])):
        if (results['value'][product]['brand'] == brand):
            brand_products['value'].append(results['value'][product])
    return brand_products

def sort_by_family(results):
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
    for product in range(len(results['value'])):
        if (results['value'][product]['gender'] == "Men" and results['value'][product]['type'] == "Cologne") :
            men_colognes[results['value'][product]['id']] = results['value'][product]
        elif (results['value'][product]['gender'] == "Women" and results['value'][product]['type'] == "Perfume") :
            women_perfumes[results['value'][product]['id']] = results['value'][product]
        elif (results['value'][product]['gender'] == "Women" and results['value'][product]['type'] == "Cologne") :
            women_colognes[results['value'][product]['id']] = results['value'][product]
        elif (results['value'][product]['gender'] == "Men" and results['value'][product]['type'] == "Body Sprays & Deodorant") :
            body_sprays[results['value'][product]['id']] = results['value'][product]
        elif (results['value'][product]['gender'] == "Women" and results['value'][product]['type'] == "Body Mist & Hair Mist") :
            body_mist[results['value'][product]['id']] = results['value'][product]
        elif (results['value'][product]['gender'] == "Women" and results['value'][product]['type'] == "Lotions & Oils") :
            lotions[results['value'][product]['id']] = results['value'][product]
        elif (results['value'][product]['gender'] == "Gift Sets" and results['value'][product]['type'] == "Cologne Gift Sets") :
            cologne_sets[results['value'][product]['id']] = results['value'][product]
        elif (results['value'][product]['gender'] == "scoringProfile] & Gift Sets" and results['value'][product]['type'] == "Perfume Gift Sets") :
            perfume_sets[results['value'][product]['id']] = results['value'][product]
        elif (results['value'][product]['gender'] == "Men" and results['value'][product]['type'] == "Bath & Shower") :
            men_bath_shower[results['value'][product]['id']] = results['value'][product]
        elif (results['value'][product]['gender'] == "Women" and results['value'][product]['type'] == "Bath & Shower") :
            women_bath_shower[results['value'][product]['id']] = results['value'][product]
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
    for family in families.keys():
        if families[family] == {}:
            families.pop(family)
    return families

def mean_by_brand_one_metric(families, metric):
    families_mean = {}
    for family in families.keys():
        families_mean[family] = {}
        for product in families[family].keys():
            brand = families[family][product]['brand']
            if brand not in families_mean[family]:
                families_mean[family][brand] = []
            families_mean[family][brand].append(families[family][product])
    for family in families_mean.keys():
        sum_metric = 0
        number_products_brand = 0
        for brand in families_mean[family].keys():
            for product in range(len(families_mean[family][brand])):
                sum_metric += families_mean[family][brand][product][metric]    
                number_products_brand += 1
            families_mean[family][brand] = {}
            families_mean[family][brand][metric] = sum_metric / number_products_brand
    return families_mean

def mean_by_brand_two_metrics(families, metric1, metric2):
    families_mean = {}
    for family in families.keys():
        families_mean[family] = {}
        for product in families[family].keys():
            brand = families[family][product]['brand']
            if brand not in families_mean[family]:
                families_mean[family][brand] = []
            families_mean[family][brand].append(families[family][product])
    for family in families_mean.keys():
        sum_metric1 = 0
        sum_metric2 = 0
        number_products_brand = 0
        for brand in families_mean[family].keys():
            for product in range(len(families_mean[family][brand])):
                sum_metric1 += families_mean[family][brand][product][metric1]
                sum_metric2 += families_mean[family][brand][product][metric2]
                number_products_brand += 1
            families_mean[family][brand] = {}
            families_mean[family][brand][metric1] = sum_metric1 / number_products_brand
            families_mean[family][brand][metric2] = sum_metric2 / number_products_brand 
    return families_mean

def mean_by_family_one_metric(sorted_brand_products, metric):
    families_mean = {}
    for family in sorted_brand_products.keys():
        families_mean[family] = {}
        sum_metric = 0
        number_products_family = 0
        for product in sorted_brand_products[family]:
            sum_metric += sorted_brand_products[family][product][metric]
            number_products_family += 1
        if sorted_brand_products[family] == {}:
            families_mean.pop(family)
        else:
            families_mean[family][metric] = sum_metric / number_products_family
    return families_mean

def mean_by_family_two_metrics(sorted_brand_products, metric1, metric2):
    families_mean = {}
    for family in sorted_brand_products.keys():
        families_mean[family] = {}
        sum_metric1 = 0
        sum_metric2 = 0
        number_products_family = 0
        for product in sorted_brand_products[family]:
            sum_metric1 += sorted_brand_products[family][product][metric1]
            sum_metric2 += sorted_brand_products[family][product][metric2]
            number_products_family += 1
        if sorted_brand_products[family] == {}:
            families_mean.pop(family)
        else:
            families_mean[family][metric1] = sum_metric1 / number_products_family
            families_mean[family][metric2] = sum_metric2 / number_products_family
    return families_mean







# brand, scoringProfile, gender, typee, sort =  fetch_parameters()
# search_results = cognitive_search(scoringProfile, brand)

# ##########################
# ## PREMIER CAS D'USAGE  ##
# ##########################
# # On choisit un type, et on classe les différentes marques dans ce type de produits
# if brand == "" : 
#     sorted_products = sort_by_family(search_results)
#     print
#     brand_price = mean_by_brand_one_metric(sorted_products, 'price')
#     brand_likes_and_positivity = mean_by_brand_two_metrics(sorted_products, 'number_likes', 'positive')

# #########################
# ## SECOND CAS D'USAGE  ##
# #########################
# # On choisit une marque, et on évalue les différentes catégories de cette marque 
# else: 
#     sorted_products = sort_by_family(search_results)
#     prices = mean_by_family_one_metric(sorted_products, 'price')
#     likes_and_positivity = mean_by_family_two_metrics(sorted_products, 'number_likes', 'positive')
#     print(likes_and_positivity)