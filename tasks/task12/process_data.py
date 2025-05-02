import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys

ID = sys.argv[1]
df_list = []
for i in range(1, 10+1):
    df = pd.load_csv(f"task12_{ID}_{2}.out")
    df_list.append(df)

df = pd.concat(df_list, ignore_index=True, sort=False)
mean_temps = df[" mean_temp"] # Gotta love spaces...

plt.figure()
plt.hist(mean_temps)
plt.xlabel("Temperatures")
plt.savefig("mean_temp_histogram.png")
print(f"Average mean temperature: {np.mean(mean_temps)}")

std_temps = df[" std_temp"]
print(f"Average std temperature: {np.mean(std_temps)}")

pct_above_18_array = df[" pct_above_18"]
number_of_buildings_50_pct_above_18 = sum([x >= 50 for x in pct_above_18_array])
print(f"Number of buildings 50% above 18: {number_of_buildings_50_pct_above_18}")

pct_below_15_array = df[" pct_below_15"]
number_of_buildings_50_pct_below_15 = sum([x >= 50 for x in pct_below_15_array])
print(f"Number of buildings 50% below 15: {number_of_buildings_50_pct_below_15}")

""" Copied from: cat task12_24858166_*.err | grep "real"
real    3m2.003s
real    3m7.784s
real    2m55.019s
real    3m1.643s
real    3m5.057s
real    3m7.211s
real    3m3.431s
real    3m2.921s
real    3m6.046s
real    3m13.700s
"""

times = np.array([
    3 * 60 + 2, 
    3 * 60 + 7.7, 
    2 * 60 + 55,
    3 * 60 + 1.6,
    3 * 60 + 5,
    3 * 60 + 7.2,
    3 * 60 + 3.4,
    3 * 60 + 2.9,
    3 * 60 + 6,
    3 * 60 + 13.7
])
print(f"Total time: {np.sum(times)}")