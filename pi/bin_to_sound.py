import time
import sys
import simpleaudio as sa

def play_sound(filename, dur):
    wave = sa.WaveObject.from_wave_file(filename)
    play = wave.play()
    time.sleep(dur)
    play.stop()

def bin_to_sound(bin_string):
    for val in bin_string:
        if val == '1':
            play_sound('beep-01a.wav', 0.1)
        else:
            time.sleep(0.1)



while True:
    bin_string = input('Enter Bin String: ')
    bin_to_sound(bin_string)
    

