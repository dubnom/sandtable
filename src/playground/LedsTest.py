from LedsDS import Leds
from time import sleep 

LEDS_MAX = 144


def main():
    leds = Leds(144,36,36,None,None)            # For LedsDS and one strip
    while True:
        for degree in range( 0, 360, 1 ):
            for led in range( 0, LEDS_MAX ):
                leds.set( led, leds.HSB( led * 5.0 + degree, 100, 50 ))
            leds.refresh()
            sleep( 1.0 / 120.0 )
    leds.close()

if __name__ == '__main__':
    main()

