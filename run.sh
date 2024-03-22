# This script sets up and run the IArgus API
echo Setting up the database
export MYSQL_DB_NAME=iargus
read -p 'Enter your username on MySQL: ' MYSQL_USER
read -s -p 'Enter your password on MySQL: ' MYSQL_PWD
echo Setting up the SMTP server
read -p 'Enter your server URL: ' SMTP_SERVER
read -p 'Enter your server login: ' SMTP_LOGIN
read -s -p 'Enter your server password: ' SMTP_PWD
read -p 'Where should the monitoring reports be sent? Enter an email address: ' SMTP_RECIPIENT
echo Done
echo WARNING - The SSL certificate currently being used is self-signed.
echo If you want to use another certificate, download it along with its private key and save them both in the iargus directory as cert.pem and key.pem.
cd iargus
pipenv run mlflow server --host 127.0.0.1 --port 8080
pipenv run python ./iargus/setup_tests.py
pipenv run uvicorn api:app --ssl-keyfile ./key.pem --ssl-certfile ./cert.pem 


