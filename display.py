import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pyvista as pv
import pandas as pd

st.title("📦 Hoarding Detection Dashboard")

# Load stuff 
point_cloud_file = pv.read("pointcloud.ply")    # PLY file
summary_path = "summary.csv"                    # CSV file 
summary_df = pd.read_csv(summary_path, parse_dates=["timestamp"])
latest = summary_df.iloc[-1]

# Create interactive point cloud 
points = np.array(point_cloud_file.points)
pointcloud = go.Figure(data=[go.Scatter3d(         # Create the 3D scatter plot
    x=points[:, 0],
    y=points[:, 1],
    z=points[:, 2],
    mode='markers',
    marker=dict(
        size=1,  
        color=points[:, 2],  # Color by z-coordinate
        colorscale='Viridis_r',  # You can change this to other scales like 'Jet', 'Hot', etc.
        colorbar=dict(title='Z value'),  # Optional: add colorbar
    )
)])

pointcloud.update_layout(
    scene=dict(
        aspectmode='data',  # Keeps the aspect ratio
        xaxis_title='X',
        yaxis_title='Y',
        zaxis_title='Z',
        # Optional: set camera position
        camera=dict(
            eye=dict(x=1.5, y=1.5, z=1.5)
        )
    ),
    width=800,
    height=600,
    margin=dict(l=0, r=0, b=0, t=0)  # Tight margins
)

# Show interactive point cloud 
st.write(f"Last Scan at {latest['timestamp']}")
st.plotly_chart(pointcloud, use_container_width=True) # Display 

# Show most recent data
col1, col2 = st.columns(2)
col1.metric("Number of Floor Points", value=latest["floor_point_count"])
col2.metric("% Change", f"{latest['floor_pct_change']:.2f}%")

# Layout in 2 columns for Stack Metrics
col3, col4 = st.columns(2)
col3.metric("Number of Tall Stacks (>1.5m)", value=latest["tall_tile_count"])
col4.metric("% Change", f"{latest['stack_pct_change']:.2f}%")

# Show alert if triggered
if latest["floor_alert"]:
    st.error(f"🚨 ALERT: Significant reduction in floor space detected ({abs(latest['floor_pct_change']):.2f}%)")
if latest["stack_alert"]:
    st.error(f"🚨 ALERT: Significant increase in tall clutter detected ({abs(latest['stack_pct_change']):.2f}%)")
else:
    st.success("✅ No abnormal changes")

# Show charts
st.subheader("Floor Point Count Over Time")
st.line_chart(summary_df.set_index("timestamp")["floor_point_count"])

st.subheader("Tall Stack Count Over Time")
st.line_chart(summary_df.set_index("timestamp")["tall_tile_count"])
