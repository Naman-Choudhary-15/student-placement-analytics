import sqlite3
import random
from datetime import date, timedelta

DATABASE = "placement.db"

# Make results reproducible
random.seed(42)

# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

# Enable foreign key support
cursor.execute("PRAGMA foreign_keys = ON")

# --------------------------------------------------
# CREATE DATABASE TABLES IF THEY DO NOT EXIST
# --------------------------------------------------

cursor.executescript("""

CREATE TABLE IF NOT EXISTS students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_no TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    branch TEXT,
    batch INTEGER,
    cgpa REAL,
    backlogs INTEGER
);

CREATE TABLE IF NOT EXISTS companies (
    company_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL,
    industry TEXT,
    location TEXT,
    package_lpa REAL,
    min_cgpa REAL,
    job_role TEXT
);

CREATE TABLE IF NOT EXISTS skills (
    skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_name TEXT NOT NULL,
    category TEXT
);

CREATE TABLE IF NOT EXISTS student_skills (
    student_skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    skill_id INTEGER NOT NULL,
    proficiency TEXT,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id)
);

CREATE TABLE IF NOT EXISTS applications (
    application_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    company_id INTEGER NOT NULL,
    application_date TEXT,
    status TEXT,
    current_stage TEXT,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE TABLE IF NOT EXISTS interviews (
    interview_id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER NOT NULL,
    interview_round TEXT,
    interview_date TEXT,
    result TEXT,
    remarks TEXT,
    FOREIGN KEY (application_id) REFERENCES applications(application_id)
);

CREATE TABLE IF NOT EXISTS placements (
    placement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    company_id INTEGER NOT NULL,
    application_id INTEGER NOT NULL,
    placement_date TEXT,
    package_lpa REAL,
    placement_type TEXT,
    status TEXT,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    FOREIGN KEY (application_id) REFERENCES applications(application_id)
);

""")

# --------------------------------------------------
# SAMPLE DATA
# --------------------------------------------------

branches = [
    "CSE",
    "CSE-DS",
    "CSE-AI",
    "CSE-AIML",
    "ECE"
]

skills_data = [
    ("Python", "Programming"),
    ("C", "Programming"),
    ("C++", "Programming"),
    ("Java", "Programming"),
    ("JavaScript", "Web Development"),
    ("HTML/CSS", "Web Development"),
    ("SQL", "Database"),
    ("MongoDB", "Database"),
    ("Machine Learning", "AI/ML"),
    ("Deep Learning", "AI/ML"),
    ("Data Analysis", "Data Science"),
    ("Power BI", "Analytics"),
    ("Excel", "Analytics"),
    ("Git", "Tools"),
    ("Communication", "Soft Skills")
]

companies_data = [
    ("TCS", "IT Services", "Noida", 6.00, 7.00, "Software Engineer"),
    ("Infosys", "IT Services", "Bangalore", 7.00, 7.00, "Systems Engineer"),
    ("Accenture", "Consulting & IT", "Gurgaon", 8.00, 7.50, "Associate Software Engineer"),
    ("Wipro", "IT Services", "Noida", 6.50, 6.50, "Project Engineer"),
    ("Cognizant", "IT Services", "Pune", 7.20, 7.00, "Programmer Analyst"),
    ("Capgemini", "IT Services", "Bangalore", 6.75, 6.50, "Analyst"),
    ("Deloitte", "Consulting", "Gurgaon", 9.00, 7.50, "Analyst"),
    ("IBM", "Technology", "Bangalore", 8.50, 7.50, "Associate Developer"),
    ("Amazon", "E-Commerce", "Bangalore", 15.00, 8.00, "SDE"),
    ("Microsoft", "Technology", "Hyderabad", 20.00, 8.50, "Software Engineer"),
    ("Google", "Technology", "Bangalore", 24.00, 8.50, "Software Engineer"),
    ("Accenture", "Consulting & IT", "Pune", 7.50, 7.00, "Technology Analyst"),
    ("HCLTech", "IT Services", "Noida", 6.00, 6.50, "Software Engineer"),
    ("Tech Mahindra", "IT Services", "Pune", 5.50, 6.00, "Associate Software Engineer"),
    ("Coforge", "IT Services", "Noida", 7.00, 7.00, "Software Engineer"),
    ("Genpact", "IT Services", "Gurgaon", 6.50, 6.50, "Business Analyst"),
    ("LTIMindtree", "IT Services", "Noida", 7.50, 7.00, "Graduate Engineer"),
    ("Oracle", "Technology", "Bangalore", 12.00, 8.00, "Application Developer"),
    ("SAP", "Enterprise Software", "Bangalore", 10.00, 7.50, "Associate Consultant"),
    ("Deloitte USI", "Consulting", "Hyderabad", 8.50, 7.50, "Analyst")
]


