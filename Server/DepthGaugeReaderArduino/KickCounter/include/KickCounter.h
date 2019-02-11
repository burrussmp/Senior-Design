#ifndef KICKCOUNTER_H
#define KICKCOUNTER_H


#include "MovingAverage.h"
#include "Arduino.h"
class KickCounter{
    
    public:
        KickCounter();
        double magnitude(double x, double y, double z);
        void newState(double mag);
        int getKicks();

    private:
        String protocol;
        String state;
        double maxThreshold;
        double minThreshold;
        double disregardThreshold;
        int kickCount;
        unsigned long time;
        unsigned int timeout;
        MovingAverage movingAverage;
};

#endif 