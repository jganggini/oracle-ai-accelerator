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

# Step 5: Download and install Miniconda for the opc user
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /home/opc/Miniconda3.sh
chmod +x /home/opc/Miniconda3.sh
/home/opc/Miniconda3.sh -b -u -p /home/opc/miniconda3

# Step 6: Configure Conda for the opc user environment
echo 'export PATH=/home/opc/miniconda3/bin:$PATH' >> /home/opc/.bashrc
echo 'source /home/opc/miniconda3/etc/profile.d/conda.sh' >> /home/opc/.bashrc
chown opc:opc /home/opc/.bashrc

# Step 7: Pre-accept Conda Terms of Service for required channels
sudo -u opc -i bash -c 'source ~/.bashrc && conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main'
sudo -u opc -i bash -c 'source ~/.bashrc && conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r'

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

# Step 12: Run the setup script using Conda base environment as opc user
sudo -u opc -i bash <<'EOF'
cd /home/opc/oracle-ai-accelerator/setup
source /home/opc/miniconda3/etc/profile.d/conda.sh
conda run -n base pip install --upgrade --force-reinstall python-dotenv
conda run -n base python setup.py --linux
EOF

# Step 13: Launch the Streamlit application using the ORACLE-AI Conda environment
sudo -u opc -i bash <<'EOF'
cd /home/opc/oracle-ai-accelerator/app
source /home/opc/miniconda3/etc/profile.d/conda.sh
echo "Using Python from: $(conda run -n ORACLE-AI which python)"
nohup conda run -n ORACLE-AI streamlit run app.py --server.port 8501 --logger.level=INFO > /home/opc/streamlit.log 2>&1 &
EOF
