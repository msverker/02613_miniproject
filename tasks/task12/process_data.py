import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys

ID = sys.argv[1]
df_list = []
for i in range(1, 10+1):
    df = pd.read_csv(f"task12_{ID}_{2}.out")
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

""" Copied from: cat task12_24858166_*.err | grep real | awk '{gsub(/real\s+|s/, ""); split($1, time_parts, "m"); minutes = time_parts[1]; seconds_ms = time_parts[2]; split(seconds_ms, ms_parts, "."); seconds = ms_parts[1]; milliseconds = ms_parts[2]; total_seconds = (minutes * 60) + seconds + (milliseconds / 1000); printf "%.3f,\n", total_seconds}'
182.003,
187.784,
175.019,
181.643,
185.057,
187.211,
183.431,
182.921,
186.046,
193.700,
"""

times = np.array([
    182.003,
    187.784,
    175.019,
    181.643,
    185.057,
    187.211,
    183.431,
    182.921,
    186.046,
    193.700,
])
print(f"Total time: {np.sum(times)} s, {np.sum(times) / 60} min")