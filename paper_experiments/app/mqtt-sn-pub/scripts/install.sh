# cd ~/
# retdec

echo "installing ruby 2.5.5 by rbenv..."

sudo apt install -y build-essential libssl-dev libreadline-dev zlib1g-dev
wget -q https://raw.githubusercontent.com/rbenv/rbenv-installer/main/bin/rbenv-installer
chmod +x ./rbenv-installer
./rbenv-installer
echo 'export PATH="$HOME/.rbenv/bin:$PATH"' >> ~/.bashrc
rbenv init
echo 'if which rbenv > /dev/null; then eval "$(rbenv init -)"; fi' >> ~/.bashrc
source ~/.bashrc

# sudo apt install rbenv

echo "successfully installed rbenv"

rbenv install 2.5.5
rbenv global 2.5.5

echo "successfully installed ruby 2.5.5"

gem install bundler
cd ../inputs 
bundle install

echo "successfully installed bundler"

echo "installing libcoap..."

git clone https://github.com/obgm/libcoap.git
cd libcoap
./autogen.sh
./configure --disable-manpages
make
sudo make install
sudo ldconfig

echo "successfully installed libcoap"
echo "done"

