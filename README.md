# animate_GPS

This is an experimental code that generates radar maps of data in a GPS file using Folium. It saves these maps as
PNGs using Selenium WebDriver (a.k.a. Selenium 2). For each snapshot this code will fire a browser window in
parallel and save images.


# Requirements:
Install `Poetry` and `Firefox`. For Mac, you can `brew cask install firefox`.

You need to install `geckodriver` that controls Firefox browser by running the following on Python console:

`from selenium import webdriver`
`from webdriver_manager.firefox import GeckoDriverManager`
`driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())`

# Setup
After installing the requirements do `make setup`. 

# Run
`python Radar.py` to run it with the test data.
