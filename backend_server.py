#!/usr/bin/env python3
"""
Flask Backend Server for Employee Performance Dashboard

This server provides REST API endpoints to serve employee data
and insights to the frontend dashboard.
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import pandas as pd
import os
import sys

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from employee_performance_analysis import EmployeePerformanceAnalyzer
from performance_insights_engine import PerformanceAnalysisEngine

app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)  # Enable CORS for frontend access

# Initialize analyzers
DATA_PATH = 'outputs/cleaned_employee_data.csv'
perf_analyzer = None
insights_engine = None

def initialize_analyzers():
    """Initialize performance analyzers with data"""
    global perf_analyzer, insights_engine
    
    if os.path.exists(DATA_PATH):
        perf_analyzer = EmployeePerformanceAnalyzer(DATA_PATH)
        insights_engine = PerformanceAnalysisEngine()
        print(f"✓ Loaded data for {len(perf_analyzer.df)} employees")
    else:
        print(f"⚠ Warning: Data file not found at {DATA_PATH}")

# Routes

@app.route('/')
def index():
    """Serve the main dashboard page"""
    return send_from_directory('frontend', 'index.html')

@app.route('/api/employees', methods=['GET'])
def get_employees():
    """Get all employees with optional filters"""
    if not perf_analyzer:
        return jsonify({'error': 'Data not loaded'}), 500
    
    # Get query parameters
    department = request.args.get('department')
    min_performance = request.args.get('min_performance', type=float)
    max_performance = request.args.get('max_performance', type=float)
    search = request.args.get('search')
    
    df = perf_analyzer.df.copy()
    
    # Apply filters
    if department:
        df = df[df['department'] == department]
    
    if min_performance is not None:
        df = df[df['overall_performance'] >= min_performance]
    
    if max_performance is not None:
        df = df[df['overall_performance'] <= max_performance]
    
    if search:
        search_lower = search.lower()
        df = df[
            df['employeenumber'].astype(str).str.contains(search_lower) |
            df['department'].str.lower().str.contains(search_lower) |
            df['jobrole'].str.lower().str.contains(search_lower)
        ]
    
    # Convert to JSON
    employees = df.to_dict('records')
    
    return jsonify({
        'count': len(employees),
        'employees': employees
    })

@app.route('/api/employees/<int:employee_id>', methods=['GET'])
def get_employee(employee_id):
    """Get detailed information for a specific employee"""
    if not perf_analyzer:
        return jsonify({'error': 'Data not loaded'}), 500
    
    profile = perf_analyzer.get_employee_profile(employee_id)
    
    if 'error' in profile:
        return jsonify(profile), 404
    
    return jsonify(profile)

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get company-wide statistics"""
    if not perf_analyzer:
        return jsonify({'error': 'Data not loaded'}), 500
    
    department = request.args.get('department')
    role = request.args.get('role')
    
    if department:
        stats = perf_analyzer.get_performance_statistics(department=department)
    elif role:
        stats = perf_analyzer.get_performance_statistics(role=role)
    else:
        stats = perf_analyzer.get_performance_statistics()
    
    return jsonify(stats)

@app.route('/api/departments', methods=['GET'])
def get_departments():
    """Get list of all departments"""
    if not perf_analyzer:
        return jsonify({'error': 'Data not loaded'}), 500
    
    departments = perf_analyzer.df['department'].unique().tolist()
    
    # Get department statistics
    dept_stats = {}
    for dept in departments:
        dept_data = perf_analyzer.df[perf_analyzer.df['department'] == dept]
        dept_stats[dept] = {
            'count': len(dept_data),
            'avg_performance': float(dept_data['overall_performance'].mean()),
            'avg_productivity': float(dept_data['productivity_score'].mean()),
            'avg_quality': float(dept_data['quality_score'].mean()),
            'avg_engagement': float(dept_data['engagement_score'].mean())
        }
    
    return jsonify({
        'departments': departments,
        'statistics': dept_stats
    })

@app.route('/api/top-performers', methods=['GET'])
def get_top_performers():
    """Get top performing employees"""
    if not perf_analyzer:
        return jsonify({'error': 'Data not loaded'}), 500
    
    n = request.args.get('n', default=10, type=int)
    
    top_performers = perf_analyzer.get_top_performers(n=n)
    
    return jsonify({
        'count': len(top_performers),
        'employees': top_performers.to_dict('records')
    })

