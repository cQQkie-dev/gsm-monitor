# 2G Network Traffic Monitoring

The goal of this project is to anonymously gather data on how much either A5/1 or A5/3 algorithms are still in use in 2G networks.
For the data collection process and RTL-SDR (or any SDR) is used as it is the most plug-and-play option.  
The heavy lifting is done by the gr-gsm software suite, especially grgsm_livemon / grgsm_livemon_headless, by [ptrkrysik](https://github.com/ptrkrysik/gr-gsm).

# Installation, Setup

Depending on your OS and available gnuradio version, you will need different versions of gr-gsm:
* gnuradio $\leq$ 3.8: [ptrkrysik's main branch](https://github.com/ptrkrysik/gr-gsm)
* gnradio $ > $ 3.8: Try [bkerler's fork](https://github.com/bkerler/gr-gsm) or [velichkov's fork](https://github.com/bkerler/gr-gsm), which work for up to gnuradio 3.11
                
