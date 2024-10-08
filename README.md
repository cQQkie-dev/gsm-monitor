2G Network Traffic Monitoring
=============================
The goal of this project is to anonymously gather data on how often either **A5/1** or **A5/3** or even **A5/4** algorithms are still used in 2G networks.\
The heavy lifting is done by the **gr-gsm** software suite, especially *grgsm_livemon / grgsm_livemon_headless*, by [ptrkrysik](https://github.com/ptrkrysik/gr-gsm). \
For the data collection process any SDR can be used, that is supported by *grgsm_livemon* and can receive the respective frequencies. \
A cheap option is any variant of [**RTL-SDR**](https://www.rtl-sdr.com/about-rtl-sdr/),  based on DVB-T Tuner Dongles with the **RTL2832U** chipset.
These usually cover the range between around ***500 kHz*** and ***1.75 GHz***, which is sufficient for all **(E-|R-)GSM-xxx** [frequency bands](https://en.wikipedia.org/wiki/GSM_frequency_bands), but not for **DCS-1800** or **PCS-1900** frequency bands. For these you could use one of Ettus Research's **USRPs**, a **HackRF One**, **BladeRF** or **LimeSDR**, but these tend to be notably more costly with the USRPs marking the high end. There are also some newer RTL-SDRs, that are still comparatively cheap, but claim to operate in the GHz range up until ***~2.3 GHz***.  

For example, I mostly used an RTL-SDR for GSM900 - as it is one of the cheapest options and very close to "plug-and-play". 

## Installation and Setup for Scripts

There are several ways to use the scripts in this repo manually on their own. For intended usage and setup as monitoring device on a Raspiberry Pi, see [below](#setup-on-raspberry-pi) In ascending order of manual adjustment needed:

1. Use run.sh: Needs a frequency as input, for details see [Usage](#usage). Builds the **Docker Image** and starts running **gsm-monitor** with provided argument inside the container. Output is written to a new output folder in the user's home directory. 

2. Build the Container from the **Dockerfile** yourself by 
    >                           docker build -t gsm-monitor . 
    and run it (by default interactively), tweak **Dockerfile** if needed. For detailed description of Docker usage, see [Usage](#usage)

3. Only use **gsm-monitor** for data collection (with appropriate frequency). Output csv-files are written to 
    >               ${OUTPUT_DIR}/tshark_${FREQUENCY}_${LAI}_${timestamp}.csv
    with the current directory as the default.

    You will need to install **gr-gsm** locally. Depending on your OS and available **gnuradio** version, you will need different versions of **gr-gsm**:
        * ***gnuradio-3.8.2.0*** or older: [ptrkrysik's main branch](https://github.com/ptrkrysik/gr-gsm)
        * ***gnuradio-3.9.0.0*** or higher: Try [bkerler's fork](https://github.com/bkerler/gr-gsm) or [velichkov's fork](https://github.com/bkerler/gr-gsm), which work for at least up to ***gnuradio-3.11.x.x***  


    Please see project's [wiki](https://osmocom.org/projects/gr-gsm/wiki/index) for information on [installation](https://osmocom.org/projects/gr-gsm/wiki/Installation) and [usage](https://github.com/ptrkrysik/gr-gsm/wiki/Usage) of **gr-gsm**.
                
## Components

* ***gsm-monitor:*** 
  * can be run without prefixed frequency, instead searches for the strongest frequency in the area via kalibrate-rtl or filters found frequencies for the strongest belonging to a certain provider
  * options include frequency, provider and output dir, check with:
    >     ./gsm-monitor --help
  * labels capture files with frequency, provider and timestamp and cell info
  * does the recording with **gr-gsm** and **tshark**
  * filters for package details, here the used encryption algorithms
  * could be rewritten to use any **wireshark / tshark** filter. 
  * has a watchdog that restarts the SDR monitoring and filtering if either **grgsm_livemon** and/or **tshark** fail, or if not enough packages are collected in a certain time span

* ***Dockerfile:*** 
  * builds the **Docker Image** on top of an **ubuntu22.04** base image and uses more recent versions of **gnuradio** as well as [bkerler's fork](https://github.com/bkerler/gr-gsm) of **gr-gsm**
  * builds **kalibrate-rtl** and adjusts *PATH* variable 
  * creates an output directory for **gsm-monitor**
  * *ENTRYPOINT* is **gsm-monitor**

* ***gsm-monitor.service***:
  * a systemd service configuration file
  * enables autostart of monitoring for e.g. Raspberry Pi on startup
  * enables pluck-and-play monitoring on Raspberry Pis

* ***run.sh:***
  * needs a frequency as input
  * automatically builds **Docker Image** and runs **gsm-monitor** with provided frequency

* ***create-plot.py***:
  * plots usage of **A5/1**, **A5/3** and **A5/4** over time, absolute and relative
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
    * Android: ***Settings*** $\rightarrow$ ***Connections*** $\rightarrow$ ***Mobile networks*** $\rightarrow$ ***Choose your SIM card and switch to only 2G*** (potentially unsafe)
    * either use a network monitoring app or use **USSD** code **\#0011#*
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

## Setup on Raspberry Pi

Clone this repo on your Raspberry Pi or pull the docker image and run inside the container there. Runs smoothly on Raspi4's, but has trouble running on Raspi2's.
To have the monitoring run automatically on start-up, have a look at the gsm-monitor.service file. This helps you to register a systemd service in the following way:

1. Config files for systemd services are usually saved at /etc/systemd/system/<service_name.service>. So we can create a symbolic link to our config file, e.g. like
>                           ln -s path/to/gsm-monitor/gsm-monitor.service /etc/systemd/system/gsm-monitor.service

2. Make systemd reload the configuration files of the units
>                           sudo systemctl daemon-reload

3. Tell systemd to start the service automatically at boot:
>                           sudo systemctl enable gsm-monitor.service

4. To test you can run:
>                           sudo systemctl start gsm-monitor.service
and
>                           sudo systemctl status gsm-monitor.service
