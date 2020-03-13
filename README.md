# WEmulate Backend

Repository for the WEmulate Backend written in Python.

## Prototype
1. Install **pip** first
    sudo apt-get install python3-pip
2. Install **virtualenv** using pip3
    sudo pip3 install virtualenv 
3. Create a virtual environment 
    virtualenv venv 
4. Activate virtualenv
    source venv/bin/activate
5. Install all requirements
   pip install -r requirements.txt
6. Start WSGI
   cd interfaces
   gunicorn --bind 0.0.0.0:5000 /wsgi:app 

