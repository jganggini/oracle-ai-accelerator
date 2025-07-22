############################################
# Virtual Cloud Network (VCN)
############################################

#https://registry.terraform.io/providers/oracle/oci/latest/docs/resources/core_vcn
resource "oci_core_vcn" "vcn" {
  #Required
  compartment_id = var.compartment_ocid

  #Optional
  display_name   = var._oci_vcn.display_name
  cidr_block     = var._oci_vcn.cidr_block
}

############################################
# VCN: Creates a new subnet in the specified VCN
############################################

# https://registry.terraform.io/providers/oracle/oci/latest/docs/resources/core_subnet
resource "oci_core_subnet" "subnet" {
  #Required
  cidr_block     = var._oci_vcn.cidr_block
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.vcn.id
  
  #Optional
  display_name               = "public-subnet"
  prohibit_internet_ingress  = false
  prohibit_public_ip_on_vnic = false
  route_table_id             = oci_core_route_table.route_table.id
  security_list_ids          = [oci_core_security_list.vcn_security_list.id]
}

############################################
# VCN: Creates a new security list for the specified VCN.
############################################

#https://registry.terraform.io/providers/oracle/oci/latest/docs/resources/core_security_list
resource "oci_core_security_list" "vcn_security_list" {
  #Required
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.vcn.id

  #Optional
  display_name = "allow-tcp-ports"
  dynamic "ingress_security_rules" {
    for_each = var._oci_vcn.ingress_tcp_ports
    content {
      protocol = "6" # TCP
      source   = "0.0.0.0/0"

      tcp_options {
        min = ingress_security_rules.value
        max = ingress_security_rules.value
      }

      description = "Allow TCP port ${ingress_security_rules.value}"
    }
  }

  egress_security_rules {
    protocol    = "all"
    destination = "0.0.0.0/0"
  }
}

############################################
# VCN: Creates a new internet gateway for the specified VCN.
############################################

#https://registry.terraform.io/providers/oracle/oci/latest/docs/resources/core_internet_gateway
resource "oci_core_internet_gateway" "internet_gateway" {
  #Required
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.vcn.id

  #Optional
  display_name = "internet-gateway"
  enabled      = true
}

############################################
# VCN: Creates a new route table for the specified VCN.
############################################

#https://registry.terraform.io/providers/oracle/oci/latest/docs/resources/core_route_table
resource "oci_core_route_table" "route_table" {
  #Required
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.vcn.id

  #Optional
  display_name = "route-to-internet"
  route_rules {
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = oci_core_internet_gateway.internet_gateway.id
  }
}
