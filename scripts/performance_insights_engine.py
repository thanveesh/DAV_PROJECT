#!/usr/bin/env python3
"""
Performance Insights Engine - Rule-Based Analysis System

This module provides AI-powered analysis of employee performance data,
generating natural language insights, recommendations, and risk assessments.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class AnalysisConfig:
    """Configuration for analysis rules and thresholds."""
    
    # Score interpretation thresholds
    exceptional_threshold: float = 80.0
    strong_threshold: float = 60.0
    adequate_threshold: float = 40.0
    
    # Anomaly detection thresholds
    decline_threshold: float = 10.0  # % decline
    improvement_threshold: float = 15.0  # % improvement
    overtime_threshold: float = 20.0  # % above standard
    
    # Risk assessment thresholds
    burnout_critical: float = 70.0
    burnout_moderate: float = 40.0
    attrition_high: float = 60.0
    attrition_moderate: float = 30.0
    
    # Business impact estimates
    avg_hourly_rate: float = 50.0
    rework_cost_multiplier: float = 2.5
    replacement_cost_multiplier: float = 1.5  # 1.5x annual salary
    
    # Comparison tolerances
    significant_difference: float = 10.0  # points
    moderate_difference: float = 5.0  # points


@dataclass
class PerformanceInsight:
    """Structure for a single insight."""
    category: str  # 'finding', 'concern', 'strength', 'recommendation'
    severity: str  # 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'POSITIVE'
    title: str
    description: str
    evidence: List[str] = field(default_factory=list)
    confidence: float = 1.0  # 0.0 to 1.0


class PerformanceInterpreter:
    """Interprets performance scores and generates natural language explanations."""
    
    def __init__(self, config: AnalysisConfig):
        self.config = config
    
    def analyze_overall_score(self, score: float) -> str:
        """
        Interpret overall performance score.
        
        Parameters:
        -----------
        score : float
            Overall performance score (0-100)
        
        Returns:
        --------
        str
            Natural language interpretation
        """
        if score >= self.config.exceptional_threshold:
            return "Exceptional performance - consistently exceeds expectations across all metrics"
        elif score >= self.config.strong_threshold:
            return "Strong performance - meets and often exceeds expectations with reliable results"
        elif score >= self.config.adequate_threshold:
            return "Adequate performance - meets basic expectations with room for growth"
        else:
            return "Below expectations - requires immediate intervention and support"
    
    def analyze_metric_balance(self, productivity: float, quality: float, 
                               engagement: float) -> Dict[str, str]:
        """
        Identify patterns in metric balance.
        
        Parameters:
        -----------
        productivity, quality, engagement : float
            Individual metric scores (0-100)
        
        Returns:
        --------
        dict
            Pattern analysis with interpretation
        """
        results = {
            'pattern': 'Balanced',
            'interpretation': '',
            'implications': []
        }
        
        metrics = {'productivity': productivity, 'quality': quality, 'engagement': engagement}
        avg = np.mean([productivity, quality, engagement])
        
        # Identify outliers
        high_metrics = [k for k, v in metrics.items() if v > avg + 15]
        low_metrics = [k for k, v in metrics.items() if v < avg - 15]
        
        # Pattern detection
        if engagement > 70 and quality < 50:
            results['pattern'] = 'Motivated but Underperforming'
            results['interpretation'] = 'High engagement but low quality suggests employee is motivated but may lack necessary skills, training, or tools'
            results['implications'] = [
                'Skill gap likely exists',
                'Training intervention recommended',
                'May need clearer quality standards'
            ]
        
        elif productivity > 70 and engagement < 40:
            results['pattern'] = 'Efficient but Disengaged'
            results['interpretation'] = 'High productivity with low engagement indicates burnout risk - employee is delivering results but at personal cost'
            results['implications'] = [
                'High risk of burnout',
                'Retention concern',
                'Work-life balance needs attention'
            ]
        
        elif all(v < 40 for v in metrics.values()):
            results['pattern'] = 'Disengaged Underperformer'
            results['interpretation'] = 'Low scores across all metrics indicate serious disengagement - critical retention and performance risk'
            results['implications'] = [
                'Immediate intervention required',
                'High attrition risk',
                'May be actively seeking other opportunities'
            ]
        
        elif productivity > 70 and quality < 50 and engagement < 50:
            results['pattern'] = 'Rushing Work'
            results['interpretation'] = 'High productivity but low quality suggests employee is prioritizing speed over quality, possibly due to workload pressure'
            results['implications'] = [
                'Workload may be excessive',
                'Quality standards not being met',
                'Need to rebalance speed vs. quality expectations'
            ]
        
        elif all(v > 70 for v in metrics.values()):
            results['pattern'] = 'High Performer'
            results['interpretation'] = 'Consistently high scores across all dimensions - exemplary employee'
            results['implications'] = [
                'Consider for leadership opportunities',
                'Ensure proper recognition',
                'Retain through career development'
            ]
        
        elif len(low_metrics) == 1:
            results['pattern'] = f'Single Weak Point: {low_metrics[0].title()}'
            results['interpretation'] = f'Overall solid performance with specific weakness in {low_metrics[0]} - targeted improvement opportunity'
            results['implications'] = [
                f'Focused {low_metrics[0]} development needed',
                'Otherwise strong performer',
                'Clear improvement path available'
            ]
        
        return results
    
    def interpret_score_level(self, metric_name: str, score: float, 
                             avg: float) -> str:
        """Generate interpretation for a specific metric score."""
        diff = score - avg
        
        if diff > 15:
            return f"{metric_name.title()} is significantly above average (+{diff:.1f} points) - clear strength"
        elif diff > 5:
            return f"{metric_name.title()} is above average (+{diff:.1f} points) - performing well"
        elif diff > -5:
            return f"{metric_name.title()} is on par with average - meeting expectations"
        elif diff > -15:
            return f"{metric_name.title()} is below average ({diff:.1f} points) - area for development"
        else:
            return f"{metric_name.title()} is significantly below average ({diff:.1f} points) - requires immediate attention"


class AnomalyDetector:
    """Detects concerning patterns and anomalies in performance data."""
    
    def __init__(self, config: AnalysisConfig):
        self.config = config
    
    def detect_anomalies(self, employee_data: pd.Series, 
                        dept_avg: Dict, company_avg: Dict) -> List[PerformanceInsight]:
        """
        Detect all anomalies in employee performance.
        
        Parameters:
        -----------
        employee_data : pd.Series
            Employee performance data
        dept_avg, company_avg : dict
            Average performance metrics
        
        Returns:
        --------
        list of PerformanceInsight
            Detected anomalies
        """
        anomalies = []
        
        # Check for extreme deviations
        overall = employee_data.get('overall_performance', 50)
        dept_overall = dept_avg.get('overall', 50)
        
        if overall < 30:
            anomalies.append(PerformanceInsight(
                category='concern',
                severity='CRITICAL',
                title='Critical Performance Level',
                description=f'Overall performance ({overall:.1f}) is critically low, indicating urgent need for intervention',
                evidence=[
                    f'Score is {dept_overall - overall:.1f} points below department average',
                    'Multiple metrics likely underperforming',
                    'High risk of performance improvement plan required'
                ],
                confidence=0.95
            ))
        
        # Overtime + quality issues
        if employee_data.get('overtime', 'No') == 'Yes' and employee_data.get('quality_score', 50) < 45:
            anomalies.append(PerformanceInsight(
                category='concern',
                severity='CRITICAL',
                title='Burnout Pattern Detected',
                description='Employee working overtime while quality declines - classic burnout indicator',
                evidence=[
                    f'Working overtime: {employee_data.get("overtime")}',
                    f'Quality score: {employee_data.get("quality_score", 0):.1f} (below average)',
                    'Pattern suggests exhaustion affecting work quality'
                ],
                confidence=0.85
            ))
        
        # Engagement crisis
        if employee_data.get('engagement_score', 50) < 30:
            anomalies.append(PerformanceInsight(
                category='concern',
                severity='HIGH',
                title='Severe Disengagement Detected',
                description=f'Engagement score ({employee_data.get("engagement_score", 0):.1f}) indicates employee is actively disengaged',
                evidence=[
                    'Likely has one foot out the door',
                    'High probability of seeking other opportunities',
                    'Retention intervention needed immediately'
                ],
                confidence=0.90
            ))
        
        # Productivity-quality imbalance
        prod = employee_data.get('productivity_score', 50)
        qual = employee_data.get('quality_score', 50)
        if prod > 70 and qual < 40:
            anomalies.append(PerformanceInsight(
                category='finding',
                severity='MEDIUM',
                title='Speed Over Quality Pattern',
                description='High productivity but low quality suggests rushing or cutting corners',
                evidence=[
                    f'Productivity: {prod:.1f} (strong)',
                    f'Quality: {qual:.1f} (weak)',
                    'May indicate pressure to deliver quickly',
                    'Quality standards may not be clear or enforced'
                ],
                confidence=0.75
            ))
        
        # Exceptional performance
        if overall > 80:
            anomalies.append(PerformanceInsight(
                category='strength',
                severity='POSITIVE',
                title='Exceptional Performer',
                description=f'Performance ({overall:.1f}) places employee in top tier',
                evidence=[
                    f'{overall - dept_overall:.1f} points above department average',
                    'Consistently exceeds expectations',
                    'Strong candidate for advancement'
                ],
                confidence=0.95
            ))
        
        # Long tenure without promotion
        years_no_promo = employee_data.get('yearssincelastpromotion', 0)
        years_company = employee_data.get('yearsatcompany', 0)
        if years_no_promo >= 5 and years_company >= 5:
            anomalies.append(PerformanceInsight(
                category='concern',
                severity='MEDIUM',
                title='Career Stagnation Risk',
                description=f'No promotion in {years_no_promo:.0f} years despite {years_company:.0f} years tenure',
                evidence=[
                    'May feel undervalued',
                    'Career development discussion overdue',
                    'Retention risk if not addressed'
                ],
                confidence=0.70
            ))
        
        return anomalies


class RootCauseAnalyzer:
    """Analyzes potential root causes for performance issues."""
    
    def generate_root_cause_hypotheses(self, metric_name: str, score: float,
                                      context: Dict) -> List[str]:
        """
        Generate hypotheses for why a metric is underperforming.
        
        Parameters:
        -----------
        metric_name : str
            Name of the metric ('quality', 'productivity', 'engagement')
        score : float
            Current score
        context : dict
            Employee context data
        
        Returns:
        --------
        list of str
            Possible root causes
        """
        hypotheses = []
        
        if metric_name.lower() == 'quality' and score < 50:
            hypotheses.extend([
                "Insufficient training or unclear quality standards - employee may not know what 'good' looks like",
                f"Heavy workload leading to rushed work - check overtime status ({context.get('overtime', 'Unknown')})",
                "Lack of regular feedback or quality review processes - issues not caught early",
                "Inadequate tools, resources, or support systems hampering quality output",
                "Possible skill mismatch between role requirements and employee capabilities"
            ])
            
            # Add context-specific hypotheses
            if context.get('overtime') == 'Yes':
                hypotheses.append("⚠️ CONFIRMED: Working overtime likely contributing to quality decline")
            
            if context.get('trainingtimeslastyear', 0) < 2:
                hypotheses.append("⚠️ CONFIRMED: Limited training (< 2 sessions) may explain quality gaps")
        
        elif metric_name.lower() == 'productivity' and score < 50:
            hypotheses.extend([
                "Technical blockers or inefficient processes slowing down work",
                "Lack of clear priorities or goals leading to scattered efforts",
                "Insufficient resources, tools, or support to complete work efficiently",
                "Personal issues or health concerns affecting output",
                "Role misalignment - tasks don't match employee's strengths or skills"
            ])
            
            if context.get('jobinvolvement', 3) <= 2:
                hypotheses.append("⚠️ CONFIRMED: Low job involvement suggests motivation issues")
            
            if context.get('yearsatcompany', 0) < 1:
                hypotheses.append("CONTEXT: New employee - productivity ramp-up expected")
        
        elif metric_name.lower() == 'engagement' and score < 50:
            hypotheses.extend([
                "Career growth concerns - no clear path for advancement or development",
                "Poor manager relationship or negative team dynamics affecting morale",
                "Compensation or recognition misalignment with expectations or market",
                "Work-life balance problems causing dissatisfaction",
                "Cultural fit issues or misalignment with company values"
            ])
            
            if context.get('yearssincelastpromotion', 0) >= 5:
                hypotheses.append("⚠️ CONFIRMED: No promotion in 5+ years likely driving disengagement")
            
            if context.get('jobsatisfaction', 3) <= 2:
                hypotheses.append("⚠️ CONFIRMED: Low job satisfaction indicates fundamental issues")
            
            if context.get('worklifebalance', 3) <= 2:
                hypotheses.append("⚠️ CONFIRMED: Poor work-life balance contributing to disengagement")
        
        return hypotheses[:5]  # Return top 5 most relevant


class ComparisonAnalyzer:
    """Analyzes performance in context of peer groups."""
    
    def analyze_peer_comparison(self, employee_scores: Dict, 
                               peer_averages: Dict,
                               tenure: float, role: str) -> Dict[str, str]:
        """
        Analyze employee scores against appropriate peer groups.
        
        Parameters:
        -----------
        employee_scores : dict
            Employee's performance scores
        peer_averages : dict
            Average scores for different peer groups
        tenure : float
            Years at company
        role : str
            Job role
        
        Returns:
        --------
        dict
            Contextual analysis
        """
        analysis = {
            'context': '',
            'interpretation': '',
            'expectation_adjustment': ''
        }
        
        overall = employee_scores.get('overall', 50)
        dept_avg = peer_averages.get('department', {}).get('overall', 50)
        company_avg = peer_averages.get('company', {}).get('overall', 50)
        role_avg = peer_averages.get('role', {}).get('overall', 50)
        
        # New employee adjustment
        if tenure < 0.5:  # Less than 6 months
            if overall < dept_avg:
                analysis['context'] = 'New employee (< 6 months tenure)'
                analysis['interpretation'] = f'Performance below average is expected during onboarding period'
                analysis['expectation_adjustment'] = 'Continue monitoring - expect improvement as employee completes training and ramps up'
            else:
                analysis['context'] = 'New employee (< 6 months tenure)'
                analysis['interpretation'] = f'Performance at or above average is impressive for new hire'
                analysis['expectation_adjustment'] = 'Fast learner - consider accelerated development path'
        
        # Strong in role but below company
        elif overall > role_avg and overall < company_avg:
            analysis['context'] = f'Performing above role average (+{overall - role_avg:.1f}) but below company average ({overall - company_avg:.1f})'
            analysis['interpretation'] = 'Strong performer within current role but has growth potential'
            analysis['expectation_adjustment'] = 'Consider for stretch assignments or promotion to higher-performing role'
        
        # Consistently above all averages
        elif overall > dept_avg and overall > company_avg and overall > role_avg:
            analysis['context'] = 'Exceeds all benchmarks (department, company, role)'
            analysis['interpretation'] = 'Top performer across all comparisons - exceptional employee'
            analysis['expectation_adjustment'] = 'Prime candidate for leadership track or critical projects'
        
        # Below all averages
        elif overall < dept_avg and overall < company_avg:
            diff = abs(overall - dept_avg)
            if diff > 15:
                analysis['context'] = f'Significantly below all averages ({diff:.1f} points)'
                analysis['interpretation'] = 'Underperforming across the board - requires structured improvement plan'
                analysis['expectation_adjustment'] = 'Immediate intervention needed - set clear goals and timeline'
            else:
                analysis['context'] = f'Moderately below averages ({diff:.1f} points)'
                analysis['interpretation'] = 'Some performance gaps but not critical'
                analysis['expectation_adjustment'] = 'Focus on targeted improvements in weakest areas'
        
        # Experienced employee context
        if tenure > 3:
            if overall < role_avg:
                analysis['expectation_adjustment'] += f' | Note: With {tenure:.0f} years experience, expect to exceed role average'
        
        return analysis


class ImpactQuantifier:
    """Quantifies business impact of performance issues."""
    
    def __init__(self, config: AnalysisConfig):
        self.config = config
    
    def calculate_business_impact(self, performance_data: pd.Series,
                                  monthly_income: float) -> Dict[str, any]:
        """
        Calculate business impact of performance issues.
        
        Parameters:
        -----------
        performance_data : pd.Series
            Employee performance data
        monthly_income : float
            Employee's monthly income
        
        Returns:
        --------
        dict
            Impact calculations
        """
        impact = {
            'lost_productivity_cost': 0,
            'quality_issue_cost': 0,
            'attrition_risk_cost': 0,
            'opportunity_gain': 0,
            'total_at_risk': 0,
            'explanations': []
        }
        
        annual_salary = monthly_income * 12
        
        # Lost productivity
        productivity_score = performance_data.get('productivity_score', 50)
        target_score = 75  # Target performance
        if productivity_score < target_score:
            productivity_gap = (target_score - productivity_score) / 100
            hours_per_year = 2080  # Standard work year
            lost_productivity_cost = productivity_gap * self.config.avg_hourly_rate * hours_per_year
            impact['lost_productivity_cost'] = lost_productivity_cost
            impact['explanations'].append(
                f"Lost productivity: {productivity_gap*100:.1f}% below target = ${lost_productivity_cost:,.0f}/year in unrealized output"
            )
        
        # Quality issues
        quality_score = performance_data.get('quality_score', 50)
        if quality_score < 50:
            error_rate = (50 - quality_score) / 100  # Estimate error rate
            quality_cost = annual_salary * error_rate * self.config.rework_cost_multiplier
            impact['quality_issue_cost'] = quality_cost
            impact['explanations'].append(
                f"Quality issues: Estimated {error_rate*100:.1f}% error rate = ${quality_cost:,.0f}/year in rework and corrections"
            )
        
        # Attrition risk
        engagement_score = performance_data.get('engagement_score', 50)
        if engagement_score < 40:
            attrition_probability = (40 - engagement_score) / 40  # 0 to 1
            replacement_cost = annual_salary * self.config.replacement_cost_multiplier
            attrition_risk_cost = replacement_cost * attrition_probability
            impact['attrition_risk_cost'] = attrition_risk_cost
            impact['explanations'].append(
                f"Attrition risk: {attrition_probability*100:.0f}% probability of leaving = ${attrition_risk_cost:,.0f} expected replacement cost"
            )
        
        # Opportunity gain if improved
        overall_score = performance_data.get('overall_performance', 50)
        dept_avg = 55  # Assume department average
        if overall_score < dept_avg:
            improvement_potential = (dept_avg - overall_score) / 100
            opportunity_gain = annual_salary * improvement_potential * 0.5  # Conservative estimate
            impact['opportunity_gain'] = opportunity_gain
            impact['explanations'].append(
                f"Improvement opportunity: If raised to department average, potential value gain = ${opportunity_gain:,.0f}/year"
            )
        
        impact['total_at_risk'] = (impact['lost_productivity_cost'] + 
                                   impact['quality_issue_cost'] + 
                                   impact['attrition_risk_cost'])
        
        return impact


class RecommendationEngine:
    """Generates prioritized, actionable recommendations."""
    
    def generate_recommendations(self, employee_data: pd.Series,
                                analysis_results: Dict) -> List[Dict]:
        """
        Generate prioritized recommendations based on analysis.
        
        Parameters:
        -----------
        employee_data : pd.Series
            Employee performance data
        analysis_results : dict
            Results from various analyses
        
        Returns:
        --------
        list of dict
            Prioritized recommendations
        """
        recommendations = []
        
        # Extract key metrics
        overall = employee_data.get('overall_performance', 50)
        quality = employee_data.get('quality_score', 50)
        productivity = employee_data.get('productivity_score', 50)
        engagement = employee_data.get('engagement_score', 50)
        overtime = employee_data.get('overtime', 'No')
        job_satisfaction = employee_data.get('jobsatisfaction', 3)
        years_no_promo = employee_data.get('yearssincelastpromotion', 0)
        training = employee_data.get('trainingtimeslastyear', 0)
        
        # CRITICAL: Low quality + overtime
        if quality < 45 and overtime == 'Yes':
            recommendations.append({
                'priority': 'CRITICAL',
                'action': 'Immediate workload review and reduction',
                'details': f'Reduce workload by 20-30% and provide quality training/coaching',
                'timeline': 'Within 1 week',
                'expected_outcome': 'Quality improvement within 4-6 weeks, reduced burnout risk',
                'responsible': 'Manager + HR',
                'success_metrics': ['Quality score improvement >10 points', 'Overtime eliminated', 'Job satisfaction increase']
            })
        
        # URGENT: Severe disengagement
        if engagement < 30:
            recommendations.append({
                'priority': 'URGENT',
                'action': 'Retention intervention - immediate career discussion',
                'details': 'Schedule 1-on-1 within 48 hours to understand concerns and create action plan',
                'timeline': 'Within 2 days',
                'expected_outcome': 'Identify and address key drivers of disengagement, create retention plan',
                'responsible': 'Manager + HR',
                'success_metrics': ['Employee commits to action plan', 'Engagement survey improvement', 'Key concerns addressed']
            })
        
        # HIGH: Low satisfaction + good performance
        if job_satisfaction <= 2 and overall > 60:
            recommendations.append({
                'priority': 'HIGH',
                'action': 'Career development and recognition discussion',
                'details': 'Good performer but dissatisfied - address compensation, growth, or recognition gaps',
                'timeline': 'Within 2 weeks',
                'expected_outcome': 'Improved satisfaction, retention of strong performer',
                'responsible': 'Manager',
                'success_metrics': ['Career plan established', 'Satisfaction score increase', 'Retention commitment']
            })
        
        # HIGH: No promotion in 5+ years
        if years_no_promo >= 5:
            recommendations.append({
                'priority': 'HIGH',
                'action': 'Career advancement discussion and promotion evaluation',
                'details': f'No promotion in {years_no_promo:.0f} years - evaluate for advancement or clarify path forward',
                'timeline': 'Within 2 weeks',
                'expected_outcome': 'Clear promotion timeline or alternative career development plan',
                'responsible': 'Manager + HR',
                'success_metrics': ['Promotion decision made', 'Career roadmap created', 'Employee satisfaction']
            })
        
        # MEDIUM: Low quality score
        if quality < 50 and overtime != 'Yes':
            recommendations.append({
                'priority': 'MEDIUM',
                'action': 'Quality improvement program',
                'details': 'Provide quality training, clear standards, and regular feedback/reviews',
                'timeline': '30-day improvement plan',
                'expected_outcome': 'Quality score improvement to department average within 60-90 days',
                'responsible': 'Manager',
                'success_metrics': ['Quality score >60', 'Defect rate reduction', 'Positive feedback from reviews']
            })
        
        # MEDIUM: Low training
        if training < 2 and (productivity < 50 or quality < 50):
            recommendations.append({
                'priority': 'MEDIUM',
                'action': 'Skill development and training program',
                'details': f'Only {training:.0f} training sessions last year - increase to at least 4/year',
                'timeline': 'Enroll in training within 30 days',
                'expected_outcome': 'Improved skills leading to better performance',
                'responsible': 'Manager + L&D',
                'success_metrics': ['4+ training sessions completed', 'Performance metrics improve', 'Skill assessment scores increase']
            })
        
        # MEDIUM: All metrics declining
        if overall < 45 and productivity < 50 and quality < 50:
            recommendations.append({
                'priority': 'MEDIUM',
                'action': 'Comprehensive performance improvement plan',
                'details': 'Multiple underperforming areas - implement structured 90-day PIP with clear milestones',
                'timeline': 'Start within 1 week',
                'expected_outcome': 'Meet defined performance targets or determine role fit',
                'responsible': 'Manager + HR',
                'success_metrics': ['Weekly goal achievement', 'Monthly performance reviews', 'Overall score >50 by day 90']
            })
        
        # LOW: Positive trajectory
        if overall >= 50 and overall < 70:
            recommendations.append({
                'priority': 'LOW',
                'action': 'Continue current development and provide stretch assignments',
                'details': 'Solid performer - maintain momentum with challenging projects',
                'timeline': 'Review in 90 days',
                'expected_outcome': 'Continued growth toward high performer status',
                'responsible': 'Manager',
                'success_metrics': ['Score improvement >5 points', 'Successfully complete stretch project', 'Ready for next level']
            })
        
        # POSITIVE: Exceptional performer
        if overall > 80:
            recommendations.append({
                'priority': 'POSITIVE',
                'action': 'Retain and develop for leadership',
                'details': 'Top performer - provide leadership opportunities, mentorship role, and career advancement',
                'timeline': 'Ongoing',
                'expected_outcome': 'Retention of key talent, development of future leader',
                'responsible': 'Manager + Senior Leadership',
                'success_metrics': ['Retention', 'Leadership project success', 'Mentee development']
            })
        
        # Sort by priority
        priority_order = {'CRITICAL': 0, 'URGENT': 1, 'HIGH': 2, 'MEDIUM': 3, 'LOW': 4, 'POSITIVE': 5}
        recommendations.sort(key=lambda x: priority_order[x['priority']])
        
        return recommendations


class RiskAssessor:
    """Assesses various employee-related risks."""
    
    def __init__(self, config: AnalysisConfig):
        self.config = config
    
    def assess_risks(self, employee_data: pd.Series) -> Dict[str, Dict]:
        """
        Assess burnout, attrition, and performance risks.
        
        Parameters:
        -----------
        employee_data : pd.Series
            Employee performance data
        
        Returns:
        --------
        dict
            Risk assessments
        """
        risks = {
            'burnout': self._assess_burnout_risk(employee_data),
            'attrition': self._assess_attrition_risk(employee_data),
            'performance': self._assess_performance_risk(employee_data)
        }
        
        return risks
    
    def _assess_burnout_risk(self, emp: pd.Series) -> Dict:
        """Calculate burnout risk score and explanation."""
        score = 0
        factors = []
        
        # Overtime factor
        if emp.get('overtime', 'No') == 'Yes':
            score += 30
            factors.append('Working overtime regularly')
        
        # Declining quality
        quality = emp.get('quality_score', 50)
        if quality < 45:
            score += 20
            factors.append(f'Low quality score ({quality:.1f}) may indicate exhaustion')
        
        # Poor work-life balance
        wlb = emp.get('worklifebalance', 3)
        if wlb <= 2:
            score += 25
            factors.append(f'Poor work-life balance (score: {wlb}/4)')
        
        # High productivity but low engagement
        if emp.get('productivity_score', 50) > 70 and emp.get('engagement_score', 50) < 40:
            score += 15
            factors.append('High output despite low engagement - unsustainable pace')
        
        # Job satisfaction
        if emp.get('jobsatisfaction', 3) <= 2:
            score += 10
            factors.append('Low job satisfaction')
        
        # Determine level
        if score >= self.config.burnout_critical:
            level = 'CRITICAL'
            explanation = 'Employee shows multiple signs of severe burnout - immediate intervention required'
            timeline = 'Burnout likely within 1-2 months without intervention'
        elif score >= self.config.burnout_moderate:
            level = 'MODERATE'
            explanation = 'Employee showing burnout warning signs - proactive measures recommended'
            timeline = 'Burnout risk within 3-6 months if issues persist'
        else:
            level = 'LOW'
            explanation = 'No significant burnout indicators detected'
            timeline = 'Current workload appears sustainable'
        
        return {
            'score': score,
            'level': level,
            'explanation': explanation,
            'timeline': timeline,
            'factors': factors
        }
    
    def _assess_attrition_risk(self, emp: pd.Series) -> Dict:
        """Calculate attrition/flight risk."""
        score = 0
        factors = []
        
        # Engagement
        engagement = emp.get('engagement_score', 50)
        if engagement < 30:
            score += 40
            factors.append(f'Severe disengagement (score: {engagement:.1f})')
        elif engagement < 50:
            score += 20
            factors.append(f'Low engagement (score: {engagement:.1f})')
        
        # Job satisfaction
        job_sat = emp.get('jobsatisfaction', 3)
        if job_sat <= 1:
            score += 30
            factors.append('Very low job satisfaction (1/4)')
        elif job_sat <= 2:
            score += 15
            factors.append('Low job satisfaction (2/4)')
        
        # No promotion in years
        years_no_promo = emp.get('yearssincelastpromotion', 0)
        if years_no_promo >= 5:
            score += 20
            factors.append(f'No promotion in {years_no_promo:.0f} years')
        
        # Environment satisfaction
        if emp.get('environmentsatisfaction', 3) <= 2:
            score += 10
            factors.append('Low environment satisfaction')
        
        # Attrition flag
        if emp.get('attrition', 'No') == 'Yes':
            score = 100
            factors = ['Already left the company']
            level = 'CONFIRMED'
            explanation = 'Employee has already left the organization'
            probability = 100
        else:
            if score >= 70:
                level = 'HIGH'
                explanation = 'Strong indicators suggest employee is likely seeking other opportunities'
                probability = 60 + (score - 70) / 30 * 30  # 60-90% range
            elif score >= 40:
                level = 'MODERATE'
                explanation = 'Some retention concerns - proactive engagement recommended'
                probability = 30 + (score - 40) / 30 * 30  # 30-60% range
            else:
                level = 'LOW'
                explanation = 'Employee appears stable and engaged'
                probability = score / 40 * 30  # 0-30% range
        
        return {
            'score': score,
            'level': level,
            'explanation': explanation,
            'probability': f'{probability:.0f}%',
            'factors': factors
        }
    
    def _assess_performance_risk(self, emp: pd.Series) -> Dict:
        """Assess risk of not meeting performance goals."""
        score = 0
        factors = []
        
        overall = emp.get('overall_performance', 50)
        
        # Current performance level
        if overall < 40:
            score += 50
            factors.append(f'Currently below expectations (score: {overall:.1f})')
        elif overall < 50:
            score += 30
            factors.append(f'Performance marginal (score: {overall:.1f})')
        
        # Declining trends (simulated - would need historical data)
        # Using engagement and satisfaction as proxies for trajectory
        if emp.get('engagement_score', 50) < 40:
            score += 20
            factors.append('Low engagement suggests declining trajectory')
        
        # Multiple weak areas
        weak_count = sum([
            emp.get('productivity_score', 50) < 50,
            emp.get('quality_score', 50) < 50,
            emp.get('engagement_score', 50) < 50
        ])
        if weak_count >= 2:
            score += 15
            factors.append(f'{weak_count} of 3 key metrics underperforming')
        
        # Job involvement
        if emp.get('jobinvolvement', 3) <= 2:
            score += 15
            factors.append('Low job involvement')
        
        # Determine level
        if score >= 70:
            level = 'HIGH'
            explanation = 'Significant risk of not meeting performance goals without intervention'
            outlook = 'Target achievement unlikely without structured improvement plan'
        elif score >= 40:
            level = 'MODERATE'
            explanation = 'Some performance concerns that could impact goal achievement'
            outlook = 'Goals achievable with focused support and monitoring'
        else:
            level = 'LOW'
            explanation = 'On track to meet performance expectations'
            outlook = 'Current trajectory suggests successful goal achievement'
        
        return {
            'score': score,
            'level': level,
            'explanation': explanation,
            'outlook': outlook,
            'factors': factors
        }


class NarrativeReportGenerator:
    """Generates comprehensive narrative analysis reports."""
    
    def __init__(self, config: AnalysisConfig):
        self.config = config
        self.interpreter = PerformanceInterpreter(config)
        self.anomaly_detector = AnomalyDetector(config)
        self.root_cause = RootCauseAnalyzer()
        self.comparison = ComparisonAnalyzer()
        self.impact = ImpactQuantifier(config)
        self.recommender = RecommendationEngine()
        self.risk_assessor = RiskAssessor(config)
    
    def generate_analysis_report(self, employee_id: int, employee_data: pd.Series,
                                dept_avg: Dict, company_avg: Dict, role_avg: Dict) -> str:
        """
        Generate comprehensive narrative analysis report.
        
        Parameters:
        -----------
        employee_id : int
            Employee ID
        employee_data : pd.Series
            Employee performance data
        dept_avg, company_avg, role_avg : dict
            Average metrics for comparison
        
        Returns:
        --------
        str
            Formatted narrative report
        """
        # Extract key data
        overall = employee_data.get('overall_performance', 0)
        productivity = employee_data.get('productivity_score', 0)
        quality = employee_data.get('quality_score', 0)
        engagement = employee_data.get('engagement_score', 0)
        role = employee_data.get('jobrole', 'Unknown')
        dept = employee_data.get('department', 'Unknown')
        tenure = employee_data.get('yearsatcompany', 0)
        monthly_income = employee_data.get('monthlyincome', 5000)
        
        # Perform analyses
        overall_interp = self.interpreter.analyze_overall_score(overall)
        metric_balance = self.interpreter.analyze_metric_balance(productivity, quality, engagement)
        anomalies = self.anomaly_detector.detect_anomalies(employee_data, dept_avg, company_avg)
        peer_comparison = self.comparison.analyze_peer_comparison(
            {'overall': overall},
            {'department': dept_avg, 'company': company_avg, 'role': role_avg},
            tenure, role
        )
        impact_calc = self.impact.calculate_business_impact(employee_data, monthly_income)
        recommendations = self.recommender.generate_recommendations(employee_data, {})
        risks = self.risk_assessor.assess_risks(employee_data)
        
        # Build report
        report = f"""
{'='*80}
PERFORMANCE ANALYSIS REPORT
{'='*80}
Employee ID: {employee_id}
Role: {role}
Department: {dept}
Tenure: {tenure:.1f} years
Analysis Date: {datetime.now().strftime('%B %d, %Y')}

