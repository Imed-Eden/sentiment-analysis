var express = require('express');
var app = express();



app.use('/', express.static(__dirname));
app.get('/',function(req,res){
	res.sendFile('/html/index.htm', {root: __dirname });
});
app.get('/get-brands', function(req,res) {
  const nconf = require('nconf');
  const AzureSearchClient = require('./AzureSearchClient.js');

  function getAzureConfiguration() {
      const config = nconf.file({ file: 'azure_search_config.json' });
      return config;
  }
  const query = "*&$count=true&$filter=brand eq 'CHANEL'"

  async function doQueriesAsync(client, query) {
      const result = await client.queryAsync(query);
      const body = await result.json();
      //const str = JSON.stringify( body, null, 4);
      //console.log(`Query: ${query} \n ${str}`);
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
  run(query).then(value => {
  	res.send(value);
  }).catch(err => {
    res.send(err)
  });

})
app.get("/search/*", function(req,res) {
  const nconf = require('nconf');
  const AzureSearchClient = require('./AzureSearchClient.js');
  
  function getAzureConfiguration() {
      const config = nconf.file({ file: 'azure_search_config.json' });
      return config;
  }
  async function doQueriesAsync(client, searchQuery) {
      const result = await client.queryAsync(searchQuery);
      const body = await result.json();
      //const str = JSON.stringify( body, null, 4);
      //console.log(`Query: ${searchQuery} \n ${str}`);
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
  var searchQuery = req.originalUrl.split('/')
  searchQuery = searchQuery[searchQuery.length - 1]
  run(searchQuery).then(value => {
  	res.send(value);
  }).catch(err => {
    res.send(err)
  });
})

app.get('/*.json' , function(req,res) {
  var parameters = req.originalUrl.split('/')
  file_name = parameters[parameters.length - 1]
  parameters = file_name.split('.')[0]
  // Looking for a brand file
  gender = ""
  type = ""
  metric1 = ""
  metric2 = ""
  if (parameters.split('_')[0] == parameters.toUpperCase()) {
  } else{
  	 	gender = parameters.split('_')[0]
  		type = parameters.split('_')[1]
  		metric1 = parameters.split('_')[2]
  		if (parameters.split('_').length > 3) {
  			metric2 = parameters.split('_')[3]
  		}
  }
  const { ShareServiceClient, StorageSharedKeyCredential } = require("@azure/storage-file-share");
  const serviceClient = new ShareServiceClient(`https://puppeteerscrapingresults.file.core.windows.net/?sv=2019-10-10&ss=bfqt&srt=sco&sp=rwdlacupx&se=2020-12-31T23:00:00Z&st=2020-05-25T08:48:45Z&spr=https&sig=Utoujty0FVtb0h30KY0rbtrR2sz2hcm88MGbyEewVQ0%3D`)//, anonymousCredential)

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
  async function get_data(gender, metric1, metric2) {
  	const shareClient = serviceClient.getShareClient('sephora');
  	const directoryClient = shareClient.getDirectoryClient('json_files');
  	const fileClient = directoryClient.getFileClient(file_name);
  	const downloadFileResponse = await fileClient.download(0);
  	var data = await streamToString(downloadFileResponse.readableStreamBody);
  	return data
  }

  get_data(gender, metric1, metric2).then(value => {
  	res.send(value);
  }).catch(err => {
    res.send(err)
  });

});

app.listen(3000, function () {
	console.log('Listening on port 3000');
});