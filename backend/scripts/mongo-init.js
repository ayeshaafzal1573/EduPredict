// MongoDB initialization script
db = db.getSiblingDB('edupredict');

// Create collections with validation
db.createCollection('users', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['email', 'first_name', 'last_name', 'role', 'hashed_password'],
      properties: {
        email: { bsonType: 'string' },
        first_name: { bsonType: 'string' },
        last_name: { bsonType: 'string' },
        role: { enum: ['student', 'teacher', 'admin', 'analyst'] },
        hashed_password: { bsonType: 'string' },
        is_active: { bsonType: 'bool' }
      }
    }
  }
});

db.createCollection('students');
db.createCollection('courses');
db.createCollection('grades');
db.createCollection('attendance');
db.createCollection('notifications');

// Create indexes for better performance
db.users.createIndex({ email: 1 }, { unique: true });
db.students.createIndex({ student_id: 1 }, { unique: true });
db.courses.createIndex({ code: 1 }, { unique: true });
db.grades.createIndex({ student_id: 1, course_id: 1 });
db.attendance.createIndex({ student_id: 1, course_id: 1, date: 1 });
db.notifications.createIndex({ user_id: 1, created_at: -1 });

print('MongoDB initialization completed');