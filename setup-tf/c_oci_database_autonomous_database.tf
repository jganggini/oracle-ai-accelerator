############################################
# Autonomous Database service
############################################

#https://registry.terraform.io/providers/oracle/oci/latest/docs/resources/database_autonomous_database
resource "oci_database_autonomous_database" "adb23ai" {
    #Required
    admin_password = var.autonomous_database_admin_password
    compartment_id = var.compartment_ocid
    db_name        = var._oci_autonomous_database.db_name

    #Optional
    compute_count            = var._oci_autonomous_database.compute_count
    compute_model            = "ECPU"
    data_storage_size_in_tbs = var._oci_autonomous_database.data_storage_size_in_tbs
    db_version               = "23ai"
    db_workload              = var._oci_autonomous_database.db_workload
    display_name             = var._oci_autonomous_database.display_name
    is_auto_scaling_enabled  = var._oci_autonomous_database.is_auto_scaling_enabled
}

############################################
# Autonomous Database Wallet: Creates and downloads a wallet for the specified Autonomous Database.
############################################

#https://registry.terraform.io/providers/oracle/oci/latest/docs/resources/database_autonomous_database_wallet
resource "oci_database_autonomous_database_wallet" "adb_wallet" {
  #Required
  autonomous_database_id = oci_database_autonomous_database.adb23ai.id
  password               = var.autonomous_database_wallet_password

  #Optional
  base64_encode_content  = true
}

############################################
# Object Storage service: Creates a new object or overwrites an existing object with the same name.
############################################

#https://registry.terraform.io/providers/oracle/oci/latest/docs/resources/objectstorage_object
resource "oci_objectstorage_object" "adb_wallet_zip" {
  #Required
  bucket     = oci_objectstorage_bucket.bucket.name
  content    = oci_database_autonomous_database_wallet.adb_wallet.content
  namespace  = data.oci_objectstorage_namespace.ns.namespace
  object     = "adb_wallet.zip"
  
  depends_on = [
    oci_database_autonomous_database_wallet.adb_wallet,
    oci_objectstorage_bucket.bucket
  ]
}