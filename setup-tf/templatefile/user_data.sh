#!/bin/bash
set -eux

# Step 1: Update package cache and install system dependencies
yum makecache
yum install -y git vim python3 python3-pip python3-devel alsa-lib-devel firewalld unzip wget

# Step 2: Install OCI CLI and related Python packages
dnf -y install oraclelinux-developer-release-el9
dnf -y install python39-oci-cli
pip3 install oci oracledb python-dotenv

# Step 3: Start and enable firewalld service
systemctl start firewalld
systemctl enable firewalld

# Step 4: Open required ports in the firewall (Streamlit and VNC)
firewall-cmd --add-port=8501/tcp --permanent
firewall-cmd --add-port=5901/tcp --permanent
firewall-cmd --reload

# Step 5: Crear entorno virtual Python (.venv) para el usuario opc
dnf -y install python3.11 python3.11-devel
python3.11 -m venv /home/opc/.venv
chown -R opc:opc /home/opc/.venv

# Step 6: Configurar activación automática de .venv para el usuario opc
echo 'if [ -d "$HOME/.venv" ]; then source "$HOME/.venv/bin/activate"; fi' >> /home/opc/.bashrc
chown opc:opc /home/opc/.bashrc

# Step 7: Actualizar pip y herramientas básicas dentro de .venv
sudo -u opc -i bash -c 'source ~/.bashrc && python -m ensurepip --upgrade --default-pip'
sudo -u opc -i bash -c 'source ~/.bashrc && python -m pip install --upgrade pip wheel setuptools'

# Step 7.1: Compile and install PortAudio (required by PyAudio on Linux)
yum install -y gcc make autoconf automake libtool alsa-lib-devel git
if [ ! -d "/root/portaudio" ]; then
  git clone --depth=1 https://github.com/PortAudio/portaudio.git /root/portaudio
fi
cd /root/portaudio
./configure --prefix=/usr/local
make -j"$(nproc)"
make install
# Asegurar que el cargador de librerías encuentre /usr/local/lib
echo '/usr/local/lib' > /etc/ld.so.conf.d/portaudio.conf
ldconfig

# Step 8: Clone the project repository
git clone https://github.com/jganggini/oracle-ai-accelerator.git /home/opc/oracle-ai-accelerator
chown -R opc:opc /home/opc/oracle-ai-accelerator

# Step 9: Configure OCI CLI with credentials
mkdir -p /home/opc/.oci
echo "${oci_config_content}" > /home/opc/.oci/config
echo "${oci_key_content}" > /home/opc/.oci/key.pem
chmod 600 /home/opc/.oci/*
chown -R opc:opc /home/opc/.oci

# Step 10: Download and extract the Autonomous Database wallet
mkdir -p /home/opc/oracle-ai-accelerator/app/wallet

# Download the base64-encoded wallet
OCI_CLI_CONFIG_FILE=/home/opc/.oci/config oci os object get \
  --bucket-name ${bucket_name} \
  --name adb_wallet.zip \
  --file /home/opc/oracle-ai-accelerator/app/wallet/adb_wallet_encoded.zip

# Decode the wallet
base64 -d /home/opc/oracle-ai-accelerator/app/wallet/adb_wallet_encoded.zip > \
        /home/opc/oracle-ai-accelerator/app/wallet/adb_wallet.zip
rm -f /home/opc/oracle-ai-accelerator/app/wallet/adb_wallet_encoded.zip

# Unzip the wallet
unzip /home/opc/oracle-ai-accelerator/app/wallet/adb_wallet.zip \
      -d /home/opc/oracle-ai-accelerator/app/wallet

# Delete the object from Object Storage
OCI_CLI_CONFIG_FILE=/home/opc/.oci/config oci os object delete \
  --bucket-name ${bucket_name} \
  --name adb_wallet.zip \
  --force

# Step 11: Create the .env file with application environment variables
echo "${env}" > /home/opc/oracle-ai-accelerator/app/.env
chmod 600 /home/opc/oracle-ai-accelerator/app/.env
chown opc:opc /home/opc/oracle-ai-accelerator/app/.env

# Step 12: Ejecutar el setup usando el entorno virtual (.venv) como usuario opc
sudo -u opc -i bash <<'EOF'
cd /home/opc/oracle-ai-accelerator/setup
source /home/opc/.venv/bin/activate
python --version
python setup.py
deactivate
EOF

# Step 13: Lanzar la aplicación Streamlit usando el entorno virtual (.venv)
sudo -u opc -i bash <<'EOF'
cd /home/opc/oracle-ai-accelerator/app
source /home/opc/.venv/bin/activate
echo "Using Python from: $(which python)"
nohup python -m streamlit run app.py --server.port 8501 --logger.level=INFO > /home/opc/streamlit.log 2>&1 &
deactivate
EOF

# Step 14: Install and configure Nginx as HTTPS reverse proxy for Streamlit (single block)
sudo bash <<'EOF'
set -eux
dnf -y install oracle-epel-release-el9
dnf -y install nginx
dnf -y install certbot python3-certbot-nginx || true

# Permitir a Nginx conectarse a upstreams (Streamlit) con SELinux enforcing
setsebool -P httpd_can_network_connect 1 || true

# Open HTTP/HTTPS (keep existing 8501 rule for compatibility, but traffic will go via Nginx)
firewall-cmd --add-service=http --permanent || true
firewall-cmd --add-service=https --permanent || true
firewall-cmd --reload || true

# Remover configuraciones por defecto que pueden colisionar con server_name "_" (si existen)
rm -f /etc/nginx/conf.d/default.conf /etc/nginx/conf.d/welcome.conf /etc/nginx/conf.d/example_ssl.conf 2>/dev/null || true

# Nginx reverse proxy config (HTTP), proxying to local Streamlit on 127.0.0.1:8501
cat >/etc/nginx/conf.d/streamlit.conf <<'NGINXCONF'
server {
    listen 80;
    listen [::]:80;
    server_name _;

    client_max_body_size 64m;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
NGINXCONF

systemctl enable nginx
systemctl restart nginx

# Create a self-signed certificate and enable HTTPS
mkdir -p /etc/ssl/private
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/streamlit-selfsigned.key \
  -out /etc/ssl/certs/streamlit-selfsigned.crt \
  -subj "/CN=localhost"

cat >/etc/nginx/conf.d/streamlit-ssl.conf <<'NGINXSSL'
server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name _;

    ssl_certificate     /etc/ssl/certs/streamlit-selfsigned.crt;
    ssl_certificate_key /etc/ssl/private/streamlit-selfsigned.key;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:10m;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;

    client_max_body_size 64m;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
NGINXSSL

nginx -t
systemctl reload nginx || true
EOF

# Step 15: Mark userdata completion (sentinel)
mkdir -p /var/local
touch /var/local/userdata.done