{'='*80}
EXECUTIVE SUMMARY
{'='*80}
{overall_interp}

Overall Performance Score: {overall:.1f}/100 (Percentile: {employee_data.get('performance_percentile', 0):.1f}%)

{metric_balance['interpretation']}

{'='*80}
PERFORMANCE OVERVIEW
{'='*80}

Overall Score: {overall:.1f}/100
├─ Productivity: {productivity:.1f}/100 ({self.interpreter.interpret_score_level('productivity', productivity, dept_avg.get('productivity', 50))})
├─ Quality: {quality:.1f}/100 ({self.interpreter.interpret_score_level('quality', quality, dept_avg.get('quality', 50))})
└─ Engagement: {engagement:.1f}/100 ({self.interpreter.interpret_score_level('engagement', engagement, dept_avg.get('engagement', 50))})

Pattern Identified: {metric_balance['pattern']}
"""
        
        if metric_balance['implications']:
            report += "\nImplications:\n"
            for imp in metric_balance['implications']:
                report += f"  • {imp}\n"
        
        # Peer comparison
        report += f"""
{'='*80}
CONTEXTUAL COMPARISON
{'='*80}
"""
        if peer_comparison['context']:
            report += f"\nContext: {peer_comparison['context']}\n"
            report += f"Interpretation: {peer_comparison['interpretation']}\n"
            report += f"Expectation Adjustment: {peer_comparison['expectation_adjustment']}\n"
        
        # Comparison to averages
        report += f"""
