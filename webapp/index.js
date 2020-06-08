var express = require('express');
var app = express();

// The Express package allows us to handle HTTP GET requests
// Depending on the request, we can perform different operations before serving the page
app.use('/', express.static(__dirname));
// If the user requests the main page, we serve the index
app.get('/',function(req,res){
	res.sendFile('/html/index.htm', {root: __dirname });
});
// This is the request that is performed by the "products.htm" page
// It allows us to get all the CHANEL products, in order to create the list for the select menu
app.get('/get-brands', function(req,res) {
  const nconf = require('nconf');
  const AzureSearchClient = require('./AzureSearchClient.js');
  const query = "*&$count=true&$filter=brand eq 'CHANEL'"
  run(query).then(value => {
  	res.send(value);
  }).catch(err => {
    res.send(err)
  });

  function getAzureConfiguration() {
      const config = nconf.file({ file: 'azure_search_config.json' });
      return config;
  }
  async function doQueriesAsync(client, query) {
      const result = await client.queryAsync(query);
      const body = await result.json();
      return body
  }
  async function run(query) {
      try {
          const cfg = getAzureConfiguration();
          const client = new AzureSearchClient(cfg.get("serviceName"), cfg.get("adminKey"), cfg.get("queryKey"), cfg.get("indexName"));
          const results = await doQueriesAsync(client, query);
          return results
      } catch (x) {
          console.log(x);
      }
  }
})

// This is the request performed by the "products.htm" page to get the table when a product is selected
// We get the family and gender of the product, and then we perform a request to Cognitive Search using these filters
// It allows us to compare the selected product with similar products.
app.get("/search/*", function(req,res) {
  const nconf = require('nconf');
  const AzureSearchClient = require('./AzureSearchClient.js');
  var searchQuery = req.originalUrl.split('/')
  searchQuery = searchQuery[searchQuery.length - 1]
  run(searchQuery).then(value => {
  	res.send(value);
  }).catch(err => {
    res.send(err)
  });

  function getAzureConfiguration() {
      const config = nconf.file({ file: 'azure_search_config.json' });
      return config;
  }
  async function doQueriesAsync(client, searchQuery) {
      const result = await client.queryAsync(searchQuery);
      const body = await result.json();
      return body
  }
  async function run(searchQuery) {
      try {
          const cfg = getAzureConfiguration();
          const client = new AzureSearchClient(cfg.get("serviceName"), cfg.get("adminKey"), cfg.get("queryKey"), cfg.get("indexName"));
          const results = await doQueriesAsync(client, searchQuery);
          return results
      } catch (x) {
          console.log(x);
      }
  }
})

// This is the request performed by the following pages:
//      - perfumes_colognes.htm
//      - brands.htm
//      - bath.htm
//      - body.htm
// It passes the name of the file corresponding to the parameters selected by the user
// This name will be used to perform an Azure Blob Storage request, and serve the content of the file to be used to draw the chart.
app.get('/*.json' , function(req,res) {
  const { ShareServiceClient, StorageSharedKeyCredential } = require("@azure/storage-file-share");
  const serviceClient = new ShareServiceClient(`https://puppeteerscrapingresults.file.core.windows.net/?sv=2019-10-10&ss=bfqt&srt=sco&sp=rwdlacupx&se=2020-12-31T23:00:00Z&st=2020-05-25T08:48:45Z&spr=https&sig=Utoujty0FVtb0h30KY0rbtrR2sz2hcm88MGbyEewVQ0%3D`)//, anonymousCredential)
  var parameters = req.originalUrl.split('/')
  file_name = parameters[parameters.length - 1]
  // If the file requested starts with an uppercase string (=> brand name), we rewrite the non-ASCII characters before making the request to Azure Blob Storage
  if (file_name.split('.')[0].split('_')[0] == file_name.split('.')[0].split('_')[0].toUpperCase()) {
    file_name = file_name.replace(/\%20/g, ' ')
    file_name = file_name.replace(/\%C3\%88/g, 'È')
    file_name = file_name.replace(/\%C3\%94/g, 'Ô')
  }
  get_data().then(value => {
    res.send(value);
  }).catch(err => {
    res.send(err)
  });
  async function streamToString(readableStream) {
    return new Promise((resolve, reject) => {
      const chunks = [];
      readableStream.on("data", (data) => {
        chunks.push(data.toString());
      });
      readableStream.on("end", () => {
        resolve(chunks.join(""));
      });
      readableStream.on("error", reject);
    });
  }
  async function get_data() {
  	const shareClient = serviceClient.getShareClient('sephora');
  	const directoryClient = shareClient.getDirectoryClient('json_files');
  	const fileClient = directoryClient.getFileClient(file_name);
  	const downloadFileResponse = await fileClient.download(0);
  	var data = await streamToString(downloadFileResponse.readableStreamBody);
  	return data
  }
});

// Our app serves on the port 3000
app.listen(3000, function () {
});
