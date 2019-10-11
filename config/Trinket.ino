#include <CapacitiveSensor.h>
#include <EEPROM.h>

#define MAX_LONG               2147483647
#define POLLING_DELAY          10

#define SWITCH_OUTPUT          1
#define SWITCH_TRIG_OUT        2
#define SWITCH_TRIG_IN         0
#define SWITCH_CALIBRATE       4

#define CS_DONE                0
#define CS_INITIALIZE          1
#define CS_PRE_CAL_OFF         2
#define CS_CAL_OFF             3
#define CS_PRE_CAL_ON          4
#define CS_CAL_ON              5
#define CS_FINISH_UP           6
#define CS_FAILED              7
  
#define PHASE_INITIALIZE       0
#define PHASE_PRE_CAL_OFF      (2000 / POLLING_DELAY)
#define PHASE_CAL_OFF          (PHASE_PRE_CAL_OFF + (3000 / POLLING_DELAY))
#define PHASE_PRE_CAL_ON       (PHASE_CAL_OFF     + (2000 / POLLING_DELAY))
#define PHASE_CAL_ON           (PHASE_PRE_CAL_ON  + (3000 / POLLING_DELAY))
#define PHASE_FINISH_UP        (PHASE_CAL_ON      + (2000 / POLLING_DELAY))
#define PHASE_FAILED           (PHASE_FINISH_UP   + (2000 / POLLING_DELAY))

class CSwitch
{
  protected:
    CapacitiveSensor *sensor;
    long     reading;
    long     trigger;
    int      numTimes;
    int      times;
    int      oldState;
    uint8_t  output;
  
  public:
    CSwitch( uint8_t s, uint8_t r, uint8_t o, int t=5 )
    {
      sensor = new CapacitiveSensor( s, r );
      pinMode( o, OUTPUT );      
      output = o;
      numTimes = t;
      times = t;
      oldState = 0;
      
      trigger = readLong( 0 );
    }

    int poll()
    {
      // Check for calibration switch or if we are already trying to calibrate
      if( digitalRead( SWITCH_CALIBRATE ))
      {
        // Wait for trailing edge to begin calibration
        while( digitalRead( SWITCH_CALIBRATE ));
        cs_state = CS_INITIALIZE;
        return -1;
      }
      if( cs_state )
      {
        if( calibrate())
          return -1;
        oldState = 0;
        times = numTimes;
      }
        
      // Perform actual readings
      reading = sensor->capacitiveSensor(30);
      int newState = reading > trigger;
      if( newState != oldState )
      {
        times = numTimes;
        oldState = newState;
      }
      else if( times < 0 )
      {
        digitalWrite( output, newState );
        return newState;
      }
      else
        times--;
      return -1;
    }
    
  private:
    int cs_state;
    int cal_counter;
    int blinker;
    long off_low_reading;
    long off_high_reading;
    long on_low_reading;
    long on_high_reading;
    
    int calibrate()
    {
      switch( cs_state )
      {
        case CS_INITIALIZE:
          digitalWrite( output, LOW );
          cal_counter = 0;
          blinker = 0;
          on_low_reading = off_low_reading = MAX_LONG;
          on_high_reading = off_high_reading = 0;
          cs_state = CS_PRE_CAL_OFF;
          break;
          
        case CS_PRE_CAL_OFF:
          digitalWrite( output, (blinker++ / 16) % 2 );
          if( cal_counter > PHASE_PRE_CAL_OFF )
          {
            sensor->reset_CS_AutoCal();
            digitalWrite( output, blinker=0 );
            cs_state = CS_CAL_OFF;
          }
          break;

        case CS_CAL_OFF:
          reading = sensor->capacitiveSensor(30);
          if( reading > off_high_reading ) off_high_reading = reading;
          if( reading < off_low_reading )  off_low_reading  = reading;
          if( cal_counter > PHASE_CAL_OFF )
            cs_state = CS_PRE_CAL_ON;
          break;

        case CS_PRE_CAL_ON:
          digitalWrite( output, (blinker++ / 25) % 2);
          if( cal_counter > PHASE_PRE_CAL_ON )
          {
            digitalWrite( output, blinker = 0 );
            cs_state = CS_CAL_ON;
          }
          break;
          
        case CS_CAL_ON:
          reading = sensor->capacitiveSensor(30);
          if( reading > on_high_reading ) on_high_reading = reading;
          if( reading < on_low_reading )  on_low_reading  = reading;
          if( cal_counter > PHASE_CAL_ON )
            cs_state = CS_FINISH_UP;
          break;
          
        case CS_FINISH_UP:
          digitalWrite( output, HIGH );
          if( cal_counter > PHASE_FINISH_UP )
          {
            // If there is any range overlap, calibration failed
            if( on_low_reading <= off_high_reading )
              cs_state = CS_FAILED;
            else
            {
              trigger = off_high_reading + ((on_low_reading - off_high_reading) * 4) / 5;
              writeLong( 0, trigger );
              digitalWrite( output, LOW );
              cs_state = CS_DONE;
            }
          }
          break;
          
        case CS_FAILED:
          digitalWrite( output, (blinker++ / 8) % 2 );
          if( cal_counter > PHASE_FAILED )
            cs_state = CS_INITIALIZE;          
          break;        
      }
      ++cal_counter;
      return( cs_state != CS_DONE );
    }

    void writeLong(uint32_t address, long v )
    {
      EEPROM.write(address,   (uint8_t) ((v >> 24) & 0xff ));
      EEPROM.write(address+1, (uint8_t) ((v >> 16) & 0xff ));
      EEPROM.write(address+2, (uint8_t) ((v >>  8) & 0xff ));
      EEPROM.write(address+3, (uint8_t) ((v >>  0) & 0xff ));
    }
    
    long readLong(uint32_t address )
    {
      return((((long) EEPROM.read(address)) << 24) | (((long) EEPROM.read(address+1)) << 16) | (((long) EEPROM.read(address+2)) << 8) | EEPROM.read(address+3));
    }
};

CSwitch Switch = CSwitch( SWITCH_TRIG_OUT, SWITCH_TRIG_IN, SWITCH_OUTPUT, 5 );

void setup()
{
  pinMode( SWITCH_CALIBRATE, INPUT );
}

void loop()
{
  int state = Switch.poll();
  delay( POLLING_DELAY );  
}