Comparison to Benchmarks:
  vs. Company Average:    {overall - company_avg.get('overall', 50):+.1f} points
  vs. Department Average: {overall - dept_avg.get('overall', 50):+.1f} points
  vs. Role Average:       {overall - role_avg.get('overall', 50):+.1f} points
"""
        
        # Key findings and anomalies
        if anomalies:
            report += f"""
{'='*80}
KEY FINDINGS & ANOMALIES
{'='*80}
"""
            for anomaly in anomalies:
                report += f"\n[{anomaly.severity}] {anomaly.title}\n"
                report += f"{anomaly.description}\n"
                if anomaly.evidence:
                    report += "Evidence:\n"
                    for evidence in anomaly.evidence:
                        report += f"  • {evidence}\n"
                report += f"Confidence: {anomaly.confidence*100:.0f}%\n"
        
        # Root cause analysis for underperforming metrics
        underperforming = []
        if productivity < 50:
            underperforming.append(('productivity', productivity))
        if quality < 50:
            underperforming.append(('quality', quality))
        if engagement < 50:
            underperforming.append(('engagement', engagement))
        
        if underperforming:
            report += f"""
{'='*80}
ROOT CAUSE ANALYSIS
{'='*80}
"""
            for metric_name, score in underperforming:
                hypotheses = self.root_cause.generate_root_cause_hypotheses(
                    metric_name, score, employee_data.to_dict()
                )
                report += f"\nIssue: {metric_name.title()} Score Below Target ({score:.1f}/100)\n"
                report += "Possible Root Causes:\n"
                for i, hypothesis in enumerate(hypotheses, 1):
                    report += f"  {i}. {hypothesis}\n"
        
        # Business impact
        if impact_calc['total_at_risk'] > 0:
            report += f"""
{'='*80}
BUSINESS IMPACT QUANTIFICATION
{'='*80}
Total Value at Risk: ${impact_calc['total_at_risk']:,.0f} annually

