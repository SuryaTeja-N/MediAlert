from flask import render_template, redirect, url_for, flash, request, jsonify, send_file, session, current_app
from flask_login import login_required, current_user
from . import main
from ..models import (
    Medication, MedicationLog, Appointment, WeightLog, Profile, 
    Symptom, HeightLog, MedicineForm, DosageSchedule
)
from .. import get_db, mail, scheduler
from flask_mail import Message
from datetime import datetime, timedelta
from ..utils.email_handler import send_email

@main.route('/')
def index():
    return render_template('home.html')

@main.route('/dashboard')
@login_required
def dashboard():
    medications = Medication.get_user_medications(current_user.id)
    return render_template('dashboard.html', medications=medications)

@main.route('/add_medication', methods=['GET', 'POST'])
@login_required
def add_medication():
    if request.method == 'POST':
        name = request.form.get('name')
        dosage_schedule = request.form.get('dosage_schedule')
        custom_value = request.form.get('custom_value')
        form_type = request.form.get('form_type')
        stock = request.form.get('stock')
        description = request.form.get('description')
        
        # Calculate next dose based on dosage schedule
        next_dose = calculate_next_dose(dosage_schedule, custom_value)
        
        # Get existing medication description if name exists
        existing_med = Medication.get_by_name(name)
        if existing_med:
            description = existing_med.description
        
        db = get_db()
        db.execute('''
            INSERT INTO medications 
            (name, dosage_schedule, form_type, stock, user_id, description, next_dose) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, dosage_schedule, form_type, stock, current_user.id, description, next_dose))
        commit_db()
        
        flash('Medication added successfully')
        schedule_reminder(name, dosage_schedule, current_user.email, next_dose)
        return redirect(url_for('main.dashboard'))
        
    # Get all medicine forms and dosage schedules for the template
    medicine_forms = MedicineForm.get_all_forms()
    dosage_schedules = DosageSchedule.get_all_schedules()
    return render_template('add_medication.html', 
                         medicine_forms=medicine_forms,
                         dosage_schedules=dosage_schedules)

def calculate_next_dose(schedule_type, custom_value=None):
    now = datetime.now()
    
    if schedule_type == DosageSchedule.ONCE_DAILY:
        return now + timedelta(days=1)
    elif schedule_type == DosageSchedule.TWICE_DAILY:
        return now + timedelta(hours=12)
    elif schedule_type == DosageSchedule.ON_DEMAND:
        return None
    elif schedule_type == DosageSchedule.EVERY_X_HOURS:
        hours = int(custom_value) if custom_value else 24
        return now + timedelta(hours=hours)
    elif schedule_type == DosageSchedule.X_TIMES_DAY:
        times = int(custom_value) if custom_value else 1
        return now + timedelta(hours=24/times)
    elif schedule_type == DosageSchedule.X_DAYS_WEEK:
        return now + timedelta(days=7/int(custom_value) if custom_value else 7)
    
    return now + timedelta(days=1)  # Default to once daily

@main.route('/get_medicine_suggestions')
@login_required
def get_medicine_suggestions():
    query = request.args.get('query', '')
    suggestions = Medication.get_medicine_suggestions(query)
    return jsonify(suggestions)

@main.route('/get_medicine_details/<name>')
@login_required
def get_medicine_details(name):
    medication = Medication.get_by_name(name)
    if medication:
        return jsonify({
            'description': medication.description,
            'form_type': medication.form_type,
            'typical_dosage': medication.dosage_schedule
        })
    return jsonify({})

@main.route('/edit_medication/<int:med_id>', methods=['GET', 'POST'])
@login_required
def edit_medication(med_id):
    medication = Medication.get_medication(med_id)
    if request.method == 'POST':
        name = request.form.get('name')
        dosage = request.form.get('dosage')
        frequency = request.form.get('frequency')
        stock = request.form.get('stock')
        description = request.form.get('description')
        next_dose = datetime.now() + timedelta(hours=int(frequency.split()[0]))
        Medication.update_medication(med_id, name, dosage, frequency, stock, description, next_dose)
        commit_db()
        flash('Medication updated successfully')
        return redirect(url_for('main.dashboard'))
    return render_template('edit_medication.html', medication=medication)

@main.route('/delete_medication/<int:med_id>')
@login_required
def delete_medication(med_id):
    Medication.delete_medication(med_id)
    commit_db()
    flash('Medication deleted successfully')
    return redirect(url_for('main.dashboard'))

@main.route('/search_medications')
@login_required
def search_medications():
    query = request.args.get('query', '')
    medications = Medication.search_medications(query)
    return render_template('search_results.html', medications=medications)

@main.route('/confirm_dose/<int:med_id>')
@login_required
def confirm_dose(med_id):
    medication = Medication.get_medication(med_id)
    if medication:
        new_stock = medication.stock - 1
        next_dose = datetime.now() + timedelta(hours=int(medication.frequency.split()[0]))
        Medication.update_medication(med_id, medication.name, medication.dosage, medication.frequency, new_stock, medication.description, next_dose)
        commit_db()
        flash('Dose confirmed')
        schedule_reminder(medication.name, medication.dosage, current_user.email, next_dose)
    return redirect(url_for('main.dashboard'))

@main.route('/snooze_dose/<int:med_id>')
@login_required
def snooze_dose(med_id):
    medication = Medication.get_medication(med_id)
    if medication:
        next_dose = datetime.now() + timedelta(minutes=15)
        Medication.update_medication(med_id, medication.name, medication.dosage, medication.frequency, medication.stock, medication.description, next_dose)
        flash('Dose snoozed for 15 minutes')
        schedule_reminder(medication.name, medication.dosage, current_user.email, next_dose)
    return redirect(url_for('main.dashboard'))

@main.route('/skip_dose/<int:med_id>')
@login_required
def skip_dose(med_id):
    medication = Medication.get_medication(med_id)
    if medication:
        try:
            next_dose = datetime.now() + timedelta(hours=int(medication.frequency.split()[0]))
            Medication.update_medication(med_id, medication.name, medication.dosage, medication.frequency, medication.stock, medication.description, next_dose)
            
            # Send email notification using current_user's email
            msg = Message('Medication Skipped Alert',
                         sender=current_app.config['MAIL_DEFAULT_SENDER'],
                         recipients=[current_user.email])  # Using current_user.email
            
            msg.html = f"""
            <h2 style="color: #e8491d;">Medication Skipped Alert</h2>
            <p>Dear {current_user.username},</p>
            <p>This is to notify you that you have skipped your medication: <strong>{medication.name}</strong> ({medication.dosage}).</p>
            <p style="color: #721c24;">Skipping medications can have serious health implications. If you're experiencing any issues with your medication, 
            please consult your healthcare provider.</p>
            <h3>Medication Details:</h3>
            <ul>
                <li>Name: {medication.name}</li>
                <li>Dosage: {medication.dosage}</li>
                <li>Skipped at: {datetime.now().strftime('%Y-%m-%d %H:%M')}</li>
            </ul>
            <p>Please remember to take your medications as prescribed. If you continue to skip medications, 
            consider discussing this with your doctor to explore alternative options.</p>
            <p>Best regards,<br>MediALERT Team</p>
            """
            
            mail.send(msg)
            flash('Dose skipped. An email notification has been sent.')
            schedule_reminder(medication.name, medication.dosage, current_user.email, next_dose)
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            flash('Dose skipped. (Email notification could not be sent)')
    
    return redirect(url_for('main.dashboard'))

@main.route('/generate_report')
@login_required
def generate_report():
    medications = Medication.get_user_medications(current_user.id)
    return render_template('report.html', medications=medications)

def schedule_reminder(med_name, dosage, email, next_dose):
    scheduler.add_job(
        send_reminder_email,
        'date',
        run_date=next_dose,
        args=[med_name, dosage, current_user.email]  # Using current_user.email
    )

def send_reminder_email(med_name, dosage, email):
    try:
        msg = Message('Medication Reminder',
                    recipients=[email])  # Remove sender parameter
        msg.body = f"Don't forget to take your {med_name} ({dosage})!"
        mail.send(msg)
        print(f"Reminder email sent successfully to {email}")
    except Exception as e:
        print(f"Failed to send reminder email: {str(e)}")
        # Log the full error for debugging
        import traceback
        print(traceback.format_exc())

@main.route('/check_stock')
@login_required
def check_stock():
    medications = Medication.get_user_medications(current_user.id)
    low_stock = [med for med in medications if med.stock <= 5]
    if low_stock:
        flash('Some medications are running low on stock!')
    return jsonify([{'name': med.name, 'stock': med.stock} for med in low_stock])

@main.route('/log_medication/<int:med_id>/<status>')
@login_required
def log_medication(med_id, status):
    medication = Medication.get_medication(med_id)
    MedicationLog.log_medication(med_id, current_user.id, status)
    
    if status == 'skipped':
        try:
            msg = Message('Medication Skipped Alert',
                         recipients=[current_user.email])  # Remove sender parameter
            msg.body = f"""
Dear {current_user.username},

This is to notify you that you have skipped your medication: {medication.name} ({medication.dosage}).

Skipping medications can have serious health implications. If you're experiencing any issues with your medication, 
please consult your healthcare provider.

Medication Details:
- Name: {medication.name}
- Dosage: {medication.dosage}
- Skipped at: {datetime.now().strftime('%Y-%m-%d %H:%M')}

Please remember to take your medications as prescribed. If you continue to skip medications, 
consider discussing this with your doctor to explore alternative options.

Best regards,
MediALERT Team
"""
            mail.send(msg)
            flash('Warning: You have skipped a medication. An email notification has been sent.')
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            # Log the full error for debugging
            import traceback
            print(traceback.format_exc())
            flash('Medication logged, but email notification could not be sent.')
    
    return redirect(url_for('main.dashboard'))

@main.route('/medication_progress')
@main.route('/medication_progress/<period>')
@login_required
def medication_progress(period='7days'):
    # Convert period to number of days
    period_days = {
        '7days': 7,
        '14days': 14,
        '1month': 30
    }
    
    days = period_days.get(period, 7)  # Default to 7 days if invalid period
    
    # Calculate the date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Get logs for the specified period
    logs = MedicationLog.get_logs_by_period(current_user.id, start_date, end_date)
    
    return render_template('medication_progress.html', 
                         logs=logs, 
                         current_period=period,
                         start_date=start_date,
                         end_date=end_date)

@main.route('/add_appointment', methods=['GET', 'POST'])
@login_required
def add_appointment():
    if request.method == 'POST':
        doctor_name = request.form.get('doctor_name')
        appointment_date = datetime.strptime(request.form.get('appointment_date'), '%Y-%m-%dT%H:%M')
        description = request.form.get('description')
        Appointment.add_appointment(current_user.id, doctor_name, appointment_date, description)
        commit_db()
        flash('Appointment added successfully')
        return redirect(url_for('main.dashboard'))
    return render_template('add_appointment.html')

@main.route('/log_weight', methods=['GET', 'POST'])
@login_required
def log_weight():
    if request.method == 'POST':
        weight = float(request.form.get('weight'))
        WeightLog.log_weight(current_user.id, weight)
        commit_db()
        flash('Weight logged successfully')
        return redirect(url_for('main.dashboard'))
    return render_template('log_weight.html')

@main.route('/weight_history')
@login_required
def weight_history():
    logs = WeightLog.get_weight_history(current_user.id)
    return render_template('weight_history.html', logs=logs)

@main.route('/add_profile', methods=['GET', 'POST'])
@login_required
def add_profile():
    if request.method == 'POST':
        name = request.form.get('name')
        relationship = request.form.get('relationship')
        Profile.add_profile(current_user.id, name, relationship)
        flash('Profile added successfully')
        return redirect(url_for('main.dashboard'))
    return render_template('add_profile.html')

@main.route('/switch_profile/<int:profile_id>')
@login_required
def switch_profile(profile_id):
    # Implement logic to switch between profiles
    flash('Switched to profile successfully')
    return redirect(url_for('main.dashboard'))

@main.route('/health_tips')
@login_required
def health_tips():
    # You can add more tips or fetch them from a database
    tips = [
        "Stay hydrated by drinking at least 8 glasses of water a day.",
        "Aim for 7-9 hours of sleep each night for optimal health.",
        "Regular exercise can help improve both physical and mental health.",
        "Eat a balanced diet rich in fruits, vegetables, and whole grains.",
        "Don't skip meals, especially breakfast, to maintain steady energy levels.",
    ]
    return render_template('health_tips.html', tips=tips)

def check_missed_medications():
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    db = get_db()
    missed_meds = db.execute('''
        SELECT m.* FROM medications m
        LEFT JOIN medication_logs ml ON m.id = ml.medication_id AND ml.taken_at > ?
        WHERE m.next_dose < ? AND ml.id IS NULL
    ''', (yesterday, now)).fetchall()
    
    for med in missed_meds:
        user = User.get(med['user_id'])
        try:
            send_missed_medication_alert(user.email, med['name'])
        except Exception as e:
            print(f"Failed to send missed medication alert: {str(e)}")

def send_missed_medication_alert(email, medication_name):
    try:
        msg = Message('Missed Medication Alert',
                    recipients=[email])  # Remove sender parameter
        msg.body = f"You missed a dose of {medication_name}. This may lead to potential health risks. Please consult your doctor if you experience any unusual symptoms."
        mail.send(msg)
        print(f"Missed medication alert sent successfully to {email}")
    except Exception as e:
        print(f"Failed to send missed medication alert: {str(e)}")
        # Log the full error for debugging
        import traceback
        print(traceback.format_exc())

# Schedule the missed medication check to run daily
scheduler.add_job(check_missed_medications, 'cron', hour=0, minute=0)

def commit_db():
    db = get_db()
    db.commit()

@main.route('/log_symptom/<int:med_id>', methods=['GET', 'POST'])
@login_required
def log_symptom(med_id):
    if request.method == 'POST':
        description = request.form.get('description')
        severity = request.form.get('severity')
        profile_id = session.get('current_profile_id', None)
        
        Symptom.log_symptom(
            user_id=current_user.id,
            profile_id=profile_id,
            medication_id=med_id,
            description=description,
            severity=severity
        )
        
        flash('Symptoms logged successfully')
        return redirect(url_for('main.medication_progress'))
        
    severity_levels = Symptom.get_severity_levels()
    return render_template('log_symptom.html', 
                         med_id=med_id,
                         severity_levels=severity_levels)

@main.route('/symptoms_history')
@login_required
def symptoms_history():
    profile_id = session.get('current_profile_id', None)
    symptoms = Symptom.get_symptoms_history(current_user.id, profile_id)
    return render_template('symptoms_history.html', symptoms=symptoms)

@main.route('/log_height', methods=['GET', 'POST'])
@login_required
def log_height():
    if request.method == 'POST':
        height = float(request.form.get('height'))
        profile_id = session.get('current_profile_id', None)
        
        HeightLog.log_height(
            user_id=current_user.id,
            profile_id=profile_id,
            height=height
        )
        
        flash('Height logged successfully')
        return redirect(url_for('main.dashboard'))
        
    return render_template('log_height.html')

@main.route('/height_history')
@login_required
def height_history():
    profile_id = session.get('current_profile_id', None)
    logs = HeightLog.get_height_history(current_user.id, profile_id)
    return render_template('height_history.html', logs=logs)

@main.route('/download_report/<format>')
@login_required
def download_report(format):
    profile_id = session.get('current_profile_id', None)
    
    # Get all necessary data
    data = {
        'medications': Medication.get_user_medications(current_user.id),
        'med_logs': MedicationLog.get_logs(current_user.id),
        'symptoms': Symptom.get_symptoms_history(current_user.id, profile_id),
        'weight_logs': WeightLog.get_weight_history(current_user.id, profile_id),
        'height_logs': HeightLog.get_height_history(current_user.id, profile_id)
    }
    
    if format == 'pdf':
        return generate_pdf_report(data)
    elif format == 'excel':
        return generate_excel_report(data)
    else:
        flash('Invalid report format')
        return redirect(url_for('main.dashboard'))

def generate_pdf_report(data):
    # Create PDF using reportlab
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    from io import BytesIO
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Add medications table
    elements.append(Paragraph('Medications', styles['Heading1']))
    med_data = [[med.name, med.dosage, med.frequency, med.stock] for med in data['medications']]
    if med_data:
        med_table = Table([['Name', 'Dosage', 'Frequency', 'Stock']] + med_data)
        med_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(med_table)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name='medical_report.pdf',
        mimetype='application/pdf'
    )

def generate_excel_report(data):
    import pandas as pd
    from io import BytesIO
    
    # Create Excel writer
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Medications sheet
        med_data = [[med.name, med.dosage, med.frequency, med.stock] for med in data['medications']]
        med_df = pd.DataFrame(med_data, columns=['Name', 'Dosage', 'Frequency', 'Stock'])
        med_df.to_excel(writer, sheet_name='Medications', index=False)
        
        # Medication logs sheet
        log_data = [[log['medication_name'], log['taken_at'], log['status']] for log in data['med_logs']]
        log_df = pd.DataFrame(log_data, columns=['Medication', 'Taken At', 'Status'])
        log_df.to_excel(writer, sheet_name='Medication Logs', index=False)
        
        # Symptoms sheet
        symptom_data = [[s['medication_name'], s['description'], s['severity'], s['logged_at']] 
                       for s in data['symptoms']]
        symptom_df = pd.DataFrame(symptom_data, 
                                columns=['Medication', 'Description', 'Severity', 'Logged At'])
        symptom_df.to_excel(writer, sheet_name='Symptoms', index=False)
    
    output.seek(0)
    
    return send_file(
        output,
        as_attachment=True,
        download_name='medical_report.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
