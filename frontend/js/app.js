// Main Application Logic
let currentPage = 1;
let currentFilters = {
    search: '',
    department: '',
    performance: ''
};

/**
 * Initialize application
 */
function initializeApp() {
    console.log('Initializing Employee Performance Dashboard...');
    
    // Update KPIs
    updateKPIs();
    
    // Create charts for overview page
    Charts.createPerformanceDistribution('performance-distribution-chart');
    Charts.createDepartmentPerformance('dept-performance-chart');
    Charts.createPerformanceTrend('performance-trend-chart');
    
    // Setup navigation
    setupNavigation();
    
    // Setup filters and search
    setupFilters();
    
    // Setup analytics tabs
    setupAnalyticsTabs();
    
    // Populate department selects
    populateDepartmentSelects();
    
    // Load employees table
    loadEmployeesTable();
    
    // Setup event listeners
    setupEventListeners();
    
    showToast('Dashboard loaded successfully!', 'success');
    console.log('Dashboard initialized with', API.stats.totalEmployees, 'employees');
}

/**
 * Update KPI cards
 */
function updateKPIs() {
    if (!API.stats) return;
    
    document.getElementById('total-employees').textContent = formatNumber(API.stats.totalEmployees);
    document.getElementById('avg-performance').textContent = API.stats.avgPerformance;
    document.getElementById('high-risk-count').textContent = formatNumber(API.stats.highRiskCount);
    document.getElementById('top-performers-count').textContent = formatNumber(API.stats.topPerformersCount);
    document.getElementById('avg-training').textContent = API.stats.avgTraining + ' hrs';
    document.getElementById('overtime-percentage').textContent = API.stats.overtimePercentage + '%';
    document.getElementById('avg-satisfaction').textContent = API.stats.avgSatisfaction + '/4';
    document.getElementById('attrition-rate').textContent = API.stats.attritionRate + '%';
}

/**
 * Setup navigation
 */
function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    const pages = document.querySelectorAll('.page');
    
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const pageName = link.dataset.page;
            
            // Update active nav link
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            
            // Show corresponding page
            pages.forEach(p => p.classList.remove('active'));
            const targetPage = document.getElementById(`${pageName}-page`);
            if (targetPage) {
                targetPage.classList.add('active');
                
                // Load page-specific content
                loadPageContent(pageName);
            }
        });
    });
}

/**
 * Load page-specific content
 */
function loadPageContent(pageName) {
    switch(pageName) {
        case 'analytics':
            // Load analytics charts if not already loaded
            if (!document.getElementById('dept-comparison-chart').children.length) {
                Charts.createDepartmentPerformance('dept-comparison-chart');
                Charts.createDepartmentComparison('dept-count-chart');
                Charts.createScatterPlot('scatter-chart', 'age', 'overall_performance');
                Charts.createHistogram('performance-histogram');
                Charts.createBoxPlot('performance-boxplot');
            }
            break;
    }
}

/**
 * Setup filters
 */
function setupFilters() {
    const searchInput = document.getElementById('employee-search');
    const deptFilter = document.getElementById('department-filter');
    const perfFilter = document.getElementById('performance-filter');
    
    if (searchInput) {
        searchInput.addEventListener('input', debounce((e) => {
            currentFilters.search = e.target.value;
            currentPage = 1;
            loadEmployeesTable();
        }, 300));
    }
    
    if (deptFilter) {
        deptFilter.addEventListener('change', (e) => {
            currentFilters.department = e.target.value;
            currentPage = 1;
            loadEmployeesTable();
        });
    }
    
    if (perfFilter) {
        perfFilter.addEventListener('change', (e) => {
            currentFilters.performance = e.target.value;
            currentPage = 1;
            loadEmployeesTable();
        });
    }
}

/**
 * Setup analytics tabs
 */
function setupAnalyticsTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.dataset.tab;
            
            // Update active tab button
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Show corresponding tab content
            tabContents.forEach(content => content.classList.remove('active'));
            const targetContent = document.getElementById(`${tabName}-tab`);
            if (targetContent) {
                targetContent.classList.add('active');
            }
        });
    });
    
    // Setup scatter plot controls
    const scatterX = document.getElementById('scatter-x');
    const scatterY = document.getElementById('scatter-y');
    
    if (scatterX && scatterY) {
        scatterX.addEventListener('change', () => {
            Charts.createScatterPlot('scatter-chart', scatterX.value, scatterY.value);
        });
        scatterY.addEventListener('change', () => {
            Charts.createScatterPlot('scatter-chart', scatterX.value, scatterY.value);
        });
    }
    
    // Setup trend metric control
    const trendMetric = document.getElementById('trend-metric');
    if (trendMetric) {
        trendMetric.addEventListener('change', () => {
            Charts.createPerformanceTrend('performance-trend-chart', trendMetric.value);
        });
    }
}

/**
 * Setup insights filters
 */
/**
 * Populate department selects
 */
function populateDepartmentSelects() {
    const departments = API.getDepartments();
    
    // Employee filter
    const deptFilter = document.getElementById('department-filter');
    if (deptFilter) {
        departments.forEach(dept => {
            const option = document.createElement('option');
            option.value = dept;
            option.textContent = dept;
            deptFilter.appendChild(option);
        });
    }
}

/**
 * Load employees table
 */
function loadEmployeesTable() {
    const tbody = document.getElementById('employees-tbody');
    if (!tbody || !API.employeeData) return;
    
    // Filter employees
    const filteredEmployees = API.filterEmployees(currentFilters);
    
    // Pagination
    const start = (currentPage - 1) * CONFIG.PAGINATION_SIZE;
    const end = start + CONFIG.PAGINATION_SIZE;
    const pageEmployees = filteredEmployees.slice(start, end);
    
    // Clear table
    tbody.innerHTML = '';
    
    // Populate table
    pageEmployees.forEach(employee => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><strong>#${employee.employeenumber}</strong></td>
            <td>${employee.department}</td>
            <td>${employee.jobrole}</td>
            <td><strong>${parseFloat(employee.overall_performance).toFixed(1)}</strong></td>
            <td>${parseFloat(employee.performance_percentile).toFixed(1)}%</td>
            <td>${getRiskBadge(employee)}</td>
            <td>
                <button class="btn-secondary btn-sm" onclick="viewEmployeeDetails(${employee.employeenumber})">
                    <i class="fas fa-eye"></i> View
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
    
    // Create pagination
    createPagination(
        filteredEmployees.length,
        currentPage,
        CONFIG.PAGINATION_SIZE,
        (page) => {
            currentPage = page;
            loadEmployeesTable();
        }
    );
}

/**
 * View employee details
 */
function viewEmployeeDetails(employeeId) {
    const employee = API.getEmployeeById(employeeId);
    if (!employee) {
        showToast('Employee not found', 'error');
        return;
    }
    
    const modalBody = document.getElementById('employee-modal-body');
    if (modalBody) {
        modalBody.innerHTML = formatEmployeeDetails(employee);
        openModal('employee-modal');
    }
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Refresh data button
    const refreshBtn = document.getElementById('refresh-data');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            showLoading(true);
            setTimeout(() => {
                API.loadEmployeeData().then(() => {
                    updateKPIs();
                    loadEmployeesTable();
                    Charts.createPerformanceDistribution('performance-distribution-chart');
                    Charts.createDepartmentPerformance('dept-performance-chart');
                    Charts.createPerformanceTrend('performance-trend-chart');
                    showLoading(false);
                    showToast('Data refreshed successfully!', 'success');
                });
            }, 1000);
        });
    }
    
    // Export data button
    const exportBtn = document.getElementById('export-data');
    if (exportBtn) {
        exportBtn.addEventListener('click', () => {
            exportData('csv');
        });
    }
    
    // Close modals on background click
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
            }
        });
    });
}

// Make functions globally available
window.viewEmployeeDetails = viewEmployeeDetails;
window.initializeApp = initializeApp;
window.downloadChart = downloadChart;
window.exportData = exportData;
