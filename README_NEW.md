# 🛰️ STAC Satellite Data Explorer Web Application

A web-based geospatial analysis tool for exploring and visualizing satellite imagery from STAC (SpatioTemporal Asset Catalog) repositories. Built with Streamlit and integrated with Microsoft Planetary Computer.

## ✨ Features

- **🔍 Scene Search**: Find satellite scenes by location, date range, and cloud cover filters
- **🗺️ Interactive Maps**: Visualize scene boundaries and search areas on Leaflet-powered web maps with multiple basemap options
- **📊 Analytics Dashboard**: Simulated NDVI and NDWI vegetation/water indices with statistical metrics
- **📈 Visualizations**: RGB, NDVI, and NDWI plots with color-mapped overlays and distribution histograms
- **⬇️ Export**: Download analysis plots as high-resolution PNG images
- **🔗 Asset Access**: Direct URLs to raw satellite assets for further processing
- **📍 Scene Metadata**: Cloud cover, acquisition date, platform, and available bands information

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Git
- `uv` package manager (recommended) or `pip`

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/stac-satellite-explorer.git
   cd stac-satellite-explorer
   ```

2. **Create and activate virtual environment**
   ```bash
   # Using uv (recommended)
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Or using pip
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   # Using uv
   uv sync
   
   # Or using pip
   pip install -r requirements.txt
   ```

### Running the Application

```bash
streamlit run stac_app.py
```

The app will open in your browser at `http://localhost:8501`

## 📖 Usage

### 1. Configure Search Parameters
   - Select a location preset (Sahara Desert, Vienna) or enter custom bounding box
   - Set date range for satellite acquisitions
   - Adjust cloud cover threshold (0-50%)
   - Choose satellite collection (Sentinel-2, Landsat, DEM)

### 2. Search Scenes
   - Click **"🔍 Search scenes"** to query Planetary Computer STAC catalog
   - Browse results sorted by acquisition date

### 3. Explore Results
   - Select a scene from the dropdown
   - View metadata in expandable section
   - Examine interactive map with scene boundary
   - Switch between basemaps (Esri Satellite, OpenStreetMap, None)

### 4. View Analytics
   - Check NDVI/NDWI metrics and vegetation/water coverage
   - View RGB, NDVI, and NDWI visualizations
   - Expand histogram panel for index distributions

### 5. Access Assets
   - Scroll to "Scene Details & Asset URLs" section
   - Expand each asset to view raw URL
   - Copy URLs for direct use with GIS tools

## 🏗️ Architecture

```
stac_app.py          # Main Streamlit application
├── Sidebar Controls # Location, date, collection selection
├── STAC Search      # Query Planetary Computer catalog
├── Scene Picker     # Select from results
├── Map Viewer       # Leaflet.js interactive map
├── Analytics        # NDVI/NDWI metrics & visualizations
└── Asset URLs       # Direct links to scene data
```

## 🔧 Technology Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | Streamlit, Leaflet.js |
| **Backend** | Python 3.8+ |
| **Mapping** | Leaflet.js, Esri Satellite Tiles |
| **Data** | Microsoft Planetary Computer STAC |
| **Satellites** | Sentinel-2, Landsat, Copernicus DEM |
| **Analysis** | NumPy, Matplotlib |
| **Package Manager** | uv (Python 1.45+) |

## 📦 Dependencies

```toml
streamlit >= 1.28.0
pystac-client >= 0.7.0
planetary-computer >= 0.5.0
numpy >= 1.24.0
matplotlib >= 3.7.0
pyproj >= 3.6.0
rasterio >= 1.3.0
requests >= 2.31.0
Pillow >= 10.0.0
```

## 🗺️ Supported Collections

- **sentinel-2-l2a**: Sentinel-2 Level-2A surface reflectance
- **landsat-c2-l2**: Landsat Collection 2 Level-2 surface reflectance
- **cop-dem-glo-30**: Copernicus DEM 30m global

## 📊 Analytics Explained

### NDVI (Normalized Difference Vegetation Index)
- **Formula**: (NIR - Red) / (NIR + Red)
- **Range**: -1 to +1
- **Interpretation**: 
  - < 0: Non-vegetated (water, cloud, snow)
  - 0.3+: Healthy vegetation
  - Color map: Red (low) → Yellow → Green (high)

### NDWI (Normalized Difference Water Index)
- **Formula**: (Green - NIR) / (Green + NIR)
- **Range**: -1 to +1
- **Interpretation**:
  - < 0: Non-water surfaces
  - 0.3+: High water content
  - Color map: Red (low) → Yellow → Blue (high)

## 🌐 Live Demo

Deploy on Streamlit Cloud for free:

1. Push code to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your repository
4. Deploy automatically on each push

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📋 Roadmap

- [ ] Real NDVI/NDWI calculation from actual bands
- [ ] Multi-scene mosaicking
- [ ] Time-series analysis
- [ ] Custom band combinations
- [ ] Export to GeoTIFF
- [ ] Vector mask overlay
- [ ] Performance optimization for large areas
- [ ] Cloud-native deployment (Docker, K8s)

## ⚠️ Known Issues

- **GeoTIFF Display**: Cloud-Optimized GeoTIFFs from Azure blobs have CORS restrictions; showing scene boundaries instead
- **Windows PROJ**: PROJ database path requires environment variable setup for band processing
- **Large Scenes**: Very large scenes (>500MB) may timeout; recommend smaller bounding boxes

## 🔗 Resources

- [STAC Specification](https://stacspec.org/)
- [Planetary Computer Documentation](https://planetarycomputer.microsoft.com/)
- [Sentinel-2 User Guide](https://sentinel.esa.int/web/sentinel/user-guides/sentinel-2-msi)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Leaflet.js Documentation](https://leafletjs.com/)

## 📝 License

MIT License - see LICENSE file for details

## 👤 Author

Created as a geospatial analysis tool for satellite imagery exploration.

## 🙏 Acknowledgments

- [Microsoft Planetary Computer](https://planetarycomputer.microsoft.com/) - STAC catalog & data
- [Copernicus Sentinel-2](https://sentinel.esa.int/web/sentinel/missions/sentinel-2) - Satellite imagery
- [Streamlit](https://streamlit.io/) - Web framework
- [Leaflet.js](https://leafletjs.com/) - Mapping library

---

**Questions or Issues?** Open a GitHub issue or reach out!

🛰️ Happy exploring satellite data!
