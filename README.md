# Wits Statistics Dashboard - REST API

## Wiki

Visit the [Wiki](https://gitlab.com/wits-potato/dashboard-backend/wikis/home) for guides & info.

## 2018 Software Design Project

This project is only intended to be the implementation of the private REST API using Django.

**No frontend work should be done here.**

### Setup

Install requirements:
```
$ pip install -r requirements.txt
```

### Run

Migrate your database:
```
$ python manage.py migrate
```
Create a super user:
```
$ python manage.py createsuperuser --email admin@example.com --username admin
```
Run the server:

```
$ django-admin runserver
```

### Design

- Frontend (built with Node.js & Webpack and served with Nginx/Apache/Something Else)
- Backend (Only Django serving the api)
- Deploy (Configs used to deploy or test both projects in a production environment using Docker)
