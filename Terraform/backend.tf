terraform {
  backend "azurerm" {
    resource_group_name  = "terraform-rg"
    storage_account_name = "terprdproject"
    container_name       = "terraform"
    key                  = "terraform.tfstate"
  }
}
