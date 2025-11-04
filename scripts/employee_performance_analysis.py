#!/usr/bin/env python3
"""
Employee Performance Analysis Module

This module provides comprehensive performance analysis for employees including:
- Individual performance metrics and KPIs
- Comparison to department and company averages
- Performance trend analysis
- Actionable insights and recommendations

"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Set plotting style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)


class EmployeePerformanceAnalyzer:
    """
    A comprehensive employee performance analysis system.
    
    This class provides methods to analyze employee performance metrics,
    generate performance profiles, identify top performers, and provide
    actionable insights.
    """
    
    def __init__(self, data_path: str):
        """
        Initialize the performance analyzer with employee data.
        
        Parameters:
        -----------
        data_path : str
            Path to the cleaned employee data CSV file
        """
        self.df = pd.read_csv(data_path)
        self._prepare_performance_metrics()
        
    def _prepare_performance_metrics(self):
        """
        Calculate derived performance metrics from available data.
        
        Creates composite scores for productivity, quality, and overall performance.
        """
        # Normalize performance rating to 0-100 scale
        if 'performancerating' in self.df.columns:
            self.df['performance_score'] = (self.df['performancerating'] / 
                                            self.df['performancerating'].max() * 100)
        
        # Calculate productivity score based on multiple factors
        self.df['productivity_score'] = self._calculate_productivity_score()
        
        # Calculate quality score
        self.df['quality_score'] = self._calculate_quality_score()
        
        # Calculate engagement score
        self.df['engagement_score'] = self._calculate_engagement_score()
        
        # Overall performance score (weighted average)
        self.df['overall_performance'] = (
            0.35 * self.df['productivity_score'] +
            0.30 * self.df['quality_score'] +
            0.20 * self.df['engagement_score'] +
            0.15 * self.df.get('performance_score', 75)  # Default if not available
        )
        
        # Calculate percentile rankings
        self.df['performance_percentile'] = self.df['overall_performance'].rank(pct=True) * 100
        
    def _calculate_productivity_score(self) -> pd.Series:
        """
        Calculate productivity score based on work metrics.
        
        Returns:
        --------
        pd.Series
            Productivity scores (0-100)
        """
        score = pd.Series(0.0, index=self.df.index)
        
        # Years at company (experience factor, capped at 20 years)
        if 'yearsatcompany' in self.df.columns:
            years_norm = np.minimum(self.df['yearsatcompany'], 20) / 20 * 30
            score += years_norm
        
        # Training times (continuous learning)
        if 'trainingtimeslastyear' in self.df.columns:
            training_norm = np.minimum(self.df['trainingtimeslastyear'], 6) / 6 * 25
            score += training_norm
        
        # Job involvement (1-4 scale)
        if 'jobinvolvement' in self.df.columns:
            involvement_norm = (self.df['jobinvolvement'] - 1) / 3 * 25
            score += involvement_norm
        
        # Total working years (overall experience)
        if 'totalworkingyears' in self.df.columns:
            total_exp_norm = np.minimum(self.df['totalworkingyears'], 30) / 30 * 20
            score += total_exp_norm
        
        return score
    
    def _calculate_quality_score(self) -> pd.Series:
        """
        Calculate quality of work score.
        
        Returns:
        --------
        pd.Series
            Quality scores (0-100)
        """
        score = pd.Series(0.0, index=self.df.index)
        
        # Performance rating
        if 'performancerating' in self.df.columns:
            perf_norm = (self.df['performancerating'] - self.df['performancerating'].min())
            perf_norm = perf_norm / (self.df['performancerating'].max() - 
                                     self.df['performancerating'].min()) * 40
            score += perf_norm
        
        # Job satisfaction (1-4 scale)
        if 'jobsatisfaction' in self.df.columns:
            sat_norm = (self.df['jobsatisfaction'] - 1) / 3 * 30
            score += sat_norm
        
        # Years in current role (mastery)
        if 'yearsincurrentrole' in self.df.columns:
            role_exp = np.minimum(self.df['yearsincurrentrole'], 10) / 10 * 30
            score += role_exp
        
        return score
    
    def _calculate_engagement_score(self) -> pd.Series:
        """
        Calculate employee engagement score.
        
        Returns:
        --------
        pd.Series
            Engagement scores (0-100)
        """
        score = pd.Series(0.0, index=self.df.index)
        
        # Environment satisfaction
        if 'environmentsatisfaction' in self.df.columns:
            env_norm = (self.df['environmentsatisfaction'] - 1) / 3 * 25
            score += env_norm
        
        # Relationship satisfaction
        if 'relationshipsatisfaction' in self.df.columns:
            rel_norm = (self.df['relationshipsatisfaction'] - 1) / 3 * 25
            score += rel_norm
        
        # Work-life balance
        if 'worklifebalance' in self.df.columns:
            wlb_norm = (self.df['worklifebalance'] - 1) / 3 * 25
            score += wlb_norm
        
        # Overtime (negative factor if excessive)
        if 'overtime_flag' in self.df.columns:
            overtime_penalty = (1 - self.df['overtime_flag']) * 25
            score += overtime_penalty
        
        return score
    
    def get_employee_profile(self, employee_id: int) -> Dict:
        """
        Generate comprehensive performance profile for a specific employee.
        
        Parameters:
        -----------
        employee_id : int
            The employee number/ID to analyze
        
        Returns:
        --------
        dict
            Detailed performance profile with metrics, ratings, and insights
        """
        # Find employee
        employee = self.df[self.df['employeenumber'] == employee_id]
        
        if employee.empty:
            return {"error": f"Employee ID {employee_id} not found"}
        
        emp = employee.iloc[0]
        
        # Get department and role averages for comparison
        dept_avg = self._get_department_averages(emp.get('department', 'Unknown'))
        company_avg = self._get_company_averages()
        role_avg = self._get_role_averages(emp.get('jobrole', 'Unknown'))
        
        # Build profile
        profile = {
            'employee_id': int(emp['employeenumber']),
            'basic_info': {
                'age': int(emp['age']) if pd.notna(emp['age']) else None,
                'gender': emp.get('gender', 'Unknown'),
                'department': emp.get('department', 'Unknown'),
                'job_role': emp.get('jobrole', 'Unknown'),
                'job_level': int(emp['joblevel']) if pd.notna(emp.get('joblevel')) else None,
                'years_at_company': int(emp['yearsatcompany']) if pd.notna(emp['yearsatcompany']) else None,
                'total_experience': int(emp['totalworkingyears']) if pd.notna(emp['totalworkingyears']) else None,
            },
            'performance_metrics': {
                'overall_performance': round(emp['overall_performance'], 2),
                'productivity_score': round(emp['productivity_score'], 2),
                'quality_score': round(emp['quality_score'], 2),
                'engagement_score': round(emp['engagement_score'], 2),
                'performance_percentile': round(emp['performance_percentile'], 1),
            },
            'comparison_to_averages': {
                'vs_company': {
                    'overall': round(emp['overall_performance'] - company_avg['overall'], 2),
                    'productivity': round(emp['productivity_score'] - company_avg['productivity'], 2),
                    'quality': round(emp['quality_score'] - company_avg['quality'], 2),
                    'engagement': round(emp['engagement_score'] - company_avg['engagement'], 2),
                },
                'vs_department': {
                    'overall': round(emp['overall_performance'] - dept_avg['overall'], 2),
                    'productivity': round(emp['productivity_score'] - dept_avg['productivity'], 2),
                    'quality': round(emp['quality_score'] - dept_avg['quality'], 2),
                    'engagement': round(emp['engagement_score'] - dept_avg['engagement'], 2),
                },
                'vs_role': {
                    'overall': round(emp['overall_performance'] - role_avg['overall'], 2),
                    'productivity': round(emp['productivity_score'] - role_avg['productivity'], 2),
                    'quality': round(emp['quality_score'] - role_avg['quality'], 2),
                    'engagement': round(emp['engagement_score'] - role_avg['engagement'], 2),
                }
            },
            'detailed_metrics': {
                'job_involvement': int(emp['jobinvolvement']) if pd.notna(emp.get('jobinvolvement')) else None,
                'job_satisfaction': int(emp['jobsatisfaction']) if pd.notna(emp.get('jobsatisfaction')) else None,
                'environment_satisfaction': int(emp['environmentsatisfaction']) if pd.notna(emp.get('environmentsatisfaction')) else None,
                'work_life_balance': int(emp['worklifebalance']) if pd.notna(emp.get('worklifebalance')) else None,
                'training_times_last_year': int(emp['trainingtimeslastyear']) if pd.notna(emp.get('trainingtimeslastyear')) else None,
                'years_since_promotion': int(emp['yearssincelastpromotion']) if pd.notna(emp.get('yearssincelastpromotion')) else None,
                'works_overtime': emp.get('overtime', 'Unknown'),
                'monthly_income': int(emp['monthlyincome']) if pd.notna(emp.get('monthlyincome')) else None,
            },
            'performance_rating': self._get_performance_rating(emp),
            'strengths': self._identify_strengths(emp, dept_avg, company_avg),
            'improvement_areas': self._identify_improvement_areas(emp, dept_avg, company_avg),
            'trend_analysis': self._analyze_performance_trend(emp),
            'recommendations': self._generate_recommendations(emp, dept_avg, company_avg),
            'risk_factors': self._identify_risk_factors(emp),
        }
        
        return profile
    
    def _get_department_averages(self, department: str) -> Dict:
        """Calculate average metrics for a specific department."""
        dept_data = self.df[self.df['department'] == department]
        return {
            'overall': dept_data['overall_performance'].mean(),
            'productivity': dept_data['productivity_score'].mean(),
            'quality': dept_data['quality_score'].mean(),
            'engagement': dept_data['engagement_score'].mean(),
        }
    
    def _get_company_averages(self) -> Dict:
        """Calculate company-wide average metrics."""
        return {
            'overall': self.df['overall_performance'].mean(),
            'productivity': self.df['productivity_score'].mean(),
            'quality': self.df['quality_score'].mean(),
            'engagement': self.df['engagement_score'].mean(),
        }
    
    def _get_role_averages(self, role: str) -> Dict:
        """Calculate average metrics for a specific job role."""
        role_data = self.df[self.df['jobrole'] == role]
        return {
            'overall': role_data['overall_performance'].mean(),
            'productivity': role_data['productivity_score'].mean(),
            'quality': role_data['quality_score'].mean(),
            'engagement': role_data['engagement_score'].mean(),
        }
    
    def _get_performance_rating(self, emp: pd.Series) -> str:
        """Determine performance rating category."""
        score = emp['overall_performance']
        percentile = emp['performance_percentile']
        
        if percentile >= 90:
            return "Exceptional (Top 10%)"
        elif percentile >= 75:
            return "Excellent (Top 25%)"
        elif percentile >= 50:
            return "Good (Above Average)"
        elif percentile >= 25:
            return "Satisfactory (Average)"
        else:
            return "Needs Improvement (Below Average)"
    
    def _identify_strengths(self, emp: pd.Series, dept_avg: Dict, company_avg: Dict) -> List[str]:
        """Identify employee's key strengths."""
        strengths = []
        
        # Check each metric against department average
        if emp['productivity_score'] > dept_avg['productivity'] + 10:
            strengths.append("High productivity and efficiency")
        
        if emp['quality_score'] > dept_avg['quality'] + 10:
            strengths.append("Excellent quality of work")
        
        if emp['engagement_score'] > dept_avg['engagement'] + 10:
            strengths.append("Strong employee engagement")
        
        # Check specific metrics
        if emp.get('jobinvolvement', 0) >= 3:
            strengths.append("High job involvement and commitment")
        
        if emp.get('trainingtimeslastyear', 0) >= 4:
            strengths.append("Active learner - high training participation")
        
        if emp.get('relationshipsatisfaction', 0) >= 3:
            strengths.append("Strong interpersonal relationships")
        
        if emp.get('worklifebalance', 0) >= 3:
            strengths.append("Maintains healthy work-life balance")
        
        if emp.get('yearsatcompany', 0) >= 5 and emp.get('attrition', 'No') == 'No':
            strengths.append("Loyal and committed to company")
        
        if not strengths:
            strengths.append("Consistent performance")
        
        return strengths
    
    def _identify_improvement_areas(self, emp: pd.Series, dept_avg: Dict, company_avg: Dict) -> List[str]:
        """Identify areas where employee can improve."""
        improvements = []
        
        # Check each metric against department average
        if emp['productivity_score'] < dept_avg['productivity'] - 10:
            improvements.append("Productivity could be improved")
        
        if emp['quality_score'] < dept_avg['quality'] - 10:
            improvements.append("Focus on improving work quality")
        
        if emp['engagement_score'] < dept_avg['engagement'] - 10:
            improvements.append("Employee engagement needs attention")
        
        # Check specific metrics
        if emp.get('jobsatisfaction', 4) <= 2:
            improvements.append("Low job satisfaction - may need role adjustment")
        
        if emp.get('environmentsatisfaction', 4) <= 2:
            improvements.append("Work environment satisfaction is low")
        
        if emp.get('worklifebalance', 4) <= 2:
            improvements.append("Work-life balance needs improvement")
        
        if emp.get('trainingtimeslastyear', 0) < 2:
            improvements.append("Limited training participation - encourage skill development")
        
        if emp.get('yearssincelastpromotion', 0) >= 5:
            improvements.append("No recent promotion - career growth discussion needed")
        
        if emp.get('overtime', 'No') == 'Yes':
            improvements.append("Working overtime - monitor workload and burnout risk")
        
        if not improvements:
            improvements.append("No major areas of concern identified")
        
        return improvements
    
    def _analyze_performance_trend(self, emp: pd.Series) -> Dict:
        """Analyze performance trend indicators."""
        trend = {
            'status': 'Stable',
            'indicators': [],
            'trajectory': 'Maintaining current performance level'
        }
        
        # Analyze years at company vs performance
        years = emp.get('yearsatcompany', 0)
        percentile = emp['performance_percentile']
        
        if percentile >= 75:
            trend['status'] = 'High Performer'
            trend['trajectory'] = 'Consistently strong performance'
        elif percentile >= 50:
            trend['status'] = 'Steady Performer'
            trend['trajectory'] = 'Reliable and consistent'
        
        # Check for growth indicators
        if emp.get('trainingtimeslastyear', 0) >= 3:
            trend['indicators'].append('Active in skill development')
        
        if emp.get('jobinvolvement', 0) >= 3:
            trend['indicators'].append('High engagement suggests growth potential')
        
        # Check for warning signs
        if emp.get('jobsatisfaction', 4) <= 2:
            trend['indicators'].append('Low satisfaction may indicate declining engagement')
        
        if emp.get('yearssincelastpromotion', 0) >= 5 and years >= 5:
            trend['indicators'].append('Overdue for promotion consideration')
        
        return trend
    
    def _generate_recommendations(self, emp: pd.Series, dept_avg: Dict, company_avg: Dict) -> List[str]:
        """Generate actionable recommendations for the employee."""
        recommendations = []
        
        # Performance-based recommendations
        percentile = emp['performance_percentile']
        
        if percentile >= 90:
            recommendations.append("Consider for leadership roles or mentorship programs")
            recommendations.append("Provide challenging projects to maintain engagement")
            recommendations.append("Discuss career advancement opportunities")
        elif percentile >= 75:
            recommendations.append("Potential candidate for specialized training programs")
            recommendations.append("Consider for team lead positions")
        elif percentile < 25:
            recommendations.append("Develop performance improvement plan")
            recommendations.append("Schedule regular check-ins with manager")
            recommendations.append("Identify training needs and skill gaps")
        
        # Specific metric recommendations
        if emp.get('trainingtimeslastyear', 0) < 2:
            recommendations.append("Encourage participation in training programs")
        
        if emp.get('worklifebalance', 4) <= 2:
            recommendations.append("Review workload and adjust if necessary")
        
        if emp.get('jobsatisfaction', 4) <= 2:
            recommendations.append("Conduct one-on-one to understand concerns")
        
        if emp.get('environmentsatisfaction', 4) <= 2:
            recommendations.append("Address workplace environment concerns")
        
        if emp.get('yearssincelastpromotion', 0) >= 5:
            recommendations.append("Evaluate for promotion or career development opportunities")
        
        if emp.get('overtime', 'No') == 'Yes' and emp.get('worklifebalance', 4) <= 2:
            recommendations.append("Monitor for burnout risk - reduce overtime if possible")
        
        # Engagement recommendations
        if emp['engagement_score'] < dept_avg['engagement'] - 10:
            recommendations.append("Implement engagement initiatives specific to this employee")
        
        return recommendations if recommendations else ["Continue current development path"]
    
    def _identify_risk_factors(self, emp: pd.Series) -> Dict:
        """Identify attrition and performance risk factors."""
        risks = {
            'attrition_risk': 'Low',
            'performance_risk': 'Low',
            'risk_factors': []
        }
        
        risk_score = 0
        
        # Attrition risk factors
        if emp.get('attrition', 'No') == 'Yes':
            risks['attrition_risk'] = 'High (Already left)'
            return risks
        
        if emp.get('jobsatisfaction', 4) <= 2:
            risk_score += 2
            risks['risk_factors'].append('Low job satisfaction')
        
        if emp.get('environmentsatisfaction', 4) <= 2:
            risk_score += 1
            risks['risk_factors'].append('Low environment satisfaction')
        
        if emp.get('worklifebalance', 4) <= 2:
            risk_score += 2
            risks['risk_factors'].append('Poor work-life balance')
        
        if emp.get('overtime', 'No') == 'Yes':
            risk_score += 1
            risks['risk_factors'].append('Working overtime')
        
        if emp.get('yearssincelastpromotion', 0) >= 5:
            risk_score += 2
            risks['risk_factors'].append('No recent promotion')
        
        if emp['overall_performance'] < 50:
            risk_score += 2
            risks['risk_factors'].append('Below average performance')
        
        # Determine overall risk
        if risk_score >= 5:
            risks['attrition_risk'] = 'High'
            risks['performance_risk'] = 'High'
        elif risk_score >= 3:
            risks['attrition_risk'] = 'Medium'
            risks['performance_risk'] = 'Medium'
        
        return risks
    
    def get_top_performers(self, n: int = 10, department: Optional[str] = None) -> pd.DataFrame:
        """
        Identify top performing employees.
        
        Parameters:
        -----------
        n : int
            Number of top performers to return
        department : str, optional
            Filter by specific department
        
        Returns:
        --------
        pd.DataFrame
            DataFrame with top performers and their metrics
        """
        df = self.df.copy()
        
        if department:
            df = df[df['department'] == department]
        
        top = df.nlargest(n, 'overall_performance')[
            ['employeenumber', 'department', 'jobrole', 'overall_performance', 
             'productivity_score', 'quality_score', 'engagement_score', 
             'performance_percentile']
        ].round(2)
        
        return top
    
    def get_employees_needing_support(self, threshold_percentile: float = 25) -> pd.DataFrame:
        """
        Identify employees who need additional support or training.
        
        Parameters:
        -----------
        threshold_percentile : float
            Percentile threshold below which employees need support
        
        Returns:
        --------
        pd.DataFrame
            DataFrame with employees needing support
        """
        needs_support = self.df[self.df['performance_percentile'] <= threshold_percentile][
            ['employeenumber', 'department', 'jobrole', 'overall_performance',
             'productivity_score', 'quality_score', 'engagement_score',
             'performance_percentile', 'jobsatisfaction', 'attrition']
        ].sort_values('overall_performance').round(2)
        
        return needs_support
    
    def get_performance_statistics(self, department: Optional[str] = None) -> Dict:
        """
        Calculate comprehensive performance statistics.
        
        Parameters:
        -----------
        department : str, optional
            Filter by specific department
        
        Returns:
        --------
        dict
            Statistical summary of performance metrics
        """
        df = self.df.copy()
        
        if department:
            df = df[df['department'] == department]
            scope = f"Department: {department}"
        else:
            scope = "Company-wide"
        
        stats = {
            'scope': scope,
            'total_employees': len(df),
            'overall_performance': {
                'mean': round(df['overall_performance'].mean(), 2),
                'median': round(df['overall_performance'].median(), 2),
                'std': round(df['overall_performance'].std(), 2),
                'min': round(df['overall_performance'].min(), 2),
                'max': round(df['overall_performance'].max(), 2),
            },
            'productivity': {
                'mean': round(df['productivity_score'].mean(), 2),
                'std': round(df['productivity_score'].std(), 2),
            },
            'quality': {
                'mean': round(df['quality_score'].mean(), 2),
                'std': round(df['quality_score'].std(), 2),
            },
            'engagement': {
                'mean': round(df['engagement_score'].mean(), 2),
                'std': round(df['engagement_score'].std(), 2),
            },
            'distribution': {
                'top_10_percent': len(df[df['performance_percentile'] >= 90]),
                'top_25_percent': len(df[df['performance_percentile'] >= 75]),
                'bottom_25_percent': len(df[df['performance_percentile'] <= 25]),
                'bottom_10_percent': len(df[df['performance_percentile'] <= 10]),
            },
            'attrition_by_performance': {
                'top_performers': round(df[df['performance_percentile'] >= 75]['attrition'].value_counts(normalize=True).get('Yes', 0) * 100, 2),
                'bottom_performers': round(df[df['performance_percentile'] <= 25]['attrition'].value_counts(normalize=True).get('Yes', 0) * 100, 2),
            }
        }
        
        return stats
    
    def visualize_employee_performance(self, employee_id: int, save_path: Optional[str] = None):
        """
        Create comprehensive visualization of employee performance.
        
        Parameters:
        -----------
        employee_id : int
            Employee number to visualize
        save_path : str, optional
            Path to save the visualization
        """
        profile = self.get_employee_profile(employee_id)
        
        if 'error' in profile:
            print(profile['error'])
            return
        
        # Create figure with subplots
        fig = plt.figure(figsize=(16, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # Title
        emp_info = profile['basic_info']
        fig.suptitle(f"Performance Analysis: Employee #{employee_id}\n"
                    f"{emp_info['job_role']} - {emp_info['department']}", 
                    fontsize=16, fontweight='bold')
        
        # 1. Overall Performance Score
        ax1 = fig.add_subplot(gs[0, 0])
        metrics = profile['performance_metrics']
        score = metrics['overall_performance']
        colors = ['#d62728' if score < 50 else '#ff7f0e' if score < 75 else '#2ca02c']
        ax1.barh(['Overall\nPerformance'], [score], color=colors[0], edgecolor='black')
        ax1.set_xlim(0, 100)
        ax1.set_xlabel('Score')
        ax1.set_title('Overall Performance Score', fontweight='bold')
        ax1.text(score + 2, 0, f'{score:.1f}', va='center', fontweight='bold')
        
        # 2. Performance Breakdown
        ax2 = fig.add_subplot(gs[0, 1])
        metric_names = ['Productivity', 'Quality', 'Engagement']
        metric_values = [metrics['productivity_score'], metrics['quality_score'], 
                        metrics['engagement_score']]
        bars = ax2.bar(metric_names, metric_values, color=['#1f77b4', '#2ca02c', '#ff7f0e'],
                      edgecolor='black')
        ax2.set_ylim(0, 100)
        ax2.set_ylabel('Score')
        ax2.set_title('Performance Breakdown', fontweight='bold')
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 2,
                    f'{height:.1f}', ha='center', va='bottom', fontweight='bold')
        
        # 3. Percentile Ranking
        ax3 = fig.add_subplot(gs[0, 2])
        percentile = metrics['performance_percentile']
        wedges, texts, autotexts = ax3.pie([percentile, 100-percentile], 
                                           labels=['Percentile', ''],
                                           autopct='%1.1f%%',
                                           startangle=90,
                                           colors=['#2ca02c', '#e0e0e0'])
        ax3.set_title(f'Performance Percentile\n(Top {100-percentile:.1f}%)', 
                     fontweight='bold')
        
        # 4. Comparison to Averages
        ax4 = fig.add_subplot(gs[1, :])
        comparisons = profile['comparison_to_averages']
        categories = ['Overall', 'Productivity', 'Quality', 'Engagement']
        company = [comparisons['vs_company']['overall'], comparisons['vs_company']['productivity'],
                  comparisons['vs_company']['quality'], comparisons['vs_company']['engagement']]
        department = [comparisons['vs_department']['overall'], comparisons['vs_department']['productivity'],
                     comparisons['vs_department']['quality'], comparisons['vs_department']['engagement']]
        role = [comparisons['vs_role']['overall'], comparisons['vs_role']['productivity'],
               comparisons['vs_role']['quality'], comparisons['vs_role']['engagement']]
        
        x = np.arange(len(categories))
        width = 0.25
        
        ax4.bar(x - width, company, width, label='vs Company Avg', color='#1f77b4', edgecolor='black')
        ax4.bar(x, department, width, label='vs Department Avg', color='#ff7f0e', edgecolor='black')
        ax4.bar(x + width, role, width, label='vs Role Avg', color='#2ca02c', edgecolor='black')
        
        ax4.set_ylabel('Difference from Average')
        ax4.set_title('Performance Comparison to Averages', fontweight='bold')
        ax4.set_xticks(x)
        ax4.set_xticklabels(categories)
        ax4.legend()
        ax4.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        ax4.grid(axis='y', alpha=0.3)
        
        # 5. Strengths
        ax5 = fig.add_subplot(gs[2, 0])
        ax5.axis('off')
        strengths_text = "STRENGTHS:\n\n" + "\n".join(f"• {s}" for s in profile['strengths'][:5])
        ax5.text(0.05, 0.95, strengths_text, transform=ax5.transAxes,
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.3))
        
        # 6. Improvement Areas
        ax6 = fig.add_subplot(gs[2, 1])
        ax6.axis('off')
        improvements_text = "IMPROVEMENT AREAS:\n\n" + "\n".join(f"• {i}" for i in profile['improvement_areas'][:5])
        ax6.text(0.05, 0.95, improvements_text, transform=ax6.transAxes,
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.3))
        
        # 7. Recommendations
        ax7 = fig.add_subplot(gs[2, 2])
        ax7.axis('off')
        recommendations_text = "RECOMMENDATIONS:\n\n" + "\n".join(f"• {r}" for r in profile['recommendations'][:5])
        ax7.text(0.05, 0.95, recommendations_text, transform=ax7.transAxes,
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Visualization saved to {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def generate_department_performance_report(self, department: str, save_path: Optional[str] = None):
        """
        Generate comprehensive performance report for a department.
        
        Parameters:
        -----------
        department : str
            Department name
        save_path : str, optional
            Path to save the visualization
        """
        dept_df = self.df[self.df['department'] == department].copy()
        
        if dept_df.empty:
            print(f"No data found for department: {department}")
            return
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 10))
        fig.suptitle(f'{department} - Performance Analysis Report', fontsize=16, fontweight='bold')
        
        # 1. Performance Distribution
        axes[0, 0].hist(dept_df['overall_performance'], bins=20, color='skyblue', edgecolor='black')
        axes[0, 0].axvline(dept_df['overall_performance'].mean(), color='red', 
                          linestyle='--', label=f'Mean: {dept_df["overall_performance"].mean():.1f}')
        axes[0, 0].set_xlabel('Overall Performance')
        axes[0, 0].set_ylabel('Number of Employees')
        axes[0, 0].set_title('Performance Distribution')
        axes[0, 0].legend()
        
        # 2. Performance by Role
        role_perf = dept_df.groupby('jobrole')['overall_performance'].mean().sort_values()
        axes[0, 1].barh(range(len(role_perf)), role_perf.values, color='lightgreen', edgecolor='black')
        axes[0, 1].set_yticks(range(len(role_perf)))
        axes[0, 1].set_yticklabels(role_perf.index, fontsize=9)
        axes[0, 1].set_xlabel('Average Performance')
        axes[0, 1].set_title('Average Performance by Role')
        
        # 3. Metric Comparison
        metrics = ['productivity_score', 'quality_score', 'engagement_score']
        metric_means = [dept_df[m].mean() for m in metrics]
        axes[0, 2].bar(['Productivity', 'Quality', 'Engagement'], metric_means,
                      color=['#1f77b4', '#2ca02c', '#ff7f0e'], edgecolor='black')
        axes[0, 2].set_ylabel('Average Score')
        axes[0, 2].set_title('Average Metric Scores')
        axes[0, 2].set_ylim(0, 100)
        
        # 4. Performance vs Attrition
        attrition_perf = dept_df.groupby('attrition')['overall_performance'].mean()
        axes[1, 0].bar(attrition_perf.index, attrition_perf.values,
                      color=['green', 'red'], edgecolor='black')
        axes[1, 0].set_ylabel('Average Performance')
        axes[1, 0].set_title('Performance by Attrition Status')
        
        # 5. Percentile Distribution
        percentile_bins = pd.cut(dept_df['performance_percentile'], 
                                bins=[0, 25, 50, 75, 90, 100],
                                labels=['Bottom 25%', '25-50%', '50-75%', '75-90%', 'Top 10%'])
        percentile_counts = percentile_bins.value_counts().sort_index()
        axes[1, 1].bar(range(len(percentile_counts)), percentile_counts.values,
                      color='coral', edgecolor='black')
        axes[1, 1].set_xticks(range(len(percentile_counts)))
        axes[1, 1].set_xticklabels(percentile_counts.index, rotation=45, ha='right')
        axes[1, 1].set_ylabel('Number of Employees')
        axes[1, 1].set_title('Performance Percentile Distribution')
        
        # 6. Summary Statistics
        axes[1, 2].axis('off')
        stats_text = f"""DEPARTMENT STATISTICS
        
Total Employees: {len(dept_df)}

Performance Metrics:
  Mean: {dept_df['overall_performance'].mean():.2f}
  Median: {dept_df['overall_performance'].median():.2f}
  Std Dev: {dept_df['overall_performance'].std():.2f}

Top Performers (>75%ile): {len(dept_df[dept_df['performance_percentile'] >= 75])}
Need Support (<25%ile): {len(dept_df[dept_df['performance_percentile'] <= 25])}

Attrition Rate: {(dept_df['attrition'] == 'Yes').mean() * 100:.1f}%
"""
        axes[1, 2].text(0.1, 0.9, stats_text, transform=axes[1, 2].transAxes,
                       fontsize=11, verticalalignment='top', family='monospace',
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Department report saved to {save_path}")
        else:
            plt.show()
        
        plt.close()


def main():
    """Main function to demonstrate the performance analysis system."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Employee Performance Analysis System')
    parser.add_argument('--input', required=True, help='Path to cleaned employee data CSV')
    parser.add_argument('--employee_id', type=int, help='Analyze specific employee by ID')
    parser.add_argument('--department', help='Generate department report')
    parser.add_argument('--top_n', type=int, default=10, help='Number of top performers to show')
    parser.add_argument('--output_dir', default='outputs/', help='Directory to save visualizations')
    
    args = parser.parse_args()
    
    # Initialize analyzer
    print("Initializing Performance Analyzer...")
    analyzer = EmployeePerformanceAnalyzer(args.input)
    print(f"Loaded data for {len(analyzer.df)} employees\n")
    
    # Company-wide statistics
    print("="*80)
    print("COMPANY-WIDE PERFORMANCE STATISTICS")
    print("="*80)
    stats = analyzer.get_performance_statistics()
    print(f"\nScope: {stats['scope']}")
    print(f"Total Employees: {stats['total_employees']}")
    print(f"\nOverall Performance:")
    print(f"  Mean: {stats['overall_performance']['mean']:.2f}")
    print(f"  Median: {stats['overall_performance']['median']:.2f}")
    print(f"  Std Dev: {stats['overall_performance']['std']:.2f}")
    print(f"  Range: {stats['overall_performance']['min']:.2f} - {stats['overall_performance']['max']:.2f}")
    print(f"\nPerformance Distribution:")
    print(f"  Top 10%: {stats['distribution']['top_10_percent']} employees")
    print(f"  Top 25%: {stats['distribution']['top_25_percent']} employees")
    print(f"  Bottom 25%: {stats['distribution']['bottom_25_percent']} employees")
    print(f"  Bottom 10%: {stats['distribution']['bottom_10_percent']} employees")
    
    # Top performers
    print(f"\n{'='*80}")
    print(f"TOP {args.top_n} PERFORMERS")
    print("="*80)
    top_performers = analyzer.get_top_performers(n=args.top_n)
    print(top_performers.to_string(index=False))
    
    # Employees needing support
    print(f"\n{'='*80}")
    print("EMPLOYEES NEEDING SUPPORT (Bottom 25%)")
    print("="*80)
    need_support = analyzer.get_employees_needing_support()
    print(f"\nTotal employees needing support: {len(need_support)}")
    print(need_support.head(10).to_string(index=False))
    
    # Individual employee analysis
    if args.employee_id:
        print(f"\n{'='*80}")
        print(f"DETAILED ANALYSIS: EMPLOYEE #{args.employee_id}")
        print("="*80)
        profile = analyzer.get_employee_profile(args.employee_id)
        
        if 'error' not in profile:
            print(f"\nBasic Information:")
            for key, value in profile['basic_info'].items():
                print(f"  {key.replace('_', ' ').title()}: {value}")
            
            print(f"\nPerformance Metrics:")
            for key, value in profile['performance_metrics'].items():
                print(f"  {key.replace('_', ' ').title()}: {value}")
            
            print(f"\nPerformance Rating: {profile['performance_rating']}")
            
            print(f"\nStrengths:")
            for strength in profile['strengths']:
                print(f"  • {strength}")
            
            print(f"\nAreas for Improvement:")
            for area in profile['improvement_areas']:
                print(f"  • {area}")
            
            print(f"\nRecommendations:")
            for rec in profile['recommendations']:
                print(f"  • {rec}")
            
            print(f"\nRisk Assessment:")
            risk = profile['risk_factors']
            print(f"  Attrition Risk: {risk['attrition_risk']}")
            print(f"  Performance Risk: {risk['performance_risk']}")
            if risk['risk_factors']:
                print(f"  Risk Factors:")
                for factor in risk['risk_factors']:
                    print(f"    - {factor}")
            
            # Generate visualization
            viz_path = f"{args.output_dir}employee_{args.employee_id}_performance.png"
            analyzer.visualize_employee_performance(args.employee_id, viz_path)
        else:
            print(profile['error'])
    
    # Department analysis
    if args.department:
        print(f"\n{'='*80}")
        print(f"DEPARTMENT ANALYSIS: {args.department}")
        print("="*80)
        dept_stats = analyzer.get_performance_statistics(department=args.department)
        print(f"\nTotal Employees: {dept_stats['total_employees']}")
        print(f"Average Performance: {dept_stats['overall_performance']['mean']:.2f}")
        print(f"Top Performers: {dept_stats['distribution']['top_25_percent']}")
        
        # Generate department report
        dept_path = f"{args.output_dir}{args.department.replace(' ', '_').replace('&', 'and')}_performance_report.png"
        analyzer.generate_department_performance_report(args.department, dept_path)


if __name__ == '__main__':
    main()