Breakdown:
"""
            for explanation in impact_calc['explanations']:
                report += f"  • {explanation}\n"
            
            if impact_calc['opportunity_gain'] > 0:
                report += f"\n💡 Opportunity: ${impact_calc['opportunity_gain']:,.0f}/year potential value if performance improves to average\n"
        
        # Recommendations
        if recommendations:
            report += f"""
{'='*80}
ACTIONABLE RECOMMENDATIONS (Prioritized)
{'='*80}
"""
            for i, rec in enumerate(recommendations[:6], 1):  # Top 6 recommendations
                report += f"""
{i}. [{rec['priority']}] {rec['action']}
   Details: {rec['details']}
   Timeline: {rec['timeline']}
   Expected Outcome: {rec['expected_outcome']}
   Responsible: {rec['responsible']}
   Success Metrics: {', '.join(rec['success_metrics'])}
"""
        
        # Risk assessment
        report += f"""
{'='*80}
RISK ASSESSMENT
{'='*80}

🔥 BURNOUT RISK: {risks['burnout']['level']} (Score: {risks['burnout']['score']}/100)
   {risks['burnout']['explanation']}
   Timeline: {risks['burnout']['timeline']}
"""
        if risks['burnout']['factors']:
            report += "   Contributing Factors:\n"
            for factor in risks['burnout']['factors']:
                report += f"     • {factor}\n"
        
        report += f"""
