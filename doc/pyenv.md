PyEnv
=====

https://github.com/pyenv/pyenv

  * Specifies which python to invoke
  * Offers an install command to install any python version you want
    (Like rbenv + ruby-install)



Prerequisites
-------------

    sudo apt install -y build-essential libreadline-dev libssl-dev libbz2-dev libsqlite3-dev



Install PyEnv
-------------


    git clone https://github.com/pyenv/pyenv.git ~/.pyenv
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
    echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
    echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n  eval "$(pyenv init -)"\nfi' >> ~/.bashrc
    exec "$SHELL"


Install Python Version
----------------------

    pyenv install <version>

If you installed prerequisites, there should be no warnings after build
and built version should be available


Specify Python Version
----------------------


    pyenv local <version>



Pip Integration
---------------

PyEnv *appears* to have a pip shim, but when I use it, it does not install
for the python that PyEnv is targeting.

You can still do this as a workaround:

    python -m pip install --user numpy
