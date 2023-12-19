2G Network Traffic Monitoring
=============================
The goal of this project is to anonymously gather data on how much either A5/1 or A5/3 algorithms are still in use in 2G networks.
For the data collection process and RTL-SDR (or any SDR) is used as it is the most plug-and-play option.  
The heavy lifting is done by the gr-gsm software suite, especially grgsm_livemon / grgsm_livemon_headless, by [ptrkrysik](https://github.com/ptrkrysik/gr-gsm).

Installation, Setup
======================
Depending on your OS and available gnuradio version, you will need different versions of gr-gsm:
* gnuradio $\leq$ 3.8: [ptrkrysik's main branch](https://github.com/ptrkrysik/gr-gsm)
* gnradio==3.9 or higher: Try [bkerler's fork](https://github.com/bkerler/gr-gsm) or [velichkov's fork](https://github.com/bkerler/gr-gsm), which work for up to gnuradio 3.11  


Please see project's [wiki](https://osmocom.org/projects/gr-gsm/wiki/index) for information on [installation](https://osmocom.org/projects/gr-gsm/wiki/Installation) and [usage](https://github.com/ptrkrysik/gr-gsm/wiki/Usage) of gr-gsm.
                
Usage
======================

* grgsm_collection_monitor: Does the recording with grgsm and tshark, filters for package details, here the used encryption algorithms,
but could be rewritten to use any wireshark / tshark filter
* grgsm_collection_monitor has a watchdog that restarts the SDR monitoring and filtering if either grgsm_livemon or tshark fails, or if not enough packages are collected in a certain time span
* cipher_suite: Takes an .json or .csv file of recorded data and produces plots of the development over time
* Dockerfile: work in progress to make testing mobile, base ubuntu image plus added tshark and gr-gsm, start with 
docker run --it -v /dev/bus/usb:/dev/bus/usb and -v local/path/to/data:/tmp/ 
* Now can be run with the run.sh script which builds the docker image and runs the container. Frequency needs to be set in the script.
