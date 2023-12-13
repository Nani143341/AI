My Django Web Application
This Django web application is a simple blog where users can create, view, edit, and delete blog posts on AI and ML.
This project is a simple project
Features
Create, read, update, and delete blog posts.
Admin interface to manage blog posts.
Bootstrap integration for improved UI.
Use of Django's built-in testing framework.

Requirements
Python 3.x
Django 3.x
Bootstrap (optional for styling)

Setup
Clone this repository.
Navigate to the root directory where all the project files are located.
Open the terminal in the root directory.
Install the required packages using pip install -r requirements.txt.
Apply database migrations using python manage.py migrate.
Create a superuser using python manage.py createsuperuser.
Run the development server using python manage.py runserver.

Usage
Access the admin interface at http://127.0.0.1:8000/admin/ and log in with the superuser credentials.
username - admin
password - 123123
Access the application at http://127.0.0.1:8000/.

Tests
Navigate to the root directory where all the project files are located.
Run tests using python manage.py test.

Customizing the Admin Site
The admin interface is customized by creating a custom admin.py file in the relevant app and registering models with custom admin classes.

Third-Party Packages
Third-party packages used in this project:
django-crispy-forms for form rendering.



