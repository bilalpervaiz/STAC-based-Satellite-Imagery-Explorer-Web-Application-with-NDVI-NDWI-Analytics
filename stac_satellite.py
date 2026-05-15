"""
STAC Satellite Data Downloader
================================
Connects to a STAC catalog, searches for satellite imagery,
downloads bands, and computes NDVI & NDWI indices.

Requirements:
    pip install pystac-client rasterio numpy matplotlib requests planetary-computer
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import requests
from datetime import datetime

# ── 1. CONNECT TO A STAC CATALOG ─────────────────────────────────────────────
# We use Microsoft Planetary Computer (free, no auth needed for search)
STAC_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"

try:
    from pystac_client import Client
    import planetary_computer
    catalog = Client.open(STAC_URL, modifier=planetary_computer.sign_inplace)
    print(f"✅ Connected to: {catalog.title}")
except ImportError:
    print("Install with: pip install pystac-client planetary-computer")
    raise


# ── 2. SEARCH FOR IMAGERY ────────────────────────────────────────────────────
# Area of Interest: Lake Tahoe, California (lon_min, lat_min, lon_max, lat_max)
BBOX = [-120.15, 38.90, -119.90, 39.10]

# Date range
DATE_RANGE = "2023-07-01/2023-09-30"

# Search Sentinel-2 Level-2A (surface reflectance, cloud-corrected)
search = catalog.search(
    collections=["sentinel-2-l2a"],
    bbox=BBOX,
    datetime=DATE_RANGE,
    query={"eo:cloud_cover": {"lt": 10}},  # Less than 10% cloud cover
    sortby="-datetime",                    # Most recent first
    max_items=5,
)

items = list(search.items())
print(f"\n🛰  Found {len(items)} scenes")
for i, item in enumerate(items):
    date = item.datetime.strftime("%Y-%m-%d")
    cloud = item.properties.get("eo:cloud_cover", "?")
    print(f"  [{i}] {date}  |  Cloud cover: {cloud:.1f}%  |  ID: {item.id}")


# ── 3. SELECT BEST SCENE ─────────────────────────────────────────────────────
best = items[0]
print(f"\n📡 Using scene: {best.id}")
print(f"   Date: {best.datetime.strftime('%Y-%m-%d')}")
print(f"   Available assets: {list(best.assets.keys())}")


# ── 4. DOWNLOAD BANDS ────────────────────────────────────────────────────────
import rasterio
from rasterio.windows import from_bounds
from rasterio.transform import from_bounds as tfrom_bounds

os.makedirs("satellite_data", exist_ok=True)

def download_band(item, band_name, out_path):
    """Download a single band clipped to our bounding box."""
    if band_name not in item.assets:
        raise ValueError(f"Band '{band_name}' not found. Available: {list(item.assets.keys())}")
    
    href = item.assets[band_name].href
    print(f"  ⬇  Downloading {band_name} → {out_path}")
    
    with rasterio.open(href) as src:
        # Reproject bbox to the raster's CRS
        from rasterio.warp import transform_bounds
        bounds_in_crs = transform_bounds("EPSG:4326", src.crs, *BBOX)
        window = from_bounds(*bounds_in_crs, transform=src.transform)
        
        data = src.read(1, window=window)
        transform = src.window_transform(window)
        profile = src.profile.copy()
        profile.update(width=data.shape[1], height=data.shape[0], transform=transform)
    
    with rasterio.open(out_path, "w", **profile) as dst:
        dst.write(data, 1)
    
    return data.astype(np.float32)

# Sentinel-2 bands:
#   B04 = Red (665 nm)   → used for NDVI
#   B08 = NIR (842 nm)   → used for NDVI
#   B03 = Green (560 nm) → used for NDWI
#   B02 = Blue  (490 nm) → used for true-colour
red   = download_band(best, "B04", "satellite_data/red.tif")
nir   = download_band(best, "B08", "satellite_data/nir.tif")
green = download_band(best, "B03", "satellite_data/green.tif")
blue  = download_band(best, "B02", "satellite_data/blue.tif")

print("✅ All bands downloaded")


# ── 5. COMPUTE INDICES ───────────────────────────────────────────────────────
def safe_divide(a, b):
    """Avoid division by zero."""
    return np.where((a + b) == 0, 0, (a - b) / (a + b))

# NDVI = (NIR - Red) / (NIR + Red)
# Range: -1 to +1 | High values = dense vegetation
ndvi = safe_divide(nir, red)

# NDWI = (Green - NIR) / (Green + NIR)   [McFeeters 1996]
# Range: -1 to +1 | High values = open water
ndwi = safe_divide(green, nir)

print(f"\n📊 NDVI  →  min: {ndvi.min():.3f}  max: {ndvi.max():.3f}  mean: {ndvi.mean():.3f}")
print(f"📊 NDWI  →  min: {ndwi.min():.3f}  max: {ndwi.max():.3f}  mean: {ndwi.mean():.3f}")

# Save index rasters
def save_index(data, path, ref_band_path):
    with rasterio.open(ref_band_path) as src:
        profile = src.profile.copy()
    profile.update(dtype=rasterio.float32, count=1)
    with rasterio.open(path, "w", **profile) as dst:
        dst.write(data.astype(np.float32), 1)
    print(f"  💾 Saved {path}")

save_index(ndvi, "satellite_data/ndvi.tif", "satellite_data/red.tif")
save_index(ndwi, "satellite_data/ndwi.tif", "satellite_data/green.tif")


# ── 6. VISUALISE ─────────────────────────────────────────────────────────────
def normalise(arr, p_low=2, p_high=98):
    lo, hi = np.percentile(arr, p_low), np.percentile(arr, p_high)
    return np.clip((arr - lo) / (hi - lo + 1e-6), 0, 1)

rgb = np.dstack([normalise(red), normalise(green), normalise(blue)])

fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.patch.set_facecolor("#0d1117")

titles  = ["True Colour (RGB)", "NDVI  (Vegetation)", "NDWI  (Water)"]
images  = [rgb, ndvi, ndwi]
cmaps   = [None, "RdYlGn", "RdYlBu"]
v_ranges = [None, (-0.2, 0.8), (-0.4, 0.6)]

for ax, img, title, cmap, vr in zip(axes, images, titles, cmaps, v_ranges):
    if cmap:
        im = ax.imshow(img, cmap=cmap, vmin=vr[0], vmax=vr[1])
        plt.colorbar(im, ax=ax, shrink=0.8, pad=0.02)
    else:
        ax.imshow(img)
    ax.set_title(title, color="white", fontsize=13, fontweight="bold", pad=10)
    ax.axis("off")

scene_date = best.datetime.strftime("%Y-%m-%d")
fig.suptitle(f"Sentinel-2 | Lake Tahoe | {scene_date}", color="white",
             fontsize=15, fontweight="bold", y=1.01)
plt.tight_layout()
plt.savefig("satellite_data/result.png", dpi=150, bbox_inches="tight",
            facecolor=fig.get_facecolor())
plt.show()
print("\n🖼  Plot saved → satellite_data/result.png")
