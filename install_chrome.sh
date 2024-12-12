#!/bin/bash


wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] https://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list'


sudo apt-get update
sudo apt-get install -y libxss1 libappindicator3-1 libindicator3-7
sudo apt-get install -y libnss3 libgconf-2-4
sudo apt update
sudo apt install google-chrome-stable -y

sudo apt-get install xvfb
