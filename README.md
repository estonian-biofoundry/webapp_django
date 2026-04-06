#### SETUP

- mkdir /home/hamza/web_django_app
- cd /home/hamza/web_django_app
- python3 -m venv .venv
- source .venv/bin/activate
- pip install -r requirements.txt
- python3 -m django --version

### CREATING DJANGO PROJECT

- django-admin (shows all the subcommands come with the package)
- django-admin startproject core . (it will create the whole project structure for django. using . at the end helps aviod nested folders)

### DJANGO FOLDER STRUCTURE EXPLANATION

In main folder the manage.py file is used to run commandline commands .
The subfolder **core** contains following files

- **init**.py is for simply making it into a module
- settings.py (this is where we change the different settings and configurations, like secret keys, database setups etc)
- urls.py (this is where we will setup the mapping from certain urls from where we will send users)
- wsgi.py & asgi.py (this is how webapp and web server communicate with each other)

### RUNNING THE APP WITH WEBSERVER

- python manage.py runserver 127.0.0.1:8003

### setup a dev db first

- create **strainqc_dev** database
- go to core/settings.py file and add following databse config

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'strainqc_dev',
        'USER': 'postgres',
        'PASSWORD': 'your_password_here',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### migrate django admin panel data models to your db

- python manage.py migrate
- python manage.py createsuperuser (this will prompt to add configurations for superuser which will be used in admin panel)

### CREATING FIRST APP AND REGISTERING IT. I created a app called accounts which will have accounts information

- python manage.py startapp accounts
- go to core/settings.py and add 'accounts' to INSTALLED_APPS list to register it

### Associate template to your first app

- create a base.html in templates
- create a login.html which extends from base in templates/accounts folder
- go to accounts/views.py and create a view which simply render this login page
- create a file accounts/urls.py and add the login to url patterns
- now go to the core urls.py and add ur accounts app url path to it so the project configs know what to look for
- finally add in core/settings.py fix the DIRS variable to correctly to [BASE_DIR / "templates"]

### Django form authentications

- create forms.py in accounts folder to extend the Django builtin form validations capabilities

```
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]

```

### Django admin setup

from terminal open the following command and enter credentials for your super user

- python manage.py createsuperuser

---

### In Production we can do the cron job for cleaning the old and expired sessions

- python manage.py clearsessions

## second app uploads

python manage.py startapp uploads

# after creating model run the following commands

Always run makemigrations first This generates the “diff” between your old model and the new one.

- python manage.py makemigrations uploads

Then run migrate. It applies the changes to the actual database.

- python manage.py migrate

### To reset a model

Roll back migrations

- python manage.py migrate _appname_ zero

Or the following if you already manually deleted a table from db, though it not recommended

- python manage.py migrate uploads zero --fake

Reapply migrations

- python manage.py migrate _appname_

### Hard reset

delete everything from the app folder/migrations except the empty init file
and then delete everything from django_migrations table in db

- DELETE FROM django_migrations WHERE app='appname';

this change comes from feature git-learning

> [!TIP]
> ❌
> [![please replace with alt text](https://img.shields.io/badge/anytext-youlike-blue)](https://example.org)

Add TOC in read me
