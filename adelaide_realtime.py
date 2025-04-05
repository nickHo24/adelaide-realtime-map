import streamlit as st
import requests
import folium
from streamlit_folium import folium_static
from google.transit import gtfs_realtime_pb2
from google.protobuf import message
import time

# ⚙️ Streamlit UI configuration
st.set_page_config(page_title="Adelaide Realtime Map", layout="wide")
st.title("🚍 Real-time Bus/Tram Map – Adelaide")

# 📡 Fetch vehicle positions via GTFS Realtime (protobuf)
def get_vehicle_positions():
    feed = gtfs_realtime_pb2.FeedMessage()
    try:
        url = "https://gtfs.adelaidemetro.com.au/v1/realtime/vehicle_positions"
        response = requests.get(url)
        feed.ParseFromString(response.content)

        vehicles = []
        for entity in feed.entity:
            if entity.HasField('vehicle'):
                v = entity.vehicle
                vehicles.append({
                    "id": v.vehicle.id,
                    "route": v.trip.route_id,
                    "lat": v.position.latitude,
                    "lon": v.position.longitude
                })
        return vehicles

    except message.DecodeError as e:
        st.error(f"❌ Failed to decode GTFS Realtime data: {e}")
        return []

# 🗺️ Draw vehicle locations on Folium map
def plot_map(vehicles):
    m = folium.Map(
        location=[-34.9285, 138.6007],
        zoom_start=12,
        control_scale=True,
        width="100%",
        height="100%"
    )

    for v in vehicles:
        folium.Marker(
            location=[v["lat"], v["lon"]],
            popup=f"🚍 Vehicle: {v['id']}<br>📍 Route: {v['route']}",
            icon=folium.Icon(color="blue", icon="bus", prefix="fa")
        ).add_to(m)

    return m

# 🔁 Auto-refresh every 15 seconds using loop
placeholder = st.empty()

while True:
    with placeholder.container():
        vehicle_data = get_vehicle_positions()
        if vehicle_data:
            st.success(f"🚀 Showing {len(vehicle_data)} active vehicles.")
            m = plot_map(vehicle_data)
            folium_static(m, width=1400, height=800)
        else:
            st.warning("🚫 No vehicle data available.")

    time.sleep(15)
    