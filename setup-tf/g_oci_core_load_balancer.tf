############################################
# Create Flexible Load Balancer
############################################
resource "oci_load_balancer_load_balancer" "flexible_lb" {
  compartment_id = var.compartment_ocid
  display_name   = var._load_balancer.display_name
  shape          = "flexible"

  shape_details {
    minimum_bandwidth_in_mbps = var._load_balancer.min_mbps
    maximum_bandwidth_in_mbps = var._load_balancer.max_mbps
  }

  subnet_ids = [oci_core_subnet.subnet.id]

reserved_ips {
    id = var.lb_reserved_ip_id
  }
}

############################################
# Streamlit's Backend Set (Port 8501)
############################################
resource "oci_load_balancer_backend_set" "backend_set_streamlit" {
  name             = "backendset-streamlit"
  load_balancer_id = oci_load_balancer_load_balancer.flexible_lb.id
  policy           = "ROUND_ROBIN"

  health_checker {
    protocol    = "HTTP"
    url_path    = "/"
    port        = 8501
    return_code = 200
  }
}

############################################
# Audio Backend's Backend Set (Port 8000)
############################################
resource "oci_load_balancer_backend_set" "audio_backend_set" {
  name             = "backendset-audio"
  load_balancer_id = oci_load_balancer_load_balancer.flexible_lb.id
  policy           = "ROUND_ROBIN"

  health_checker {
    protocol    = "HTTP"
    url_path    = "/health"
    port        = 8000
    return_code = 200
  }
}

############################################
# TLS Certificate for HTTPS
############################################
resource "oci_load_balancer_certificate" "lb_certificate" {
  load_balancer_id = oci_load_balancer_load_balancer.flexible_lb.id
  certificate_name = "app-autosigned-cert"

	private_key        = file("${path.module}/templatefile/key_ca.pem")
	public_certificate = file("${path.module}/templatefile/cert.pem")

}


############################################
# HTTPS Listener with Rule Set
############################################
# Path Route Set
resource "oci_load_balancer_path_route_set" "https_path_routes" {
  load_balancer_id = oci_load_balancer_load_balancer.flexible_lb.id
  name             = "https_path_routes"

  path_routes {
    path             = "/ws/audio*"
    backend_set_name = oci_load_balancer_backend_set.audio_backend_set.name
    path_match_type {
      match_type = "PREFIX_MATCH"
    }
  }

  path_routes {
    path             = "/health"
    backend_set_name = oci_load_balancer_backend_set.backend_set_streamlit.name
    path_match_type {
      match_type = "EXACT_MATCH"
    }
  }
}


resource "oci_load_balancer_listener" "https_listener" {
  load_balancer_id         = oci_load_balancer_load_balancer.flexible_lb.id
  name                     = "https-listener"
  default_backend_set_name = oci_load_balancer_backend_set.backend_set_streamlit.name
  port                     = 443
  protocol                 = "HTTP"

  ssl_configuration {
    certificate_name        = oci_load_balancer_certificate.lb_certificate.certificate_name
    verify_peer_certificate = false
  }

  path_route_set_name = oci_load_balancer_path_route_set.https_path_routes.name
}



############################################
# Backends: Streamlit (Port 8501)
############################################
resource "oci_load_balancer_backend" "backend_streamlit" {
  load_balancer_id = oci_load_balancer_load_balancer.flexible_lb.id
  backendset_name = oci_load_balancer_backend_set.backend_set_streamlit.name
  ip_address       = oci_core_instance.linux_instance.private_ip
  port             = 8501
  weight           = 1
}

############################################
# Backends: Audio (Port 8000)
############################################
resource "oci_load_balancer_backend" "backend_audio" {
  load_balancer_id = oci_load_balancer_load_balancer.flexible_lb.id
  backendset_name = oci_load_balancer_backend_set.audio_backend_set.name
  ip_address       = oci_core_instance.linux_instance.private_ip
  port             = 8000
  weight           = 1
}