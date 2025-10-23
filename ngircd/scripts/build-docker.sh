sudo rm -rf rootfs
mkdir rootfs
sh ./scripts/create_rootfs.sh ngircd rootfs/
cp ngircd rootfs/
cp config.ini rootfs/
sudo docker build -t localhost/ngircd .
sudo docker save localhost/ngircd | gzip > ngircd-docker-image.tar.gz
sudo docker rmi localhost/ngircd
