from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import get_db
from datetime import datetime, timedelta

class User(UserMixin):
    def __init__(self, id, username, email, password_hash):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash

    @staticmethod
    def get(user_id):
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        if not user:
            return None
        return User(id=user['id'], username=user['username'], email=user['email'], password_hash=user['password_hash'])

    @staticmethod
    def get_by_username(username):
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if not user:
            return None
        return User(id=user['id'], username=user['username'], email=user['email'], password_hash=user['password_hash'])

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Medication:
    def __init__(self, id, name, dosage_schedule, form_type, stock, user_id, description=None, next_dose=None, profile_id=None):
        self.id = id
        self.name = name
        self.dosage_schedule = dosage_schedule
        self.form_type = form_type
        self.stock = stock
        self.user_id = user_id
        self.description = description
        self.next_dose = next_dose
        self.profile_id = profile_id

    @staticmethod
    def get_user_medications(user_id):
        db = get_db()
        medications = db.execute('SELECT * FROM medications WHERE user_id = ?', (user_id,)).fetchall()
        return [Medication(
            id=row['id'],
            name=row['name'],
            dosage_schedule=row['dosage_schedule'],
            form_type=row['form_type'],
            stock=row['stock'],
            user_id=row['user_id'],
            description=row['description'],
            next_dose=row['next_dose'],
            profile_id=row['profile_id']
        ) for row in medications]

    @staticmethod
    def get_medication(med_id):
        db = get_db()
        med = db.execute('SELECT * FROM medications WHERE id = ?', (med_id,)).fetchone()
        if not med:
            return None
        return Medication(
            id=med['id'],
            name=med['name'],
            dosage_schedule=med['dosage_schedule'],
            form_type=med['form_type'],
            stock=med['stock'],
            user_id=med['user_id'],
            description=med['description'],
            next_dose=med['next_dose'],
            profile_id=med['profile_id']
        )

    @staticmethod
    def update_medication(med_id, name, dosage_schedule, form_type, stock, description, next_dose):
        db = get_db()
        db.execute('''
            UPDATE medications 
            SET name = ?, dosage_schedule = ?, form_type = ?, stock = ?, 
                description = ?, next_dose = ? 
            WHERE id = ?
        ''', (name, dosage_schedule, form_type, stock, description, next_dose, med_id))
        db.commit()

    @staticmethod
    def delete_medication(med_id):
        db = get_db()
        db.execute('DELETE FROM medications WHERE id = ?', (med_id,))
        db.commit()

    @staticmethod
    def search_medications(query):
        db = get_db()
        medications = db.execute('SELECT * FROM medications WHERE name LIKE ?', ('%' + query + '%',)).fetchall()
        return [Medication(id=row['id'], name=row['name'], dosage_schedule=row['dosage_schedule'], form_type=row['form_type'],
                           stock=row['stock'], user_id=row['user_id'], description=row['description'],
                           next_dose=row['next_dose'], profile_id=row['profile_id']) for row in medications]

    @staticmethod
    def get_medicine_suggestions(partial_name):
        db = get_db()
        medicines = db.execute('''
            SELECT DISTINCT name 
            FROM medications 
            WHERE name LIKE ? 
            LIMIT 10
        ''', ('%' + partial_name + '%',)).fetchall()
        return [med['name'] for med in medicines]

    @staticmethod
    def get_profile_medications(profile_id):
        db = get_db()
        medications = db.execute('''
            SELECT * FROM medications 
            WHERE profile_id = ? 
            ORDER BY name
        ''', (profile_id,)).fetchall()
        return [Medication(
            id=row['id'],
            name=row['name'],
            dosage_schedule=row['dosage_schedule'],
            form_type=row['form_type'],
            stock=row['stock'],
            user_id=row['user_id'],
            description=row['description'],
            next_dose=row['next_dose'],
            profile_id=row['profile_id']
        ) for row in medications]

    @staticmethod
    def get_by_name(name):
        db = get_db()
        med = db.execute('SELECT * FROM medications WHERE name = ?', (name,)).fetchone()
        if not med:
            return None
        return Medication(
            id=med['id'],
            name=med['name'],
            dosage_schedule=med['dosage_schedule'],
            form_type=med['form_type'],
            stock=med['stock'],
            user_id=med['user_id'],
            description=med['description'],
            next_dose=med['next_dose'],
            profile_id=med['profile_id']
        )

