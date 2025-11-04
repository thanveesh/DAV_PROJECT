# Employee Performance Analysis Dashboard - Frontend

## Overview

A modern, responsive web-based dashboard for visualizing and analyzing employee performance data. Built with vanilla JavaScript, HTML5, and CSS3, featuring interactive charts powered by Plotly.js and Chart.js.

## Features

### 📊 Overview Dashboard
- Real-time KPI cards (Total Employees, Avg Performance, High Risk, Top Performers)
- Performance distribution pie chart
- Department performance comparison
- Performance trends over time
- Quick statistics grid

### 👥 Employee Directory
- Searchable and filterable employee table
- Filter by department and performance level
- Pagination support
- Detailed employee profile modals
- Risk level indicators

### 📈 Advanced Analytics
- **Correlation Analysis**: Heatmap showing relationships between performance factors
- **Department Comparison**: Side-by-side department analytics
- **Scatter Analysis**: Customizable multidimensional plots
- **Distribution Analysis**: Histograms and box plots

### 💡 AI Insights
- High-risk employee identification
- Key findings and patterns
- Actionable recommendations with priority levels
- Risk alerts and critical issues

### 📄 Reports & Export
- Executive summary generation
- Department-specific reports
- CSV data export
- Risk assessment reports
- Recent reports history

## Technology Stack

- **Frontend Framework**: Vanilla JavaScript (ES6+)
- **Styling**: Custom CSS3 with CSS Grid and Flexbox
- **Charts**: Plotly.js 2.26.0 for interactive visualizations
- **Icons**: Font Awesome 6.4.0
- **Architecture**: Modular JavaScript with separation of concerns

## File Structure

```
frontend/
├── index.html              # Main HTML file
├── css/
│   └── styles.css          # Complete styling
├── js/
│   ├── config.js           # Configuration and constants
│   ├── api.js              # Data loading and API calls
│   ├── charts.js           # Chart creation functions
│   ├── utils.js            # Utility functions
│   └── app.js              # Main application logic
└── README.md               # This file
```

## Installation

### Prerequisites
- Python 3.7+ (for running local server)
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Quick Start

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Start a local web server:**
   
   **Option 1: Python HTTP Server**
   ```bash
   python -m http.server 8000
   ```
   
   **Option 2: Python 3 HTTP Server**
   ```bash
   python3 -m http.server 8000
   ```
   
   **Option 3: Node.js HTTP Server (if Node.js installed)**
   ```bash
   npx http-server -p 8000
   ```

3. **Open browser:**
   Navigate to `http://localhost:8000`

## Configuration

Edit `js/config.js` to customize:

```javascript
const CONFIG = {
    API_BASE_URL: 'http://localhost:5000/api',
    DATA_PATH: '../outputs/cleaned_employee_data.csv',
    REFRESH_INTERVAL: 300000, // 5 minutes
    PAGINATION_SIZE: 20,
    
    THRESHOLDS: {
        TOP_PERFORMER: 75,
        ABOVE_AVERAGE: 50,
        BELOW_AVERAGE: 25,
        HIGH_RISK: 10
    }
};
```

## Usage

### Navigation

- **Overview**: Dashboard home with KPIs and key charts
- **Employees**: Browse and search employee directory
- **Analytics**: Advanced analytics with multiple chart types
- **AI Insights**: View AI-generated insights and recommendations
- **Reports**: Generate and download reports

### Features

#### Viewing Employee Details
1. Navigate to "Employees" page
2. Click "View" button on any employee row
3. Modal displays complete employee profile with metrics

#### Filtering Employees
- Use search box to find by ID, department, or role
- Select department from dropdown
- Select performance level filter

#### Generating Reports
1. Navigate to "Reports" page
2. Select report type
3. Click "Generate" button
4. Report will be created and added to recent reports

#### Exporting Data
- Click export icon in header
- CSV file downloads automatically

## API Integration

The dashboard can work in two modes:

