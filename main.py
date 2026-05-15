"""
STAC Satellite Explorer — Streamlit Web App
============================================
Run locally:   streamlit run stac_app.py
Deploy free:   https://streamlit.io/cloud  (connect your GitHub repo)

pip install streamlit pystac-client planetary-computer rasterio numpy matplotlib
"""

import os
import sys
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from datetime import date, timedelta
import warnings
warnings.filterwarnings("ignore")

# ── Import mapping libraries ───────────────────────────────────────────────────
try:
    import folium
    from streamlit_folium import st_folium
    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False

# ── Fix PROJ database path on Windows ───────────────────────────────────────
try:
    import pyproj
    proj_dir = os.path.dirname(pyproj.__file__)
    proj_data_dir = os.path.join(proj_dir, 'proj', 'data')
    os.environ['PROJ_LIB'] = proj_data_dir
except Exception:
    pass

try:
    import pyproj.datadir
    os.environ['PROJ_LIB'] = pyproj.datadir.get_data_dir()
except Exception:
    pass

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="STAC Satellite Explorer",
    page_icon="🛰️",
    layout="wide",
)

st.markdown("""
<style>
    .stApp { background: #ffffff; }
    h1, h2, h3, p, label { color: #000000 !important; }
    .metric-card {
        background: #f5f5f5;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    .metric-val { font-size: 1.8rem; font-weight: 600; }
    .metric-label { font-size: 0.75rem; color: #666666; margin-top: 4px; }
    .scene-badge {
        display: inline-block;
        background: #f0f0f0;
        border: 1px solid #d0d0d0;
        border-radius: 6px;
        padding: 4px 10px;
        font-size: 0.75rem;
        color: #666666;
        margin: 2px;
    }
    div[data-testid="stSidebar"] { background: #f9f9f9; border-right: 1px solid #e0e0e0; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar — search parameters ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛰️ Search parameters")
    st.markdown("---")

    PRESETS = {
        "Sahara Desert, DZ": {"bbox": (2.5, 28.0, 3.5, 29.0)},
        "Vienna, AT": {"bbox": (16.2, 48.1, 16.6, 48.3)},
        "Custom": {"bbox": None},
    }

    preset = st.selectbox("Location preset", list(PRESETS.keys()))
    bbox_default = PRESETS[preset]["bbox"]

    st.markdown("**Bounding box** *(lon/lat)*")
    col1, col2 = st.columns(2)
    if bbox_default:
        west  = col1.number_input("West lon",  value=float(bbox_default[0]), step=0.01, format="%.2f")
        south = col1.number_input("South lat", value=float(bbox_default[1]), step=0.01, format="%.2f")
        east  = col2.number_input("East lon",  value=float(bbox_default[2]), step=0.01, format="%.2f")
        north = col2.number_input("North lat", value=float(bbox_default[3]), step=0.01, format="%.2f")
    else:
        west  = col1.number_input("West lon",  value=-120.0, step=0.01)
        south = col1.number_input("South lat", value=38.0,   step=0.01)
        east  = col2.number_input("East lon",  value=-119.5, step=0.01)
        north = col2.number_input("North lat", value=38.5,   step=0.01)

    st.markdown("**Date range**")
    d_from = st.date_input("From", value=date(2023, 7, 1))
    d_to   = st.date_input("To",   value=date(2023, 9, 30))

    max_cloud = st.slider("Max cloud cover (%)", 0, 50, 10)
    max_items = st.slider("Max scenes to return", 1, 20, 5)

    collection = st.selectbox(
        "STAC collection",
        ["sentinel-2-l2a", "landsat-c2-l2", "cop-dem-glo-30"],
    )

    search_btn = st.button("🔍  Search scenes", type="primary", use_container_width=True)

# ── Main panel ────────────────────────────────────────────────────────────────
st.title("🛰️ STAC Satellite Explorer")
st.caption("Search and visualise satellite imagery from Spatiotemporal Asset Catalogs (STAC)")

if not search_btn:
    st.info("Configure your search in the sidebar, then click **Search scenes**.")
    st.stop()

# ── STAC search ───────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def search_stac(bbox, date_from, date_to, cloud_max, n_items, collection):
    try:
        from pystac_client import Client
        import planetary_computer

        catalog = Client.open(
            "https://planetarycomputer.microsoft.com/api/stac/v1",
            modifier=planetary_computer.sign_inplace,
        )
        search = catalog.search(
            collections=[collection],
            bbox=bbox,
            datetime=f"{date_from}/{date_to}",
            query={"eo:cloud_cover": {"lt": cloud_max}},
            sortby="-datetime",
            max_items=n_items,
        )
        return list(search.items()), None
    except Exception as e:
        return None, str(e)


bbox_tuple = (west, south, east, north)

with st.spinner("Connecting to Planetary Computer STAC…"):
    items, error = search_stac(
        bbox_tuple, str(d_from), str(d_to), max_cloud, max_items, collection
    )

if error:
    st.error(f"STAC search failed: {error}")
    st.info(
        "**Tip:** install dependencies with:\n"
        "```\npip install pystac-client planetary-computer rasterio\n```"
    )
    st.stop()

if not items:
    st.warning("No scenes found for your criteria. Try widening the date range or cloud cover limit.")
    st.stop()

st.success(f"Found **{len(items)}** scene(s) with ≤{max_cloud}% cloud cover")

# ── Scene picker ──────────────────────────────────────────────────────────────
scene_labels = [
    f"{it.datetime.strftime('%Y-%m-%d')}  |  cloud {it.properties.get('eo:cloud_cover', '?'):.1f}%  |  {it.id[:30]}…"
    for it in items
]
chosen_idx = st.selectbox("Select scene", range(len(items)), format_func=lambda i: scene_labels[i])
item = items[chosen_idx]

with st.expander("Scene metadata"):
    cols = st.columns(3)
    cols[0].metric("Date", item.datetime.strftime("%Y-%m-%d"))
    cols[1].metric("Cloud cover", f"{item.properties.get('eo:cloud_cover', '?'):.1f}%")
    cols[2].metric("Platform", item.properties.get("platform", "Sentinel-2"))
    st.write("**Available bands:**", ", ".join(item.assets.keys()))

# ── Scene visualization ───────────────────────────────────────────────────────
st.markdown("---")

# Show preview image if available
if "visual" in item.assets:
    st.subheader("📷 Scene Preview")
    try:
        preview_url = item.assets["visual"].href
        st.image(preview_url, use_container_width=True)
    except Exception:
        st.info("Preview image not available")

# Show thumbnail or asset details
st.subheader("📊 Scene Assets")
asset_cols = st.columns(min(3, len(item.assets)))
for idx, (asset_name, asset) in enumerate(item.assets.items()):
    with asset_cols[idx % len(asset_cols)]:
        st.write(f"**{asset_name}**")
        if asset.media_type:
            st.caption(f"Type: {asset.media_type}")
        st.button("View Asset", key=f"asset_{asset_name}", disabled=True)

# ── Mock indices dashboard ────────────────────────────────────────────────────
st.markdown("---")
st.subheader("📈 Simulated Analysis Metrics")

# Generate mock data for visualization
np.random.seed(42)
ndvi = np.random.normal(0.4, 0.2, (100, 100))
ndvi = np.clip(ndvi, -1, 1)
ndwi = np.random.normal(0.1, 0.25, (100, 100))
ndwi = np.clip(ndwi, -1, 1)
rgb = np.random.rand(100, 100, 3)

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("NDVI mean", f"{ndvi.mean():.3f}")
m2.metric("NDVI max", f"{ndvi.max():.3f}")
m3.metric("NDWI mean", f"{ndwi.mean():.3f}")
m4.metric("Veg cover", f"{(ndvi > 0.3).mean() * 100:.1f}%")
m5.metric("Water cover", f"{(ndwi > 0.0).mean() * 100:.1f}%")

st.markdown("---")

# ── Visualisation ─────────────────────────────────────────────────────────────
def percentile_clip(arr, lo=2, hi=98):
    vmin, vmax = np.percentile(arr, lo), np.percentile(arr, hi)
    return np.clip((arr - vmin) / (vmax - vmin + 1e-6), 0, 1)
def percentile_clip(arr, lo=2, hi=98):
    vmin, vmax = np.percentile(arr, lo), np.percentile(arr, hi)
    return np.clip((arr - vmin) / (vmax - vmin + 1e-6), 0, 1)

rgb = np.dstack([
    percentile_clip(np.random.rand(100, 100)),
    percentile_clip(np.random.rand(100, 100)),
    percentile_clip(np.random.rand(100, 100)),
])

fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.patch.set_facecolor("#ffffff")

plots = [
    (rgb,  None,       None,          (-0.2, 0.8), "True colour (RGB)"),
    (ndvi, "RdYlGn",   None,          (-0.2, 0.8), "NDVI  —  vegetation index"),
    (ndwi, "RdYlBu",   None,          (-0.4, 0.6), "NDWI  —  water index"),
]

for ax, (img, cmap, norm, vr, title) in zip(axes, plots):
    ax.set_facecolor("#ffffff")
    if cmap:
        im = ax.imshow(img, cmap=cmap, vmin=vr[0], vmax=vr[1])
        cbar = plt.colorbar(im, ax=ax, shrink=0.8, pad=0.02)
        cbar.ax.yaxis.set_tick_params(color="black")
        plt.setp(cbar.ax.yaxis.get_ticklabels(), color="black", fontsize=9)
    else:
        ax.imshow(img)
    ax.set_title(title, color="black", fontsize=12, pad=8)
    ax.axis("off")

fig.suptitle(
    f"{collection.upper()}  ·  {item.datetime.strftime('%Y-%m-%d')}",
    color="black", fontsize=13, y=1.02,
)
plt.tight_layout()
st.pyplot(fig, use_container_width=True)

# ── Histogram ────────────────────────────────────────────────────────────────
with st.expander("Index histograms"):
    fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 3))
    fig2.patch.set_facecolor("#ffffff")
    for ax in (ax1, ax2):
        ax.set_facecolor("#f5f5f5")
        ax.tick_params(colors="black")
        for spine in ax.spines.values():
            spine.set_edgecolor("#d0d0d0")

    ax1.hist(ndvi.ravel(), bins=60, color="#3fb950", alpha=0.85, range=(-0.5, 1.0))
    ax1.set_title("NDVI distribution", color="black")
    ax1.axvline(0.3, color="black", linestyle="--", linewidth=0.8, label="veg threshold")
    ax1.legend(labelcolor="black", framealpha=0)

    ax2.hist(ndwi.ravel(), bins=60, color="#58a6ff", alpha=0.85, range=(-0.8, 0.8))
    ax2.set_title("NDWI distribution", color="black")
    ax2.axvline(0.0, color="black", linestyle="--", linewidth=0.8, label="water threshold")
    ax2.legend(labelcolor="black", framealpha=0)

    st.pyplot(fig2, use_container_width=True)

# ── Download output ───────────────────────────────────────────────────────────
import io
buf = io.BytesIO()
fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor="#ffffff")
st.download_button(
    "⬇️  Download visualisation (PNG)",
    data=buf.getvalue(),
    file_name=f"stac_{item.datetime.strftime('%Y%m%d')}.png",
    mime="image/png",
)

st.markdown("---")
st.caption(
    "Data: [Microsoft Planetary Computer](https://planetarycomputer.microsoft.com) · "
    "Imagery: Copernicus Sentinel-2 · "
    "Indices: NDVI (McFeeters 1996), NDWI (Gao 1996)"
)

# ── Interactive Web Map ────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("🗺️ Scene Location Map")

if HAS_FOLIUM:
    # Calculate center of bounding box
    center_lat = (south + north) / 2
    center_lon = (west + east) / 2
    
    # Create folium map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=8,
        tiles="OpenStreetMap"
    )
    
    # Add bounding box rectangle
    bbox_coords = [
        [south, west],
        [south, east],
        [north, east],
        [north, west],
        [south, west]
    ]
    
    folium.Polygon(
        bbox_coords,
        color="blue",
        fill=True,
        fillColor="blue",
        fillOpacity=0.1,
        weight=2,
        popup="Search Area",
        tooltip="Search Bounding Box"
    ).add_to(m)
    
    # Add center marker
    folium.Marker(
        location=[center_lat, center_lon],
        popup=f"Search Center<br>{center_lat:.2f}, {center_lon:.2f}",
        tooltip="Search Center",
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(m)
    
    # Try to add scene geometry if available
    if item.geometry:
        try:
            from shapely.geometry import shape
            geom = shape(item.geometry)
            
            # Add scene footprint
            if geom.geom_type == 'Polygon':
                coords = list(geom.exterior.coords)
                folium.Polygon(
                    [[lat, lon] for lon, lat in coords],
                    color="red",
                    fill=True,
                    fillColor="red",
                    fillOpacity=0.2,
                    weight=2,
                    popup=f"Scene: {item.id[:50]}",
                    tooltip=f"Scene Footprint ({item.datetime.strftime('%Y-%m-%d')})"
                ).add_to(m)
            elif geom.geom_type == 'MultiPolygon':
                for poly in geom.geoms:
                    coords = list(poly.exterior.coords)
                    folium.Polygon(
                        [[lat, lon] for lon, lat in coords],
                        color="red",
                        fill=True,
                        fillColor="red",
                        fillOpacity=0.2,
                        weight=2
                    ).add_to(m)
        except Exception:
            pass
    
    # Display map
    st_folium(m, width=1400, height=500)
    
    # Scene info
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Scene ID:** `{item.id}`")
        st.write(f"**Date:** {item.datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    with col2:
        st.write(f"**Collection:** {collection}")
        st.write(f"**Cloud Cover:** {item.properties.get('eo:cloud_cover', 'N/A'):.1f}%")

else:
    st.info(
        "📍 **Interactive map visualization** requires additional packages.\n\n"
        "Install with:\n"
        "```bash\n"
        "pip install folium streamlit-folium\n"
        "```\n\n"
        "Or if using `uv`:\n"
        "```bash\n"
        "uv add folium streamlit-folium\n"
        "```"
    )
    
    # Show basic info without map
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Scene ID:** `{item.id}`")
        st.write(f"**Date:** {item.datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    with col2:
        st.write(f"**Collection:** {collection}")
        st.write(f"**Cloud Cover:** {item.properties.get('eo:cloud_cover', 'N/A'):.1f}%")
    
    # Show bounding box info
    st.write(f"**Search Area:** West={west:.2f}, East={east:.2f}, South={south:.2f}, North={north:.2f}")
