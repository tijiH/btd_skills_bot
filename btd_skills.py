from time import sleep

from pynput.keyboard import Key, Controller

keyboard = Controller()

while True:
    sleep(5)
    keyboard.press('&')
    keyboard.release('&')

    sleep(0.1)
    keyboard.press('é')
    keyboard.release('é')

    sleep(0.1)
    keyboard.press('\"')
    keyboard.release('\"')

    sleep(0.1)
    keyboard.press('\'')
    keyboard.release('\'')

    sleep(0.1)
    keyboard.press('(')
    keyboard.release('(')

    sleep(0.1)
    keyboard.press('-')
    keyboard.release('-')

    sleep(0.1)
    keyboard.press('è')
    keyboard.release('è')

    sleep(0.1)
    keyboard.press('_')
    keyboard.release('_')

    sleep(0.1)
    keyboard.press('ç')
    keyboard.release('ç')

    sleep(0.1)
    keyboard.press('à')
    keyboard.release('à')

    sleep(0.1)
    keyboard.press('=')
    keyboard.release('=')

    sleep(0.1)
    keyboard.press(';')
    keyboard.release(';')

