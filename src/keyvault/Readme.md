# Keyvault Force Soft Delete    

S360 complains about soft delete not being enabled on Azure Key Vaults. 

This code will find all vaults in a subscripiton, check if soft delete is enabled, then apply the soft delete if it's not set.

The only setting from configuration.json required is the subscriptions list.