#include "KickCounter.h"


KickCounter::KickCounter():
protocol("NULL"),
state("NULL"),
maxThreshold(14),
minThreshold(8),
disregardThreshold(20),
kickCount(0),
time(millis()),
timeout(3000),
movingAverage()
{
}
double KickCounter::magnitude(double x, double y, double z){
          return sqrt(x*x+y*y+z*z);
        }

void KickCounter::newState(double mag){
  if (millis() - time > timeout){
    protocol = "NULL";
    maxThreshold = 14;
    minThreshold = 8;
    state = "NULL";
    time = millis();
    return;
  }
  movingAverage.addElement(mag);
  double threshold = movingAverage.getStandardDeviation();
  if (threshold > 6 && threshold < 18){
    maxThreshold = threshold;
    minThreshold = -threshold;
  }
  if (protocol == "NULL"){
      if (mag > maxThreshold){
          protocol = "HIGHTOLOW";
          state = "HIGH";
      }
      if (mag < minThreshold){
          protocol = "LOWTOHIGH";
          state = "LOW";
      }
  }
  if (mag > disregardThreshold || mag < 0){
      return;
  }
  if (protocol == "HIGHTOLOW"){
      if (mag < minThreshold && state == "HIGH"){
          state = "LOW";
      }
      if (mag > maxThreshold && state == "LOW"){
          state = "HIGH";
          kickCount = kickCount + 1;
          time = millis();
      }
  }
  if (protocol == "LOWTOHIGH"){
      if (mag < minThreshold && state == "HIGH"){
          state = "LOW";
          kickCount = kickCount + 1;
          time = millis();
      }
      if (mag > maxThreshold && state == "LOW"){
          state = "HIGH";
      }
  }
}
int KickCounter::getKicks(){
  return kickCount;
}
