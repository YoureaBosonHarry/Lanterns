import board
from flask import Flask
from flask import request
import multiprocessing
import neopixel
import numpy as np
import os
import socket
import time

# Initiate flask app
app = Flask(__name__)

num_leds = int(os.environ.get("NUMLEDS"))
num_lanterns = int(os.environ.get("NUM_LANTERNS", 4))
num_leds_per_lantern = int(os.environ.get("NUM_LEDS_PER_LANTERNS", 8))

global current_pattern
global pixels
global process
current_pattern = None
process = None

# Configure and initialize NeoPixels, run "pinout" on command line to view viable pins
pixels = neopixel.NeoPixel(board.D18, num_leds, auto_write=False)

def clear_pixels():
    pixels.fill((0, 0, 0))
    pixels.show()

def fade(end_r, end_g, end_b, freq):
    samples = np.linspace(0, 1, 255, endpoint=False)
    signal = np.absolute(np.sin(2 * np.pi * freq * samples))
    for i in signal:
        pixels.fill((int(end_r*i), int(end_g*i), int(end_b*i)))
        pixels.show()
        time.sleep(0.01)

def solid(r, g, b):
    pixels.fill((r, g, b))
    pixels.show()
    time.sleep(2)

def candy_cane(r, g, b, wait):
    for i in range(num_leds):
        if i % 2 == 0:
            pixels[i] = ((r, 0, 0))
        else:
            pixels[i] = ((r, g, b))
    pixels.show()
    time.sleep(wait)
    for i in range(num_leds):
        if i % 2 == 0:
            pixels[i] = ((r, g, b))
        else:
            pixels[i] = ((r, 0, 0))
    pixels.show()
    time.sleep(wait)

def twinkle(r, g, b, freq):
    on_leds = np.random.choice(2, num_leds)
    for i in range(num_leds):
        if on_leds[i] == 0:
            pixels[i] = ((0, 0, 0))
        else:
            pixels[i] = ((np.random.randint(0, r if r > 0 else 1), np.random.randint(0, g if g > 0 else 1), np.random.randint(0, b if b > 0 else 1)))
    pixels.show()
    time.sleep(freq)

def blink(r, g, b, freq):
    current_lantern = 1
    j = 0
    for i in range(num_lanterns):
       while j < (current_lantern * num_leds_per_lantern):
           pixels[j] = ((r, g, b))
           j += 1
       pixels.show()
       time.sleep(freq)
       current_lantern += 1
       clear_pixels()

def flame(r, g, b):
    for i in range(num_leds):
        intensity = np.random.randint(0, 100)
        pixels[i] = ((255, intensity, 0))
    pixels.show()
    time.sleep(0.2)

def select_pattern(r, g, b, wait):
    while current_pattern == 'fade':
        fade(r, g, b, wait)
    while current_pattern == 'solid':
        solid(r, g, b)
    while current_pattern == 'blink':
        blink(r, g, b, wait)
    while current_pattern == 'candy_cane':
        candy_cane(r, g, b, wait)
    while current_pattern == 'twinkle':
        twinkle(r, g, b, wait)
    while current_pattern == 'flame':
        flame(r, g, b)
    clear_pixels()

@app.route('/change_pattern', methods=['POST'])
def neopixel_callback():
    global current_pattern
    global process
    if process:
        process.terminate()
    pattern = request.args.get('pattern')
    hex = request.args.get('hex_color')
    freq = request.args.get('frequency')
    r, g, b = tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
    current_pattern = pattern
    process = multiprocessing.Process(target=select_pattern, args=(r, g, b, float(freq),))
    process.start()
    return "OK"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)
