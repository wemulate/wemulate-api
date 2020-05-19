# WEmulate Backend

Repository for the WEmulate Backend written in Python.

## Content
* [Development Setup](#development-setup)
   * [With Mockup](#with-mockup)
      * [Install Dependencies](#install-dependencies)
      * [Set Environment Variables](#set-environment-variables)
   * [Without Mockup](#with-mockup) 
      * [Install Dependencies](#install-dependencies-1)
      * [Set Environment Variables](#set-environment-variables-1)
   * [Start Project](#start-project)
   * [Start Frontend (Optional)](#start-frontend-(optional))
* [Production Setup](#production-setup)


## Development Setup

### With Mockup

For development purposes the backend can be used with mocked dependencies. To use a mocked environment with a temporaty SQLite database the steps in the follwing subchapters have to be executed.

#### Install Dependencies
To start the backend in the development modus a few requirements are necessary. Following are the necessary steps to install the required software parts:

1. Install Python (Python 3.7 Recommended): `sudo apt install python3.7` 
2. Install pip: `sudo apt-get install python3-pip`
3. Install virtualenv: using pip3 `sudo pip3 install virtualenv`
4. Activate virtualenv: `source venv/bin/activate`
5. Install all requirements: `pip install -r requirements.txt`


#### Set Environment Variables
The backend uses environment variables to read out information which are needed to connect to the database and also the Salt API. The environment variable `WEMULATE_TESTING` has to be set to `True` to tell the backend it should use mocked dependencies. The following command can be used for this purpose:
```
export POSTGRES_USER=wemulate POSTGRES_PASSWORD=wemulateEPJ2020 POSTGRES_DB=wemulate POSTGRES_HOST=localhost POSTGRES_PORT=5432 SALT_API=http://localhost:8000 SALT_PASSWORD='EPJ@2020!!' WEMULATE_TESTING='True'
```
The project is now ready to [start](#start-project)

### Without Mockup
It is also possible to start the backend with all dependencies and surrounding systems.

#### Install Dependencies
1. Install Python  (Python 3.7 Recommended): `sudo apt install python3.7`
2. Install pip: `sudo apt-get install python3-pip`
3. Install virtualenv: using pip3 `sudo pip3 install virtualenv`
4. Activate virtualenv: `source venv/bin/activate`
5. Install all requirements: `pip install -r requirements.txt`
6. Install Salt-Minion locally: `sudo apt install -y salt-minion`
7. Change Minion Name: `sudo vim /etc/salt/minion_id`
8. Change the Address, where the Minion search its Master, to localhost (127.0.0.1)
   * `sudo vim /etc/salt/minion`
   * Change config line from `master: salt` to `master: 127.0.0.1`
9. Change master config to acceppt all public keys
   * `sudo vim /etc/salt/master`
   * Change the line `# auto_accept: False` to `auto_accept: True`
10. Copy the local files to mountpoint: `sudo cp -r salt/ /mnt/srv` 
11. Start Salt and Postgres container: ` docker-compose -f local-development/docker-compose.yml up -d`

#### Set Environment Variables
The backend uses environment variables to read out information which are needed to connect to the database and also the Salt API.
Following environment variables has to be set  that the backend can find the corresponding container resources:
```
export POSTGRES_USER=wemulate POSTGRES_PASSWORD=wemulateEPJ2020 POSTGRES_DB=wemulate POSTGRES_HOST=localhost POSTGRES_PORT=5432 SALT_API=http://localhost:8000 SALT_PASSWORD='EPJ@2020!!' WEMULATE_TESTING='False'
```

### Start Project
With and also without mocking the web server interface gateway `gunicorn` has to be started to start the application. Following commands can be used.
```
cd gunicorn --bind 0.0.0.0:5000 project/wsgi:app
```

### Start Frontend (Optional)
For testing reasons it's often desired to also start the front end component. More information you can find [here](https://gitlab.dev.ifs.hsr.ch/epj/2020/wemulate/wemulate-frontend/)

_Hint: use the `quasar dev` approach_


 ## Production Setup
 The GitLab pipeline creates a working production container each time you commit to the repository.
In order to deploy the whole WEmulate project. Please have a look at the [Deployment Repository](https://gitlab.dev.ifs.hsr.ch/epj/2020/wemulate/wemulate-deployment).

