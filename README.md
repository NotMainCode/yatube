# Yatube

A social network of bloggers, where users can publish posts with pictures.

After creating an account users can:
- publish posts
- subscribe to favorite authors
- publish comments to posts.

Anonymous users can only view posts and comments to them.

## Technology

Python 3.7

Django 2.2.16

## For launch

Create and activate virtual environment
```
py -3.7 -m venv venv

source venv/Scripts/activate
```

Install dependencies from requirements.txt file
```
pip install -r requirements.txt
```

Perform migrations
```
py manage.py migrate
```

Run project
```
py manage.py runserver 8008
```

## Author

https://github.com/NotMainCode


###
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)