from app import create_app, db
from app.core.models import Course

def check_and_create_courses():
    app = create_app()
    with app.app_context():
        # Check if there are any courses
        courses = Course.query.all()
        if not courses:
            print("No courses found. Creating default courses...")
            default_courses = [
                {"name": "Bachelor of Science in Computer Science", "code": "BSCS"},
                {"name": "Bachelor of Science in Information Technology", "code": "BSIT"},
                {"name": "Bachelor of Science in Information Systems", "code": "BSIS"},
                {"name": "Bachelor of Science in Computer Engineering", "code": "BSCpE"},
            ]
            
            for course_data in default_courses:
                course = Course(name=course_data["name"], code=course_data["code"])
                db.session.add(course)
            
            try:
                db.session.commit()
                print("Successfully created default courses!")
                courses = Course.query.all()
                print("\nAvailable Courses:")
                for course in courses:
                    print(f"- {course.code}: {course.name}")
            except Exception as e:
                db.session.rollback()
                print(f"Error creating courses: {str(e)}")
        else:
            print("\nExisting Courses:")
            for course in courses:
                print(f"- {course.code}: {course.name}")

if __name__ == "__main__":
    check_and_create_courses()
