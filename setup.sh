#!/usr/bin/env bash

virtualenv venv
source venv/bin/activate
pip install -r requirements.txt


if [ "$(uname)" == "Darwin" ]; then
    curl https://chromedriver.storage.googleapis.com/81.0.4044.69/chromedriver_mac64.zip -o chromedriver.zip
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    curl https://chromedriver.storage.googleapis.com/81.0.4044.69/chromedriver_linux64.zip -o chromedriver.zip
fi

unzip chromedriver.zip
rm chromedriver.zip

echo "Add the chromedriver executable to your path or install geckodriver"

echo "dont forget to activate venv `source venv/bin/activate`"
