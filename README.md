# WEmulate Backend

Repository for the WEmulate Backend written in Python.

## Prototype
1. Install **pip** first `sudo apt-get install python3-pip`
2. Install **virtualenv** using pip3 `sudo pip3 install virtualenv`
3. Create a virtual environment `virtualenv venv`
4. Activate virtualenv `source venv/bin/activate`
5. Install Postgres and Python extensions: `sudo apt-get install libpq-dev python-dev`
6. Install all requirements `pip install -r requirements.txt`
7. Start Postgres (DB) container: `docker run --name wemulate-db -e POSTGRES_PASSWORD=wemulateEPJ2020 -d -p 5432:5432 postgres`
7. Start WSGI `cd interfaces; gunicorn --bind 0.0.0.0:5000 wsgi:app`

### Salt
1. `sudo apt install -y salt-master salt-minion salt-api`
2. Change Minion Name: `sudo vim /etc/salt/minion_id`
3. Change the Address, where the Minion search its Master, to localhost (127.0.0.1)
   * `sudo vim /etc/salt/minion`
   * Change config line from `master: salt` to `master: 127.0.0.1`
4. Change master config to acceppt all public keys
   * `sudo vim /etc/salt/master`
   * Change the line `# auto_accept: False` to `auto_accept: True`
5. Start the Salt-Master and Salt-Minion with `sudo salt-master` and `sudo salt-minion`
   or start it as daemon: `sudo salt-master -d` and `sudo salt-minion -d`
   * **Hint**: [Run Salt as unpriviledged user](https://docs.saltstack.com/en/master/ref/configuration/nonroot.html#configuration-non-root-user)
6. Check if the Public Key has been accepted: `salt-key -L`
7. Add API config to master (in `/etc/salt/master.d/api.conf`):
```yaml
rest_cherrypy:
  port: 8000
  disable_ssl: True
external_auth:
    sharedsecret:
        salt: ['.*', '@wheel', '@jobs', '@runner']
sharedsecret: "EPJ@2020!!"
```
8. Copy the module to the minion:
   * Copy the module folder in the FILE_ROOTS (default /srv/salt/_modules)
   * Sync the files from the master to the minions --> `sudo salt-run saltutil.sync_all`
   * (Eventually first run `sudo salt '*' saltutil.clear_cache`)