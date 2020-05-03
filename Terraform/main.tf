#########################################################
# Setting the Azure Terraform Provider
provider "azurerm" {
  # whilst the `version` attribute is optional, we recommend pinning to a given version of the Provider
  version = "~> 2.1.0"
  features {}
}

#########################################################
# Creating Resource Group 
resource azurerm_resource_group rg {
    tags = {
                environment = var.environment
                project = var.project
                description = "this is a resource group"
                creator = var.creator
    }

    name     = "${var.trigram}-${var.project}-${var.environment}-rg"
    location = var.location
}

#########################################################
# Generating the account storage
resource azurerm_storage_account storage {
  tags = {
         "environment" = var.environment
         "project" = var.project
         "description" = "this is the account storage"
         "creator" = var.creator
  }

  name                     = "${var.trigram}${var.project}${var.environment}strg"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  account_tier             = "Standard"
  account_replication_type = "LRS"

  account_kind = "StorageV2"
  enable_https_traffic_only = "true"
  is_hns_enabled = "false"
}

#########################################################
# Creating a Account File Share
resource azurerm_storage_share share {
  name                 = "sephora"
  storage_account_name = azurerm_storage_account.storage.name
  quota                = 50
}

#########################################################
# Creating an ACR
resource azurerm_container_registry acr {
  name                     = "${var.trigram}${var.project}${var.environment}acr"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  sku                      = "Basic"
  admin_enabled            = true
}

#########################################################
# Creating an ACI
resource azurerm_container_group aci {
  name                = "${var.trigram}-${var.project}-${var.environment}-aci"
  location            = "Central US"
  resource_group_name = azurerm_resource_group.rg.name
  ip_address_type     = "public"
  os_type             = "linux"

  image_registry_credential {
    server   = "${azurerm_container_registry.acr.login_server}"
    username = "${azurerm_container_registry.acr.admin_username}"
    password = "${azurerm_container_registry.acr.admin_password}"
  }

  container {
    name   = "scraper-sephora"
    image  = "${azurerm_container_registry.acr.login_server}/puppeteer-scrap:50"
    cpu    = "4"
    memory = "16"
    port   = "80"
  }
}
