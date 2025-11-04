# 📊 Employee Performance Dashboard

A streamlined web-based dashboard for analyzing and visualizing employee performance metrics.

![Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.0+-green.svg)

## 🚀 Quick Start

### Local Development

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch dashboard
python backend_server.py

# 3. Open browser
http://localhost:5000
```

### Deploy to Render

1. Fork/clone this repository
2. Create a new Web Service on Render
3. Connect your repository
4. Use these settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python backend_server.py`
   - **Environment**: Python 3
5. Deploy!

## ✨ Features

### 📈 Three Interactive Dashboard Pages
1. **Overview** - KPIs, performance distribution, department metrics
2. **Employees** - Searchable table with detailed profiles (1,470 employees)
3. **Analytics** - Department comparison, scatter plots, distributions

### 🎯 Key Capabilities
- ✅ Real-time search and filtering
- ✅ Interactive Plotly.js visualizations
- ✅ Department comparisons
- ✅ CSV data export
- ✅ Fully responsive design
- ✅ REST API backend

## 🏗️ Project Structure

```
employee_management_project/
├── frontend/                      # Web dashboard
│   ├── index.html                # Main page
│   ├── css/styles.css            # Styling
│   └── js/                       # JavaScript modules
│       ├── api.js                # API calls
│       ├── app.js                # Main logic
│       ├── charts.js             # Visualizations
│       ├── config.js             # Configuration
│       └── utils.js              # Helper functions
├── scripts/                      # Python analysis modules
│   ├── employee_performance_analysis.py
│   └── performance_insights_engine.py
├── data/                         # Raw data
│   └── WA_HR-Employee-Attrition_unprocessed.csv
├── outputs/                      # Processed data
│   └── cleaned_employee_data.csv
├── backend_server.py            # Flask API server
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🔌 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Dashboard UI |
| `GET /api/employees` | All employees (with filters) |
| `GET /api/employees/<id>` | Employee details |
| `GET /api/statistics` | Company statistics |
| `GET /api/departments` | Department list |
| `GET /api/top-performers` | Top performers |
| `GET /api/high-risk` | High-risk employees |
| `GET /api/insights/<id>` | Employee insights |
| `GET /api/analytics/correlation` | Correlation matrix |
| `GET /api/analytics/trends` | Performance trends |
| `GET /api/export/csv` | Export data |
| `GET /api/health` | Health check |

## 🛠️ Tech Stack

**Frontend**: HTML5, CSS3, JavaScript ES6+, Plotly.js, Chart.js  
**Backend**: Python 3.7+, Flask 2.0+, Pandas, NumPy  
**Data**: 1,470 employees, 35 features per employee

## 📊 Performance Metrics

The dashboard analyzes:
- **Productivity Score** - Work output & efficiency
- **Quality Score** - Accuracy & standards
- **Engagement Score** - Job satisfaction & involvement
- **Overall Performance** - Composite performance metric
- **Department Metrics** - Cross-department comparisons

## 🐛 Troubleshooting

**Charts not displaying?**
- Verify internet connection (loads CDN libraries)
- Check browser console for errors
- Ensure backend server is running

**Backend errors?**
```bash
pip install -r requirements.txt
python backend_server.py
```

**Port already in use?**
```bash
# Linux/Mac
lsof -i :5000
kill -9 <PID>

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

## 📱 Browser Support

✅ Chrome 90+  
✅ Firefox 88+  
✅ Safari 14+  
✅ Edge 90+

## 🔒 Production Deployment

For production on Render:
1. Environment variables are automatically set
2. Server runs on port specified by Render
3. CORS is enabled for cross-origin requests
4. Debug mode disabled in production

For other platforms:
- Set `PORT` environment variable
- Disable Flask debug mode
- Enable HTTPS
- Consider adding authentication

## 📄 License

This project is for educational and analytical purposes.

---

**Version**: 3.0.0 | **Updated**: Nov 4, 2025 | **Status**: ✅ Production Ready

Made with ❤️ for data-driven HR analytics
