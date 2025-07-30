############################################
# Creates a PEM (and OpenSSH) formatted private key.
############################################

#https://registry.terraform.io/providers/hashicorp/tls/latest/docs/resources/private_key
resource "tls_private_key" "instance_ssh" {
  algorithm = "RSA"
  rsa_bits  = 2048
}

############################################
# Object Storage service: Uploads private key to Object Storage
############################################

#https://registry.terraform.io/providers/oracle/oci/latest/docs/resources/objectstorage_object
resource "oci_objectstorage_object" "private_key" {
  #Required
  bucket     = oci_objectstorage_bucket.bucket.name
  content    = tls_private_key.instance_ssh.private_key_pem
  namespace  = data.oci_objectstorage_namespace.ns.namespace
  object     = "instance_private_key.pem"

  depends_on = [oci_objectstorage_bucket.bucket]
}

############################################
# Data Source: Oracle Linux Image
############################################

#https://registry.terraform.io/providers/oracle/oci/latest/docs/data-sources/core_images
data "oci_core_images" "oracle_linux" {
  #Required
  compartment_id           = var.compartment_ocid
  
  #Optional
  operating_system         = "Oracle Linux"
  operating_system_version = "9"
  shape                    = var._oci_instance.shape.name
  sort_by                  = "TIMECREATED"
  sort_order               = "DESC"
}

############################################
# Data Source: Availability Domains
############################################

#https://registry.terraform.io/providers/oracle/oci/latest/docs/data-sources/identity_availability_domains
data "oci_identity_availability_domains" "ads" {
  compartment_id = var.tenancy_ocid
}

############################################
# The template_file data source renders a template from a template string
############################################

#https://registry.terraform.io/providers/hashicorp/template/latest/docs/data-sources/file
data "template_file" "user_data" {
  template = file("${path.module}/templatefile/user_data.sh")

  vars = {
    bucket_name        = oci_objectstorage_bucket.bucket.name
    oci_config_content = file("${path.module}/.oci/config")
    oci_key_content    = file("${path.module}/.oci/key.pem")
    env = templatefile("${path.module}/templatefile/.env.tmpl", {
      compartment_ocid                       = var.compartment_ocid
      autonomous_database_admin_password     = var.autonomous_database_admin_password
      autonomous_database_db_name            = var._oci_autonomous_database.db_name
      autonomous_database_developer_password = var.autonomous_database_developer_password
      autonomous_database_wallet_password    = var.autonomous_database_wallet_password
      namespace                              = data.oci_objectstorage_namespace.ns.namespace
      bucket_name                            = oci_objectstorage_bucket.bucket.name
      region                                 = var.region
    })
  }
}

############################################
# Compute Instance
############################################

#https://registry.terraform.io/providers/oracle/oci/latest/docs/resources/core_instance
resource "oci_core_instance" "linux_instance" {
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  compartment_id      = var.compartment_ocid
  shape               = var._oci_instance.shape.name

  source_details {
    source_id   = data.oci_core_images.oracle_linux.images[0].id
    source_type = "image"
  }

  shape_config {
    memory_in_gbs = var._oci_instance.shape.memory_in_gbs
    ocpus         = var._oci_instance.shape.ocpus
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.subnet.id
    assign_public_ip = true
  }

  display_name = var._oci_instance.display_name

  metadata = {
    ssh_authorized_keys = tls_private_key.instance_ssh.public_key_openssh
    #https://cloudinit.readthedocs.io/en/latest/explanation/format.html
    user_data           = base64encode(data.template_file.user_data.rendered)
  }

  depends_on = [
    oci_objectstorage_object.adb_wallet_zip
  ]
}

############################################
# Wait until user_data.sh finishes
############################################

resource "null_resource" "wait_for_userdata" {
  depends_on = [oci_core_instance.linux_instance]

  connection {
    type        = "ssh"
    host        = oci_core_instance.linux_instance.public_ip
    user        = "opc"
    private_key = tls_private_key.instance_ssh.private_key_pem
  }

  provisioner "remote-exec" {
    inline = [
      "echo '[INI] Setup started...............'",
      "while ! grep -q 'Cloud-init v.* finished at' /var/log/cloud-init-output.log; do sleep 10; done",
      "echo ''",
      "echo ''",
      "echo 'Network URL: http://${oci_core_instance.linux_instance.public_ip}:8501'",
      "echo ''",
      "echo ''",
      "echo '[END] Setup completed.............'",
    ]
  }
}
