2G Network Traffic Monitoring
=============================
The goal of this project is to anonymously gather data on how often either **A5/1** or **A5/3** algorithms are still used in 2G networks.\
The heavy lifting is done by the **gr-gsm** software suite, especially *grgsm_livemon / grgsm_livemon_headles*s, by [ptrkrysik](https://github.com/ptrkrysik/gr-gsm). \
For the data collection process any SDR can be used, that is supported by grgsm_livemon and can receive the edaquate frequencies. \
For example, I used an RTL-SDR for GSM900 - as it is one of the cheapest and most plug-and-play options.  

## Installation, Setup

There are several ways on how to use this repo. In ascending order of manual adjustment needed:

1. Use run.sh: Needs a frequency as input, for details see [Usage](#usage). Builds the **Docker Image** and starts running **gsm-monitor** with provided argument inside the container. Output is written to a new output folder in the same directory as the cloned repo  

2. Build the Container from the **Dockerfile** yourself and run it (by default interactively), tweak **Dockerfile** if needed. Output written to new output folder in the same directory as the cloned repo

3. Only use **gsm-monitor** for data collection (with appropriate frequency). Output csv-files are written to *output/tshark_"$timestamp"_test.csv*.\
You will need to install **gr-gsm** locally. Depending on your OS and available **gnuradio** version, you will need different versions of **gr-gsm**:
    * ***gnuradio-3.8.2.0*** or older: [ptrkrysik's main branch](https://github.com/ptrkrysik/gr-gsm)
    * ***gnuradio-3.9.0.0*** or higher: Try [bkerler's fork](https://github.com/bkerler/gr-gsm) or [velichkov's fork](https://github.com/bkerler/gr-gsm), which work for at least up to ***gnuradio-3.11.x.x***  


Please see project's [wiki](https://osmocom.org/projects/gr-gsm/wiki/index) for information on [installation](https://osmocom.org/projects/gr-gsm/wiki/Installation) and [usage](https://github.com/ptrkrysik/gr-gsm/wiki/Usage) of **gr-gsm**.
                
## Components

* ***gsm-monitor:*** 
  * does the recording with **gr-gsm** and **tshark**
  * filters for package details, here the used encryption algorithms
  * could be rewritten to use any **wireshark / tshark** filter. 
  * has a watchdog that restarts the SDR monitoring and filtering if either **grgsm_livemon** and/or **tshark** fail, or if not enough packages are collected in a certain time span

* ***Dockerfile:*** 
  * builds the **Docker Image** on top of an **ubuntu22.04** base image and uses more recent versions of **gnuradio** as well as [bkerler's fork](https://github.com/bkerler/gr-gsm) of **gr-gsm**
  * creates an output directory for **gsm-monitor**
  * *ENTRYPOINT* is **gsm-monitor**

* ***run.sh:***
  * needs a frequency as input
  * automatically builds **Docker Image** and runs **gsm-monitor** with provided frequency

* ***create-plot.py***:
  * plots usage of **A5/1** and **A5/3** over time, absolute and relative
  * should be reworked / cleaned-up (histplot)
  * remove monitoring 

## Usage

The basic usage is to run the **gsm-monitor** script with an appropriate frequency to monitor usage of different 2G encryption algorithms on this frequency over long timespans and write each occurance to a csv file with an identifier for the used algorithm and a timestamp.

Example usage: 
>                           ./gsm-monitor 933.4M

for frequency *933.4 MHz* ~ *E/U/ARFCN 1016*, i.e. **gsm-monitor** follows the notational convention of **gr-gsm**.\
 If you wanted to customize sample rate, gain or use arfcn, **gsm-monitor** could be changed/rewritten accordingly with additional arguments (check ***grgsm_livemon -h*** for options)

To find the correct frequency for your use case, there are several possibilities:

1. Switching to 2G on your phone and looking at the frequency in the network settings:
    * Android: ***Settings***$\rightarrow$ ***Connections*** $\rightarrow$ ***Mobile networks*** $\rightarrow$ ***Choose your SIM card and switch to only 2G*** (potentially unsafe)
    * either use a network monitoring app or use **USSD** code ****#0011#***
    * if you used the USSD code, you'll find the ARFCN under ***BCCH arfcn***
    * **ARFCN** stands for [*absolute radio frequency channel number*](https://en.wikipedia.org/wiki/Absolute_radio-frequency_channel_number) and translates to a frequency in the 2G network
    * you can use a tool like [cellmapper's frequency calculator](https://www.cellmapper.net/arfcn) to translate the **ARFCN** to an actual frequency

2. Using a tool like [kalibrate-rtl](https://github.com/steve-m/kalibrate-rtl) to scan for a list of the strongest signals in your immediate area (requires SDR) 
3. Using online maps like [cellmapper](https://www.cellmapper.net/map) to find the strongest signal in your area


You can build and run a **docker container** from the ***Dockerfile***:
>                           docker build -t gsm-monitor .
To run it interactively: 
>                           docker run -it --privileged \
>                             -v /etc/timezone:/etc/timezone:ro \
>                             -v /etc/localtime:/etc/localtime:ro \
>                             -v /dev/bus/usb:/dev/bus/usb \
>                             -v "$(pwd)/output:/output" \
>                             gsm-monitor {frequency}

But be aware that ***--privileged*** flag might not be secure in general.\
Finally you can just run the **run.sh** script to build the container and deploy **gsm-monitor** with the chosen frequency. 
Example usage:
>                           ./run.sh 933.4M

This might be useful if you already settled on the frequency you want to monitor. For example, the docker image could be build on a **Rasperry Pi** or similiar single-board computers connected to an SDR and deployed to monitor a fixed frequency over extended periods of time.