**A modern WAN Emulator developed by the Institute for Networked Solutions**
# WEmulate API Module
This is the API module which builds on the [CLI module](https://github.com/wemulate/wemulate).

Have a look at the [documentation](https://wemulate.github.io/wemulate) for detailed information.

## Installation
Install the API module via the install script:
```bash
$ sh -c "$(curl -fsSL https://raw.githubusercontent.com/wemulate/wemulate/main/install/install.sh)"
```

## Development
Configure poetry to create the environment inside the project path, in order that VSCode can recognize the virtual environment.
```
$ poetry config virtualenvs.in-project true
```
Install the virtualenv.
```
$ poetry install
```
Start the application with the following command:
```
$ uvicorn api.app:app --host 0.0.0.0 --port 8080 --reload
```