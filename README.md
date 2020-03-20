# Overview

This repository contains the initial efforts to create a ground station for the satellite. Currently it contains two 'gateways' - one which is a basic test with no features to check out the system, the other one with more features that will hopefully remain a development version and change with the satellite. Each one contains: 
- Code to simulate a satellite. 
- A Python 'gateway' which communicates with major tom, a GUI/API service. 
- Code to translate information from the radio inputs to the gateway. 

The ultimate goal of the system is to create a simple and intiutive ground station service for talking to the satellite on orbit. 

The ground station system as it currently stands is somewhat integrated into Major Tom, the service discussed earlier. However, radio parsing code and so forth can function independently if needed. 

See the groundstation wiki page for the latest source of truth: https://github.com/spacecraft-design-lab-2019/documentation/wiki/Groundstation