class MedicationLog:
    def __init__(self, id, medication_id, user_id, taken_at, status):
        self.id = id
        self.medication_id = medication_id
        self.user_id = user_id
        self.taken_at = taken_at
        self.status = status

    @staticmethod
    def log_medication(medication_id, user_id, status):
        db = get_db()
        db.execute('INSERT INTO medication_logs (medication_id, user_id, taken_at, status) VALUES (?, ?, ?, ?)',
                   (medication_id, user_id, datetime.now(), status))
        db.commit()

    @staticmethod
    def get_logs(user_id, days=7):
        db = get_db()
        logs = db.execute('SELECT * FROM medication_logs WHERE user_id = ? AND taken_at >= ? ORDER BY taken_at DESC',
                          (user_id, datetime.now() - timedelta(days=days))).fetchall()
        return [MedicationLog(id=row['id'], medication_id=row['medication_id'], user_id=row['user_id'],
                              taken_at=row['taken_at'], status=row['status']) for row in logs]

    @staticmethod
    def get_logs_by_period(user_id, start_date, end_date):
        db = get_db()
        logs = db.execute('''
            SELECT ml.*, m.name as medication_name,
                   datetime(ml.taken_at) as taken_at
            FROM medication_logs ml
            JOIN medications m ON ml.medication_id = m.id
            WHERE m.user_id = ? AND ml.taken_at BETWEEN ? AND ?
            ORDER BY ml.taken_at DESC
        ''', (user_id, start_date, end_date)).fetchall()
        
        # Convert the logs to a list of dictionaries with proper datetime objects
        formatted_logs = []
        for log in logs:
            log_dict = dict(log)
            try:
                # Try parsing with milliseconds
                log_dict['taken_at'] = datetime.strptime(log['taken_at'].split('.')[0], '%Y-%m-%d %H:%M:%S')
            except (ValueError, AttributeError):
                # If that fails, try without milliseconds
                try:
                    log_dict['taken_at'] = datetime.strptime(log['taken_at'], '%Y-%m-%d %H:%M:%S')
                except (ValueError, AttributeError):
                    # If all parsing fails, use the current time
                    log_dict['taken_at'] = datetime.now()
            formatted_logs.append(log_dict)
        
        return formatted_logs

class Appointment:
    def __init__(self, id, user_id, doctor_name, appointment_date, description):
        self.id = id
        self.user_id = user_id
        self.doctor_name = doctor_name
        self.appointment_date = appointment_date
        self.description = description

    @staticmethod
    def add_appointment(user_id, doctor_name, appointment_date, description):
        db = get_db()
        db.execute('INSERT INTO appointments (user_id, doctor_name, appointment_date, description) VALUES (?, ?, ?, ?)',
                   (user_id, doctor_name, appointment_date, description))
        db.commit()

    @staticmethod
    def get_upcoming_appointments(user_id):
        db = get_db()
        appointments = db.execute('SELECT * FROM appointments WHERE user_id = ? AND appointment_date > ? ORDER BY appointment_date',
                                  (user_id, datetime.now())).fetchall()
        return [Appointment(id=row['id'], user_id=row['user_id'], doctor_name=row['doctor_name'],
                            appointment_date=row['appointment_date'], description=row['description']) for row in appointments]

class WeightLog:
    def __init__(self, id, user_id, weight, logged_at):
        self.id = id
        self.user_id = user_id
        self.weight = weight
        self.logged_at = logged_at

    @staticmethod
    def log_weight(user_id, weight):
        db = get_db()
        db.execute('INSERT INTO weight_logs (user_id, weight, logged_at) VALUES (?, ?, ?)',
                   (user_id, weight, datetime.now()))
        db.commit()

    @staticmethod
    def get_weight_history(user_id):
        db = get_db()
        logs = db.execute('SELECT * FROM weight_logs WHERE user_id = ? ORDER BY logged_at DESC', (user_id,)).fetchall()
        return [WeightLog(id=row['id'], user_id=row['user_id'], weight=row['weight'], logged_at=row['logged_at']) for row in logs]

class Profile:
    def __init__(self, id, user_id, name, relationship):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.relationship = relationship

    @staticmethod
    def add_profile(user_id, name, relationship):
        db = get_db()
        db.execute('INSERT INTO profiles (user_id, name, relationship) VALUES (?, ?, ?)',
                   (user_id, name, relationship))
        db.commit()

    @staticmethod
    def get_profiles(user_id):
        db = get_db()
        profiles = db.execute('SELECT * FROM profiles WHERE user_id = ?', (user_id,)).fetchall()
        return [Profile(id=row['id'], user_id=row['user_id'], name=row['name'], relationship=row['relationship']) for row in profiles]

    @staticmethod
    def get_profile(profile_id):
        db = get_db()
        profile = db.execute('SELECT * FROM profiles WHERE id = ?', (profile_id,)).fetchone()
        if profile:
            return Profile(
                id=profile['id'],
                user_id=profile['user_id'],
                name=profile['name'],
                relationship=profile['relationship']
            )
        return None

    def get_all_data(self):
        """Get all profile-related data"""
        return {
            'medications': Medication.get_profile_medications(self.id),
            'weight_logs': WeightLog.get_weight_history(self.user_id, self.id),
            'height_logs': HeightLog.get_height_history(self.user_id, self.id),
            'symptoms': Symptom.get_symptoms_history(self.user_id, self.id),
            'appointments': Appointment.get_upcoming_appointments(self.user_id, self.id)
        }

