from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

DATABASE = "placement.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

@app.route("/")
def dashboard():

    conn = get_db_connection()

    total_students = conn.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    total_companies = conn.execute(
        "SELECT COUNT(*) FROM companies"
    ).fetchone()[0]

    total_applications = conn.execute(
        "SELECT COUNT(*) FROM applications"
    ).fetchone()[0]

    total_placements = conn.execute(
        "SELECT COUNT(*) FROM placements"
    ).fetchone()[0]

    placement_rate = round(
        (total_placements / total_students) * 100, 2
    ) if total_students else 0

    average_package = conn.execute("""
        SELECT AVG(package_lpa)
        FROM placements
    """).fetchone()[0] or 0

    highest_package = conn.execute("""
        SELECT MAX(package_lpa)
        FROM placements
    """).fetchone()[0] or 0

    average_package = round(average_package, 2)
    highest_package = round(highest_package, 2)

    company_data = conn.execute("""
    SELECT
        MIN(c.company_name) AS company_name,
        COUNT(p.placement_id) AS placed_students

    FROM companies c

    LEFT JOIN placements p
        ON c.company_id = p.company_id

    GROUP BY LOWER(TRIM(c.company_name))

    HAVING COUNT(p.placement_id) > 0

    ORDER BY placed_students DESC
""").fetchall()

    branch_data = conn.execute("""
        SELECT
            s.branch,
            COUNT(s.student_id) AS total_students,
            COUNT(p.placement_id) AS placed_students
        FROM students s
        LEFT JOIN placements p
            ON s.student_id = p.student_id
        GROUP BY s.branch
        ORDER BY placed_students DESC
    """).fetchall()

    application_data = conn.execute("""
        SELECT status, COUNT(*) AS total
        FROM applications
        GROUP BY status
    """).fetchall()

    recent_placements = conn.execute("""
        SELECT
            s.name,
            s.branch,
            c.company_name,
            p.package_lpa,
            p.placement_date
        FROM placements p
        JOIN students s
            ON p.student_id = s.student_id
        JOIN companies c
            ON p.company_id = c.company_id
        ORDER BY p.placement_date DESC
        LIMIT 10
    """).fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        total_students=total_students,
        total_companies=total_companies,
        total_applications=total_applications,
        total_placements=total_placements,
        placement_rate=placement_rate,
        average_package=average_package,
        highest_package=highest_package,
        company_data=company_data,
        branch_data=branch_data,
        application_data=application_data,
        recent_placements=recent_placements
    )


# --------------------------------------------------
# STUDENTS
# --------------------------------------------------

@app.route("/students")
def students():

    conn = get_db_connection()

    search = request.args.get("search", "").strip()
    branch = request.args.get("branch", "").strip()
    status = request.args.get("status", "").strip()

    query = """
        SELECT
            s.student_id,
            s.roll_no,
            s.name,
            s.email,
            s.phone,
            s.branch,
            s.batch,
            s.cgpa,
            s.backlogs,

            CASE
                WHEN p.placement_id IS NOT NULL
                THEN 'Placed'
                ELSE 'Not Placed'
            END AS placement_status

        FROM students s

        LEFT JOIN placements p
            ON s.student_id = p.student_id

        WHERE 1=1
    """

    parameters = []

    # Search
    if search:
        query += """
            AND (
                s.name LIKE ?
                OR s.roll_no LIKE ?
            )
        """

        search_value = f"%{search}%"

        parameters.extend([
            search_value,
            search_value
        ])

    # Branch filter
    if branch:
        query += " AND s.branch = ?"
        parameters.append(branch)

    # Placement filter
    if status == "Placed":
        query += """
            AND p.placement_id IS NOT NULL
        """

    elif status == "Not Placed":
        query += """
            AND p.placement_id IS NULL
        """

    query += """
        ORDER BY s.student_id
    """

    students_data = conn.execute(
        query,
        parameters
    ).fetchall()

    # Get available branches
    branches = conn.execute("""
        SELECT DISTINCT branch
        FROM students
        ORDER BY branch
    """).fetchall()

    conn.close()

    return render_template(
        "students.html",
        students=students_data,
        branches=branches,
        search=search,
        selected_branch=branch,
        selected_status=status
    )
