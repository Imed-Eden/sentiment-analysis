# Sephora's product scraper

This helps to set up a system that gets all the information about Sephora products mainly fragrances, lotions etc. such as :
1. Price
2. Brand
3. Product Name
4. Reviews
5. Comments
6. Marks


This system is based on a docker image that is especially created to host Puppeteer, Node and Azure Cli environment.
The data is stored in a json file to be sent to Azure File Storage (Share Files). The system run inside an Azure Container Instances (ACI).


**Tips for running this locally**

You'll need to perform the following :

1. Clone this repo
2. Make sure to chmod the shell executable transferStorageScript.sh
3. To run on your machine:
  + `docker build -t name-you-want .`
  + `docker run -it name-you-want`
