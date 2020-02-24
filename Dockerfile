FROM arm32v7/debian

RUN apt-get update
RUN apt-get install -y build-essential python3-dev python3-pip

RUN pip3 install --upgrade pip
RUN pip3 install --upgrade setuptools
RUN pip3 install RPi.GPIO
RUN pip3 install adafruit-circuitpython-neopixel
RUN pip3 install rpi_ws281x
RUN pip3 install numpy
RUN pip3 install Flask

WORKDIR /NeoPixels

COPY . /NeoPixels

ENTRYPOINT ["python3", "NeoPixels.py"]
