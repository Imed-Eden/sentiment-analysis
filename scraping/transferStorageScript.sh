export AZURE_STORAGE_ACCOUNT=<account_name>
export AZURE_STORAGE_SHARE=<share-name>
export AZURE_STORAGE_RESOURCE_GROUP=<resource-group-name>

EXPIRE=$(date -u -d "3 months" '+%Y-%m-%dT%H:%M:%SZ')
START=$(date -u -d "-1 day" '+%Y-%m-%dT%H:%M:%SZ')
export AZURE_STORAGE_SAS_TOKEN=$(az storage account generate-sas --account-name $AZURE_STORAGE_ACCOUNT --account-key <key> --start $START --expiry $EXPIRE --https-only --permissions acdlpruw --resource-types sco --services f | sed 's/%3A/:/g;s/\"//g')

export result=`az storage file upload --source products.json -s $AZURE_STORAGE_SHARE --account-name $AZURE_STORAGE_ACCOUNT --sas-token $AZURE_STORAGE_SAS_TOKEN`
