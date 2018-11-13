
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


# MySQL Setup:
1. $ mysqladmin -u "root" password "newpwd"
2. $ mysql -u root -p
3. $ CREATE DATABASE wits_dashboard;
4. $ EXIT:


# MySQL restart:
1. $ mysql -u root -p
2. $ DROP DATABASE wits_dashboard;
3. $ CREATE DATABASE wits_dashboard;
4. EXIT;


# Django Connection Options:
The following environment variables exist for our django app. Specify these to overwrite any defaults.
- DJANGO_MYSQL_USER (default: root)
- DJANGO_MYSQL_PASS (default: password)
- DJANGO_MYSQL_HOST (default: localhost)
- DJANGO_MYSQL_PORT (default: 3306)

A final environment variable exists if you wish to switch back to the legacy SQLite database:
- DJANGO_USE_SQLITE (default: false, valid options are: ['false', 'true'] make sure the case is correct)



