HasGeek Eventframe
==================

Event frame provides functionality common across HasGeek events, to simplify
the process of setting up per-event websites.

Getting Started
---------------

* Clone the repository

        $ git clone git://github.com/hasgeek/eventframe.git
        $ cd eventframe

* Setup a virtual env

        $ virtualenv env
        $ . env/bin/activate

* Install required python packages

        $ pip install -r requirements.txt

* Create `settings.py`

        $ cp instance/settings-sample.py instance/settings.py

* Edit `setting.py` and add the following details
    
        # Add 0.0.0.0 to ADMIN_HOSTS
        ADMIN_HOSTS = ['eventframe.hasgeek.com', 'efdev.hasgeek.in', '0.0.0.0']

        # Set path to themes. Using absolute path is preferred.
        THEME_PATHS = 'eventframe/themes'

        # You need to have client-id/secret from LastUser.
        # If you don't have one already, register one at https://auth.hasgeek.com/apps
        LASTUSER_CLIENT_ID = '....'
        LASTUSER_CLIENT_SECRET = '...'

        # You may have to customize other field as needed

* Run the app

        $ python runserver.py
         * Running on http://0.0.0.0:8090/
         * Restarting with reloader    
        ...

    If you want to start the app on a different port, pass the port as argument.

        $ python runserver.py 8080
         * Running on http://0.0.0.0:8080/
         * Restarting with reloader    
        ...

* Create first website
    * Visit <http://0.0.0.0:8080/> (substitute your port here).
    * Click on "Login or Sign up" link in the top-right corner.
    * After login, visit <http://0.0.0.0:8080/_new> and create new website by filling in the following details:
        * Title: Hello Eventframe       # Title of the wesite
        * URL name: hello-eventframe    # slug for the website
        * Website URL: <http://127.0.0.1:8080/>
        * Hostnames: `127.0.0.1`

* Adding pages
    * Visit http://0.0.0.0:8080/hello-eventframe/
    * Click on "+New -> Page"
    * Add `Title` and `Page Content`. Leave `URL Name` empty as we are adding the root page.
    * Click Save.
    * Visit http://127.0.0.1:8080/ to the view the newly added page.
    * You can add more pages by following above steps.
    
One eventframe instance can serve multiple websites and each website is attached to one hostname. In the above setup, we are using <http://0.0.0.0:8080/> for the admin panel and <http://127.0.0.1:8080/> for the website that we have created. You can try creating another website and set Hostname to `localhost`.


