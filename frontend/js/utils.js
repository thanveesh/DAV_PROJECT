// Utility Functions
/**
 * Show/hide loading overlay
 */
function showLoading(show) {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.toggle('active', show);
    }
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info', duration = 3000) {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const icon = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    }[type] || 'fa-info-circle';
    
    toast.innerHTML = `
        <i class="fas ${icon}"></i>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'toastSlideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

/**
 * Open modal
 */
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
    }
}

/**
 * Close modal
 */
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
    }
}

/**
 * Format number with commas
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/**
 * Format currency
 */
function formatCurrency(amount) {
    return '$' + formatNumber(Math.round(amount));
}

/**
 * Get performance badge
 */
function getPerformanceBadge(percentile) {
    const p = parseFloat(percentile);
    if (p >= 75) {
        return '<span class="badge badge-success"><i class="fas fa-star"></i> Top Performer</span>';
    } else if (p >= 50) {
        return '<span class="badge badge-info"><i class="fas fa-thumbs-up"></i> Above Average</span>';
    } else if (p >= 25) {
        return '<span class="badge badge-warning"><i class="fas fa-minus"></i> Below Average</span>';
    } else {
        return '<span class="badge badge-danger"><i class="fas fa-exclamation-triangle"></i> Needs Support</span>';
    }
}

/**
 * Get risk level badge
 */
function getRiskBadge(employee) {
    const percentile = parseFloat(employee.performance_percentile);
    const qualityScore = parseFloat(employee.quality_score);
    const engagementScore = parseFloat(employee.engagement_score);
    
    if (percentile <= 10 || 
        (employee.overtime === 'Yes' && qualityScore < 45) ||
        engagementScore < 30) {
        return '<span class="badge badge-danger"><i class="fas fa-exclamation-circle"></i> High Risk</span>';
    } else if (percentile <= 25 || engagementScore < 50) {
        return '<span class="badge badge-warning"><i class="fas fa-exclamation-triangle"></i> Moderate Risk</span>';
    } else {
        return '<span class="badge badge-success"><i class="fas fa-check-circle"></i> Low Risk</span>';
    }
}

/**
 * Download chart as image
 */
function downloadChart(chartId) {
    Plotly.downloadImage(chartId, {
        format: 'png',
        width: 1200,
        height: 800,
        filename: `${chartId}_${new Date().toISOString().split('T')[0]}`
    });
    showToast('Chart downloaded successfully!', 'success');
}

/**
 * Export data as CSV
 */
function exportData(format) {
    if (format === 'csv' && API.employeeData) {
        API.exportToCSV(API.employeeData, `employee_data_${new Date().toISOString().split('T')[0]}.csv`);
        showToast('Data exported successfully!', 'success');
    }
}

/**
 * Generate report
 */
function generateReport(reportType) {
    showLoading(true);
    
    setTimeout(() => {
        showLoading(false);
        showToast(`${reportType} report generated successfully!`, 'success');
        
        // Add to recent reports table
        addRecentReport(reportType);
    }, 1500);
}

/**
 * Generate department report
 */
function generateDeptReport() {
    const select = document.getElementById('dept-report-select');
    const department = select.value;
    
    if (!department) {
        showToast('Please select a department', 'warning');
        return;
    }
    
    showLoading(true);
    setTimeout(() => {
        showLoading(false);
        showToast(`${department} report generated successfully!`, 'success');
        addRecentReport(`Department: ${department}`);
    }, 1500);
}

/**
 * Add recent report to table
 */
function addRecentReport(reportType) {
    const tbody = document.getElementById('recent-reports-tbody');
    if (!tbody) return;
    
    const now = new Date();
    const dateStr = now.toLocaleString();
    const size = (Math.random() * 5 + 1).toFixed(1) + ' MB';
    
    const row = document.createElement('tr');
    row.innerHTML = `
        <td>${reportType} Report</td>
        <td><span class="badge badge-info">PDF</span></td>
        <td>${dateStr}</td>
        <td>${size}</td>
        <td>
            <button class="btn-secondary btn-sm" onclick="showToast('Download started', 'success')">
                <i class="fas fa-download"></i> Download
            </button>
        </td>
    `;
    
    tbody.insertBefore(row, tbody.firstChild);
    
    // Keep only last 5 reports
    while (tbody.children.length > 5) {
        tbody.removeChild(tbody.lastChild);
    }
}

/**
 * Create pagination
 */
function createPagination(totalItems, currentPage, itemsPerPage, onPageChange) {
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    const container = document.getElementById('employees-pagination');
    if (!container) return;
    
    container.innerHTML = '';
    
    // Previous button
    const prevBtn = document.createElement('button');
    prevBtn.innerHTML = '<i class="fas fa-chevron-left"></i>';
    prevBtn.disabled = currentPage === 1;
    prevBtn.onclick = () => onPageChange(currentPage - 1);
    container.appendChild(prevBtn);
    
    // Page numbers
    const maxButtons = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxButtons / 2));
    let endPage = Math.min(totalPages, startPage + maxButtons - 1);
    
    if (endPage - startPage < maxButtons - 1) {
        startPage = Math.max(1, endPage - maxButtons + 1);
    }
    
    for (let i = startPage; i <= endPage; i++) {
        const pageBtn = document.createElement('button');
        pageBtn.textContent = i;
        pageBtn.classList.toggle('active', i === currentPage);
        pageBtn.onclick = () => onPageChange(i);
        container.appendChild(pageBtn);
    }
    
    // Next button
    const nextBtn = document.createElement('button');
    nextBtn.innerHTML = '<i class="fas fa-chevron-right"></i>';
    nextBtn.disabled = currentPage === totalPages;
    nextBtn.onclick = () => onPageChange(currentPage + 1);
    container.appendChild(nextBtn);
}

/**
 * Debounce function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Format employee details for modal
 */
function formatEmployeeDetails(employee) {
    return `
        <div class="employee-details">
            <div class="detail-section">
                <h3><i class="fas fa-user"></i> Basic Information</h3>
                <div class="detail-grid">
                    <div class="detail-item">
                        <label>Employee ID</label>
                        <span>${employee.employeenumber}</span>
                    </div>
                    <div class="detail-item">
                        <label>Age</label>
                        <span>${employee.age} years</span>
                    </div>
                    <div class="detail-item">
                        <label>Department</label>
                        <span>${employee.department}</span>
                    </div>
                    <div class="detail-item">
                        <label>Job Role</label>
                        <span>${employee.jobrole}</span>
                    </div>
                    <div class="detail-item">
                        <label>Years at Company</label>
                        <span>${employee.yearsatcompany} years</span>
                    </div>
                    <div class="detail-item">
                        <label>Monthly Income</label>
                        <span>${formatCurrency(employee.monthlyincome)}</span>
                    </div>
                </div>
            </div>
            
            <div class="detail-section">
                <h3><i class="fas fa-chart-line"></i> Performance Metrics</h3>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <label>Overall Performance</label>
                        <div class="metric-value">${parseFloat(employee.overall_performance).toFixed(1)}</div>
                        <div class="metric-bar">
                            <div class="metric-fill" style="width: ${employee.overall_performance}%; background: ${CONFIG.COLORS.primary}"></div>
                        </div>
                        <span class="metric-label">Percentile: ${parseFloat(employee.performance_percentile).toFixed(1)}%</span>
                    </div>
                    <div class="metric-card">
                        <label>Productivity Score</label>
                        <div class="metric-value">${parseFloat(employee.productivity_score).toFixed(1)}</div>
                        <div class="metric-bar">
                            <div class="metric-fill" style="width: ${employee.productivity_score}%; background: ${CONFIG.COLORS.success}"></div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <label>Quality Score</label>
                        <div class="metric-value">${parseFloat(employee.quality_score).toFixed(1)}</div>
                        <div class="metric-bar">
                            <div class="metric-fill" style="width: ${employee.quality_score}%; background: ${CONFIG.COLORS.info}"></div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <label>Engagement Score</label>
                        <div class="metric-value">${parseFloat(employee.engagement_score).toFixed(1)}</div>
                        <div class="metric-bar">
                            <div class="metric-fill" style="width: ${employee.engagement_score}%; background: ${CONFIG.COLORS.warning}"></div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="detail-section">
                <h3><i class="fas fa-info-circle"></i> Additional Information</h3>
                <div class="detail-grid">
                    <div class="detail-item">
                        <label>Job Satisfaction</label>
                        <span>${employee.jobsatisfaction}/4</span>
                    </div>
                    <div class="detail-item">
                        <label>Work-Life Balance</label>
                        <span>${employee.worklifebalance}/4</span>
                    </div>
                    <div class="detail-item">
                        <label>Job Involvement</label>
                        <span>${employee.jobinvolvement}/4</span>
                    </div>
                    <div class="detail-item">
                        <label>Performance Rating</label>
                        <span>${employee.performancerating}/4</span>
                    </div>
                    <div class="detail-item">
                        <label>Training Hours (Last Year)</label>
                        <span>${employee.trainingtimeslastyear} hours</span>
                    </div>
                    <div class="detail-item">
                        <label>Overtime</label>
                        <span class="badge ${employee.overtime === 'Yes' ? 'badge-warning' : 'badge-success'}">
                            ${employee.overtime}
                        </span>
                    </div>
                    <div class="detail-item">
                        <label>Attrition Status</label>
                        <span class="badge ${employee.attrition === 'Yes' ? 'badge-danger' : 'badge-success'}">
                            ${employee.attrition === 'Yes' ? 'Left Company' : 'Active'}
                        </span>
                    </div>
                    <div class="detail-item">
                        <label>Risk Level</label>
                        <span>${getRiskBadge(employee)}</span>
                    </div>
                </div>
            </div>
            
            <div class="modal-actions">
                <button class="btn-primary" onclick="showToast('Report generated for Employee #${employee.employeenumber}', 'success')">
                    <i class="fas fa-file-download"></i> Generate Report
                </button>
                <button class="btn-secondary" onclick="closeModal('employee-modal')">
                    <i class="fas fa-times"></i> Close
                </button>
            </div>
        </div>
        
        <style>
            .employee-details { padding: 1rem; }
            .detail-section { margin-bottom: 2rem; }
            .detail-section h3 { margin-bottom: 1rem; font-size: 1.125rem; display: flex; align-items: center; gap: 0.5rem; }
            .detail-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; }
            .detail-item { display: flex; flex-direction: column; gap: 0.25rem; }
            .detail-item label { font-size: 0.875rem; color: #6b7280; font-weight: 600; }
            .detail-item span { font-size: 1rem; color: #111827; }
            .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; }
            .metric-card { padding: 1rem; background: #f9fafb; border-radius: 0.5rem; }
            .metric-card label { font-size: 0.75rem; color: #6b7280; font-weight: 600; text-transform: uppercase; }
            .metric-value { font-size: 2rem; font-weight: 700; margin: 0.5rem 0; }
            .metric-bar { height: 8px; background: #e5e7eb; border-radius: 4px; overflow: hidden; margin: 0.5rem 0; }
            .metric-fill { height: 100%; transition: width 0.3s ease; }
            .metric-label { font-size: 0.75rem; color: #6b7280; }
            .modal-actions { display: flex; gap: 1rem; justify-content: flex-end; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #e5e7eb; }
        </style>
    `;
}