### 1. CSV Mode (Current)
Loads data directly from `cleaned_employee_data.csv` file. Suitable for static analysis.

### 2. API Mode (Future)
Connect to backend API by updating `api.js`:

```javascript
async loadEmployeeData() {
    const response = await fetch(`${CONFIG.API_BASE_URL}/employees`);
    const data = await response.json();
    this.employeeData = data;
    this.calculateStatistics();
}
```

## Performance Optimization

- **Lazy Loading**: Charts loaded only when page is accessed
- **Debounced Search**: Search input debounced to reduce redraws
- **Pagination**: Large datasets paginated for better performance
- **Efficient Rendering**: Only visible elements rendered

## Browser Compatibility

| Browser | Version | Status |
|---------|---------|--------|
| Chrome | 90+ | ✅ Fully Supported |
| Firefox | 88+ | ✅ Fully Supported |
| Safari | 14+ | ✅ Fully Supported |
| Edge | 90+ | ✅ Fully Supported |

## Responsive Design

The dashboard is fully responsive with breakpoints at:
- Desktop: 1024px and above
- Tablet: 768px to 1023px
- Mobile: 767px and below

## Troubleshooting

### Charts not displaying
- Ensure Plotly.js CDN is accessible
- Check browser console for errors
- Verify data is loading correctly

### Data not loading
- Check CSV file path in `config.js`
- Ensure web server is running
- Verify CORS settings if using external API

### Styling issues
- Clear browser cache
- Ensure `styles.css` is loaded
- Check browser developer tools

## Customization

### Adding New Charts
1. Add chart function to `charts.js`:
   ```javascript
   createMyChart(containerId) {
       const chartData = [/* your data */];
       const layout = {/* your layout */};
       Plotly.newPlot(containerId, chartData, layout);
   }
   ```

2. Add container to HTML:
   ```html
   <div id="my-chart" class="chart-container"></div>
   ```

3. Call in `app.js`:
   ```javascript
   Charts.createMyChart('my-chart');
   ```

### Changing Color Theme
Edit CSS variables in `styles.css`:
```css
:root {
    --primary-color: #your-color;
    --secondary-color: #your-color;
    /* ... */
}
```

## Development

### Code Structure

- **config.js**: All configuration constants
- **api.js**: Data loading, filtering, and export
- **charts.js**: All chart creation functions
- **utils.js**: Helper functions (formatting, modals, toasts)
- **app.js**: Main application logic and event handlers

### Adding New Pages

1. Add page section to `index.html`:
   ```html
   <section id="mypage-page" class="page">
       <!-- Your content -->
   </section>
   ```

2. Add navigation link:
   ```html
   <a href="#mypage" class="nav-link" data-page="mypage">
       <i class="fas fa-icon"></i> My Page
   </a>
   ```

3. Add page load logic to `app.js`:
   ```javascript
   case 'mypage':
       loadMyPageContent();
       break;
   ```

## Performance Metrics

- **Initial Load**: < 2 seconds
- **Chart Render**: < 500ms
- **Search/Filter**: < 100ms (debounced)
- **Page Navigation**: Instant

## Security Considerations

- No sensitive data stored in browser
- Input sanitization for search queries
- HTTPS recommended for production
- CORS configuration for API access

## Future Enhancements

- [ ] Real-time data updates via WebSockets
- [ ] User authentication and authorization
- [ ] Custom dashboard builder
- [ ] Advanced filtering with saved filters
- [ ] Email report scheduling
- [ ] Mobile app version
- [ ] Dark mode theme
- [ ] Multi-language support

## Support

For issues or questions:
1. Check browser console for errors
2. Review this README
3. Check `../docs/` for additional documentation

## License

This dashboard is part of the Employee Performance Analysis project.

## Credits

- Built with ❤️ for data-driven HR analytics
- Charts powered by Plotly.js and Chart.js
- Icons by Font Awesome

---

**Version**: 1.0.0  
**Last Updated**: November 4, 2025  
**Author**: Employee Performance Analysis Team