🚪 ATTRITION RISK: {risks['attrition']['level']} (Probability: {risks['attrition']['probability']})
   {risks['attrition']['explanation']}
"""
        if risks['attrition']['factors']:
            report += "   Risk Factors:\n"
            for factor in risks['attrition']['factors']:
                report += f"     • {factor}\n"
        
        report += f"""
📊 PERFORMANCE RISK: {risks['performance']['level']} (Score: {risks['performance']['score']}/100)
   {risks['performance']['explanation']}
   Outlook: {risks['performance']['outlook']}
"""
        if risks['performance']['factors']:
            report += "   Concerns:\n"
            for factor in risks['performance']['factors']:
                report += f"     • {factor}\n"
        
        # Next steps
        urgent_recs = [r for r in recommendations if r['priority'] in ['CRITICAL', 'URGENT']]
        if urgent_recs:
            report += f"""
{'='*80}
IMMEDIATE NEXT STEPS
{'='*80}
"""
            for rec in urgent_recs:
                report += f"⚠️  {rec['action']} - {rec['timeline']}\n"
        
        report += f"""
{'='*80}
END OF REPORT
{'='*80}
"""
        
        return report


class PerformanceAnalysisEngine:
    """Main orchestration class for performance analysis."""
    
    def __init__(self, config: Optional[AnalysisConfig] = None):
        """
        Initialize the analysis engine.
        
        Parameters:
        -----------
        config : AnalysisConfig, optional
            Configuration for analysis rules and thresholds
        """
        self.config = config or AnalysisConfig()
        self.interpreter = PerformanceInterpreter(self.config)
        self.anomaly_detector = AnomalyDetector(self.config)
        self.root_cause = RootCauseAnalyzer()
        self.comparison = ComparisonAnalyzer()
        self.impact = ImpactQuantifier(self.config)
        self.recommender = RecommendationEngine()
        self.risk_assessor = RiskAssessor(self.config)
        self.report_generator = NarrativeReportGenerator(self.config)
    
    def analyze(self, employee_data: pd.Series, dept_avg: Dict, 
                company_avg: Dict, role_avg: Dict) -> Dict:
        """
        Perform comprehensive analysis on employee data.
        
        Parameters:
        -----------
        employee_data : pd.Series
            Employee performance data
        dept_avg, company_avg, role_avg : dict
            Average metrics for comparison
        
        Returns:
        --------
        dict
            Complete analysis results
        """
        # Extract key metrics
        overall = employee_data.get('overall_performance', 0)
        productivity = employee_data.get('productivity_score', 0)
        quality = employee_data.get('quality_score', 0)
        engagement = employee_data.get('engagement_score', 0)
        tenure = employee_data.get('yearsatcompany', 0)
        role = employee_data.get('jobrole', 'Unknown')
        monthly_income = employee_data.get('monthlyincome', 5000)
        
        results = {
            'interpretation': {
                'overall': self.interpreter.analyze_overall_score(overall),
                'metric_balance': self.interpreter.analyze_metric_balance(productivity, quality, engagement),
                'productivity': self.interpreter.interpret_score_level('productivity', productivity, dept_avg.get('productivity', 50)),
                'quality': self.interpreter.interpret_score_level('quality', quality, dept_avg.get('quality', 50)),
                'engagement': self.interpreter.interpret_score_level('engagement', engagement, dept_avg.get('engagement', 50))
            },
            'anomalies': self.anomaly_detector.detect_anomalies(employee_data, dept_avg, company_avg),
            'root_causes': {},
            'comparisons': self.comparison.analyze_peer_comparison(
                {'overall': overall}, 
                {'department': dept_avg, 'company': company_avg, 'role': role_avg},
                tenure, role
            ),
            'impact': self.impact.calculate_business_impact(employee_data, monthly_income),
            'recommendations': self.recommender.generate_recommendations(employee_data, {}),
            'risks': self.risk_assessor.assess_risks(employee_data),
            'report': None
        }
        
        # Generate root causes for underperforming metrics
        if productivity < 50:
            results['root_causes']['productivity'] = self.root_cause.generate_root_cause_hypotheses(
                'productivity', productivity, employee_data.to_dict()
            )
        if quality < 50:
            results['root_causes']['quality'] = self.root_cause.generate_root_cause_hypotheses(
                'quality', quality, employee_data.to_dict()
            )
        if engagement < 50:
            results['root_causes']['engagement'] = self.root_cause.generate_root_cause_hypotheses(
                'engagement', engagement, employee_data.to_dict()
            )
        
        # Generate full narrative report
        results['report'] = self.report_generator.generate_analysis_report(
            int(employee_data.get('employeenumber', 0)),
            employee_data,
            dept_avg,
            company_avg,
            role_avg
        )
        
        return results


def main():
    """Example usage of the Performance Analysis Engine."""
    
    # Example: Load data and analyze an employee
    print("Performance Insights Engine - Example Usage\n")
    print("="*80)
    
    # Create sample employee data
    sample_employee = pd.Series({
        'employeenumber': 1012,
        'overall_performance': 26.38,
        'productivity_score': 14.67,
        'quality_score': 0.0,
        'engagement_score': 50.0,
        'jobrole': 'Sales Executive',
        'department': 'Research & Development',
        'yearsatcompany': 8,
        'overtime': 'No',
        'jobsatisfaction': 1,
        'worklifebalance': 2,
        'trainingtimeslastyear': 0,
        'yearssincelastpromotion': 5,
        'monthlyincome': 4000,
        'jobinvolvement': 2,
        'environmentsatisfaction': 1,
        'performance_percentile': 0.07
    })
    
    # Sample averages
    dept_avg = {'overall': 50.3, 'productivity': 43.6, 'quality': 45.2, 'engagement': 62.7}
    company_avg = {'overall': 50.17, 'productivity': 43.57, 'quality': 35.28, 'engagement': 62.70}
    role_avg = {'overall': 52.0, 'productivity': 45.0, 'quality': 40.0, 'engagement': 60.0}
    
    # Initialize engine
    engine = PerformanceAnalysisEngine()
    
    # Perform analysis
    print("Analyzing Employee #1012...\n")
    results = engine.analyze(sample_employee, dept_avg, company_avg, role_avg)
    
    # Print the narrative report
    print(results['report'])
    
    print("\n" + "="*80)
    print("Analysis complete! Full structured results available in results dict.")
    print("="*80)


if __name__ == '__main__':
    main()