class MedicineForm:
    TABLET = 'tablet'
    CAPSULE = 'capsule'
    LIQUID = 'liquid'
    DROPS = 'drops'
    OTHER = 'other'

    @staticmethod
    def get_all_forms():
        return [
            MedicineForm.TABLET,
            MedicineForm.CAPSULE,
            MedicineForm.LIQUID,
            MedicineForm.DROPS,
            MedicineForm.OTHER
        ]

class DosageSchedule:
    ONCE_DAILY = 'once_daily'
    TWICE_DAILY = 'twice_daily'
    ON_DEMAND = 'on_demand'
    EVERY_X_HOURS = 'every_x_hours'
    X_TIMES_DAY = 'x_times_day'
    X_DAYS_WEEK = 'x_days_week'

    @staticmethod
    def get_all_schedules():
        return [
            DosageSchedule.ONCE_DAILY,
            DosageSchedule.TWICE_DAILY,
            DosageSchedule.ON_DEMAND,
            DosageSchedule.EVERY_X_HOURS,
            DosageSchedule.X_TIMES_DAY,
            DosageSchedule.X_DAYS_WEEK
        ]

class Symptom:
    def __init__(self, id, user_id, profile_id, medication_id, description, severity, logged_at):
        self.id = id
        self.user_id = user_id
        self.profile_id = profile_id
        self.medication_id = medication_id
        self.description = description
        self.severity = severity
        self.logged_at = logged_at

    SEVERITY_NONE = 'none'
    SEVERITY_MILD = 'mild'
    SEVERITY_MODERATE = 'moderate'
    SEVERITY_SEVERE = 'severe'

    @staticmethod
    def get_severity_levels():
        return [
            Symptom.SEVERITY_NONE,
            Symptom.SEVERITY_MILD,
            Symptom.SEVERITY_MODERATE,
            Symptom.SEVERITY_SEVERE
        ]

    @staticmethod
    def log_symptom(user_id, profile_id, medication_id, description, severity):
        db = get_db()
        db.execute('''
            INSERT INTO symptoms 
            (user_id, profile_id, medication_id, description, severity, logged_at) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, profile_id, medication_id, description, severity, datetime.now()))
        db.commit()

    @staticmethod
    def get_symptoms_history(user_id, profile_id=None, days=30):
        db = get_db()
        query = '''
            SELECT s.*, m.name as medication_name 
            FROM symptoms s
            LEFT JOIN medications m ON s.medication_id = m.id
            WHERE s.user_id = ? AND s.logged_at >= ?
        '''
        params = [user_id, datetime.now() - timedelta(days=days)]
        
        if profile_id:
            query += ' AND s.profile_id = ?'
            params.append(profile_id)
            
        query += ' ORDER BY s.logged_at DESC'
        
        symptoms = db.execute(query, params).fetchall()
        return symptoms

class HeightLog:
    def __init__(self, id, user_id, profile_id, height, logged_at):
        self.id = id
        self.user_id = user_id
        self.profile_id = profile_id
        self.height = height
        self.logged_at = logged_at

    @staticmethod
    def log_height(user_id, profile_id, height):
        db = get_db()
        db.execute('''
            INSERT INTO height_logs 
            (user_id, profile_id, height, logged_at) 
            VALUES (?, ?, ?, ?)
        ''', (user_id, profile_id, height, datetime.now()))
        db.commit()

    @staticmethod
    def get_height_history(user_id, profile_id=None):
        db = get_db()
        query = '''
            SELECT * FROM height_logs 
            WHERE user_id = ?
        '''
        params = [user_id]
        
        if profile_id:
            query += ' AND profile_id = ?'
            params.append(profile_id)
            
        query += ' ORDER BY logged_at DESC'
        
        logs = db.execute(query, params).fetchall()
        return [HeightLog(
            id=row['id'],
            user_id=row['user_id'],
            profile_id=row['profile_id'],
            height=row['height'],
            logged_at=row['logged_at']
        ) for row in logs]

from . import login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.get(int(user_id))
