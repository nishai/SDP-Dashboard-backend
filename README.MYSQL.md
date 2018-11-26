# Why MySQL not SQLite:
SQLite is not optimised for many concurrent requests.
As soon as many requests are recieved at the same time,
there is a high probability SQLite will throw a "database
is locked error", and fail to return a request.

Thus for our app, we need to use MySQL instead.


# MySQL Server Commands:
- $ mysql.server start
- $ mysql.server stop
- $ mysql.server restart
- $ mysql.server status


# MySQL Setup:install mysql, then mysql-serverthen1. $ systemctl enable mysql
2. $ mysqladmin -u "root" password "newpwd"
3. $ mysql -u root -p
 - CREATE DATABASE wits_dashboard;
 - EXIT;pyenv stuffdo the rest in virtual env:1. $ pip3 install -r requirements.txt
2. $ make migrate
3. $ python3 manage.py import --wits all.csv --schools schools.csv --lowercaseif you get an error about mysql_config, run the following:
$ sudo apt-get install libmysqlclient-dev


# MySQL Timouts:
1. $ mysql -u root -p
  - SET GLOBAL connect_timeout=30;
  - SET GLOBAL wait_timeout=30;
  - SET GLOBAL interactive_timeout=30;

connect_timeout:     Number of seconds the mysqld server waits for a connect packet before responding with 'Bad handshake'
interactive_timeout: Number of seconds the server waits for activity on an interactive connection before closing it
wait_timeout:        Number of seconds the server waits for activity on a connection before closing it


# MySQL restart:
1. $ mysql -u root -p
  - DROP DATABASE wits_dashboard;
  - CREATE DATABASE wits_dashboard;
  - EXIT;


# Django Connection Options:
The following environment variables exist for our django app. Specify these to overwrite any defaults.
- DJANGO_MYSQL_USER (default: root)
- DJANGO_MYSQL_PASS (default: password)
- DJANGO_MYSQL_HOST (default: localhost)
- DJANGO_MYSQL_PORT (default: 3306)


SQLITE SUPPORT IS COMPLETELY DROPPED


