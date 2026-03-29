cd /tmp

git clone https://github.com/DobroSaBokja/highrowglif.git

rm highrowglif/install.sh
rm highrowglif/README.md
rm highrowglif/.gitignore
rm -rf highrowglif/.git

sudo cp -r highrowglif /usr/local/lib/highrowglif
sudo rm /usr/local/lib/highrowglif/highrowglif

sudo mv /tmp/highrowglif/highrowglif /usr/local/bin/highrowglif
rm -rf highrowglif

sudo chmod +x /usr/local/bin/highrowglif
