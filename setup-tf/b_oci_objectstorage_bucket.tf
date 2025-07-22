############################################
# Bucket: Creates a bucket in the given namespace with a bucket name
############################################

#https://registry.terraform.io/providers/oracle/oci/latest/docs/resources/objectstorage_bucket
resource "oci_objectstorage_bucket" "bucket" {
  #Required
  compartment_id = var.compartment_ocid
  name           = var._oci_bucket_name.name  
  namespace      = data.oci_objectstorage_namespace.ns.namespace

  #Optional
  access_type    = var._oci_bucket_name.access_type
  storage_tier   = "Standard"
}

############################################
# Data Source: Bucket: Object Storage namespace.
############################################

#https://registry.terraform.io/providers/oracle/oci/latest/docs/data-sources/objectstorage_namespace
data "oci_objectstorage_namespace" "ns" {
  #Optional
  compartment_id = var.compartment_ocid
}