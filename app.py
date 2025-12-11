from flask import Flask
from database import db
import os
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta, date
import random

app = Flask(__name__)

# APP CONFIGURATION
app.config['SECRET_KEY'] = 'planify_secret_key'

# -- ENSURE INSTANCE FOLDER EXISTS --
os.makedirs(app.instance_path, exist_ok=True)

# DATABASE CONNECTION
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(app.instance_path, 'planify.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# FLASK-LOGIN SETUP
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

from models import User, Course, LessonPlan, LearningMaterial, Enrollment, AttendanceRecord, ContactMessage


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# IMPORT ROUTES
from routes import *


def initialize_database():
    """Initialize database with dummy data"""
    db.create_all()
    print("Database ready!")

    # Check if data already exists
    if User.query.filter_by(username="admin").first():
        print("Database already initialized with data.")
        return

    print("\nCreating dummy data...\n")

    try:
        # ==========================================
        # CREATE USERS
        # ==========================================
        print("Creating users...")

        dummy_users = [
            User(
                first_name="Admin",
                last_name="User",
                username="admin",
                email="admin@example.com",
                contact_number="09123456789",
                role="admin",
                password=generate_password_hash("Admin123")
            ),
            # EDUCATORS (4 educators)
            User(
                first_name="Jane",
                last_name="Smith",
                username="educator1",
                email="educator1@example.com",
                contact_number="09222222222",
                role="educator",
                password=generate_password_hash("Educator123")
            ),
            User(
                first_name="Elaine",
                last_name="Villanueva",
                username="evillanueva",
                email="evillanueva@example.com",
                contact_number="09333333333",
                role="educator",
                password=generate_password_hash("villanueva123")
            ),
            User(
                first_name="Roland",
                last_name="Santos",
                username="rsantos",
                email="rsantos@example.com",
                contact_number="09444444444",
                role="educator",
                password=generate_password_hash("rsantos123")
            ),
            User(
                first_name="Patricia",
                last_name="Cruz",
                username="pcruz",
                email="pcruz@example.com",
                contact_number="09555555555",
                role="educator",
                password=generate_password_hash("pcruz123")
            ),
            # STUDENTS (20 students)
            User(
                first_name="John",
                last_name="Doe",
                username="student1",
                email="student1@example.com",
                contact_number="09111111111",
                role="student",
                password=generate_password_hash("Student123")
            ),
            User(
                first_name="Alfred",
                last_name="Torres",
                username="atorres",
                email="atorres@example.com",
                contact_number="09666666666",
                role="student",
                password=generate_password_hash("atorres123")
            ),
            User(
                first_name="Bianca",
                last_name="Mendoza",
                username="bmendoza",
                email="bmendoza@example.com",
                contact_number="09777777777",
                role="student",
                password=generate_password_hash("bmendoza123")
            ),
            User(
                first_name="Cedric",
                last_name="Gonzales",
                username="cgonzales",
                email="cgonzales@example.com",
                contact_number="09888888888",
                role="student",
                password=generate_password_hash("cgonzales123")
            ),
            User(
                first_name="Danica",
                last_name="Flores",
                username="dflores",
                email="dflores@example.com",
                contact_number="09999999999",
                role="student",
                password=generate_password_hash("dflores123")
            ),
            User(
                first_name="Ethan",
                last_name="Navarro",
                username="enavarro",
                email="enavarro@example.com",
                contact_number="09122222222",
                role="student",
                password=generate_password_hash("enavarro123")
            ),
            User(
                first_name="Fiona",
                last_name="Salazar",
                username="fsalazar",
                email="fsalazar@example.com",
                contact_number="09133333333",
                role="student",
                password=generate_password_hash("fsalazar123")
            ),
            User(
                first_name="Gabriel",
                last_name="David",
                username="gdavid",
                email="gdavid@example.com",
                contact_number="09144444444",
                role="student",
                password=generate_password_hash("gdavid123")
            ),
            User(
                first_name="Hannah",
                last_name="Ocampo",
                username="hocampo",
                email="hocampo@example.com",
                contact_number="09155555555",
                role="student",
                password=generate_password_hash("hocampo123")
            ),
            User(
                first_name="Ian",
                last_name="Perez",
                username="iperez",
                email="iperez@example.com",
                contact_number="09166666666",
                role="student",
                password=generate_password_hash("iperez123")
            ),
            User(
                first_name="Jasmine",
                last_name="Ramos",
                username="jramos",
                email="jramos@example.com",
                contact_number="09177777777",
                role="student",
                password=generate_password_hash("jramos123")
            ),
            User(
                first_name="Kyle",
                last_name="Bautista",
                username="kbautista",
                email="kbautista@example.com",
                contact_number="09188888888",
                role="student",
                password=generate_password_hash("kbautista123")
            ),
            User(
                first_name="Lara",
                last_name="Domingo",
                username="ldomingo",
                email="ldomingo@example.com",
                contact_number="09199999999",
                role="student",
                password=generate_password_hash("ldomingo123")
            ),
            User(
                first_name="Marcus",
                last_name="Jimenez",
                username="mjimenez",
                email="mjimenez@example.com",
                contact_number="09112222222",
                role="student",
                password=generate_password_hash("mjimenez123")
            ),
            User(
                first_name="Nicole",
                last_name="Padilla",
                username="npadilla",
                email="npadilla@example.com",
                contact_number="09113333333",
                role="student",
                password=generate_password_hash("npadilla123")
            ),
            User(
                first_name="Oscar",
                last_name="Valdez",
                username="ovaldez",
                email="ovaldez@example.com",
                contact_number="09114444444",
                role="student",
                password=generate_password_hash("ovaldez123")
            ),
            User(
                first_name="Paula",
                last_name="Marasigan",
                username="pmarasigan",
                email="pmarasigan@example.com",
                contact_number="09115555555",
                role="student",
                password=generate_password_hash("pmarasigan123")
            ),
            User(
                first_name="Quentin",
                last_name="Abadilla",
                username="qabadilla",
                email="qabadilla@example.com",
                contact_number="09116666666",
                role="student",
                password=generate_password_hash("qabadilla123")
            ),
            User(
                first_name="Rhea",
                last_name="Lagman",
                username="rlagman",
                email="rlagman@example.com",
                contact_number="09117777777",
                role="student",
                password=generate_password_hash("rlagman123")
            ),
            User(
                first_name="Samuel",
                last_name="Fernandez",
                username="sfernandez",
                email="sfernandez@example.com",
                contact_number="09118888888",
                role="student",
                password=generate_password_hash("sfernandez123")
            ),
            User(
                first_name="Trixie",
                last_name="Gutierrez",
                username="tgutierrez",
                email="tgutierrez@example.com",
                contact_number="09119999999",
                role="student",
                password=generate_password_hash("tgutierrez123")
            )
        ]

        for user in dummy_users:
            db.session.add(user)
        db.session.commit()
        print("✓ Users created!")

        # ==========================================
        # CREATE COURSES (10 courses)
        # ==========================================
        print("Creating courses...")

        educators = User.query.filter_by(role='educator').all()

        courses_data = [
            # Jane Smith (educator1) - 3 courses
            {"name": "Introduction to Programming", "code": "CS101", "block": "BSIT 2101",
             "desc": "Learn the fundamentals of programming using Python", "educator_id": educators[0].id},
            {"name": "Data Structures", "code": "CS201", "block": "BSIT 2102",
             "desc": "Advanced data structures and algorithms", "educator_id": educators[0].id},
            {"name": "Web Development", "code": "CS301", "block": "BSIT 3101",
             "desc": "Building modern web applications", "educator_id": educators[0].id},

            # Elaine Villanueva - 3 courses
            {"name": "Database Management", "code": "IT211", "block": "BSIT 2201",
             "desc": "Database design and SQL programming", "educator_id": educators[1].id},
            {"name": "Network Administration", "code": "IT311", "block": "BSIT 3201",
             "desc": "Computer networking fundamentals", "educator_id": educators[1].id},
            {"name": "Cybersecurity Basics", "code": "IT411", "block": "BSIT 4201",
             "desc": "Introduction to information security", "educator_id": educators[1].id},

            # Roland Santos - 2 courses
            {"name": "Mobile App Development", "code": "CS401", "block": "BSCS 4101",
             "desc": "Android and iOS development", "educator_id": educators[2].id},
            {"name": "Software Engineering", "code": "CS402", "block": "BSCS 4102",
             "desc": "Software development lifecycle", "educator_id": educators[2].id},

            # Patricia Cruz - 2 courses
            {"name": "Artificial Intelligence", "code": "CS501", "block": "BSCS 5101",
             "desc": "Machine learning and AI fundamentals", "educator_id": educators[3].id},
            {"name": "Computer Graphics", "code": "CS502", "block": "BSCS 5102",
             "desc": "2D and 3D graphics programming", "educator_id": educators[3].id},
        ]

        courses = []
        for course_data in courses_data:
            course = Course(
                course_name=course_data["name"],
                course_code=course_data["code"],
                block_section=course_data["block"],
                description=course_data["desc"],
                educator_id=course_data["educator_id"],
                enrollment_code=Course.generate_enrollment_code(),
                created_at=datetime.utcnow() - timedelta(days=random.randint(30, 90))
            )
            courses.append(course)
            db.session.add(course)

        db.session.commit()
        print("✓ Courses created!")

        # ==========================================
        # ENROLL STUDENTS IN COURSES
        # ==========================================
        print("Enrolling students...")

        students = User.query.filter_by(role='student').all()
        all_courses = Course.query.all()

        enrollment_count = 0
        for student in students:
            for course in all_courses:
                enrollment = Enrollment(
                    student_id=student.id,
                    course_id=course.id,
                    enrolled_at=datetime.utcnow() - timedelta(days=random.randint(25, 85))
                )
                db.session.add(enrollment)
                enrollment_count += 1

        db.session.commit()
        print(f"✓ Enrolled {len(students)} students in {len(all_courses)} courses! (Total: {enrollment_count} enrollments)")

        # ==========================================
        # CREATE LESSON PLANS (20 lesson plans)
        # ==========================================
        print("Creating lesson plans...")

        lesson_plans_data = [
            {"title": "Introduction to Python Basics", "topic": "Variables and Data Types",
             "objectives": "Understand variables, data types, and basic operations in Python"},
            {"title": "Control Structures in Programming", "topic": "If-Else and Loops",
             "objectives": "Master conditional statements and iteration"},
            {"title": "Functions and Modules", "topic": "Code Reusability",
             "objectives": "Learn to create and use functions effectively"},
            {"title": "Object-Oriented Programming", "topic": "Classes and Objects",
             "objectives": "Understand OOP principles and implementation"},
            {"title": "Arrays and Lists", "topic": "Linear Data Structures",
             "objectives": "Work with arrays and list operations"},
            {"title": "Linked Lists Implementation", "topic": "Dynamic Data Structures",
             "objectives": "Implement singly and doubly linked lists"},
            {"title": "Stack and Queue Operations", "topic": "LIFO and FIFO Structures",
             "objectives": "Master stack and queue implementations"},
            {"title": "Trees and Graph Basics", "topic": "Non-linear Structures",
             "objectives": "Understand tree and graph traversals"},
            {"title": "HTML Fundamentals", "topic": "Web Page Structure",
             "objectives": "Create semantic HTML documents"},
            {"title": "CSS Styling Techniques", "topic": "Web Design", "objectives": "Style web pages using CSS"},
            {"title": "JavaScript Essentials", "topic": "Client-Side Programming",
             "objectives": "Add interactivity to web pages"},
            {"title": "Relational Database Design", "topic": "ER Diagrams and Normalization",
             "objectives": "Design efficient database schemas"},
            {"title": "SQL Query Writing", "topic": "Data Manipulation", "objectives": "Write complex SQL queries"},
            {"title": "Network Protocols", "topic": "TCP/IP and OSI Model",
             "objectives": "Understand network communication"},
            {"title": "Firewall Configuration", "topic": "Network Security",
             "objectives": "Configure and manage firewalls"},
            {"title": "Android Development Setup", "topic": "Development Environment",
             "objectives": "Set up Android Studio and create first app"},
            {"title": "iOS Development Basics", "topic": "Swift Programming",
             "objectives": "Learn Swift and iOS app structure"},
            {"title": "Agile Methodology", "topic": "Software Development Process",
             "objectives": "Implement agile practices in projects"},
            {"title": "Machine Learning Algorithms", "topic": "Supervised Learning",
             "objectives": "Understand regression and classification"},
            {"title": "Neural Networks", "topic": "Deep Learning Basics",
             "objectives": "Build simple neural networks"},
        ]

        lesson_plans = []
        for idx, lp_data in enumerate(lesson_plans_data):
            course = all_courses[idx % len(all_courses)]
            lesson_plan = LessonPlan(
                title=lp_data["title"],
                topic=lp_data["topic"],
                objectives=lp_data["objectives"],
                description=f"This lesson covers {lp_data['topic'].lower()} in detail with practical examples.",
                course_id=course.id,
                educator_id=course.educator_id,
                created_at=datetime.utcnow() - timedelta(days=random.randint(15, 70)),
                updated_at=datetime.utcnow() - timedelta(days=random.randint(1, 15))
            )
            lesson_plans.append(lesson_plan)
            db.session.add(lesson_plan)

        db.session.commit()
        print("✓ Lesson plans created!")

        # ==========================================
        # CREATE LEARNING MATERIALS
        # ==========================================
        print("Creating learning materials...")

        materials_data = [
            "Python_Basics.pdf", "Variables_Tutorial.docx", "Control_Structures.pdf",
            "Functions_Examples.pdf", "OOP_Concepts.pptx", "Array_Operations.pdf",
            "LinkedList_Guide.pdf", "Stack_Queue_Tutorial.docx", "Tree_Traversal.pdf",
            "Graph_Algorithms.pdf", "HTML_Reference.pdf", "CSS_Cheatsheet.pdf",
            "JavaScript_Guide.pdf", "Database_Design.docx", "SQL_Query_Examples.pdf",
            "TCP_IP_Protocol.pdf", "Network_Security.pptx", "Android_Setup.pdf",
            "Swift_Programming.pdf", "Agile_Framework.pdf", "ML_Algorithms.pdf",
            "Neural_Networks.pdf", "Practice_Exercises.pdf", "Project_Template.docx",
            "Code_Examples.txt", "Assignment.pdf", "Lab_Manual.pdf",
            "Study_Guide.pdf", "Review_Questions.docx", "Final_Project.pdf",
        ]

        material_count = 0
        for idx, lesson_plan in enumerate(lesson_plans):
            num_materials = random.randint(1, 2)
            for i in range(num_materials):
                material_idx = (idx * 2 + i) % len(materials_data)
                material = LearningMaterial(
                    lesson_plan_id=lesson_plan.id,
                    filename=materials_data[material_idx],
                    filepath=f"static/uploads/dummy_{materials_data[material_idx]}",
                    uploaded_at=datetime.utcnow() - timedelta(days=random.randint(5, 60))
                )
                db.session.add(material)
                material_count += 1

        db.session.commit()
        print(f"✓ Learning materials created! (Total: {material_count})")

        # ==========================================
        # CREATE ATTENDANCE RECORDS
        # ==========================================
        print("Creating attendance records for past 20 days...")
        print("  (This may take a moment...)")

        statuses = ['present', 'absent', 'late', 'excused']
        attendance_count = 0

        for days_ago in range(20, 0, -1):
            attendance_date = date.today() - timedelta(days=days_ago)

            for course in all_courses:
                course_enrollments = Enrollment.query.filter_by(course_id=course.id).all()

                for enrollment in course_enrollments:
                    status = random.choices(
                        statuses,
                        weights=[70, 10, 15, 5],
                        k=1
                    )[0]

                    attendance = AttendanceRecord(
                        course_id=course.id,
                        student_id=enrollment.student_id,
                        date=attendance_date,
                        status=status,
                        recorded_by=course.educator_id,
                        recorded_at=datetime.combine(attendance_date, datetime.min.time()) +
                                   timedelta(hours=9, minutes=random.randint(0, 30))
                    )
                    db.session.add(attendance)
                    attendance_count += 1

            # Commit every day (every 200 records) to avoid memory issues
            if days_ago % 5 == 0:
                db.session.commit()
                print(f"  Progress: {21 - days_ago}/20 days completed...")

        db.session.commit()
        print(f"✓ Attendance records created! (Total: {attendance_count})")

        # ==========================================
        # CREATE CONTACT MESSAGES
        # ==========================================
        print("Creating contact messages...")

        contact_messages_data = [
            {"name": "Maria Garcia", "email": "maria.garcia@email.com",
             "message": "I'm interested in enrolling in your programming courses."},
            {"name": "Robert Lee", "email": "robert.lee@email.com",
             "message": "How can I reset my password?"},
            {"name": "Sarah Johnson", "email": "sarah.j@email.com",
             "message": "Are there any scholarship opportunities?"},
            {"name": "David Kim", "email": "david.kim@email.com",
             "message": "I would like to report a technical issue."},
            {"name": "Emily Chen", "email": "emily.chen@email.com",
             "message": "Can you recommend which course is best for beginners?"},
            {"name": "Michael Brown", "email": "m.brown@email.com",
             "message": "Is there a mobile app version?"},
            {"name": "Jessica White", "email": "j.white@email.com",
             "message": "How do I view my attendance history?"},
            {"name": "Christopher Davis", "email": "c.davis@email.com",
             "message": "I'm having trouble downloading materials."},
            {"name": "Amanda Martinez", "email": "amanda.m@email.com",
             "message": "What are the system requirements?"},
            {"name": "Daniel Wilson", "email": "d.wilson@email.com",
             "message": "Can I enroll in multiple courses?"},
            {"name": "Lisa Anderson", "email": "lisa.a@email.com",
             "message": "How do I contact my instructor?"},
            {"name": "James Taylor", "email": "james.t@email.com",
             "message": "Is there a deadline for enrollment?"},
            {"name": "Jennifer Thomas", "email": "j.thomas@email.com",
             "message": "I need help understanding the grading system."},
            {"name": "Matthew Jackson", "email": "matt.j@email.com",
             "message": "Are the courses self-paced?"},
            {"name": "Ashley Moore", "email": "ashley.m@email.com",
             "message": "Can I get a certificate upon completion?"},
            {"name": "Joshua Martin", "email": "josh.m@email.com",
             "message": "The platform is running slow."},
            {"name": "Stephanie Lee", "email": "steph.lee@email.com",
             "message": "How can I update my profile?"},
            {"name": "Andrew Harris", "email": "a.harris@email.com",
             "message": "I accidentally unenrolled from a course."},
            {"name": "Michelle Clark", "email": "m.clark@email.com",
             "message": "Are there any prerequisites for advanced courses?"},
            {"name": "Kevin Rodriguez", "email": "k.rodriguez@email.com",
             "message": "Thank you for this excellent platform!"},
        ]

        for idx, msg_data in enumerate(contact_messages_data):
            message = ContactMessage(
                name=msg_data["name"],
                email=msg_data["email"],
                message=msg_data["message"],
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                is_read=random.choice([True, False]) if idx < 15 else False
            )
            db.session.add(message)

        db.session.commit()
        print(f"✓ Contact messages created! (Total: {len(contact_messages_data)})")

        print("\n" + "=" * 60)
        print("✅ DATABASE INITIALIZATION COMPLETE!")
        print("=" * 60)
        print(f"✓ {len(dummy_users)} Users")
        print(f"✓ {len(courses)} Courses")
        print(f"✓ {enrollment_count} Enrollments")
        print(f"✓ {len(lesson_plans)} Lesson Plans")
        print(f"✓ {material_count} Learning Materials")
        print(f"✓ {attendance_count} Attendance Records")
        print(f"✓ {len(contact_messages_data)} Contact Messages")
        print("=" * 60 + "\n")

    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Error during database initialization: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    with app.app_context():
        initialize_database()
    app.run(debug=True)