# --------------------------------------------------
# COMPANIES
# --------------------------------------------------

@app.route("/companies")
def companies():

    conn = get_db_connection()

    search = request.args.get("search", "").strip()
    industry = request.args.get("industry", "").strip()

    query = """
        SELECT
            c.company_id,
            c.company_name,
            c.industry,
            c.location,
            c.package_lpa,
            c.min_cgpa,
            c.job_role,
            COUNT(p.placement_id) AS placed_students
        FROM companies c

        LEFT JOIN placements p
            ON c.company_id = p.company_id

        WHERE 1=1
    """

    parameters = []

    # Search company name or location
    if search:

        query += """
            AND (
                c.company_name LIKE ?
                OR c.location LIKE ?
            )
        """

        search_value = f"%{search}%"

        parameters.extend([
            search_value,
            search_value
        ])

    # Industry filter
    if industry:

        query += """
            AND c.industry = ?
        """

        parameters.append(industry)

    query += """
        GROUP BY
            c.company_id,
            c.company_name,
            c.industry,
            c.location,
            c.package_lpa,
            c.min_cgpa,
            c.job_role

        ORDER BY c.company_name
    """

    companies_data = conn.execute(
        query,
        parameters
    ).fetchall()

    # Get available industries
    industries = conn.execute("""
        SELECT DISTINCT industry
        FROM companies
        ORDER BY industry
    """).fetchall()

    conn.close()

    return render_template(
        "companies.html",
        companies=companies_data,
        industries=industries,
        search=search,
        selected_industry=industry
    )
# --------------------------------------------------
# APPLICATIONS
# --------------------------------------------------

@app.route("/applications")
def applications():

    conn = get_db_connection()

    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()

    query = """
        SELECT
            a.application_id,
            s.roll_no,
            s.name AS student_name,
            s.branch,
            c.company_name,
            c.job_role,
            a.status
        FROM applications a

        JOIN students s
            ON a.student_id = s.student_id

        JOIN companies c
            ON a.company_id = c.company_id

        WHERE 1=1
    """

    parameters = []

    # Search student or company
    if search:

        query += """
            AND (
                s.name LIKE ?
                OR s.roll_no LIKE ?
                OR c.company_name LIKE ?
            )
        """

        search_value = f"%{search}%"

        parameters.extend([
            search_value,
            search_value,
            search_value
        ])

    # Status filter
    if status:

        query += """
            AND a.status = ?
        """

        parameters.append(status)

    query += """
        ORDER BY a.application_id DESC
    """

    applications_data = conn.execute(
        query,
        parameters
    ).fetchall()

    # Available application statuses
    statuses = conn.execute("""
        SELECT DISTINCT status
        FROM applications
        WHERE status IS NOT NULL
        ORDER BY status
    """).fetchall()

    conn.close()

    return render_template(
        "applications.html",
        applications=applications_data,
        statuses=statuses,
        search=search,
        selected_status=status
    )
# --------------------------------------------------
# INTERVIEWS
# --------------------------------------------------

