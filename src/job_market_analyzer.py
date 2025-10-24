"""
Job Market Analysis Module
Enhanced with real CSV dataset analysis capabilities
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from collections import Counter
import re
from typing import Dict, List, Any, Tuple, Optional
import os


class JobMarketAnalyzer:
    """Enhanced job market analyzer using real CSV datasets"""
    
    def __init__(self, dataset_path: str = "dataset"):
        self.dataset_path = dataset_path
        self.df = None
        self.load_data()
    
    def load_data(self) -> None:
        """Load and combine datasets"""
        try:
            # Load both datasets
            df1 = pd.read_csv(os.path.join(self.dataset_path, "ai_job_dataset.csv"))
            df2 = pd.read_csv(os.path.join(self.dataset_path, "ai_job_dataset1.csv"))
            
            # Combine datasets
            self.df = pd.concat([df1, df2], ignore_index=True)
            
            # Clean and preprocess data
            self._preprocess_data()
            
            print(f"Loaded {len(self.df)} job records from datasets")
            
        except Exception as e:
            print(f"Error loading datasets: {e}")
            self.df = pd.DataFrame()
    
    def _preprocess_data(self) -> None:
        """Preprocess the combined dataset"""
        if self.df.empty:
            return
        
        # Convert salary to numeric, handling different currencies
        self.df['salary_usd'] = pd.to_numeric(self.df['salary_usd'], errors='coerce')
        
        # Clean experience levels
        self.df['experience_level'] = self.df['experience_level'].str.upper()
        
        # Clean company locations (use as country)
        self.df['country'] = self.df['company_location']
        
        # Parse skills
        self.df['skills_list'] = self.df['required_skills'].apply(self._parse_skills)
        
        # Convert dates
        self.df['posting_date'] = pd.to_datetime(self.df['posting_date'], errors='coerce')
        
        # Remove rows with missing critical data
        self.df = self.df.dropna(subset=['job_title', 'salary_usd', 'industry'])
        
        # Filter reasonable salary ranges (remove outliers)
        self.df = self.df[(self.df['salary_usd'] >= 10000) & (self.df['salary_usd'] <= 500000)]
    
    def _parse_skills(self, skills_str: str) -> List[str]:
        """Parse skills string into list"""
        if pd.isna(skills_str):
            return []
        
        # Split by comma and clean
        skills = [skill.strip() for skill in str(skills_str).split(',')]
        return [skill for skill in skills if len(skill) > 1]
    
    def get_salary_analysis(self, experience_level: str = None, industry: str = None) -> Dict[str, Any]:
        """Analyze salary trends"""
        df_filtered = self.df.copy()
        
        if experience_level:
            df_filtered = df_filtered[df_filtered['experience_level'] == experience_level.upper()]
        
        if industry:
            df_filtered = df_filtered[df_filtered['industry'].str.contains(industry, case=False, na=False)]
        
        if df_filtered.empty:
            return {"error": "No data found for the specified filters"}
        
        # Calculate statistics
        salary_stats = {
            'mean': df_filtered['salary_usd'].mean(),
            'median': df_filtered['salary_usd'].median(),
            'min': df_filtered['salary_usd'].min(),
            'max': df_filtered['salary_usd'].max(),
            'std': df_filtered['salary_usd'].std(),
            'count': len(df_filtered)
        }
        
        # Salary by experience level
        exp_salary = df_filtered.groupby('experience_level')['salary_usd'].agg(['mean', 'count']).reset_index()
        
        # Top paying industries
        industry_salary = df_filtered.groupby('industry')['salary_usd'].mean().sort_values(ascending=False).head(10)
        
        return {
            'stats': salary_stats,
            'by_experience': exp_salary.to_dict('records'),
            'by_industry': industry_salary.to_dict(),
            'data': df_filtered[['job_title', 'salary_usd', 'experience_level', 'industry', 'company_location']].to_dict('records')
        }
    
    def get_skill_demand_analysis(self, top_n: int = 20) -> Dict[str, Any]:
        """Analyze skill demand trends"""
        # Flatten all skills
        all_skills = []
        for skills_list in self.df['skills_list']:
            all_skills.extend(skills_list)
        
        # Count skills
        skill_counts = Counter(all_skills)
        top_skills = skill_counts.most_common(top_n)
        
        # Skills by experience level
        skills_by_exp = {}
        for exp_level in self.df['experience_level'].unique():
            if pd.isna(exp_level):
                continue
            exp_df = self.df[self.df['experience_level'] == exp_level]
            exp_skills = []
            for skills_list in exp_df['skills_list']:
                exp_skills.extend(skills_list)
            skills_by_exp[exp_level] = Counter(exp_skills).most_common(10)
        
        # Skills by industry
        skills_by_industry = {}
        for industry in self.df['industry'].value_counts().head(10).index:
            industry_df = self.df[self.df['industry'] == industry]
            industry_skills = []
            for skills_list in industry_df['skills_list']:
                industry_skills.extend(skills_list)
            skills_by_industry[industry] = Counter(industry_skills).most_common(10)
        
        return {
            'top_skills': top_skills,
            'by_experience': skills_by_exp,
            'by_industry': skills_by_industry,
            'total_unique_skills': len(skill_counts)
        }
    
    def get_industry_trends(self) -> Dict[str, Any]:
        """Analyze industry trends"""
        # Job counts by industry
        industry_counts = self.df['industry'].value_counts().head(15)
        
        # Average salary by industry
        industry_salary = self.df.groupby('industry')['salary_usd'].agg(['mean', 'count']).reset_index()
        industry_salary = industry_salary[industry_salary['count'] >= 10]  # Filter industries with at least 10 jobs
        industry_salary = industry_salary.sort_values('mean', ascending=False)
        
        # Remote work trends by industry
        remote_by_industry = self.df.groupby('industry')['remote_ratio'].mean().sort_values(ascending=False)
        
        # Experience level distribution by industry
        exp_by_industry = self.df.groupby(['industry', 'experience_level']).size().unstack(fill_value=0)
        
        return {
            'job_counts': industry_counts.to_dict(),
            'salary_ranking': industry_salary.to_dict('records'),
            'remote_trends': remote_by_industry.to_dict(),
            'experience_distribution': exp_by_industry.to_dict()
        }
    
    def get_geographic_analysis(self) -> Dict[str, Any]:
        """Analyze geographic opportunities"""
        # Top countries by job count
        country_counts = self.df['country'].value_counts().head(15)
        
        # Average salary by country
        country_salary = self.df.groupby('country')['salary_usd'].agg(['mean', 'count']).reset_index()
        country_salary = country_salary[country_salary['count'] >= 5]  # Filter countries with at least 5 jobs
        country_salary = country_salary.sort_values('mean', ascending=False)
        
        # Remote work by country
        remote_by_country = self.df.groupby('country')['remote_ratio'].mean().sort_values(ascending=False)
        
        # Top industries by country
        top_industries_by_country = {}
        for country in country_counts.head(10).index:
            country_df = self.df[self.df['country'] == country]
            top_industries_by_country[country] = country_df['industry'].value_counts().head(5).to_dict()
        
        return {
            'job_counts': country_counts.to_dict(),
            'salary_ranking': country_salary.to_dict('records'),
            'remote_trends': remote_by_country.to_dict(),
            'top_industries_by_country': top_industries_by_country
        }
    
    def get_job_title_analysis(self, search_term: str = None) -> Dict[str, Any]:
        """Analyze specific job titles"""
        df_filtered = self.df.copy()
        
        if search_term:
            df_filtered = df_filtered[
                df_filtered['job_title'].str.contains(search_term, case=False, na=False)
            ]
        
        if df_filtered.empty:
            return {"error": "No jobs found for the specified search term"}
        
        # Most common job titles
        job_counts = df_filtered['job_title'].value_counts().head(20)
        
        # Salary analysis for job titles
        job_salary = df_filtered.groupby('job_title')['salary_usd'].agg(['mean', 'count', 'std']).reset_index()
        job_salary = job_salary[job_salary['count'] >= 3]  # Filter jobs with at least 3 occurrences
        job_salary = job_salary.sort_values('mean', ascending=False)
        
        # Experience level distribution
        exp_dist = df_filtered['experience_level'].value_counts()
        
        # Skills for this job type
        job_skills = []
        for skills_list in df_filtered['skills_list']:
            job_skills.extend(skills_list)
        top_job_skills = Counter(job_skills).most_common(15)
        
        return {
            'job_counts': job_counts.to_dict(),
            'salary_analysis': job_salary.to_dict('records'),
            'experience_distribution': exp_dist.to_dict(),
            'top_skills': top_job_skills,
            'total_jobs': len(df_filtered)
        }
    
    def get_certification_recommendations(self, skills: List[str]) -> Dict[str, List[str]]:
        """Map skills to relevant certifications"""
        certification_mapping = {
            'python': ['Python Institute PCAP', 'AWS Certified Developer', 'Google Cloud Professional Developer'],
            'tensorflow': ['Google TensorFlow Developer Certificate', 'AWS Machine Learning Specialty'],
            'pytorch': ['PyTorch Scholarship Challenge', 'Deep Learning Specialization (Coursera)'],
            'aws': ['AWS Certified Solutions Architect', 'AWS Certified Machine Learning Specialty'],
            'azure': ['Microsoft Azure AI Engineer Associate', 'Microsoft Azure Data Scientist Associate'],
            'gcp': ['Google Cloud Professional ML Engineer', 'Google Cloud Professional Data Engineer'],
            'kubernetes': ['Certified Kubernetes Administrator (CKA)', 'Certified Kubernetes Application Developer (CKAD)'],
            'docker': ['Docker Certified Associate', 'Kubernetes and Docker Security'],
            'sql': ['Microsoft SQL Server Certification', 'Oracle Database SQL Certified Associate'],
            'spark': ['Databricks Certified Associate Developer', 'Cloudera Certified Spark Developer'],
            'hadoop': ['Cloudera Certified Hadoop Developer', 'Hortonworks Data Platform Certification'],
            'tableau': ['Tableau Desktop Specialist', 'Tableau Server Certified Associate'],
            'power bi': ['Microsoft Power BI Data Analyst Associate', 'Microsoft Power Platform Fundamentals'],
            'r': ['R Programming Certification', 'Data Science with R (Coursera)'],
            'java': ['Oracle Certified Java Developer', 'Spring Professional Certification'],
            'scala': ['Lightbend Scala Professional', 'Databricks Certified Associate Developer'],
            'linux': ['CompTIA Linux+', 'Red Hat Certified System Administrator'],
            'git': ['GitHub Certified Developer', 'GitLab Certified Associate'],
            'nlp': ['Natural Language Processing Specialization', 'Deep Learning Specialization'],
            'computer vision': ['Computer Vision Specialization', 'Deep Learning Specialization'],
            'deep learning': ['Deep Learning Specialization (Coursera)', 'Fast.ai Practical Deep Learning'],
            'machine learning': ['Machine Learning Specialization (Stanford)', 'AWS Machine Learning Specialty'],
            'data science': ['IBM Data Science Professional Certificate', 'Google Data Analytics Certificate'],
            'mlops': ['MLOps Specialization (Coursera)', 'AWS Machine Learning Specialty']
        }
        
        recommendations = {}
        for skill in skills:
            skill_lower = skill.lower()
            for key, certs in certification_mapping.items():
                if key in skill_lower or skill_lower in key:
                    recommendations[skill] = certs
                    break
        
        return recommendations
    
    def create_salary_visualization(self, analysis_data: Dict[str, Any]) -> go.Figure:
        """Create salary visualization"""
        if 'by_experience' not in analysis_data:
            return None
        
        exp_data = analysis_data['by_experience']
        if not exp_data:
            return None
        
        fig = go.Figure(data=[
            go.Bar(
                x=[item['experience_level'] for item in exp_data],
                y=[item['mean'] for item in exp_data],
                text=[f"${int(item['mean']):,}" for item in exp_data],
                textposition='auto',
                marker_color=['#28a745', '#007bff', '#ffc107', '#dc3545', '#6f42c1']
            )
        ])
        
        fig.update_layout(
            title="Average Salary by Experience Level",
            xaxis_title="Experience Level",
            yaxis_title="Average Salary (USD)",
            showlegend=False,
            height=400
        )
        
        return fig
    
    def create_skill_demand_chart(self, skill_data: Dict[str, Any]) -> go.Figure:
        """Create skill demand visualization"""
        if 'top_skills' not in skill_data:
            return None
        
        skills, counts = zip(*skill_data['top_skills'][:15])
        
        fig = go.Figure(data=[
            go.Bar(
                x=list(counts),
                y=list(skills),
                orientation='h',
                marker_color='#007bff',
                text=list(counts),
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title="Most In-Demand Skills",
            xaxis_title="Number of Job Postings",
            yaxis_title="Skills",
            height=500,
            yaxis={'categoryorder': 'total ascending'}
        )
        
        return fig
    
    def create_industry_trends_chart(self, industry_data: Dict[str, Any]) -> go.Figure:
        """Create industry trends visualization"""
        if 'job_counts' not in industry_data:
            return None
        
        industries = list(industry_data['job_counts'].keys())[:10]
        counts = list(industry_data['job_counts'].values())[:10]
        
        fig = go.Figure(data=[
            go.Bar(
                x=industries,
                y=counts,
                marker_color='#28a745',
                text=counts,
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title="Top Industries by Job Count",
            xaxis_title="Industry",
            yaxis_title="Number of Jobs",
            height=400,
            xaxis_tickangle=-45
        )
        
        return fig
    
    def create_geographic_chart(self, geo_data: Dict[str, Any]) -> go.Figure:
        """Create geographic opportunities chart"""
        if 'salary_ranking' not in geo_data:
            return None
        
        countries = [item['country'] for item in geo_data['salary_ranking'][:10]]
        salaries = [item['mean'] for item in geo_data['salary_ranking'][:10]]
        
        fig = go.Figure(data=[
            go.Bar(
                x=countries,
                y=salaries,
                marker_color='#ff6b6b',
                text=[f"${int(s):,}" for s in salaries],
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title="Average Salary by Country (Top 10)",
            xaxis_title="Country",
            yaxis_title="Average Salary (USD)",
            height=400,
            xaxis_tickangle=-45
        )
        
        return fig
    
    def get_summary_insights(self) -> Dict[str, Any]:
        """Generate summary insights from the dataset"""
        if self.df.empty:
            return {"error": "No data available"}
        
        total_jobs = len(self.df)
        avg_salary = self.df['salary_usd'].mean()
        top_industry = self.df['industry'].value_counts().index[0]
        top_country = self.df['country'].value_counts().index[0]
        
        # Most common skills
        all_skills = []
        for skills_list in self.df['skills_list']:
            all_skills.extend(skills_list)
        top_skill = Counter(all_skills).most_common(1)[0][0] if all_skills else "N/A"
        
        # Remote work percentage
        remote_percentage = (self.df['remote_ratio'] > 0).mean() * 100
        
        # Experience level distribution
        exp_dist = self.df['experience_level'].value_counts()
        
        return {
            'total_jobs': total_jobs,
            'average_salary': avg_salary,
            'top_industry': top_industry,
            'top_country': top_country,
            'top_skill': top_skill,
            'remote_percentage': remote_percentage,
            'experience_distribution': exp_dist.to_dict()
        }