# --------------------------------------------------
# CLEAR OLD DATA
# --------------------------------------------------

tables = [
    "placements",
    "interviews",
    "applications",
    "student_skills",
    "skills",
    "companies",
    "students"
]

for table in tables:
    cursor.execute(f"DELETE FROM {table}")


# --------------------------------------------------
# INSERT SKILLS
# --------------------------------------------------

for skill_name, category in skills_data:
    cursor.execute("""
        INSERT INTO skills (skill_name, category)
        VALUES (?, ?)
    """, (skill_name, category))


# --------------------------------------------------
# INSERT COMPANIES
# --------------------------------------------------

for company in companies_data:
    cursor.execute("""
        INSERT INTO companies
        (company_name, industry, location, package_lpa, min_cgpa, job_role)
        VALUES (?, ?, ?, ?, ?, ?)
    """, company)


# --------------------------------------------------
# INSERT STUDENTS
# --------------------------------------------------

student_ids = []

first_names = [
    "Aarav", "Aditi", "Aditya", "Akash", "Aman",
    "Ananya", "Ankit", "Arjun", "Ayush", "Bhavya",
    "Dev", "Diya", "Harsh", "Ishita", "Karan",
    "Kavya", "Manish", "Mehak", "Mohit", "Naman",
    "Neha", "Nikhil", "Piyush", "Pranav", "Priya",
    "Rahul", "Riya", "Rohan", "Sakshi", "Sahil",
    "Shivam", "Shreya", "Simran", "Tanya", "Varun"
]

last_names = [
    "Sharma", "Choudhary", "Singh", "Kumar", "Gupta",
    "Verma", "Yadav", "Patel", "Joshi", "Rawat",
    "Mehta", "Agarwal", "Mishra", "Bisht", "Thakur"
]

used_roll_numbers = set()

