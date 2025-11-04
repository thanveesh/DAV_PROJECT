// API and Data Loading Module
const API = {
    employeeData: null,
    stats: null,
    
    /**
     * Load employee data from Backend API
     */
    async loadEmployeeData() {
        try {
            showLoading(true);
            
            // Fetch from backend API
            const response = await fetch(`${CONFIG.API_BASE_URL}/employees`);
            
            if (!response.ok) {
                throw new Error(`API returned ${response.status}`);
            }
            
            const data = await response.json();
            this.employeeData = data.employees || data;
            this.calculateStatistics();
            
            showLoading(false);
            showToast('Employee data loaded successfully!', 'success');
            return this.employeeData;
        } catch (error) {
            console.error('Error loading employee data from API:', error);
            console.log('Falling back to sample data...');
            showToast('Using sample data for demonstration', 'warning');
            this.generateSampleData();
            showLoading(false);
            return this.employeeData;
        }
    },
    
    /**
     * Parse CSV text to JSON
     */
    parseCSV(csvText) {
        const lines = csvText.trim().split('\n');
        const headers = lines[0].split(',').map(h => h.trim().toLowerCase());
        
        const data = [];
        for (let i = 1; i < lines.length; i++) {
            const values = lines[i].split(',');
            if (values.length === headers.length) {
                const row = {};
                headers.forEach((header, index) => {
                    row[header] = values[index].trim();
                });
                data.push(row);
            }
        }
        
        return data;
    },
    
    /**
     * Generate sample data for demonstration
     */
    generateSampleData() {
        const departments = ['Sales', 'Research & Development', 'Human Resources'];
        const roles = ['Sales Executive', 'Research Scientist', 'Manager', 'Laboratory Technician'];
        const sampleSize = 1470;
        
        this.employeeData = [];
        
        for (let i = 1; i <= sampleSize; i++) {
            const productivity = Math.random() * 100;
            const quality = Math.random() * 100;
            const engagement = Math.random() * 100;
            const overall_performance = (0.35 * productivity + 0.30 * quality + 0.20 * engagement + 0.15 * (Math.random() * 100));
            
            const employee = {
                employeenumber: i,
                age: Math.floor(Math.random() * 40) + 20,
                department: departments[Math.floor(Math.random() * departments.length)],
                jobrole: roles[Math.floor(Math.random() * roles.length)],
                monthlyincome: Math.floor(Math.random() * 15000) + 2000,
                yearsatcompany: Math.floor(Math.random() * 20),
                performancerating: Math.floor(Math.random() * 2) + 3,
                jobsatisfaction: Math.floor(Math.random() * 4) + 1,
                worklifebalance: Math.floor(Math.random() * 4) + 1,
                overtime: Math.random() > 0.7 ? 'Yes' : 'No',
                trainingtimeslastyear: Math.floor(Math.random() * 6),
                jobinvolvement: Math.floor(Math.random() * 4) + 1,
                attrition: Math.random() > 0.84 ? 'Yes' : 'No',
                productivity_score: productivity.toFixed(2),
                quality_score: quality.toFixed(2),
                engagement_score: engagement.toFixed(2),
                overall_performance: overall_performance.toFixed(2),
                performance_percentile: 0
            };
            
            this.employeeData.push(employee);
        }
        
        // Calculate percentiles
        this.employeeData.sort((a, b) => parseFloat(a.overall_performance) - parseFloat(b.overall_performance));
        this.employeeData.forEach((emp, index) => {
            emp.performance_percentile = ((index + 1) / sampleSize * 100).toFixed(2);
        });
        
        this.calculateStatistics();
    },
    
    /**
     * Calculate statistics from employee data
     */
    calculateStatistics() {
        if (!this.employeeData || this.employeeData.length === 0) {
            return;
        }
        
        const total = this.employeeData.length;
        
        // Calculate average performance - handle both string and number formats
        const avgPerformance = this.employeeData.reduce((sum, e) => {
            const perf = parseFloat(e.overall_performance || e.OverallPerformance || 0);
            return sum + perf;
        }, 0) / total;
        
        // Count top performers - handle different field name formats
        const topPerformers = this.employeeData.filter(e => {
            const perf = parseFloat(e.performance_percentile || e.PerformancePercentile || 0);
            return perf >= CONFIG.THRESHOLDS.TOP_PERFORMER;
        }).length;
        
        // Count high risk employees
        const highRisk = this.employeeData.filter(e => {
            const perf = parseFloat(e.performance_percentile || e.PerformancePercentile || 0);
            const quality = parseFloat(e.quality_score || e.QualityScore || 0);
            const engagement = parseFloat(e.engagement_score || e.EngagementScore || 0);
            const overtime = e.overtime || e.OverTime || 'No';
            
            return perf <= CONFIG.THRESHOLDS.HIGH_RISK ||
                   (overtime === 'Yes' && quality < 45) ||
                   engagement < 30;
        }).length;
        
        // Department stats
        const deptStats = {};
        this.employeeData.forEach(emp => {
            const dept = emp.department || emp.Department || 'Unknown';
            if (!deptStats[dept]) {
                deptStats[dept] = {
                    count: 0,
                    totalPerformance: 0,
                    performances: []
                };
            }
            const perf = parseFloat(emp.overall_performance || emp.OverallPerformance || 0);
            deptStats[dept].count++;
            deptStats[dept].totalPerformance += perf;
            deptStats[dept].performances.push(perf);
        });
        
        for (const dept in deptStats) {
            deptStats[dept].avgPerformance = deptStats[dept].totalPerformance / deptStats[dept].count;
        }
        
        // Other stats - handle different field formats
        const overtimeCount = this.employeeData.filter(e => 
            (e.overtime || e.OverTime) === 'Yes'
        ).length;
        
        const attritionCount = this.employeeData.filter(e => 
            (e.attrition || e.Attrition) === 'Yes'
        ).length;
        
        const avgTraining = this.employeeData.reduce((sum, e) => {
            const training = parseInt(e.trainingtimeslastyear || e.TrainingTimesLastYear || 0);
            return sum + training;
        }, 0) / total;
        
        const avgSatisfaction = this.employeeData.reduce((sum, e) => {
            const satisfaction = parseInt(e.jobsatisfaction || e.JobSatisfaction || 0);
            return sum + satisfaction;
        }, 0) / total;
        
        this.stats = {
            totalEmployees: total,
            avgPerformance: avgPerformance.toFixed(2),
            topPerformersCount: topPerformers,
            highRiskCount: highRisk,
            departmentStats: deptStats,
            overtimePercentage: ((overtimeCount / total) * 100).toFixed(1),
            attritionRate: ((attritionCount / total) * 100).toFixed(1),
            avgTraining: avgTraining.toFixed(1),
            avgSatisfaction: avgSatisfaction.toFixed(1)
        };
    },
    
    /**
     * Get employee by ID
     */
    getEmployeeById(employeeId) {
        return this.employeeData.find(e => parseInt(e.employeenumber) === parseInt(employeeId));
    },
    
    /**
     * Filter employees
     */
    filterEmployees(filters) {
        let filtered = [...this.employeeData];
        
        // Search filter
        if (filters.search) {
            const searchTerm = filters.search.toLowerCase();
            filtered = filtered.filter(e => 
                e.employeenumber.toString().includes(searchTerm) ||
                e.department.toLowerCase().includes(searchTerm) ||
                e.jobrole.toLowerCase().includes(searchTerm)
            );
        }
        
        // Department filter
        if (filters.department) {
            filtered = filtered.filter(e => e.department === filters.department);
        }
        
        // Performance filter
        if (filters.performance) {
            const percentile = parseFloat(e => e.performance_percentile);
            switch (filters.performance) {
                case 'top':
                    filtered = filtered.filter(e => parseFloat(e.performance_percentile) >= 75);
                    break;
                case 'above':
                    filtered = filtered.filter(e => {
                        const p = parseFloat(e.performance_percentile);
                        return p >= 50 && p < 75;
                    });
                    break;
                case 'below':
                    filtered = filtered.filter(e => {
                        const p = parseFloat(e.performance_percentile);
                        return p >= 25 && p < 50;
                    });
                    break;
                case 'support':
                    filtered = filtered.filter(e => parseFloat(e.performance_percentile) < 25);
                    break;
            }
        }
        
        return filtered;
    },
    
    /**
     * Get department list
     */
    getDepartments() {
        if (!this.employeeData) return [];
        return [...new Set(this.employeeData.map(e => e.department))].sort();
    },
    
    /**
     * Get high risk employees
     */
    getHighRiskEmployees() {
        return this.employeeData.filter(e => 
            parseFloat(e.performance_percentile) <= CONFIG.THRESHOLDS.HIGH_RISK ||
            (e.overtime === 'Yes' && parseFloat(e.quality_score) < 45) ||
            parseFloat(e.engagement_score) < 30
        ).slice(0, 10);
    },
    
    /**
     * Export data as CSV
     */
    exportToCSV(data, filename) {
        if (!data || data.length === 0) return;
        
        const headers = Object.keys(data[0]);
        const csv = [
            headers.join(','),
            ...data.map(row => headers.map(header => row[header]).join(','))
        ].join('\n');
        
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        window.URL.revokeObjectURL(url);
    }
};

// Initialize data on load
if (typeof window !== 'undefined') {
    window.addEventListener('DOMContentLoaded', () => {
        API.loadEmployeeData().then(() => {
            if (typeof initializeApp === 'function') {
                initializeApp();
            }
        });
    });
}
