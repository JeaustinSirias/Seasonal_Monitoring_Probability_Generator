# Seasonal Monitoring Probability Generator (SMPG Project)
This is an **academic tool** to support climatological researches for [Geophysical Center of Investigations](http://www.cigefi.ucr.ac.cr/). This tool offers multiple features to compliment seasonal rainfall probability analysis according to past years observed data.

![user_interfase](https://github.com/JeaustinSirias/Seasonal_Monitoring_Probability_Generator/blob/main/docs/graphic_user_interfase.png)

## Features
* Build your own custon rainfall scenarios by providing reference values for each station, location or polygon
* Analize your region by providing a CSV file with past years rainfall observed data
* Dekadal analysis and forecast for custom seasons, including *from-behind* analyisis
* Save your own statistics by including analog years and multiple summaries.

## Building instructions
This software is designed to be a desktop application. Installation is not needed unlesss you decide to work with its Python package. An you can find the lastest stable release [here](https://github.com/JeaustinSirias/Seasonal_Monitoring_Probability_Generator/releases/tag/v1.2.0).


**1.** First clone this repository in a local directory inside your computer by using the next instruction in your command window:
```
$ git clone https://github.com/JeaustinSirias/Seasonal_Monitoring_Probability_Generator.git
```
**2.** Move to the cloned directory by using your command window and type:

```
$ make require 
```
in order to install all the needed dependences. You can choose either installing the package as it follows:

```
$ make install
```
or just running it by typing:

```
$ make run
```
It also contains a **Dockerfile** to build the application by using a container in case you do not want to mind about dependences &  requirements installation. All you have to do is type the next instruction:

```
$ make container
```