@app.route('/api/high-risk', methods=['GET'])
def get_high_risk():
    """Get high-risk employees needing support"""
    if not perf_analyzer:
        return jsonify({'error': 'Data not loaded'}), 500
    
    threshold = request.args.get('threshold', default=10, type=int)
    
    high_risk = perf_analyzer.df[
        (perf_analyzer.df['performance_percentile'] <= threshold) |
        ((perf_analyzer.df['overtime'] == 'Yes') & (perf_analyzer.df['quality_score'] < 45)) |
        (perf_analyzer.df['engagement_score'] < 30)
    ]
    
    return jsonify({
        'count': len(high_risk),
        'employees': high_risk.to_dict('records')
    })

@app.route('/api/insights/<int:employee_id>', methods=['GET'])
def get_employee_insights(employee_id):
    """Get AI-powered insights for a specific employee"""
    if not perf_analyzer or not insights_engine:
        return jsonify({'error': 'Analyzers not initialized'}), 500
    
    # Get employee data
    employee_data = perf_analyzer.df[
        perf_analyzer.df['employeenumber'] == employee_id
    ]
    
    if len(employee_data) == 0:
        return jsonify({'error': 'Employee not found'}), 404
    
    employee_data = employee_data.iloc[0]
    
    # Get profile
    profile = perf_analyzer.get_employee_profile(employee_id)
    if 'error' in profile:
        return jsonify(profile), 404
    
    # Get averages for comparison
    dept = profile['basic_info']['department']
    role = profile['basic_info']['job_role']
    
    dept_avg = perf_analyzer._get_department_averages(dept)
    company_avg = perf_analyzer._get_company_averages()
    role_avg = perf_analyzer._get_role_averages(role)
    
    # Generate insights
    insights = insights_engine.analyze(employee_data, dept_avg, company_avg, role_avg)
    
    return jsonify(insights)

@app.route('/api/analytics/correlation', methods=['GET'])
def get_correlation_matrix():
    """Get correlation matrix for performance factors"""
    if not perf_analyzer:
        return jsonify({'error': 'Data not loaded'}), 500
    
    # Select numeric columns
    numeric_cols = [
        'age', 'monthlyincome', 'yearsatcompany', 'trainingtimeslastyear',
        'productivity_score', 'quality_score', 'engagement_score', 'overall_performance'
    ]
    
    correlation = perf_analyzer.df[numeric_cols].corr()
    
    return jsonify({
        'variables': numeric_cols,
        'matrix': correlation.to_dict()
    })

@app.route('/api/analytics/trends', methods=['GET'])
def get_performance_trends():
    """Get performance trends over time"""
    if not perf_analyzer:
        return jsonify({'error': 'Data not loaded'}), 500
    
    metric = request.args.get('metric', default='overall_performance')
    
    # Group by years at company
    trends = perf_analyzer.df.groupby('yearsatcompany')[metric].agg(['mean', 'count', 'std'])
    
    return jsonify({
        'metric': metric,
        'data': trends.to_dict('index')
    })

@app.route('/api/export/csv', methods=['GET'])
def export_csv():
    """Export employee data as CSV"""
    if not perf_analyzer:
        return jsonify({'error': 'Data not loaded'}), 500
    
    # Create CSV
    csv_data = perf_analyzer.df.to_csv(index=False)
    
    from flask import Response
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=employee_data.csv'}
    )

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'data_loaded': perf_analyzer is not None,
        'employee_count': len(perf_analyzer.df) if perf_analyzer else 0
    })

# Error handlers

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Main

if __name__ == '__main__':
    print("="*60)
    print("Employee Performance Dashboard - Backend Server")
    print("="*60)
    
    # Initialize analyzers
    initialize_analyzers()
    
    port = int(os.environ.get('PORT', 5000))
    print("\n📊 Starting server...")
    print(f"🌐 Frontend: http://localhost:{port}")
    print(f"🔌 API: http://localhost:{port}/api")
    print("\n💡 Available endpoints:")
    print("   GET /api/employees")
    print("   GET /api/employees/<id>")
    print("   GET /api/statistics")
    print("   GET /api/departments")
    print("   GET /api/top-performers")
    print("   GET /api/high-risk")
    print("   GET /api/insights/<id>")
    print("   GET /api/analytics/correlation")
    print("   GET /api/analytics/trends")
    print("   GET /api/export/csv")
    print("   GET /api/health")
    print("\n" + "="*60)
    print("Press Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    # Run server (debug=False in production)
    app.run(debug=os.environ.get('FLASK_ENV') != 'production', host='0.0.0.0', port=port)
