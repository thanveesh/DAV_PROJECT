// Configuration
const CONFIG = {
    API_BASE_URL: 'http://localhost:5000/api',
    DATA_PATH: '../outputs/cleaned_employee_data.csv',
    INSIGHTS_PATH: '../outputs/insights_reports/',
    REFRESH_INTERVAL: 300000, // 5 minutes
    PAGINATION_SIZE: 20,
    
    // Performance thresholds
    THRESHOLDS: {
        TOP_PERFORMER: 75,
        ABOVE_AVERAGE: 50,
        BELOW_AVERAGE: 25,
        HIGH_RISK: 10
    },
    
    // Chart colors
    COLORS: {
        primary: '#2563eb',
        secondary: '#7c3aed',
        success: '#10b981',
        warning: '#f59e0b',
        danger: '#ef4444',
        info: '#06b6d4',
        gradient: ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981']
    }
};

// Export for other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}