@app.route("/interviews")
def interviews():

    conn = get_db_connection()

    search = request.args.get("search", "").strip()
    result = request.args.get("result", "").strip()

    query = """
        SELECT
            i.interview_id,
            s.roll_no,
            s.name AS student_name,
            s.branch,
            c.company_name,
            c.job_role,
            i.interview_round,
            i.interview_date,
            i.result,
            i.remarks

        FROM interviews i

        JOIN applications a
            ON i.application_id = a.application_id

        JOIN students s
            ON a.student_id = s.student_id

        JOIN companies c
            ON a.company_id = c.company_id

        WHERE 1=1
    """

    parameters = []

    # Search student, roll number or company
    if search:

        query += """
            AND (
                s.name LIKE ?
                OR s.roll_no LIKE ?
                OR c.company_name LIKE ?
            )
        """

        search_value = f"%{search}%"

        parameters.extend([
            search_value,
            search_value,
            search_value
        ])

    # Result filter
    if result:

        query += """
            AND i.result = ?
        """

        parameters.append(result)

    query += """
        ORDER BY i.interview_date DESC,
                 i.interview_id DESC
    """

    interviews_data = conn.execute(
        query,
        parameters
    ).fetchall()

    # Available interview results
    results = conn.execute("""
        SELECT DISTINCT result
        FROM interviews
        WHERE result IS NOT NULL
        ORDER BY result
    """).fetchall()

    conn.close()

    return render_template(
        "interviews.html",
        interviews=interviews_data,
        results=results,
        search=search,
        selected_result=result
    )
# --------------------------------------------------
# PLACEMENTS
# --------------------------------------------------

@app.route("/placements")
def placements():

    conn = get_db_connection()

    search = request.args.get("search", "").strip()
    branch = request.args.get("branch", "").strip()

    query = """
        SELECT
            p.placement_id,
            s.roll_no,
            s.name AS student_name,
            s.branch,
            s.batch,
            c.company_name,
            c.job_role,
            p.package_lpa,
            p.placement_date

        FROM placements p

        JOIN students s
            ON p.student_id = s.student_id

        JOIN companies c
            ON p.company_id = c.company_id

        WHERE 1=1
    """

    parameters = []

    # Search student, roll number or company
    if search:

        query += """
            AND (
                s.name LIKE ?
                OR s.roll_no LIKE ?
                OR c.company_name LIKE ?
            )
        """

        search_value = f"%{search}%"

        parameters.extend([
            search_value,
            search_value,
            search_value
        ])

    # Branch filter
    if branch:

        query += """
            AND s.branch = ?
        """

        parameters.append(branch)

    query += """
        ORDER BY p.placement_date DESC,
                 p.placement_id DESC
    """

    placements_data = conn.execute(
        query,
        parameters
    ).fetchall()

    branches = conn.execute("""
        SELECT DISTINCT branch
        FROM students
        ORDER BY branch
    """).fetchall()

    conn.close()

    return render_template(
        "placements.html",
        placements=placements_data,
        branches=branches,
        search=search,
        selected_branch=branch
    )
# --------------------------------------------------
# ANALYTICS
# --------------------------------------------------

