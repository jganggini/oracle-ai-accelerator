############################################
# Compartments and Region
############################################

variable "tenancy_ocid" {
  description = "🔐 OCID del tenancy."
  type        = string
  
  validation {
    condition     = length(var.tenancy_ocid) > 0
    error_message = "El nombre del [Tenancy OCID] no puede estar vacío."
  }
}

variable "compartment_ocid" {
  description = "🔐 OCID del compartment donde se desplegarán los recursos."
  type        = string
  
  validation {
    condition     = length(var.compartment_ocid) > 0
    error_message = "El nombre del [Compartment OCID] no puede estar vacío."
  }
}

variable "region" {
  description = "🌍 OCID de la Región donde se desplegarán los recursos (por ejemplo, us-chicago-1)"
  type        = string
  
  validation {
    condition     = length(var.region) > 0
    error_message = "El nombre de la [region OCID] no puede estar vacío."
  }
}


############################################
# Bucket
############################################

variable "_oci_bucket_name" {
  description = "🪣 Bucket [variables.tf][⚠️ No changes required]"
  
  default = {
    name: "buk-oracle-ai",     # Nombre del bucket en Object Storage donde se almacenarán archivos.
    access_type: "ObjectRead"  # Nivel de acceso del bucket. Puede ser 'NoPublicAccess', 'ObjectRead'.
  }
}

############################################
# Autonomous Database
############################################

variable "_oci_autonomous_database" {
  description = "🗂️ Autonomous Database [variables.tf][⚠️ No changes required]"

  default = {
    db_name: "adb23ai"
    display_name: "adb23ai"
    compute_count: 4              # Número de ECPU/OCPU asignadas (según compute_model)
    data_storage_size_in_tbs: 1   # Tamaño del almacenamiento (en terabytes)
    db_workload: "OLTP"           # Tipo de carga de trabajo: OLTP para ATP o DW para ADW
    is_auto_scaling_enabled: true # Habilitar escalamiento automático
  }
}

variable "autonomous_database_admin_password" {
  description = <<EOT
🔑 Contraseña del usuario ADMIN para la base de datos autónoma. 
Debe tener entre 12 y 30 caracteres, incluir al menos una mayúscula, una minúscula y un número. 
No puede contener comillas dobles (") ni la palabra "admin" (sin importar mayúsculas/minúsculas).
EOT

  type      = string
  sensitive = true

  validation {
    condition = (
      length(var.autonomous_database_admin_password) >= 12 &&
      length(var.autonomous_database_admin_password) <= 30 &&
      can(regex("[A-Z]", var.autonomous_database_admin_password)) &&
      can(regex("[a-z]", var.autonomous_database_admin_password)) &&
      can(regex("[0-9]", var.autonomous_database_admin_password)) &&
      !can(regex("\"", var.autonomous_database_admin_password)) &&
      !can(regex("(?i)admin", var.autonomous_database_admin_password))
    )
    error_message = <<EOT
La contraseña debe tener entre 12 y 30 caracteres, contener al menos una letra mayúscula, una minúscula y un número. 
No puede contener comillas dobles (") ni la palabra "admin" (sin importar mayúsculas/minúsculas).
EOT
  }
}

variable "autonomous_database_wallet_password" {
  description = <<EOT
🔑 Contraseña del WALLET para la base de datos autónoma. 
Debe tener entre 12 y 30 caracteres, incluir al menos una mayúscula, una minúscula y un número. 
No puede contener comillas dobles (") ni la palabra "admin" (sin importar mayúsculas/minúsculas).
EOT

  type      = string
  sensitive = true

  validation {
    condition = (
      length(var.autonomous_database_wallet_password) >= 12 &&
      length(var.autonomous_database_wallet_password) <= 30 &&
      can(regex("[A-Z]", var.autonomous_database_wallet_password)) &&
      can(regex("[a-z]", var.autonomous_database_wallet_password)) &&
      can(regex("[0-9]", var.autonomous_database_wallet_password)) &&
      !can(regex("\"", var.autonomous_database_wallet_password)) &&
      !can(regex("(?i)admin", var.autonomous_database_wallet_password))
    )
    error_message = <<EOT
La contraseña debe tener entre 12 y 30 caracteres, contener al menos una letra mayúscula, una minúscula y un número. 
No puede contener comillas dobles (") ni la palabra "admin" (sin importar mayúsculas/minúsculas).
EOT
  }
}

variable "autonomous_database_developer_password" {
  description = <<EOT
🔑 Contraseña del usuario ADW23AI para la base de datos autónoma. 
Debe tener entre 12 y 30 caracteres, incluir al menos una mayúscula, una minúscula y un número. 
No puede contener comillas dobles (") ni la palabra "admin" (sin importar mayúsculas/minúsculas).
EOT

  type      = string
  sensitive = true

  validation {
    condition = (
      length(var.autonomous_database_developer_password) >= 12 &&
      length(var.autonomous_database_developer_password) <= 30 &&
      can(regex("[A-Z]", var.autonomous_database_developer_password)) &&
      can(regex("[a-z]", var.autonomous_database_developer_password)) &&
      can(regex("[0-9]", var.autonomous_database_developer_password)) &&
      !can(regex("\"", var.autonomous_database_developer_password)) &&
      !can(regex("(?i)admin", var.autonomous_database_developer_password))
    )
    error_message = <<EOT
La contraseña debe tener entre 12 y 30 caracteres, contener al menos una letra mayúscula, una minúscula y un número. 
No puede contener comillas dobles (") ni la palabra "admin" (sin importar mayúsculas/minúsculas).
EOT
  }
}

############################################
# Virtual Cloud Network
############################################

variable "_oci_vcn" {
  description = "🌐 VCN [variables.tf][⚠️ No changes required]"

  default = {
    display_name: "vcn-oracle-ai"   # Nombre del VCN
    cidr_block: "10.0.0.0/24"       # Rango de direcciones IP para el VCN
    ingress_tcp_ports : [22, 8501]  # Puertos TCP permitidos: SSH (22) y Streamlit (8501)
  }
}

############################################
# Compute Instance
############################################

variable "_oci_instance" {
  description = "🖥️ Instance [variables.tf][⚠️ No changes required]"
  
  default = {
    display_name: "oracle-linux-9-app"
    shape: {
      name = "VM.Standard.E5.Flex"     # Tipo infraestuctura
      ocpus = 4                        # Número de OCPUs asignadas
      memory_in_gbs = 64               # Memoria asignada en GB
    }
  }
}