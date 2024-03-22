# Installation script for the IArgus API. 
echo Starting installation process...
echo Requirements:
echo - Python3+
echo - A working MySQL server on this machine
sudo apt install git
git clone https://github.com/vinpap/iargus.git
cd iargus
python -m pip install --upgrade pip
pip install pipenv
pipenv install
read -p 'Enter your username on MySQL: ' uservar
read -s -p 'Enter your MySQL password: ' passvar
mysql -u $uservar -p $passvar -e "source ./db_creation.sql;"
echo Done!



