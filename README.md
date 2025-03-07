## Flowtrex is Project Management System - ERP Django app

### Read Carefully:

##### Creat a python virtual environment and active environment

* Create pyenv: `python -m venv .venv`
* Active pyenv: `.venv\Scripts\Activate.ps1`

###### Install packages: 
    pip install -r requirements.txt

#### Migrate and Migration Model:
* Migration: 
    `python manage.py makemigrations`
* Migrate:
    `python manage.py migrate`

#### Rename `.env.example` with `.env`
#### Generate a Django Secret key
`python key-gen.py`

#### Create SuperUser
`python manage.py createsuperuser`

#### Run Django app
`python manage.py runserver`

#### Site Features List 

* Dashboard
* Kanban Board
* Project List
* Project Summery
* Task Comment
* Settings