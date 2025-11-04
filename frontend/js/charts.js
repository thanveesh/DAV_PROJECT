// Charts Module - Handle all visualizations
const Charts = {
    /**
     * Create performance distribution pie chart
     */
    createPerformanceDistribution(containerId) {
        if (!API.employeeData || API.employeeData.length === 0) {
            console.warn('No employee data available for chart');
            return;
        }
        
        const data = API.employeeData;
        const counts = {
            'Top Performers (≥75%)': data.filter(e => {
                const perf = parseFloat(e.performance_percentile || e.PerformancePercentile || 0);
                return perf >= 75;
            }).length,
            'Above Average (50-75%)': data.filter(e => {
                const p = parseFloat(e.performance_percentile || e.PerformancePercentile || 0);
                return p >= 50 && p < 75;
            }).length,
            'Below Average (25-50%)': data.filter(e => {
                const p = parseFloat(e.performance_percentile || e.PerformancePercentile || 0);
                return p >= 25 && p < 50;
            }).length,
            'Need Support (< 25%)': data.filter(e => {
                const perf = parseFloat(e.performance_percentile || e.PerformancePercentile || 0);
                return perf < 25;
            }).length
        };
        
        const chartData = [{
            values: Object.values(counts),
            labels: Object.keys(counts),
            type: 'pie',
            marker: {
                colors: [CONFIG.COLORS.success, CONFIG.COLORS.info, CONFIG.COLORS.warning, CONFIG.COLORS.danger]
            },
            textinfo: 'label+percent',
            textposition: 'outside',
            hovertemplate: '<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        }];
        
        const layout = {
            height: 350,
            margin: { t: 0, b: 0, l: 0, r: 0 },
            showlegend: true,
            legend: {
                orientation: 'v',
                x: 1,
                y: 0.5
            }
        };
        
        try {
            Plotly.newPlot(containerId, chartData, layout, {responsive: true, displayModeBar: false});
        } catch (error) {
            console.error('Error creating performance distribution chart:', error);
        }
    },
    
    /**
     * Create department performance bar chart
     */
    createDepartmentPerformance(containerId) {
        if (!API.stats || !API.stats.departmentStats) return;
        
        const deptStats = API.stats.departmentStats;
        const departments = Object.keys(deptStats);
        const avgPerformances = departments.map(d => deptStats[d].avgPerformance.toFixed(2));
        
        const chartData = [{
            x: departments,
            y: avgPerformances,
            type: 'bar',
            marker: {
                color: CONFIG.COLORS.gradient,
                line: {
                    color: 'white',
                    width: 2
                }
            },
            text: avgPerformances.map(v => v + ' pts'),
            textposition: 'outside',
            hovertemplate: '<b>%{x}</b><br>Avg Performance: %{y:.2f}<extra></extra>'
        }];
        
        const layout = {
            height: 350,
            margin: { t: 20, b: 80, l: 50, r: 20 },
            xaxis: {
                title: 'Department',
                tickangle: -45
            },
            yaxis: {
                title: 'Average Performance Score',
                range: [0, 100]
            },
            plot_bgcolor: '#f9fafb',
            paper_bgcolor: 'white'
        };
        
        Plotly.newPlot(containerId, chartData, layout, {responsive: true, displayModeBar: false});
    },
    
    /**
     * Create performance trend line chart
     */
    createPerformanceTrend(containerId, metric = 'overall') {
        if (!API.employeeData) return;
        
        // Group by years at company for trend analysis
        const trendData = {};
        API.employeeData.forEach(emp => {
            const years = parseInt(emp.yearsatcompany);
            if (!trendData[years]) {
                trendData[years] = { count: 0, total: 0 };
            }
            trendData[years].count++;
            
            let value;
            switch(metric) {
                case 'productivity':
                    value = parseFloat(emp.productivity_score);
                    break;
                case 'quality':
                    value = parseFloat(emp.quality_score);
                    break;
                case 'engagement':
                    value = parseFloat(emp.engagement_score);
                    break;
                default:
                    value = parseFloat(emp.overall_performance);
            }
            trendData[years].total += value;
        });
        
        const years = Object.keys(trendData).map(Number).sort((a, b) => a - b);
        const avgScores = years.map(y => (trendData[y].total / trendData[y].count).toFixed(2));
        
        const chartData = [{
            x: years,
            y: avgScores,
            type: 'scatter',
            mode: 'lines+markers',
            line: {
                color: CONFIG.COLORS.primary,
                width: 3
            },
            marker: {
                size: 8,
                color: CONFIG.COLORS.secondary
            },
            hovertemplate: '<b>Years: %{x}</b><br>Avg Score: %{y:.2f}<extra></extra>'
        }];
        
        const layout = {
            height: 350,
            margin: { t: 20, b: 50, l: 50, r: 20 },
            xaxis: {
                title: 'Years at Company'
            },
            yaxis: {
                title: 'Average Performance Score',
                range: [0, 100]
            },
            plot_bgcolor: '#f9fafb',
            paper_bgcolor: 'white'
        };
        
        Plotly.newPlot(containerId, chartData, layout, {responsive: true, displayModeBar: false});
    },
    
    /**
     * Create correlation heatmap
     */
    createCorrelationHeatmap(containerId) {
        if (!API.employeeData) return;
        
        // Calculate correlations between numeric variables
        const variables = [
            'age', 'monthlyincome', 'yearsatcompany', 'trainingtimeslastyear',
            'productivity_score', 'quality_score', 'engagement_score', 'overall_performance'
        ];
        
        const labels = [
            'Age', 'Income', 'Years', 'Training',
            'Productivity', 'Quality', 'Engagement', 'Overall'
        ];
        
        const n = variables.length;
        const correlationMatrix = Array(n).fill(0).map(() => Array(n).fill(0));
        
        // Calculate correlation coefficients
        for (let i = 0; i < n; i++) {
            for (let j = 0; j < n; j++) {
                const x = API.employeeData.map(e => parseFloat(e[variables[i]]));
                const y = API.employeeData.map(e => parseFloat(e[variables[j]]));
                correlationMatrix[i][j] = this.calculateCorrelation(x, y);
            }
        }
        
        const chartData = [{
            z: correlationMatrix,
            x: labels,
            y: labels,
            type: 'heatmap',
            colorscale: 'RdBu',
            zmid: 0,
            hovertemplate: '%{y} vs %{x}<br>Correlation: %{z:.2f}<extra></extra>'
        }];
        
        const layout = {
            height: 500,
            margin: { t: 20, b: 80, l: 80, r: 20 },
            xaxis: { tickangle: -45 },
            yaxis: { tickangle: 0 }
        };
        
        Plotly.newPlot(containerId, chartData, layout, {responsive: true, displayModeBar: false});
    },
    
    /**
     * Create scatter plot
     */
    createScatterPlot(containerId, xVar, yVar) {
        if (!API.employeeData) return;
        
        const xData = API.employeeData.map(e => parseFloat(e[xVar]));
        const yData = API.employeeData.map(e => parseFloat(e[yVar]));
        const colors = API.employeeData.map(e => parseFloat(e.performance_percentile));
        const text = API.employeeData.map(e => `Employee #${e.employeenumber}<br>${e.department}`);
        
        const chartData = [{
            x: xData,
            y: yData,
            mode: 'markers',
            type: 'scatter',
            marker: {
                size: 8,
                color: colors,
                colorscale: 'Viridis',
                showscale: true,
                colorbar: {
                    title: 'Performance<br>Percentile',
                    thickness: 15
                }
            },
            text: text,
            hovertemplate: '%{text}<br>X: %{x}<br>Y: %{y:.2f}<extra></extra>'
        }];
        
        const layout = {
            height: 500,
            margin: { t: 20, b: 50, l: 50, r: 20 },
            xaxis: { title: this.getVariableLabel(xVar) },
            yaxis: { title: this.getVariableLabel(yVar) },
            plot_bgcolor: '#f9fafb',
            paper_bgcolor: 'white'
        };
        
        Plotly.newPlot(containerId, chartData, layout, {responsive: true, displayModeBar: false});
    },
    
    /**
     * Create histogram
     */
    createHistogram(containerId) {
        if (!API.employeeData) return;
        
        const performances = API.employeeData.map(e => parseFloat(e.overall_performance));
        
        const chartData = [{
            x: performances,
            type: 'histogram',
            nbinsx: 30,
            marker: {
                color: CONFIG.COLORS.primary,
                line: {
                    color: 'white',
                    width: 1
                }
            },
            hovertemplate: 'Range: %{x}<br>Count: %{y}<extra></extra>'
        }];
        
        const layout = {
            height: 350,
            margin: { t: 20, b: 50, l: 50, r: 20 },
            xaxis: { title: 'Performance Score' },
            yaxis: { title: 'Number of Employees' },
            plot_bgcolor: '#f9fafb',
            paper_bgcolor: 'white'
        };
        
        Plotly.newPlot(containerId, chartData, layout, {responsive: true, displayModeBar: false});
    },
    
    /**
     * Create box plot
     */
    createBoxPlot(containerId) {
        if (!API.employeeData || !API.stats) return;
        
        const departments = Object.keys(API.stats.departmentStats);
        const traces = [];
        
        departments.forEach((dept, index) => {
            const deptData = API.employeeData.filter(e => e.department === dept);
            const performances = deptData.map(e => parseFloat(e.overall_performance));
            
            traces.push({
                y: performances,
                type: 'box',
                name: dept,
                marker: { color: CONFIG.COLORS.gradient[index % CONFIG.COLORS.gradient.length] },
                boxmean: 'sd'
            });
        });
        
        const layout = {
            height: 350,
            margin: { t: 20, b: 80, l: 50, r: 20 },
            yaxis: { title: 'Performance Score' },
            xaxis: { tickangle: -45 },
            showlegend: false
        };
        
        Plotly.newPlot(containerId, traces, layout, {responsive: true, displayModeBar: false});
    },
    
    /**
     * Create department comparison charts
     */
    createDepartmentComparison(containerId) {
        if (!API.stats || !API.stats.departmentStats) return;
        
        const deptStats = API.stats.departmentStats;
        const departments = Object.keys(deptStats);
        const counts = departments.map(d => deptStats[d].count);
        
        const chartData = [{
            x: departments,
            y: counts,
            type: 'bar',
            marker: {
                color: CONFIG.COLORS.gradient
            },
            text: counts,
            textposition: 'outside',
            hovertemplate: '<b>%{x}</b><br>Employees: %{y}<extra></extra>'
        }];
        
        const layout = {
            height: 350,
            margin: { t: 20, b: 80, l: 50, r: 20 },
            xaxis: {
                title: 'Department',
                tickangle: -45
            },
            yaxis: {
                title: 'Number of Employees'
            },
            plot_bgcolor: '#f9fafb',
            paper_bgcolor: 'white'
        };
        
        Plotly.newPlot(containerId, chartData, layout, {responsive: true, displayModeBar: false});
    },
    
    /**
     * Helper: Calculate correlation coefficient
     */
    calculateCorrelation(x, y) {
        const n = x.length;
        const sum_x = x.reduce((a, b) => a + b, 0);
        const sum_y = y.reduce((a, b) => a + b, 0);
        const sum_xy = x.reduce((sum, xi, i) => sum + xi * y[i], 0);
        const sum_x2 = x.reduce((sum, xi) => sum + xi * xi, 0);
        const sum_y2 = y.reduce((sum, yi) => sum + yi * yi, 0);
        
        const numerator = n * sum_xy - sum_x * sum_y;
        const denominator = Math.sqrt((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y));
        
        return denominator === 0 ? 0 : numerator / denominator;
    },
    
    /**
     * Helper: Get readable variable label
     */
    getVariableLabel(varName) {
        const labels = {
            'age': 'Age',
            'yearsatcompany': 'Years at Company',
            'monthlyincome': 'Monthly Income',
            'trainingtimeslastyear': 'Training Hours',
            'overall_performance': 'Overall Performance',
            'productivity_score': 'Productivity Score',
            'quality_score': 'Quality Score',
            'engagement_score': 'Engagement Score'
        };
        return labels[varName] || varName;
    }
};
