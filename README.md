# Overview

This repository contains the initial efforts to create a ground station for the satellite. Currently it contains two 'gateways', test-gateway and gateway1. 
* test-gateway is a HOOTL test of Major Tom, making use of some development resources from Major Tom's creators. 
* gateway1 is an attempt at a gateway that actually works with the radio. 

Each gateway contains a top-level run file, a satellite class that handles commands, and a telemetry parser. They are designed to communicate over serial with a radio module. 

The ultimate goal of the system is to create a simple and intiutive ground station service for talking to the satellite on orbit. 

The ground station system as it currently stands is somewhat integrated into Major Tom, the service discussed earlier. However, radio parsing code and so forth can function independently if needed. 

See the groundstation wiki page for the latest source of truth: https://github.com/spacecraft-design-lab-2019/documentation/wiki/Groundstation
