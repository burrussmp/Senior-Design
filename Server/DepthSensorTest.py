from DepthSensor import Sensor
import time
import csv
s = Sensor()
csvfile = open("PressureTest.csv", "w")
writer=csv.writer(csvfile)
pressures = ["pressures"]
temps = ["temps"]
trials = 10
i = 0
while(i<trials):
    press, temp = s.read()
    pressures.append(press)
    temps.append(temp)
    #print("Pressure: %f"%press)
    #meterOfWaterPerMilliBar = 0.01019744288922
    #depth = press*meterOfWaterPerMilliBar
    #print("Depth=%f m, temp=%f C"% (depth, temp))
    i = i + 1
    time.sleep(1)
writer.writerow(temps)
writer.writerow(pressures)
csvfile.close()    


