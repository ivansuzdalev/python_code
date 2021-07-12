from pybrain.tools.shortcuts import buildNetwork
from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.structure import TanhLayer
import re
import pickle
import numpy as np
import matplotlib.pyplot as plt
offset1 = 10
offset2 = 15

ds = SupervisedDataSet(12, 1)

file1_array = []
file1 = open("traffic_kpoint_rez.csv", "r")

for line in file1:
    line = line.lstrip()
    file1_array.append(line)

file2_array = []
file2 = open("traffic_velocity_rez.csv", "r")

for line in file2:
    line = line.lstrip()
    file2_array.append(line)

file1.close()
file2.close()


key = 0
counter = 0
for line_f1 in file1_array:
    if (counter == 3900):
        break
    counter = counter + 1
    line_f1 = line_f1.lstrip()
    f1_line_array = line_f1.split(",")

    line_f2 = file2_array[key]
    f2_line_array = line_f2.split(",")

    el0 = float(f1_line_array[0]) / 100
    #el0 = 0
    el2 = float(f1_line_array[2 + offset1]) * 60
    el3 = float(f1_line_array[3 + offset1]) * 60
    el4 = float(f1_line_array[4 + offset1]) * 60
    el5 = float(f1_line_array[5 + offset1]) * 60
    el6 = float(f1_line_array[6 + offset1]) * 60

    el7 = float(f2_line_array[2 + offset1])
    el8 = float(f2_line_array[3 + offset1])
    el9 = float(f2_line_array[4 + offset1])
    el10 = float(f2_line_array[5 + offset1])
    el11 = float(f2_line_array[6 + offset1])
    el12 = float(f2_line_array[7 + offset1])

    rez = float(f1_line_array[7 + offset1]) * 60
    ds.addSample([el0, el2, el3, el4, el5, el6, el7, el8, el9, el10, el11, el12], rez)
    key = key + 1
file1.close()
file2.close()


out = open("out.csv", "w")
#net = buildNetwork(6, 700, 50, 1, hiddenclass=TanhLayer)
net = buildNetwork(12, 200, 10, 1, 1)

print(net['in'])
print(net['hidden0'])
print(net['hidden1'])
print(net['out'])

trainer = BackpropTrainer(net, learningrate=0.001, momentum=0.9, verbose=True)
trainer.trainOnDataset(ds, 20)
trainer.testOnData(verbose=True)

key = 0

for line_f1 in file1_array:
    line_f1 = line_f1.lstrip()
    f1_line_array = line_f1.split(",")
    line_f2 = file2_array[key]
    f2_line_array = line_f2.split(",")

    el0 = float(f1_line_array[0]) / 100
    #el0 = 0
    el2 = float(f1_line_array[2 + offset2]) * 60
    el3 = float(f1_line_array[3 + offset2]) * 60
    el4 = float(f1_line_array[4 + offset2]) * 60
    el5 = float(f1_line_array[5 + offset2]) * 60
    el6 = float(f1_line_array[6 + offset2]) * 60

    el7 = float(f2_line_array[2 + offset2])
    el8 = float(f2_line_array[3 + offset2])
    el9 = float(f2_line_array[4 + offset2])
    el10 = float(f2_line_array[5 + offset2])
    el11 = float(f2_line_array[6 + offset2])
    el12 = float(f2_line_array[7 + offset2])


    rez = float(f1_line_array[7 + offset2]) * 60

    result1 = net.activate([el0, el2, el3, el4, el5, el6, el7, el8, el9, el10, el11, el12])

    out.write(str(el0))
    out.write(",")
    out.write(str(el2))
    out.write(",")
    out.write(str(el3))
    out.write(",")
    out.write(str(el4))
    out.write(",")
    out.write(str(el5))
    out.write(",")
    out.write(str(el6))
    out.write(",")
    out.write(str(el7))
    out.write(",")
    out.write(str(rez))
    out.write(",")
    out.write(result1.astype('|S10'))
    out.write("\n")
    key = key + 1
out.close()


