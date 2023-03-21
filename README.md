# Yatube
### Description
Bloggers social network where you can publish your posts, subscribe to other authors and comment published posts

### Tech
Python 3.7
Django 2.2.19
colorama 0.4.5
Pillow 8.3.1
sorl-thumbnail 12.7.0

## Installation
To run the project: Clone the repository and open it in the command line:
```
git clone git@github.com:valliv2007/yatube_final.git
cd yatube_final
```
Create and activate a virtual environment:
```
python -m venv venv
source venv/Scripts/activate
```
Install the dependencies from the requirements.txt file:
```
python -m pip install --upgrade pip
pip install -r requirements.txt
```
Run migrations:
```
python manage.py migrate
```
Launch the project:
```
python manage.py runserver
```
