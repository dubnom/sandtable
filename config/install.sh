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
apt-get update
apt-get upgrade

apt-get install ntp ntpdate -y
apt-get install vim -y
apt-get install python-dev -y
apt-get install libjpeg-dev -y
apt-get install fonts-liberation -y
apt-get install ttf-mscorefonts-installer -y
apt-get install swig -y
apt-get install ffmpeg -y
apt-get install imagemagick -y
apt-get install potrace -y
apt-get install libagg-dev -y
apt-get install libpotrace-dev -y
apt-get install libgeos-dev -y
apt-get install python-numpy python-scipy -y

apt-get install telnet -y
apt-get install smbclient -y

apt install connectd -y
connectd_installer

pip install Image
pip install bottle
pip install cython
pip install pypotrace
pip install shapely
pip install apscheduler
pip install sqlalchemy
pip install fontTools=3.44.0

# Gphoto2
wget https://raw.githubusercontent.com/gonzalo/gphoto2-updater/master/gphoto2-updater.sh
chmod +x gphoto2-updater.sh
./gphoto2-updater.sh
pip install gphoto2

# Fadecandy
cd ~
git clone https://github.com/scanlime/fadecandy
cd fadecandy/server/
make submodules
make
mv fcserver /usr/local/bin

# Directories
cd /home/sandtable/sandtable
mkdir store
chown -R www-data pictures clipart scripts movies store data 

# Update /etc/rc.local with config/rclocal

# Create symbolic links
mkdir /var/www
ln -s /home/sandtable/sandtable /var/www/sandtable
