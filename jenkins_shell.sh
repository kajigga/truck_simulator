PYENV_HOME=$WORKSPACE/.pyenv/

# Delete previously built virtualenv
if [ -d $PYENV_HOME ]; then
    rm -rf $PYENV_HOME
fi

# Create virtualenv and install necessary packages
virtualenv --no-site-packages $PYENV_HOME
. $PYENV_HOME/bin/activate
pip install -r $WORKSPACE/requirements.txt
pip install --quiet nosexcover
pip install --quiet pylint
nosetests --with-xcoverage --with-xunit  --cover-erase ./tests/
pylint -f parseable ./tests/ | tee pylint.out
