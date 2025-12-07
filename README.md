### INF601 - Advanced Programming in Python
### Nicholas Kitchen
### Final Project

# Project Title
 
Final Project - Zooventory
 
## Description
 
Zooventory is an application that makes it easy to track animals, food consumption, and weight change. After getting signed up and logged in, the user will see a dashboard with information for the last 30 days.
The user can add animals and food items, and edit and delete them if needed. 

A user can also add animal species by either creating them themselves or using an API to autofill information.
***Note: The species database is shared across all users. Therefore, the program will always favor the API's response for a species. When creating a species, the program will send a request to the API with the name of the animal.
If an exact name match is found, the response from the API will be used and the user's input will be overwritten.*** Species cannot be deleted since other users could be using them, but they can be edited if your creation was successful.

The user can use a feeding calculator or weight calculator provided inside the app.

The feeding calculator does 2 things:
1. It will subtract the entered amount from the food supply.
2. It will log the last time an animal has been fed.

The weight calculator does 2 things:
1. It will set the weight for the selected animal.
2. It will log the time of the weight change.

The user can set feeding schedules for their animals. When a feeding time passes, a notification will display in the user's inbox for them to read.
 
## Getting Started

### Dependencies
 
Please install all the required packages:
```
pip install -r requirements.txt
```
 
### Installing

Please run the following command to move your working directory into the project:
```
cd ./finalprojectNicholasKitchen
```

Please create the database and migrate it into the project:

``` 
python manage.py makemigrations
```

``` 
python manage.py migrate
```

Please create your admin user. You will need to enter a username and password. Email is optional:

``` 
python manage.py createsuperuser
```

### Adding Test Data
The file load_test_data.py can be used to load some test data for demo purposes. If you want to add test data, then run the following command:

```
python load_test_data.py
```

**Test Username: 1234test**

**Test Password: 1234test**

### Executing program

Please enter the following into the console to run the server:
```
python manage.py runserver
```

*If an error appears saying you cannot access that port, try running a different port. For example:*
```
python manage.py runserver 8001
```
 
## Authors
 
Nicholas Kitchen
 
## Version History

* 0.1
    * Initial Release
 
## Acknowledgments

* [Django](https://docs.djangoproject.com/en/5.2/)
* [Jinja](https://jinja.palletsprojects.com/en/stable/)
* [ChatGPT](https://chatgpt.com/g/g-p-691368c335548191b6bc3f4285a9fc9e-finalprojectnicholaskitchen/project)