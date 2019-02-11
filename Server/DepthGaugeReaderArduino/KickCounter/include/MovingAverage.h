#ifndef MOVINGAVERAGE_H
#define MOVINGAVERAGE_H


#include "arduino.h"
#include <stdint.h>
#include "queue.h"
class MovingAverage{
  int MAXSIZEOFQ = 60;    
    public:
        MovingAverage();
        void addElement(double element);
        double getStandardDeviation();

    private:
        double sumElements;
        double mean;
        double std;
        queue myQ;
};
#endif