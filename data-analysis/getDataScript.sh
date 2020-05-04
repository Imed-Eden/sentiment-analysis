export AZURE_STORAGE_ACCOUNT=<"storage account name">
export AZURE_STORAGE_SHARE=<"storage share files name
export KEY=<"key of the account storage
export SOURCE_FILE=<"source path file">
export DESTINATION_FILE=<"destination path file">

az storage file download --account-name $AZURE_STORAGE_ACCOUNT --account-key $KEY --share-name $AZURE_STORAGE_SHARE --path $SOURCE_FILE --dest $DESTINATION_FILE
