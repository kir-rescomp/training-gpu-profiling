#!/usr/bin/env python3

# If you are running this as a Python script and not a notebook,
# kaleido==0.2.1 is required to suppress number of warning related to Chrome back-end
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# import the CSV file generated at the end of the Slurm script. It should be on the submission directory
# in this example, filename is "gpu-stats-15140945.csv

fn = "gpu-stats-15140945.csv"
title = "My GPU Job"
output_file = fn.rsplit(".", 1)[0]  # "gpu-stats-15126097"

# prepare dataframe
df = pd.read_csv(fn)
df.rename(columns=lambda c: c.strip(), inplace=True)
df.dropna(inplace=True)
df["sw_thermal_slowdown"] = df["clocks_event_reasons.sw_thermal_slowdown"].apply(lambda x: 0 if "Not" in x else 1)
df["time"] = pd.to_datetime(df["timestamp"])

# one trace per GPU
gpus = df["uuid"].unique()

cols_to_plot = [
    "utilization.gpu [%]",
    "utilization.memory [%]",
    "memory.used [MiB]",
    "temperature.gpu",
    "sw_thermal_slowdown",
    "clocks.current.sm [MHz]",
    "power.draw [W]",
]

fig = make_subplots(rows=len(cols_to_plot), cols=1, subplot_titles=cols_to_plot, shared_xaxes=True)

for row0, measure in enumerate(cols_to_plot):
    for gpu in gpus:
        gdf = df[df["uuid"] == gpu]
        fig.append_trace(go.Scatter(
            x=gdf["time"],
            y=gdf[measure],
            name=gpu[-8:],           # last 8 chars of UUID is readable enough
            legendgroup=gpu,
            showlegend=(row0 == 0),  # only show legend once
        ), row=row0+1, col=1)

fig.update_layout(
    height=220 * len(cols_to_plot),
    width=1100,
    title_text=title,
    template="plotly_dark",
    legend=dict(orientation="h", y=1.02, x=1, xanchor="right"),
)
fig.update_traces(line=dict(width=1))

for a in fig.layout.annotations:
    if a["text"] == "utilization.gpu [%]":
        a["text"] = "utilization.gpu [%%] (mean = %.1f %%)" % (df["utilization.gpu [%]"].mean(),)

fig.write_html(output_file + ".html")
fig.write_image(output_file + ".png")
print(f"Saved {output_file}.html and {output_file}.png")
