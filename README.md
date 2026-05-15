# 🛰️ STAC Satellite Data Explorer Web Application

A web-based geospatial analysis tool for exploring and visualizing satellite imagery from STAC (SpatioTemporal Asset Catalog) repositories. Built with Streamlit and integrated with Microsoft Planetary Computer.

## ✨ Features

- **🗺️ Interactive Maps**: Visualize scene boundaries and search areas on Leaflet-powered web maps with multiple basemap options
- **📊 Analytics Dashboard**: Simulated NDVI and NDWI vegetation/water indices with statistical metrics
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
gdal >= 3.6.0
rasterio >= 1.3.0
requests >= 2.31.0
Pillow >= 10.0.0
```

## 🗺️ Supported Collections

- **sentinel-2-l2a**: Sentinel-2 Level-2A surface reflectance
- **landsat-c2-l2**: Landsat Collection 2 Level-2 surface reflectance
- **cop-dem-glo-30**: Copernicus DEM 30m global


## 🔗 Resources

- [STAC Specification](https://stacspec.org/)
- [Planetary Computer Documentation](https://planetarycomputer.microsoft.com/)
- [Sentinel-2 User Guide](https://sentinel.esa.int/web/sentinel/user-guides/sentinel-2-msi)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Leaflet.js Documentation](https://leafletjs.com/)

## 📝 License

MIT License - see LICENSE file for details

## Acknowledgments

- [Microsoft Planetary Computer](https://planetarycomputer.microsoft.com/) - STAC catalog & data
- [Copernicus Sentinel-2](https://sentinel.esa.int/web/sentinel/missions/sentinel-2) - Satellite imagery
- [Streamlit](https://streamlit.io/) - Web framework
- [Leaflet.js](https://leafletjs.com/) - Mapping library

---