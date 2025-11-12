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