for i in range(1, 301):

    while True:
        roll_no = f"250133154{random.randint(1000, 9999)}"

        if roll_no not in used_roll_numbers:
            used_roll_numbers.add(roll_no)
            break

    name = f"{random.choice(first_names)} {random.choice(last_names)}"

    email_name = name.lower().replace(" ", ".")
    email = f"{email_name}{i}@example.com"

    phone = f"9{random.randint(100000000, 999999999)}"

    branch = random.choice(branches)

    batch = 2026

    # Generate CGPA between 5.8 and 9.8
    cgpa = round(random.uniform(5.8, 9.8), 2)

    # Students with lower CGPA have slightly higher chance of backlogs
    if cgpa < 6.5:
        backlogs = random.choices(
            [0, 1, 2],
            weights=[50, 35, 15]
        )[0]
    else:
        backlogs = random.choices(
            [0, 1],
            weights=[90, 10]
        )[0]

    cursor.execute("""
        INSERT INTO students
        (roll_no, name, email, phone, branch, batch, cgpa, backlogs)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        roll_no,
        name,
        email,
        phone,
        branch,
        batch,
        cgpa,
        backlogs
    ))

    student_ids.append(cursor.lastrowid)


# --------------------------------------------------
# INSERT STUDENT SKILLS
# --------------------------------------------------

skill_ids = [
    row[0]
    for row in cursor.execute(
        "SELECT skill_id FROM skills"
    ).fetchall()
]

for student_id in student_ids:

    # Each student gets 3–7 skills
    number_of_skills = random.randint(3, 7)

    selected_skills = random.sample(
        skill_ids,
        number_of_skills
    )

    for skill_id in selected_skills:

        proficiency = random.choice([
            "Beginner",
            "Intermediate",
            "Advanced"
        ])

        cursor.execute("""
            INSERT INTO student_skills
            (student_id, skill_id, proficiency)
            VALUES (?, ?, ?)
        """, (
            student_id,
            skill_id,
            proficiency
        ))


# --------------------------------------------------
# GET COMPANY IDS
# --------------------------------------------------

company_rows = cursor.execute("""
    SELECT company_id, min_cgpa
    FROM companies
""").fetchall()


# --------------------------------------------------
# INSERT APPLICATIONS
# --------------------------------------------------

application_ids = []

start_date = date(2026, 7, 1)

for student_id in student_ids:

    student = cursor.execute("""
        SELECT cgpa, backlogs
        FROM students
        WHERE student_id = ?
    """, (student_id,)).fetchone()

    cgpa = student[0]
    backlogs = student[1]

    # Each student applies to 2–5 companies
    number_of_applications = random.randint(2, 5)

    selected_companies = random.sample(
        company_rows,
        min(number_of_applications, len(company_rows))
    )

    for company_id, min_cgpa in selected_companies:

        application_date = start_date + timedelta(
            days=random.randint(0, 60)
        )

        # Eligibility
        eligible = (
            cgpa >= min_cgpa and
            backlogs <= 1
        )

        if not eligible:
            status = "Rejected"
            stage = "Eligibility"
        else:

            outcome = random.random()

            if outcome < 0.18:
                status = "Rejected"
                stage = "Aptitude"

            elif outcome < 0.40:
                status = "Shortlisted"
                stage = "Technical"

            elif outcome < 0.60:
                status = "Shortlisted"
                stage = "Interview"

            elif outcome < 0.88:
                status = "Rejected"
                stage = "Interview"

            else:
                status = "Selected"
                stage = "Final"

        cursor.execute("""
            INSERT INTO applications
            (student_id, company_id, application_date, status, current_stage)
            VALUES (?, ?, ?, ?, ?)
        """, (
            student_id,
            company_id,
            application_date.isoformat(),
            status,
            stage
        ))

        application_ids.append({
            "application_id": cursor.lastrowid,
            "student_id": student_id,
            "company_id": company_id,
            "status": status,
            "stage": stage,
            "application_date": application_date
        })


# --------------------------------------------------
# INSERT INTERVIEWS
# --------------------------------------------------

for application in application_ids:

    # Only shortlisted/selected applications get interviews
    if application["status"] in ["Shortlisted", "Selected"]:

        number_of_rounds = random.choice([1, 2, 2, 3])

        rounds = [
            "Aptitude",
            "Technical",
            "HR"
        ]

        for r in range(number_of_rounds):

            interview_date = application["application_date"] + timedelta(
                days=random.randint(7, 25)
            )

            if application["status"] == "Selected":
                result = "Passed"
            else:
                result = random.choice([
                    "Passed",
                    "Passed",
                    "Failed"
                ])

            cursor.execute("""
                INSERT INTO interviews
                (application_id, interview_round, interview_date, result, remarks)
                VALUES (?, ?, ?, ?, ?)
            """, (
                application["application_id"],
                rounds[min(r, 2)],
                interview_date.isoformat(),
                result,
                "Performance recorded during recruitment process"
            ))


# --------------------------------------------------
# INSERT PLACEMENTS
# --------------------------------------------------

# Some selected applications become final placements
selected_applications = [
    app for app in application_ids
    if app["status"] == "Selected"
]

# Keep one placement per student
placed_students = set()

random.shuffle(selected_applications)

for application in selected_applications:

    student_id = application["student_id"]

    if student_id in placed_students:
        continue

    company_id = application["company_id"]

    company = cursor.execute("""
        SELECT package_lpa
        FROM companies
        WHERE company_id = ?
    """, (company_id,)).fetchone()

    base_package = company[0]

    # Small variation in package
    package = round(
        base_package * random.uniform(0.95, 1.10),
        2
    )

    placement_date = application["application_date"] + timedelta(
        days=random.randint(25, 60)
    )

    cursor.execute("""
        INSERT INTO placements
        (student_id, company_id, application_id,
         placement_date, package_lpa, placement_type, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        student_id,
        company_id,
        application["application_id"],
        placement_date.isoformat(),
        package,
        "Full-Time",
        "Placed"
    ))

    placed_students.add(student_id)


# --------------------------------------------------
# SAVE DATABASE
# --------------------------------------------------

conn.commit()


# --------------------------------------------------
# DISPLAY SUMMARY
# --------------------------------------------------

students_count = cursor.execute(
    "SELECT COUNT(*) FROM students"
).fetchone()[0]

companies_count = cursor.execute(
    "SELECT COUNT(*) FROM companies"
).fetchone()[0]

skills_count = cursor.execute(
    "SELECT COUNT(*) FROM skills"
).fetchone()[0]

applications_count = cursor.execute(
    "SELECT COUNT(*) FROM applications"
).fetchone()[0]

interviews_count = cursor.execute(
    "SELECT COUNT(*) FROM interviews"
).fetchone()[0]

placements_count = cursor.execute(
    "SELECT COUNT(*) FROM placements"
).fetchone()[0]


print()
print("=" * 55)
print(" STUDENT PLACEMENT ANALYTICS - DATABASE SEEDING")
print("=" * 55)
print()
print(f"Students       : {students_count}")
print(f"Companies      : {companies_count}")
print(f"Skills         : {skills_count}")
print(f"Applications   : {applications_count}")
print(f"Interviews     : {interviews_count}")
print(f"Placements     : {placements_count}")
print()
print("Database successfully populated!")
print("=" * 55)

conn.close()