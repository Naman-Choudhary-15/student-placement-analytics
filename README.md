Student Placement Analytics Platform

A web-based Student Placement Analytics Platform developed as an
Advances in Computing (ADC) project. The system manages student
placement records and converts them into useful placement statistics and
visual analytics.

Project Information

Item                     Details

Project Title            Student Placement Analytics Platform
Subject                  Advances in Computing (ADC)
Course Code              CCSDS0302
Domain / Industry Area   Quality Education
SDG Alignment            SDG 4 -- Quality Education
Backend                  Python + Flask
Database                 SQLite
Frontend                 HTML, CSS, JavaScript
Charts                   Chart.js

Overview

The Student Placement Analytics Platform is designed to provide a
centralized system for managing and analyzing placement-related
information.

The platform maintains information about:

Students

Recruiting companies

Student applications

Interviews

Placements

Skills

Placement analytics

The system provides an administrative dashboard where placement data can
be searched, filtered, monitored, and analyzed through charts and key
performance indicators.

Objectives

Maintain student placement records in a structured relational
database.

Manage company and recruitment information.

Track student applications and interview progress.

Maintain final placement details such as company, role, package, and
placement date.

Calculate important placement metrics.

Provide branch-wise and company-wise placement analysis.

Present placement information through an easy-to-use web dashboard.

Main Modules

1. Dashboard

The dashboard provides an overview of placement performance through key
metrics and visualizations, including:

Total students

Total companies

Applications

Interviews

Placed students

Placement rate

Average package

Highest package

Company-wise placements

Branch-wise placements

2. Students

The Students module provides access to student records and supports:

Student record viewing

Student search

Branch filtering

Placement-status filtering

3. Companies

The Companies module maintains information about recruiting
organizations participating in the placement process.

4. Applications

The Applications module tracks student applications submitted to
companies and their recruitment status.

5. Interviews

The Interviews module records interview-related information, including:

Application

Interview round

Interview date

Result

Remarks

6. Placements

The Placements module stores final placement information, including:

Student

Company

Job role

Package

Placement date

7. Analytics

The Analytics module converts stored placement records into visual and
numerical insights.

It includes:

Placement KPIs

Branch-wise placement analysis

Company-wise placement analysis

Recruitment funnel

Package distribution

Interview-result analysis

Application-status analysis

Company package analysis

System Architecture

                    User / Placement Admin
                              |
                              v
                    Web Interface
                 HTML + CSS + JavaScript
                              |
                              v
                       Flask Backend
                         Python
                              |
                              v
                       SQL Queries
                              |
                              v
                       SQLite Database
                              |
              +---------------+---------------+
              |               |               |
              v               v               v
          Student Data    Recruitment Data  Placement Data
                              |
                              v
                         Analytics
                              |
                              v
                     Charts / Dashboard

Database

The application uses SQLite as its relational database.

The major tables are:

Students
Companies
Skills
Applications
Interviews
Placements

The recruitment flow can be represented as:

Student
   |
   v
Application
   |
   v
Interview
   |
   v
Placement
   |
   +----> Company

Placement Metrics

The dashboard calculates metrics from the stored database records.

Placement Rate

Placement Rate =
(Placed Students / Total Students) × 100

For example, with 76 placed students out of 300 students:

(76 / 300) × 100 = 25.33%

Average Package

The average package is calculated from the package values of placed
students.

Highest Package

The highest package is obtained by finding the maximum package value
among placement records.

Technology Stack

Frontend

HTML5

CSS3

JavaScript

Chart.js

Backend

Python 3.11

Flask

Database

SQLite

Development Tools

Visual Studio Code

Git

GitHub

Project Structure

Student Placement Analytics/
│
├── app.py
├── seed_data.py
├── requirements.txt
├── .gitignore
│
├── static/
│   └── style.css
│
└── templates/
    ├── dashboard.html
    ├── students.html
    ├── companies.html
    ├── applications.html
    ├── interviews.html
    ├── placements.html
    └── analytics.html

placement.db is intentionally excluded from the Git repository
through .gitignore. The database can be recreated using
seed_data.py.

Installation and Setup

1. Clone the repository

git clone https://github.com/Naman-Choudhary-15/student-placement-analytics.git
cd student-placement-analytics

2. Install dependencies

pip install -r requirements.txt

3. Create/populate the database

python seed_data.py

The seed script creates/populates the project database with sample
placement data.

4. Run the Flask application

python app.py

5. Open the application

Open the following address in a browser:

http://127.0.0.1:5000/

Application Routes

The main application sections are:

/
 /students
 /companies
 /applications
 /interviews
 /placements
 /analytics

Sample Dataset

The current seeded dataset contains:

300 students

20 companies

15 skills

1041 applications

687 interviews

76 placements

These values are generated by the project's seed_data.py script and
are intended for development, demonstration, and academic evaluation.

Key Features

Centralized placement data management

Student search and filtering

Recruitment-company records

Application tracking

Interview tracking

Placement tracking

Placement-rate calculation

Average and highest package analysis

Branch-wise placement visualization

Company-wise placement visualization

Recruitment funnel visualization

Analytics dashboard

SQLite database integration

Flask-based web application

Future Scope

Possible future enhancements include:

Role-based authentication for administrators, placement officers,
students, and recruiters

Import/export of placement data using CSV or Excel

Automated report generation

Advanced predictive placement analytics

Student-wise performance dashboards

Real-time notifications

Deployment to a cloud platform

Integration with institutional ERP systems

Academic Purpose

This project was developed as part of the Advances in Computing
(ADC) coursework and demonstrates the integration of:

Web development

Python programming

Database management

SQL queries

Data processing

Data visualization

Placement analytics

Project Status

Status: Completed / Working Prototype

The current version includes the major placement-management modules and
an analytics dashboard backed by SQLite.