import os

DOCUMENTS_DIR = "documents"

roles = {
    "CEO": [
        ("strategy", "CEO Responsibilities - Strategy",
         "The CEO defines the company's long-term strategy, business direction, and organizational priorities. The CEO evaluates business opportunities, approves major initiatives, and ensures that departments work toward common company goals."),
        ("leadership", "CEO Responsibilities - Leadership",
         "The CEO provides executive leadership, communicates organizational goals, and coordinates with senior management. The CEO is responsible for making high-level decisions and establishing company-wide priorities."),
        ("finance", "CEO Responsibilities - Financial Oversight",
         "The CEO reviews financial performance, budgets, revenue targets, and major investments. Financial decisions are made in coordination with the finance leadership team."),
        ("risk", "CEO Responsibilities - Risk Management",
         "The CEO oversees major organizational risks including financial, operational, cybersecurity, and business continuity risks. Significant risks are reviewed with relevant department leaders."),
        ("operations", "CEO Responsibilities - Operations",
         "The CEO monitors overall business operations and ensures that departments have appropriate resources, processes, and objectives to operate effectively."),
        ("growth", "CEO Responsibilities - Business Growth",
         "The CEO evaluates opportunities for business expansion, partnerships, new products, and market development while considering company resources and strategic priorities."),
        ("culture", "CEO Responsibilities - Organizational Culture",
         "The CEO promotes professional standards, ethical behavior, collaboration, accountability, and a positive organizational culture across the company."),
        ("performance", "CEO Responsibilities - Performance",
         "The CEO reviews company-level performance indicators and works with senior leaders to identify improvements, operational issues, and strategic priorities."),
        ("stakeholders", "CEO Responsibilities - Stakeholders",
         "The CEO communicates with investors, board members, strategic partners, customers, and senior employees regarding major organizational matters."),
        ("decisions", "CEO Responsibilities - Decision Making",
         "The CEO makes high-impact organizational decisions after reviewing relevant business, financial, operational, and strategic information.")
    ],

    "Director": [
        ("planning", "Director Responsibilities - Planning",
         "Directors translate company strategy into departmental plans, objectives, and measurable initiatives."),
        ("teams", "Director Responsibilities - Team Management",
         "Directors manage department leaders, coordinate teams, assign priorities, and monitor execution of organizational plans."),
        ("budget", "Director Responsibilities - Budget",
         "Directors participate in departmental budgeting, resource allocation, expense monitoring, and financial planning."),
        ("projects", "Director Responsibilities - Projects",
         "Directors oversee major projects, review milestones, identify risks, and ensure projects remain aligned with business objectives."),
        ("performance", "Director Responsibilities - Performance",
         "Directors review department performance metrics and work with managers to address operational gaps."),
        ("communication", "Director Responsibilities - Communication",
         "Directors communicate organizational priorities between executive leadership and department teams."),
        ("risk", "Director Responsibilities - Risk",
         "Directors identify departmental risks and coordinate mitigation plans with relevant managers and specialists."),
        ("resources", "Director Responsibilities - Resources",
         "Directors evaluate staffing, technology, and operational resource requirements for their departments."),
        ("quality", "Director Responsibilities - Quality",
         "Directors establish quality expectations and review department processes to maintain consistent operational standards."),
        ("reporting", "Director Responsibilities - Reporting",
         "Directors prepare management reports covering department progress, performance, risks, and major initiatives.")
    ],

    "VP": [
        ("strategy", "VP Responsibilities - Strategy",
         "Vice Presidents support executive strategy by translating organizational goals into plans for their business areas."),
        ("leadership", "VP Responsibilities - Leadership",
         "Vice Presidents provide leadership to directors and senior managers and coordinate execution across multiple teams."),
        ("performance", "VP Responsibilities - Performance",
         "Vice Presidents monitor business performance indicators and review progress against organizational objectives."),
        ("operations", "VP Responsibilities - Operations",
         "Vice Presidents oversee operational activities across their business areas and coordinate improvements."),
        ("budget", "VP Responsibilities - Budget",
         "Vice Presidents participate in budget planning, resource allocation, and financial reviews."),
        ("projects", "VP Responsibilities - Projects",
         "Vice Presidents oversee strategic projects and ensure cross-functional teams remain aligned with business objectives."),
        ("risk", "VP Responsibilities - Risk",
         "Vice Presidents review significant business risks and coordinate mitigation actions with department leaders."),
        ("communication", "VP Responsibilities - Communication",
         "Vice Presidents communicate priorities between executive leadership and operational departments."),
        ("growth", "VP Responsibilities - Growth",
         "Vice Presidents evaluate growth opportunities, partnerships, and initiatives within their business areas."),
        ("reporting", "VP Responsibilities - Reporting",
         "Vice Presidents review reports from directors and provide business updates to executive leadership.")
    ],

    "Manager": [
        ("planning", "Manager Responsibilities - Planning",
         "Managers create team plans, assign work, establish priorities, and track progress toward department objectives."),
        ("team", "Manager Responsibilities - Team Management",
         "Managers supervise team members, provide guidance, conduct performance reviews, and support employee development."),
        ("projects", "Manager Responsibilities - Project Management",
         "Managers coordinate project activities, monitor deadlines, track risks, and communicate project status."),
        ("work", "Manager Responsibilities - Work Allocation",
         "Managers distribute tasks based on team skills, workload, priorities, and project requirements."),
        ("quality", "Manager Responsibilities - Quality",
         "Managers review team output and ensure that work follows established processes and quality standards."),
        ("issues", "Manager Responsibilities - Issue Management",
         "Managers identify operational issues, coordinate solutions, and escalate critical problems when necessary."),
        ("meetings", "Manager Responsibilities - Meetings",
         "Managers conduct team meetings, communicate priorities, review progress, and address blockers."),
        ("resources", "Manager Responsibilities - Resources",
         "Managers identify staffing, software, hardware, and training requirements for their teams."),
        ("reporting", "Manager Responsibilities - Reporting",
         "Managers prepare team performance reports and provide updates to department leadership."),
        ("development", "Manager Responsibilities - Employee Development",
         "Managers support employee growth through mentoring, feedback, training recommendations, and career discussions.")
    ],

    "TeamLead": [
        ("tasks", "TeamLead Responsibilities - Task Assignment",
         "Team Leads assign technical and operational tasks to team members based on priorities, skills, and workload."),
        ("guidance", "TeamLead Responsibilities - Technical Guidance",
         "Team Leads provide technical guidance, review implementation approaches, and help team members resolve complex issues."),
        ("code", "TeamLead Responsibilities - Code Review",
         "Team Leads review code changes for quality, maintainability, correctness, and adherence to team standards."),
        ("planning", "TeamLead Responsibilities - Sprint Planning",
         "Team Leads participate in sprint planning, estimate work, identify dependencies, and coordinate team execution."),
        ("issues", "TeamLead Responsibilities - Issue Resolution",
         "Team Leads investigate technical issues and coordinate solutions with engineers and senior technical staff."),
        ("communication", "TeamLead Responsibilities - Communication",
         "Team Leads communicate project progress, blockers, and technical risks to managers."),
        ("quality", "TeamLead Responsibilities - Quality",
         "Team Leads establish technical quality practices and ensure team deliverables meet expected standards."),
        ("mentoring", "TeamLead Responsibilities - Mentoring",
         "Team Leads mentor engineers, support technical learning, and provide constructive feedback."),
        ("deployment", "TeamLead Responsibilities - Deployment",
         "Team Leads coordinate deployment activities and verify that technical changes are ready for release."),
        ("documentation", "TeamLead Responsibilities - Documentation",
         "Team Leads ensure important technical decisions, processes, and system information are documented.")
    ],

    "SeniorEngineer": [
        ("design", "SeniorEngineer Responsibilities - System Design",
         "Senior Engineers design scalable software components, review architecture decisions, and select appropriate technical approaches."),
        ("code", "SeniorEngineer Responsibilities - Code Review",
         "Senior Engineers perform detailed code reviews and ensure implementation follows engineering standards."),
        ("mentoring", "SeniorEngineer Responsibilities - Mentoring",
         "Senior Engineers mentor engineers, explain technical concepts, and help team members solve difficult engineering problems."),
        ("debugging", "SeniorEngineer Responsibilities - Debugging",
         "Senior Engineers investigate complex production and development issues and identify reliable technical solutions."),
        ("architecture", "SeniorEngineer Responsibilities - Architecture",
         "Senior Engineers contribute to architecture decisions involving services, databases, APIs, security, and scalability."),
        ("testing", "SeniorEngineer Responsibilities - Testing",
         "Senior Engineers promote automated testing, integration testing, and reliable validation practices."),
        ("performance", "SeniorEngineer Responsibilities - Performance",
         "Senior Engineers analyze application performance and recommend improvements for scalability and efficiency."),
        ("security", "SeniorEngineer Responsibilities - Security",
         "Senior Engineers consider authentication, authorization, data protection, and secure coding practices."),
        ("deployment", "SeniorEngineer Responsibilities - Deployment",
         "Senior Engineers support release and deployment processes and investigate issues after deployment."),
        ("documentation", "SeniorEngineer Responsibilities - Documentation",
         "Senior Engineers maintain architecture documentation and technical decisions for important systems.")
    ],

    "Engineer": [
        ("development", "Engineer Responsibilities - Software Development",
         "Engineers are responsible for designing, developing, and maintaining software applications according to project requirements."),
        ("testing", "Engineer Responsibilities - Testing",
         "Engineers write and execute tests to verify that software components work correctly and meet expected requirements."),
        ("debugging", "Engineer Responsibilities - Debugging",
         "Engineers investigate bugs, identify root causes, and implement fixes while minimizing impact on existing functionality."),
        ("code", "Engineer Responsibilities - Code Quality",
         "Engineers write readable, maintainable code and follow established coding standards and development practices."),
        ("collaboration", "Engineer Responsibilities - Collaboration",
         "Engineers collaborate with Team Leads, Senior Engineers, product teams, and other stakeholders during software development."),
        ("deployment", "Engineer Responsibilities - Deployment",
         "Engineers support application deployment activities and verify that new releases operate correctly."),
        ("documentation", "Engineer Responsibilities - Documentation",
         "Engineers maintain technical documentation for software components, APIs, configuration, and development procedures."),
        ("security", "Engineer Responsibilities - Security",
         "Engineers follow secure coding practices and consider authentication, authorization, input validation, and data protection."),
        ("maintenance", "Engineer Responsibilities - Maintenance",
         "Engineers maintain existing applications, fix defects, improve performance, and implement approved enhancements."),
        ("version", "Engineer Responsibilities - Version Control",
         "Engineers use version control systems to manage source code, review changes, collaborate with developers, and maintain project history.")
    ],

    "Analyst": [
        ("data", "Analyst Responsibilities - Data Analysis",
         "Analysts collect, clean, analyze, and interpret data to support organizational decision-making."),
        ("reporting", "Analyst Responsibilities - Reporting",
         "Analysts prepare reports and dashboards that communicate business performance and important trends."),
        ("requirements", "Analyst Responsibilities - Requirements",
         "Analysts gather business requirements from stakeholders and translate them into clear documentation."),
        ("research", "Analyst Responsibilities - Research",
         "Analysts conduct research and compare relevant information to support business and operational decisions."),
        ("metrics", "Analyst Responsibilities - Metrics",
         "Analysts define and monitor relevant metrics to measure business processes and outcomes."),
        ("quality", "Analyst Responsibilities - Data Quality",
         "Analysts validate data accuracy, identify inconsistencies, and coordinate corrections when required."),
        ("trends", "Analyst Responsibilities - Trend Analysis",
         "Analysts identify patterns and trends in historical and current data."),
        ("communication", "Analyst Responsibilities - Communication",
         "Analysts communicate findings to managers and stakeholders using clear summaries, reports, and visualizations."),
        ("process", "Analyst Responsibilities - Process Analysis",
         "Analysts evaluate business processes and identify opportunities for efficiency improvements."),
        ("documentation", "Analyst Responsibilities - Documentation",
         "Analysts document assumptions, data sources, analysis methods, findings, and recommendations.")
    ],

    "HR": [
        ("recruitment", "HR Responsibilities - Recruitment",
         "HR manages recruitment activities including job requirements, candidate screening, interviews, selection coordination, and onboarding."),
        ("onboarding", "HR Responsibilities - Onboarding",
         "HR coordinates employee onboarding, documentation, orientation, and initial organizational processes."),
        ("policies", "HR Responsibilities - Policies",
         "HR maintains employee policies and communicates organizational rules, procedures, and workplace standards."),
        ("performance", "HR Responsibilities - Performance",
         "HR supports performance management processes including reviews, feedback procedures, and employee development."),
        ("training", "HR Responsibilities - Training",
         "HR coordinates employee training programs and tracks learning and development activities."),
        ("attendance", "HR Responsibilities - Attendance",
         "HR maintains attendance records and supports organizational processes related to working hours and leave."),
        ("employee", "HR Responsibilities - Employee Relations",
         "HR handles employee concerns, workplace communication, and formal employee relations processes."),
        ("records", "HR Responsibilities - Records",
         "HR maintains employee records and ensures personnel information is handled according to organizational policies."),
        ("benefits", "HR Responsibilities - Benefits",
         "HR coordinates employee benefits and communicates relevant information about available programs."),
        ("exit", "HR Responsibilities - Exit Process",
         "HR coordinates resignation, exit documentation, knowledge transfer, and employee separation procedures.")
    ],

    "Intern": [
        ("learning", "Intern Responsibilities - Learning",
         "Interns learn company processes, tools, technologies, and professional practices under the guidance of assigned team members."),
        ("tasks", "Intern Responsibilities - Assigned Tasks",
         "Interns complete assigned tasks according to instructions, project requirements, and established deadlines."),
        ("documentation", "Intern Responsibilities - Documentation",
         "Interns maintain clear documentation of assigned work, findings, progress, and completed activities."),
        ("teamwork", "Intern Responsibilities - Teamwork",
         "Interns collaborate with team members, attend relevant meetings, and communicate progress and blockers."),
        ("testing", "Intern Responsibilities - Testing",
         "Interns may assist with software testing, data validation, documentation checks, or other supervised quality activities."),
        ("research", "Intern Responsibilities - Research",
         "Interns conduct supervised research and summarize findings relevant to their assigned projects."),
        ("communication", "Intern Responsibilities - Communication",
         "Interns communicate clearly with mentors and team members about task progress, questions, and issues."),
        ("tools", "Intern Responsibilities - Tools",
         "Interns learn and use tools required by their project while following company security and usage guidelines."),
        ("feedback", "Intern Responsibilities - Feedback",
         "Interns receive feedback from mentors and use it to improve technical skills, work quality, and professional practices."),
        ("security", "Intern Responsibilities - Security",
         "Interns follow company security policies and protect confidential information while working on assigned tasks.")
    ]
}


os.makedirs(DOCUMENTS_DIR, exist_ok=True)

count = 0

for role, documents in roles.items():

    for index, (_, title, content) in enumerate(documents, start=1):

        filename = f"{role}_doc{index}.txt"
        filepath = os.path.join(DOCUMENTS_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as file:
            file.write(f"{title}\n\n")
            file.write(f"Role: {role}\n\n")
            file.write(content)

        count += 1

print(f"Successfully generated {count} role-based documents.")