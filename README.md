# Overview

This repository contains the initial efforts to create a ground station for the satellite. Currently it contains: 
- Code to simulate a satellite. 
- A Python 'gateway' which communicates with major tom, a GUI/API service. 
- Code to translate information from the radio inputs to the gateway. 

The ultimate goal of the system is to create a simple and intiutive ground station service for talking to the satellite on orbit. 

The ground station system as it currently stands is somewhat integrated into Major Tom, the service discussed earlier. However, radio parsing code and so forth can function independently if needed. 
