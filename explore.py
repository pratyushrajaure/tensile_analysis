#This file was made in practice session

import pandas as pd
import matplotlib.pyplot as plt

data1 = pd.read_csv("data/raw/test_01.csv")
data2 = pd.read_csv("data/raw/test_02.csv")

#print(data2.describe())

def plottingfunc(dis, force, name):
    plt.plot(dis, force, label=name)
    plt.xlabel("Displacement")
    plt.ylabel("force")
    plt.title("Force vs Displacement")
    plt.legend()
    plt.grid()
    plt.show()


plottingfunc(data1["displacement_m"], data1["force_N"], "Test 1")
plottingfunc(data2["displacement_mm"], data2["force_N"], "Test 2")
