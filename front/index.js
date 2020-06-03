var express = require('express');
var app = express();



app.use('/', express.static(__dirname));
app.get('/',function(req,res){
	res.sendFile('/html/index.htm', {root: __dirname });
});
app.get('/*.json' , function(req,res) {
  var parameters = req.originalUrl.split('/')
  file_name = parameters[parameters.length - 1]
  parameters = file_name.split('.')[0]

  // gender = ""
  // type = ""
  // metric1 = ""
  // metric2 = ""
  // if (parameters.split('_')[0] == parameters.toUpperCase()) {
  //     brand = parameters.split('_')[0]
  // 		metric1 = parameters.split('_')[1]
  // 		if (parameters.split('_').length >= 2) {
  // 			metric2 = parameters.split('_')[2]
  // 		}
  // } else{
  // 	 	gender = parameters.split('_')[0]
  // 		type = parameters.split('_')[1]
  // 		metric1 = parameters.split('_')[2]
  // 		if (parameters.split('_').length >= 3) {
  // 			metric2 = parameters.split('_')[3]
  // 		}
  // }
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
  async function get_data(/*gender, metric1, metric2*/) {
  	const shareClient = serviceClient.getShareClient('sephora');
  	const directoryClient = shareClient.getDirectoryClient('json_files');
  	const fileClient = directoryClient.getFileClient(file_name);
  	const downloadFileResponse = await fileClient.download(0);
  	var data = await streamToString(downloadFileResponse.readableStreamBody);
  	return data
  }

  get_data(/*gender, metric1, metric2*/).then(value => {
  	res.send(value);
  }).catch(err => {
    res.send(err)
  });

});

app.listen(8080, function () {
	console.log('Listening on port 8080');
});
