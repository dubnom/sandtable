#/bin/bash
# need:
#	create sandtable user
#		adduser sandtable
#		adduser sandtable sudo
#		adduser sandtable adm
#	fqdn,
# 	git email and name
# 	src/machines parameters
#	table parameters
# interactive: timezone setting, user info

# Set st_led to one of the following:
#  DotStar
#  FadeCandy
#  OPC
#  None
st_led=DotStar

# Set st_samba to enable or disable
st_samba=enable

# Set st_remote to enable or disable
st_remote=disable

# Directories
cd /home/sandtable/sandtable
mkdir store
chown -R www-data pictures clipart scripts movies store data 

# Create symbolic links
mkdir /var/www
ln -s /home/sandtable/sandtable /var/www/sandtable

# Update /etc/rc.local with config/rclocal
# FIX: This currently is done manually

# Install required packages
apt-get update
apt-get upgrade

apt-get install -y ntp ntpdate
apt-get install -y vim
apt-get install -y python3-dev
apt-get install -y libjpeg-dev
apt-get install -y fonts-liberation
apt-get install -y ttf-mscorefonts-installer
apt-get install -y swig
apt-get install -y ffmpeg
apt-get install -y imagemagick
apt-get install -y potrace
apt-get install -y libagg-dev
apt-get install -y libpotrace-dev
apt-get install -y libgeos-dev
apt-get install -y python-numpy python-scipy

# Python3 packages
pip3 install Image
pip3 install bottle
pip3 install cython
pip3 install pypotrace
pip3 install shapely
pip3 install apscheduler
pip3 install sqlalchemy
#pip3 install fontTools=3.44.0
pip3 install fontTools

# Gphoto2
wget https://raw.githubusercontent.com/gonzalo/gphoto2-updater/master/gphoto2-updater.sh
chmod +x gphoto2-updater.sh
./gphoto2-updater.sh
pip3 install gphoto2


# Optional Samba support
if [ $st_samba == 'enable' ]
then
    apt-get install -y smbclient
fi

# Optional remote connection support
if [ $st_remote == 'enable' ]
then
    apt install connectd -y
    connectd_installer
fi

# Optional lighting system support
#
# FadeCandy
if [ $st_led == 'FadeCandy' ]
then
    cd ~
    git clone https://github.com/scanlime/fadecandy
    cd fadecandy/server/
    make submodules
    make
    mv fcserver /usr/local/bin

# DotStar
elif [ $st_led == 'DotStar' ]
then
    # Enable SPI and I2C
    pip3 install RPI.GPIO
    pip3 install adafruit-blinka

# OPC
elif [ $st_led == 'OPC' ]
then
    # FIX: OPC not yet done
    echo ERROR: OPC Install not yet supported

# None
elif [ $st_led != 'None' ]
    echo ERROR: '$st_led' is not a known lighting system
fi
