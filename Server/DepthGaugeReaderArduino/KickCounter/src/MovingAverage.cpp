#include "MovingAverage.h"

MovingAverage::MovingAverage():
sumElements(0.0),
mean(0.0),
std(0.0),
myQ()
{
}
void MovingAverage::addElement(double element)
{
  double oldElement = 0.0;
  if (element > 20 || element < -20)
  {
    return;
  }
  if (myQ.size() == MovingAverage::MAXSIZEOFQ)
  {
    //oldElement = myQ.front();
    //std::cout << oldElement << std::endl;
    //printf("Old Element: %0.2f\n", oldElement);
    //myQ.pop();
    oldElement = myQ.dequeue();
  }
  //printf("Size: %d\n",myQ.size());
  myQ.enqueue(element);
  sumElements = element + sumElements-oldElement;
  mean = sumElements/((double)myQ.size());
  //printf("mean: %0.2f\n",mean);
}
double MovingAverage::getStandardDeviation()
{
  int index = myQ.size();
  if (index > 1){
    double variance = 0.0;
    for (int i = 0; i < index; ++i)
    {
      double element = myQ.dequeue();
      //std::cout << element << " "; 
      //printf("Element: %0.2f\n", element);
      //myQ.pop();
      variance += (element - mean)*(element-mean);
      myQ.enqueue(element);;
    }
    variance = variance / (myQ.size() - 1);
    std = sqrt(variance);
    return std;
  }
  return -1;
}