@app.route("/analytics")
def analytics():

    conn = get_db_connection()

    # ---------------------------------------------
    # BASIC KPI DATA
    # ---------------------------------------------

    total_students = conn.execute("""
        SELECT COUNT(*)
        FROM students
    """).fetchone()[0]

    total_companies = conn.execute("""
        SELECT COUNT(*)
        FROM companies
    """).fetchone()[0]

    total_applications = conn.execute("""
        SELECT COUNT(*)
        FROM applications
    """).fetchone()[0]

    total_interviews = conn.execute("""
        SELECT COUNT(*)
        FROM interviews
    """).fetchone()[0]

    total_placements = conn.execute("""
        SELECT COUNT(*)
        FROM placements
    """).fetchone()[0]


    # ---------------------------------------------
    # PLACEMENT RATE
    # ---------------------------------------------

    placement_rate = 0

    if total_students > 0:

        placement_rate = round(
            (total_placements / total_students) * 100,
            2
        )


    # ---------------------------------------------
    # PACKAGE ANALYSIS
    # ---------------------------------------------

    package_data = conn.execute("""
        SELECT
            ROUND(AVG(package_lpa), 2) AS average_package,
            MAX(package_lpa) AS highest_package,
            MIN(package_lpa) AS lowest_package
        FROM placements
    """).fetchone()


    average_package = package_data["average_package"] or 0
    highest_package = package_data["highest_package"] or 0
    lowest_package = package_data["lowest_package"] or 0


    # ---------------------------------------------
    # BRANCH-WISE PLACEMENTS
    # ---------------------------------------------

    branch_data = conn.execute("""
        SELECT
            s.branch,
            COUNT(p.placement_id) AS placed_students
        FROM students s

        LEFT JOIN placements p
            ON s.student_id = p.student_id

        GROUP BY s.branch

        ORDER BY placed_students DESC
    """).fetchall()


    # ---------------------------------------------
    # BRANCH-WISE TOTAL STUDENTS
    # ---------------------------------------------

    branch_students = conn.execute("""
        SELECT
            branch,
            COUNT(*) AS total_students
        FROM students
        GROUP BY branch
        ORDER BY total_students DESC
    """).fetchall()


    # ---------------------------------------------
    # COMPANY-WISE PLACEMENTS
    # ---------------------------------------------

    company_data = conn.execute("""
    SELECT
        MIN(c.company_name) AS company_name,
        COUNT(p.placement_id) AS placed_students

    FROM companies c

    LEFT JOIN placements p
        ON c.company_id = p.company_id

    GROUP BY LOWER(TRIM(c.company_name))

    HAVING COUNT(p.placement_id) > 0

    ORDER BY placed_students DESC
""").fetchall()


    # ---------------------------------------------
    # COMPANY PACKAGE ANALYSIS
    # ---------------------------------------------

    company_package_data = conn.execute("""
    SELECT
        MIN(c.company_name) AS company_name,
        ROUND(AVG(p.package_lpa), 2) AS average_package,
        MAX(p.package_lpa) AS highest_package,
        COUNT(p.placement_id) AS placements

    FROM placements p

    JOIN companies c
        ON p.company_id = c.company_id

    GROUP BY LOWER(TRIM(c.company_name))

    ORDER BY average_package DESC
""").fetchall()

    # ---------------------------------------------
    # RECRUITMENT FUNNEL
    # ---------------------------------------------

    recruitment_funnel = {
        "students": total_students,
        "applications": total_applications,
        "interviews": total_interviews,
        "placements": total_placements
    }


    # ---------------------------------------------
    # INTERVIEW RESULTS
    # ---------------------------------------------

    interview_results = conn.execute("""
        SELECT
            result,
            COUNT(*) AS total
        FROM interviews
        WHERE result IS NOT NULL
        GROUP BY result
        ORDER BY total DESC
    """).fetchall()


    # ---------------------------------------------
    # APPLICATION STATUS
    # ---------------------------------------------

    application_status = conn.execute("""
        SELECT
            status,
            COUNT(*) AS total
        FROM applications
        WHERE status IS NOT NULL
        GROUP BY status
        ORDER BY total DESC
    """).fetchall()


    # ---------------------------------------------
    # PLACEMENT PACKAGE DISTRIBUTION
    # ---------------------------------------------

    package_distribution = conn.execute("""
        SELECT
            CASE
                WHEN package_lpa < 5 THEN '< 5 LPA'
                WHEN package_lpa >= 5
                     AND package_lpa < 8 THEN '5 - 8 LPA'
                WHEN package_lpa >= 8
                     AND package_lpa < 12 THEN '8 - 12 LPA'
                WHEN package_lpa >= 12
                     AND package_lpa < 18 THEN '12 - 18 LPA'
                ELSE '18+ LPA'
            END AS package_range,

            COUNT(*) AS total

        FROM placements

        GROUP BY package_range

        ORDER BY
            MIN(package_lpa)
    """).fetchall()


    conn.close()


    return render_template(
        "analytics.html",

        total_students=total_students,
        total_companies=total_companies,
        total_applications=total_applications,
        total_interviews=total_interviews,
        total_placements=total_placements,

        placement_rate=placement_rate,

        average_package=average_package,
        highest_package=highest_package,
        lowest_package=lowest_package,

        branch_data=branch_data,
        branch_students=branch_students,

        company_data=company_data,
        company_package_data=company_package_data,

        recruitment_funnel=recruitment_funnel,

        interview_results=interview_results,
        application_status=application_status,

        package_distribution=package_distribution
    )

if __name__ == "__main__":
    app.run(debug=True)