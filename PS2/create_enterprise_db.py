"""
=============================================================================
ENTERPRISE DATABASE CREATOR - Healthcare Management System
=============================================================================
Creates impressive sample databases for DataForge AI Migration Demo:

SOURCE: Legacy Hospital Information System (HIS) - 15+ tables
        Uses old naming conventions, abbreviations, legacy data types
        
TARGET: Modern Healthcare Data Platform (HDP) - 15+ tables  
        Uses clean naming, modern conventions, proper normalization

This simulates a real-world enterprise migration scenario that will
impress judges with complexity and realistic data.
=============================================================================
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random
import hashlib
import uuid

# Faker-like data generators (no external dependency)
FIRST_NAMES = ["James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda", 
               "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
               "Thomas", "Sarah", "Christopher", "Karen", "Charles", "Lisa", "Daniel", "Nancy",
               "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley"]

LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
              "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
              "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White"]

DEPARTMENTS = ["Emergency", "Cardiology", "Neurology", "Oncology", "Pediatrics", "Orthopedics",
               "Radiology", "Pathology", "Surgery", "Internal Medicine", "Psychiatry", "Dermatology"]

DIAGNOSES = ["Hypertension", "Type 2 Diabetes", "Coronary Artery Disease", "Pneumonia", 
             "Acute Bronchitis", "Urinary Tract Infection", "Migraine", "Depression",
             "Anxiety Disorder", "Osteoarthritis", "Chronic Back Pain", "Asthma",
             "COPD", "Atrial Fibrillation", "Heart Failure", "Stroke", "Appendicitis"]

MEDICATIONS = ["Lisinopril", "Metformin", "Atorvastatin", "Amlodipine", "Metoprolol",
               "Omeprazole", "Losartan", "Albuterol", "Gabapentin", "Hydrochlorothiazide",
               "Sertraline", "Levothyroxine", "Azithromycin", "Amoxicillin", "Prednisone"]

PROCEDURES = ["Blood Test", "X-Ray", "MRI Scan", "CT Scan", "Ultrasound", "ECG",
              "Endoscopy", "Colonoscopy", "Biopsy", "Angiography", "Echocardiogram"]

INSURANCE = ["BlueCross BlueShield", "Aetna", "Cigna", "UnitedHealthcare", "Humana",
             "Medicare", "Medicaid", "Kaiser Permanente", "Anthem"]

CITIES = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia",
          "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville"]

STATES = ["NY", "CA", "IL", "TX", "AZ", "PA", "FL", "OH", "MI", "GA", "NC", "WA"]


def random_date(start_year=2020, end_year=2025):
    """Generate random date"""
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    random_days = random.randint(0, delta.days)
    return start + timedelta(days=random_days)


def random_phone():
    """Generate random phone number"""
    return f"({random.randint(200,999)}) {random.randint(200,999)}-{random.randint(1000,9999)}"


def random_ssn():
    """Generate random SSN (masked)"""
    return f"XXX-XX-{random.randint(1000, 9999)}"


def create_source_database():
    """
    SOURCE DATABASE: Legacy Hospital Information System (HIS)
    Uses abbreviations, old conventions, non-normalized structure
    """
    source_path = "data/enterprise_source_his.db"
    
    if os.path.exists(source_path):
        os.remove(source_path)
    
    conn = sqlite3.connect(source_path)
    c = conn.cursor()
    
    print("🏥 Creating Legacy Hospital Information System (HIS)...")
    
    # =========================================================================
    # TABLE 1: PATIENTS (Legacy naming - pat, pt_)
    # =========================================================================
    c.execute("""
        CREATE TABLE pat (
            pt_id INTEGER PRIMARY KEY,
            pt_mrn VARCHAR(20) UNIQUE,
            pt_fname VARCHAR(50),
            pt_lname VARCHAR(50),
            pt_mname VARCHAR(50),
            pt_dob DATE,
            pt_gender CHAR(1),
            pt_ssn VARCHAR(15),
            pt_email VARCHAR(100),
            pt_phone VARCHAR(20),
            pt_cell VARCHAR(20),
            pt_addr1 VARCHAR(200),
            pt_addr2 VARCHAR(200),
            pt_city VARCHAR(50),
            pt_state VARCHAR(2),
            pt_zip VARCHAR(10),
            pt_emerg_contact VARCHAR(100),
            pt_emerg_phone VARCHAR(20),
            pt_blood_type VARCHAR(5),
            pt_allergies TEXT,
            pt_status INTEGER,
            ins_id INTEGER,
            ins_policy_no VARCHAR(50),
            ins_group_no VARCHAR(50),
            created_dt DATETIME,
            modified_dt DATETIME,
            created_by INTEGER,
            modified_by INTEGER
        )
    """)
    
    # =========================================================================
    # TABLE 2: PHYSICIANS (Legacy - doc, dr_, phy_)
    # =========================================================================
    c.execute("""
        CREATE TABLE doc (
            dr_id INTEGER PRIMARY KEY,
            dr_npi VARCHAR(15) UNIQUE,
            dr_fname VARCHAR(50),
            dr_lname VARCHAR(50),
            dr_suffix VARCHAR(20),
            dr_specialty VARCHAR(100),
            dr_dept_id INTEGER,
            dr_email VARCHAR(100),
            dr_phone VARCHAR(20),
            dr_license_no VARCHAR(50),
            dr_license_state VARCHAR(2),
            dr_license_exp DATE,
            dr_dea_no VARCHAR(20),
            dr_status INTEGER,
            dr_hire_dt DATE,
            created_dt DATETIME,
            modified_dt DATETIME
        )
    """)
    
    # =========================================================================
    # TABLE 3: DEPARTMENTS (Legacy - dept)
    # =========================================================================
    c.execute("""
        CREATE TABLE dept (
            dept_id INTEGER PRIMARY KEY,
            dept_code VARCHAR(10) UNIQUE,
            dept_name VARCHAR(100),
            dept_head_id INTEGER,
            dept_phone VARCHAR(20),
            dept_location VARCHAR(100),
            dept_floor INTEGER,
            dept_budget DECIMAL(15,2),
            dept_status INTEGER,
            created_dt DATETIME
        )
    """)
    
    # =========================================================================
    # TABLE 4: APPOINTMENTS (Legacy - appt)
    # =========================================================================
    c.execute("""
        CREATE TABLE appt (
            appt_id INTEGER PRIMARY KEY,
            pt_id INTEGER,
            dr_id INTEGER,
            dept_id INTEGER,
            appt_dt DATETIME,
            appt_dur INTEGER,
            appt_type VARCHAR(50),
            appt_reason TEXT,
            appt_status VARCHAR(20),
            appt_notes TEXT,
            room_no VARCHAR(20),
            check_in_dt DATETIME,
            check_out_dt DATETIME,
            no_show INTEGER DEFAULT 0,
            created_dt DATETIME,
            created_by INTEGER,
            FOREIGN KEY (pt_id) REFERENCES pat(pt_id),
            FOREIGN KEY (dr_id) REFERENCES doc(dr_id),
            FOREIGN KEY (dept_id) REFERENCES dept(dept_id)
        )
    """)
    
    # =========================================================================
    # TABLE 5: ENCOUNTERS / VISITS (Legacy - enc)
    # =========================================================================
    c.execute("""
        CREATE TABLE enc (
            enc_id INTEGER PRIMARY KEY,
            pt_id INTEGER,
            dr_id INTEGER,
            dept_id INTEGER,
            enc_type VARCHAR(50),
            enc_dt DATETIME,
            discharge_dt DATETIME,
            chief_complaint TEXT,
            presenting_problem TEXT,
            enc_status VARCHAR(20),
            disposition VARCHAR(100),
            admit_src VARCHAR(50),
            room_no VARCHAR(20),
            bed_no VARCHAR(10),
            acuity_level INTEGER,
            created_dt DATETIME,
            FOREIGN KEY (pt_id) REFERENCES pat(pt_id),
            FOREIGN KEY (dr_id) REFERENCES doc(dr_id)
        )
    """)
    
    # =========================================================================
    # TABLE 6: DIAGNOSES (Legacy - diag, dx)
    # =========================================================================
    c.execute("""
        CREATE TABLE diag (
            dx_id INTEGER PRIMARY KEY,
            enc_id INTEGER,
            pt_id INTEGER,
            dx_code VARCHAR(20),
            dx_code_type VARCHAR(10),
            dx_desc TEXT,
            dx_type VARCHAR(20),
            dx_priority INTEGER,
            onset_dt DATE,
            resolved_dt DATE,
            dx_status VARCHAR(20),
            diagnosed_by INTEGER,
            created_dt DATETIME,
            FOREIGN KEY (enc_id) REFERENCES enc(enc_id),
            FOREIGN KEY (pt_id) REFERENCES pat(pt_id)
        )
    """)
    
    # =========================================================================
    # TABLE 7: MEDICATIONS / PRESCRIPTIONS (Legacy - med, rx)
    # =========================================================================
    c.execute("""
        CREATE TABLE med (
            rx_id INTEGER PRIMARY KEY,
            pt_id INTEGER,
            enc_id INTEGER,
            dr_id INTEGER,
            med_name VARCHAR(200),
            med_ndc VARCHAR(20),
            med_dose VARCHAR(50),
            med_unit VARCHAR(20),
            med_route VARCHAR(50),
            med_freq VARCHAR(100),
            rx_qty INTEGER,
            rx_refills INTEGER,
            rx_start_dt DATE,
            rx_end_dt DATE,
            rx_status VARCHAR(20),
            rx_notes TEXT,
            pharmacy_id INTEGER,
            dispensed_dt DATETIME,
            created_dt DATETIME,
            FOREIGN KEY (pt_id) REFERENCES pat(pt_id),
            FOREIGN KEY (dr_id) REFERENCES doc(dr_id)
        )
    """)
    
    # =========================================================================
    # TABLE 8: LAB ORDERS & RESULTS (Legacy - lab)
    # =========================================================================
    c.execute("""
        CREATE TABLE lab (
            lab_id INTEGER PRIMARY KEY,
            enc_id INTEGER,
            pt_id INTEGER,
            dr_id INTEGER,
            lab_code VARCHAR(20),
            lab_name VARCHAR(200),
            lab_category VARCHAR(100),
            lab_value VARCHAR(100),
            lab_unit VARCHAR(50),
            lab_range_low DECIMAL(10,2),
            lab_range_high DECIMAL(10,2),
            lab_flag VARCHAR(10),
            specimen_type VARCHAR(50),
            collection_dt DATETIME,
            result_dt DATETIME,
            lab_status VARCHAR(20),
            performed_by INTEGER,
            verified_by INTEGER,
            lab_notes TEXT,
            created_dt DATETIME,
            FOREIGN KEY (enc_id) REFERENCES enc(enc_id),
            FOREIGN KEY (pt_id) REFERENCES pat(pt_id)
        )
    """)
    
    # =========================================================================
    # TABLE 9: PROCEDURES (Legacy - proc)
    # =========================================================================
    c.execute("""
        CREATE TABLE proc (
            proc_id INTEGER PRIMARY KEY,
            enc_id INTEGER,
            pt_id INTEGER,
            dr_id INTEGER,
            proc_code VARCHAR(20),
            proc_code_type VARCHAR(10),
            proc_desc TEXT,
            proc_dt DATETIME,
            proc_duration INTEGER,
            proc_status VARCHAR(20),
            proc_result TEXT,
            proc_complications TEXT,
            anesthesia_type VARCHAR(50),
            proc_location VARCHAR(100),
            assistant_id INTEGER,
            proc_notes TEXT,
            created_dt DATETIME,
            FOREIGN KEY (enc_id) REFERENCES enc(enc_id),
            FOREIGN KEY (pt_id) REFERENCES pat(pt_id)
        )
    """)
    
    # =========================================================================
    # TABLE 10: VITALS (Legacy - vitals)
    # =========================================================================
    c.execute("""
        CREATE TABLE vitals (
            vital_id INTEGER PRIMARY KEY,
            enc_id INTEGER,
            pt_id INTEGER,
            measured_dt DATETIME,
            bp_systolic INTEGER,
            bp_diastolic INTEGER,
            heart_rate INTEGER,
            resp_rate INTEGER,
            temp_f DECIMAL(5,2),
            o2_sat DECIMAL(5,2),
            weight_lbs DECIMAL(6,2),
            height_in DECIMAL(5,2),
            bmi DECIMAL(5,2),
            pain_level INTEGER,
            measured_by INTEGER,
            vital_notes TEXT,
            created_dt DATETIME,
            FOREIGN KEY (enc_id) REFERENCES enc(enc_id),
            FOREIGN KEY (pt_id) REFERENCES pat(pt_id)
        )
    """)
    
    # =========================================================================
    # TABLE 11: INSURANCE (Legacy - ins)
    # =========================================================================
    c.execute("""
        CREATE TABLE ins (
            ins_id INTEGER PRIMARY KEY,
            ins_name VARCHAR(200),
            ins_type VARCHAR(50),
            ins_addr VARCHAR(200),
            ins_city VARCHAR(50),
            ins_state VARCHAR(2),
            ins_zip VARCHAR(10),
            ins_phone VARCHAR(20),
            ins_fax VARCHAR(20),
            ins_email VARCHAR(100),
            ins_payer_id VARCHAR(50),
            ins_status INTEGER,
            created_dt DATETIME
        )
    """)
    
    # =========================================================================
    # TABLE 12: BILLING / CLAIMS (Legacy - bill, claim)
    # =========================================================================
    c.execute("""
        CREATE TABLE bill (
            bill_id INTEGER PRIMARY KEY,
            enc_id INTEGER,
            pt_id INTEGER,
            ins_id INTEGER,
            claim_no VARCHAR(50),
            bill_dt DATE,
            service_dt DATE,
            bill_status VARCHAR(20),
            total_charges DECIMAL(12,2),
            ins_payment DECIMAL(12,2),
            pt_payment DECIMAL(12,2),
            adjustments DECIMAL(12,2),
            balance_due DECIMAL(12,2),
            due_dt DATE,
            paid_dt DATE,
            bill_notes TEXT,
            submitted_dt DATETIME,
            created_dt DATETIME,
            FOREIGN KEY (enc_id) REFERENCES enc(enc_id),
            FOREIGN KEY (pt_id) REFERENCES pat(pt_id),
            FOREIGN KEY (ins_id) REFERENCES ins(ins_id)
        )
    """)
    
    # =========================================================================
    # TABLE 13: ALLERGIES (Legacy - allergy)
    # =========================================================================
    c.execute("""
        CREATE TABLE allergy (
            allergy_id INTEGER PRIMARY KEY,
            pt_id INTEGER,
            allergen VARCHAR(200),
            allergen_type VARCHAR(50),
            reaction TEXT,
            severity VARCHAR(20),
            onset_dt DATE,
            verified INTEGER DEFAULT 0,
            verified_by INTEGER,
            allergy_status VARCHAR(20),
            created_dt DATETIME,
            FOREIGN KEY (pt_id) REFERENCES pat(pt_id)
        )
    """)
    
    # =========================================================================
    # TABLE 14: STAFF / EMPLOYEES (Legacy - emp)
    # =========================================================================
    c.execute("""
        CREATE TABLE emp (
            emp_id INTEGER PRIMARY KEY,
            emp_no VARCHAR(20) UNIQUE,
            emp_fname VARCHAR(50),
            emp_lname VARCHAR(50),
            emp_email VARCHAR(100),
            emp_phone VARCHAR(20),
            emp_role VARCHAR(100),
            emp_dept_id INTEGER,
            emp_supervisor_id INTEGER,
            emp_hire_dt DATE,
            emp_term_dt DATE,
            emp_status INTEGER,
            emp_hourly_rate DECIMAL(10,2),
            created_dt DATETIME,
            FOREIGN KEY (emp_dept_id) REFERENCES dept(dept_id)
        )
    """)
    
    # =========================================================================
    # TABLE 15: ROOMS/BEDS (Legacy - room)
    # =========================================================================
    c.execute("""
        CREATE TABLE room (
            room_id INTEGER PRIMARY KEY,
            room_no VARCHAR(20) UNIQUE,
            room_type VARCHAR(50),
            dept_id INTEGER,
            floor_no INTEGER,
            bed_count INTEGER,
            room_status VARCHAR(20),
            equipment TEXT,
            daily_rate DECIMAL(10,2),
            created_dt DATETIME,
            FOREIGN KEY (dept_id) REFERENCES dept(dept_id)
        )
    """)
    
    # =========================================================================
    # INSERT SAMPLE DATA
    # =========================================================================
    
    print("📊 Populating departments...")
    for i, dept in enumerate(DEPARTMENTS):
        c.execute("""
            INSERT INTO dept (dept_id, dept_code, dept_name, dept_phone, dept_location, 
                             dept_floor, dept_budget, dept_status, created_dt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (i+1, dept[:3].upper(), dept, random_phone(), f"Building A, Floor {(i%5)+1}",
              (i%5)+1, random.randint(500000, 5000000), 1, random_date(2018, 2020)))
    
    print("📊 Populating insurance companies...")
    for i, ins in enumerate(INSURANCE):
        c.execute("""
            INSERT INTO ins (ins_id, ins_name, ins_type, ins_addr, ins_city, ins_state,
                            ins_zip, ins_phone, ins_payer_id, ins_status, created_dt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (i+1, ins, "Commercial" if i < 5 else "Government", 
              f"{random.randint(100,999)} Insurance Blvd", random.choice(CITIES),
              random.choice(STATES), f"{random.randint(10000,99999)}", random_phone(),
              f"PAY{str(i+1).zfill(5)}", 1, random_date(2015, 2018)))
    
    print("📊 Populating physicians...")
    physicians = []
    for i in range(30):
        fname = random.choice(FIRST_NAMES)
        lname = random.choice(LAST_NAMES)
        physicians.append((i+1, fname, lname))
        c.execute("""
            INSERT INTO doc (dr_id, dr_npi, dr_fname, dr_lname, dr_suffix, dr_specialty,
                           dr_dept_id, dr_email, dr_phone, dr_license_no, dr_license_state,
                           dr_license_exp, dr_dea_no, dr_status, dr_hire_dt, created_dt, modified_dt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (i+1, f"NPI{str(random.randint(1000000000, 9999999999))}", fname, lname,
              random.choice(["MD", "DO", "MD, PhD"]), random.choice(DEPARTMENTS),
              random.randint(1, len(DEPARTMENTS)), f"{fname.lower()}.{lname.lower()}@hospital.org",
              random_phone(), f"LIC{random.randint(100000, 999999)}", random.choice(STATES),
              random_date(2025, 2028), f"DEA{random.randint(1000000, 9999999)}", 1,
              random_date(2010, 2022), random_date(2018, 2020), datetime.now()))
    
    print("📊 Populating staff...")
    for i in range(50):
        fname = random.choice(FIRST_NAMES)
        lname = random.choice(LAST_NAMES)
        c.execute("""
            INSERT INTO emp (emp_id, emp_no, emp_fname, emp_lname, emp_email, emp_phone,
                           emp_role, emp_dept_id, emp_status, emp_hourly_rate, emp_hire_dt, created_dt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (i+1, f"EMP{str(i+1).zfill(5)}", fname, lname, 
              f"{fname.lower()}.{lname.lower()}@hospital.org", random_phone(),
              random.choice(["Nurse", "Lab Tech", "Radiology Tech", "Admin", "Receptionist"]),
              random.randint(1, len(DEPARTMENTS)), 1, random.randint(25, 75),
              random_date(2015, 2023), random_date(2018, 2020)))
    
    print("📊 Populating rooms...")
    for i in range(40):
        c.execute("""
            INSERT INTO room (room_id, room_no, room_type, dept_id, floor_no, bed_count,
                            room_status, daily_rate, created_dt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (i+1, f"{(i//10)+1}{str(i%10+100)[1:]}", 
              random.choice(["Private", "Semi-Private", "ICU", "OR", "ER"]),
              random.randint(1, len(DEPARTMENTS)), (i//10)+1,
              random.randint(1, 4), random.choice(["Available", "Occupied", "Maintenance"]),
              random.randint(500, 2500), random_date(2018, 2020)))
    
    print("📊 Populating patients (500 records)...")
    patients = []
    for i in range(500):
        fname = random.choice(FIRST_NAMES)
        lname = random.choice(LAST_NAMES)
        patients.append((i+1, fname, lname))
        dob = random_date(1940, 2015)
        c.execute("""
            INSERT INTO pat (pt_id, pt_mrn, pt_fname, pt_lname, pt_mname, pt_dob, pt_gender,
                           pt_ssn, pt_email, pt_phone, pt_cell, pt_addr1, pt_city, pt_state,
                           pt_zip, pt_emerg_contact, pt_emerg_phone, pt_blood_type, pt_status,
                           ins_id, ins_policy_no, created_dt, modified_dt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (i+1, f"MRN{str(i+1).zfill(8)}", fname, lname, random.choice(FIRST_NAMES)[0],
              dob.strftime("%Y-%m-%d"), random.choice(["M", "F"]), random_ssn(),
              f"{fname.lower()}.{lname.lower()}@email.com", random_phone(), random_phone(),
              f"{random.randint(100,9999)} {random.choice(['Main', 'Oak', 'Elm', 'Pine'])} St",
              random.choice(CITIES), random.choice(STATES), f"{random.randint(10000,99999)}",
              f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}", random_phone(),
              random.choice(["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]), 1,
              random.randint(1, len(INSURANCE)), f"POL{random.randint(100000, 999999)}",
              random_date(2018, 2023), datetime.now()))
    
    print("📊 Populating appointments (1500 records)...")
    for i in range(1500):
        pt = random.choice(patients)
        dr = random.choice(physicians)
        appt_dt = random_date(2023, 2025)
        c.execute("""
            INSERT INTO appt (appt_id, pt_id, dr_id, dept_id, appt_dt, appt_dur, appt_type,
                            appt_reason, appt_status, room_no, no_show, created_dt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (i+1, pt[0], dr[0], random.randint(1, len(DEPARTMENTS)), appt_dt,
              random.choice([15, 30, 45, 60]), random.choice(["New Visit", "Follow-up", "Annual", "Urgent"]),
              random.choice(DIAGNOSES), random.choice(["Scheduled", "Completed", "Cancelled", "No-Show"]),
              f"{random.randint(1,5)}{random.randint(10,99)}", random.choice([0, 0, 0, 1]),
              appt_dt - timedelta(days=random.randint(1, 30))))
    
    print("📊 Populating encounters (800 records)...")
    encounters = []
    for i in range(800):
        pt = random.choice(patients)
        dr = random.choice(physicians)
        enc_dt = random_date(2023, 2025)
        encounters.append((i+1, pt[0], dr[0]))
        c.execute("""
            INSERT INTO enc (enc_id, pt_id, dr_id, dept_id, enc_type, enc_dt, discharge_dt,
                           chief_complaint, enc_status, room_no, acuity_level, created_dt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (i+1, pt[0], dr[0], random.randint(1, len(DEPARTMENTS)),
              random.choice(["Outpatient", "Inpatient", "Emergency", "Observation"]),
              enc_dt, enc_dt + timedelta(hours=random.randint(1, 72)),
              random.choice(DIAGNOSES), random.choice(["Active", "Discharged"]),
              f"{random.randint(1,5)}{random.randint(10,99)}", random.randint(1, 5), enc_dt))
    
    print("📊 Populating diagnoses (2000 records)...")
    for i in range(2000):
        enc = random.choice(encounters)
        c.execute("""
            INSERT INTO diag (dx_id, enc_id, pt_id, dx_code, dx_code_type, dx_desc, dx_type,
                            dx_priority, onset_dt, dx_status, diagnosed_by, created_dt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (i+1, enc[0], enc[1], f"ICD{random.randint(10, 99)}.{random.randint(0,9)}",
              "ICD-10", random.choice(DIAGNOSES), random.choice(["Primary", "Secondary"]),
              random.randint(1, 3), random_date(2022, 2024), 
              random.choice(["Active", "Resolved"]), enc[2], random_date(2023, 2025)))
    
    print("📊 Populating medications (2500 records)...")
    for i in range(2500):
        enc = random.choice(encounters)
        start_dt = random_date(2023, 2025)
        c.execute("""
            INSERT INTO med (rx_id, pt_id, enc_id, dr_id, med_name, med_dose, med_unit,
                           med_route, med_freq, rx_qty, rx_refills, rx_start_dt, rx_end_dt,
                           rx_status, created_dt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (i+1, enc[1], enc[0], enc[2], random.choice(MEDICATIONS),
              str(random.choice([5, 10, 20, 25, 50, 100, 250, 500])),
              random.choice(["mg", "mcg", "ml"]),
              random.choice(["Oral", "IV", "IM", "Topical", "Inhalation"]),
              random.choice(["Once daily", "Twice daily", "Three times daily", "As needed"]),
              random.randint(30, 180), random.randint(0, 5), start_dt,
              start_dt + timedelta(days=random.randint(30, 365)),
              random.choice(["Active", "Completed", "Discontinued"]), start_dt))
    
    print("📊 Populating lab results (3000 records)...")
    for i in range(3000):
        enc = random.choice(encounters)
        c.execute("""
            INSERT INTO lab (lab_id, enc_id, pt_id, dr_id, lab_code, lab_name, lab_category,
                           lab_value, lab_unit, lab_range_low, lab_range_high, lab_flag,
                           collection_dt, result_dt, lab_status, created_dt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (i+1, enc[0], enc[1], enc[2], f"LAB{random.randint(1000, 9999)}",
              random.choice(["Complete Blood Count", "Basic Metabolic Panel", "Lipid Panel",
                           "Liver Function", "Thyroid Panel", "Urinalysis", "HbA1c"]),
              random.choice(["Hematology", "Chemistry", "Microbiology"]),
              str(round(random.uniform(50, 200), 2)),
              random.choice(["mg/dL", "mmol/L", "%", "U/L"]),
              round(random.uniform(40, 80), 2), round(random.uniform(100, 200), 2),
              random.choice(["Normal", "High", "Low", "Critical"]),
              random_date(2023, 2025), random_date(2023, 2025),
              random.choice(["Final", "Preliminary"]), random_date(2023, 2025)))
    
    print("📊 Populating procedures (1000 records)...")
    for i in range(1000):
        enc = random.choice(encounters)
        c.execute("""
            INSERT INTO proc (proc_id, enc_id, pt_id, dr_id, proc_code, proc_code_type,
                            proc_desc, proc_dt, proc_duration, proc_status, proc_location, created_dt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (i+1, enc[0], enc[1], enc[2], f"CPT{random.randint(10000, 99999)}",
              "CPT", random.choice(PROCEDURES), random_date(2023, 2025),
              random.randint(15, 180), random.choice(["Completed", "Scheduled"]),
              random.choice(["OR 1", "OR 2", "Radiology", "Endoscopy Suite"]),
              random_date(2023, 2025)))
    
    print("📊 Populating vitals (4000 records)...")
    for i in range(4000):
        enc = random.choice(encounters)
        c.execute("""
            INSERT INTO vitals (vital_id, enc_id, pt_id, measured_dt, bp_systolic, bp_diastolic,
                              heart_rate, resp_rate, temp_f, o2_sat, weight_lbs, height_in,
                              bmi, pain_level, created_dt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (i+1, enc[0], enc[1], random_date(2023, 2025),
              random.randint(90, 180), random.randint(60, 100),
              random.randint(50, 120), random.randint(12, 24),
              round(random.uniform(97.0, 103.0), 1), round(random.uniform(92, 100), 1),
              round(random.uniform(100, 300), 1), round(random.uniform(60, 78), 1),
              round(random.uniform(18, 40), 1), random.randint(0, 10),
              random_date(2023, 2025)))
    
    print("📊 Populating billing (800 records)...")
    for i in range(800):
        enc = random.choice(encounters)
        total = round(random.uniform(500, 50000), 2)
        ins_pay = round(total * random.uniform(0.5, 0.9), 2)
        c.execute("""
            INSERT INTO bill (bill_id, enc_id, pt_id, ins_id, claim_no, bill_dt, service_dt,
                            bill_status, total_charges, ins_payment, pt_payment, balance_due, created_dt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (i+1, enc[0], enc[1], random.randint(1, len(INSURANCE)),
              f"CLM{random.randint(100000, 999999)}", random_date(2023, 2025),
              random_date(2023, 2025), random.choice(["Submitted", "Paid", "Pending", "Denied"]),
              total, ins_pay, round(total - ins_pay, 2), 
              round(random.uniform(0, total - ins_pay), 2), random_date(2023, 2025)))
    
    print("📊 Populating allergies (600 records)...")
    for i in range(600):
        pt = random.choice(patients)
        c.execute("""
            INSERT INTO allergy (allergy_id, pt_id, allergen, allergen_type, reaction, severity,
                               onset_dt, verified, allergy_status, created_dt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (i+1, pt[0], random.choice(["Penicillin", "Sulfa", "Aspirin", "Latex", "Peanuts", "Shellfish"]),
              random.choice(["Drug", "Food", "Environmental"]),
              random.choice(["Hives", "Anaphylaxis", "Rash", "Swelling", "Breathing difficulty"]),
              random.choice(["Mild", "Moderate", "Severe"]), random_date(2010, 2023),
              1, "Active", random_date(2020, 2024)))
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Created SOURCE database: {source_path}")
    print("   Tables: pat, doc, dept, appt, enc, diag, med, lab, proc, vitals, ins, bill, allergy, emp, room")
    print("   Total records: ~17,000+")
    
    return source_path


def create_target_database():
    """
    TARGET DATABASE: Modern Healthcare Data Platform (HDP)
    Uses clean naming, snake_case, modern conventions
    """
    target_path = "data/enterprise_target_hdp.db"
    
    if os.path.exists(target_path):
        os.remove(target_path)
    
    conn = sqlite3.connect(target_path)
    c = conn.cursor()
    
    print("\n🏥 Creating Modern Healthcare Data Platform (HDP)...")
    
    # =========================================================================
    # TABLE 1: PATIENTS (Modern naming)
    # =========================================================================
    c.execute("""
        CREATE TABLE patients (
            patient_id INTEGER PRIMARY KEY,
            medical_record_number VARCHAR(20) UNIQUE,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            middle_name VARCHAR(100),
            date_of_birth DATE,
            gender VARCHAR(20),
            social_security_number VARCHAR(15),
            email_address VARCHAR(255),
            phone_number VARCHAR(30),
            mobile_number VARCHAR(30),
            address_line_1 VARCHAR(500),
            address_line_2 VARCHAR(500),
            city VARCHAR(100),
            state_code VARCHAR(10),
            zip_code VARCHAR(20),
            emergency_contact_name VARCHAR(200),
            emergency_contact_phone VARCHAR(30),
            blood_type VARCHAR(10),
            known_allergies TEXT,
            is_active BOOLEAN,
            insurance_provider_id INTEGER,
            policy_number VARCHAR(100),
            group_number VARCHAR(100),
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            created_by_user_id INTEGER,
            updated_by_user_id INTEGER
        )
    """)
    
    # =========================================================================
    # TABLE 2: PROVIDERS/PHYSICIANS (Modern naming)
    # =========================================================================
    c.execute("""
        CREATE TABLE healthcare_providers (
            provider_id INTEGER PRIMARY KEY,
            national_provider_identifier VARCHAR(20) UNIQUE,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            credentials_suffix VARCHAR(50),
            specialty VARCHAR(200),
            department_id INTEGER,
            email_address VARCHAR(255),
            phone_number VARCHAR(30),
            license_number VARCHAR(100),
            license_state VARCHAR(10),
            license_expiration_date DATE,
            dea_number VARCHAR(30),
            is_active BOOLEAN,
            hire_date DATE,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
    """)
    
    # =========================================================================
    # TABLE 3: DEPARTMENTS (Modern naming)
    # =========================================================================
    c.execute("""
        CREATE TABLE departments (
            department_id INTEGER PRIMARY KEY,
            department_code VARCHAR(20) UNIQUE,
            department_name VARCHAR(200),
            department_head_id INTEGER,
            phone_number VARCHAR(30),
            location_description VARCHAR(200),
            floor_number INTEGER,
            annual_budget DECIMAL(18,2),
            is_active BOOLEAN,
            created_at TIMESTAMP
        )
    """)
    
    # =========================================================================
    # TABLE 4: APPOINTMENTS (Modern naming)
    # =========================================================================
    c.execute("""
        CREATE TABLE appointments (
            appointment_id INTEGER PRIMARY KEY,
            patient_id INTEGER,
            provider_id INTEGER,
            department_id INTEGER,
            scheduled_datetime TIMESTAMP,
            duration_minutes INTEGER,
            appointment_type VARCHAR(100),
            reason_for_visit TEXT,
            appointment_status VARCHAR(50),
            clinical_notes TEXT,
            room_number VARCHAR(30),
            check_in_time TIMESTAMP,
            check_out_time TIMESTAMP,
            is_no_show BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP,
            created_by_user_id INTEGER
        )
    """)
    
    # =========================================================================
    # TABLE 5: PATIENT ENCOUNTERS (Modern naming)
    # =========================================================================
    c.execute("""
        CREATE TABLE patient_encounters (
            encounter_id INTEGER PRIMARY KEY,
            patient_id INTEGER,
            provider_id INTEGER,
            department_id INTEGER,
            encounter_type VARCHAR(100),
            encounter_start_datetime TIMESTAMP,
            discharge_datetime TIMESTAMP,
            chief_complaint TEXT,
            present_illness_history TEXT,
            encounter_status VARCHAR(50),
            discharge_disposition VARCHAR(200),
            admission_source VARCHAR(100),
            room_number VARCHAR(30),
            bed_number VARCHAR(20),
            acuity_score INTEGER,
            created_at TIMESTAMP
        )
    """)
    
    # =========================================================================
    # TABLE 6: CLINICAL DIAGNOSES (Modern naming)
    # =========================================================================
    c.execute("""
        CREATE TABLE clinical_diagnoses (
            diagnosis_id INTEGER PRIMARY KEY,
            encounter_id INTEGER,
            patient_id INTEGER,
            diagnosis_code VARCHAR(30),
            code_system VARCHAR(20),
            diagnosis_description TEXT,
            diagnosis_classification VARCHAR(50),
            priority_rank INTEGER,
            onset_date DATE,
            resolution_date DATE,
            diagnosis_status VARCHAR(50),
            diagnosing_provider_id INTEGER,
            created_at TIMESTAMP
        )
    """)
    
    # =========================================================================
    # TABLE 7: MEDICATION ORDERS (Modern naming)
    # =========================================================================
    c.execute("""
        CREATE TABLE medication_orders (
            order_id INTEGER PRIMARY KEY,
            patient_id INTEGER,
            encounter_id INTEGER,
            prescribing_provider_id INTEGER,
            medication_name VARCHAR(300),
            ndc_code VARCHAR(30),
            dosage_amount VARCHAR(100),
            dosage_unit VARCHAR(30),
            administration_route VARCHAR(100),
            frequency_instructions VARCHAR(200),
            quantity_prescribed INTEGER,
            refills_authorized INTEGER,
            start_date DATE,
            end_date DATE,
            order_status VARCHAR(50),
            pharmacy_notes TEXT,
            pharmacy_id INTEGER,
            dispensed_datetime TIMESTAMP,
            created_at TIMESTAMP
        )
    """)
    
    # =========================================================================
    # TABLE 8: LABORATORY RESULTS (Modern naming)
    # =========================================================================
    c.execute("""
        CREATE TABLE laboratory_results (
            result_id INTEGER PRIMARY KEY,
            encounter_id INTEGER,
            patient_id INTEGER,
            ordering_provider_id INTEGER,
            test_code VARCHAR(30),
            test_name VARCHAR(300),
            test_category VARCHAR(150),
            result_value VARCHAR(200),
            result_unit VARCHAR(100),
            reference_range_low DECIMAL(12,4),
            reference_range_high DECIMAL(12,4),
            abnormal_flag VARCHAR(20),
            specimen_type VARCHAR(100),
            collection_datetime TIMESTAMP,
            result_datetime TIMESTAMP,
            result_status VARCHAR(50),
            performing_technician_id INTEGER,
            verifying_provider_id INTEGER,
            clinical_notes TEXT,
            created_at TIMESTAMP
        )
    """)
    
    # =========================================================================
    # TABLE 9: CLINICAL PROCEDURES (Modern naming)
    # =========================================================================
    c.execute("""
        CREATE TABLE clinical_procedures (
            procedure_id INTEGER PRIMARY KEY,
            encounter_id INTEGER,
            patient_id INTEGER,
            performing_provider_id INTEGER,
            procedure_code VARCHAR(30),
            code_system VARCHAR(20),
            procedure_description TEXT,
            procedure_datetime TIMESTAMP,
            duration_minutes INTEGER,
            procedure_status VARCHAR(50),
            outcome_notes TEXT,
            complications TEXT,
            anesthesia_type VARCHAR(100),
            procedure_location VARCHAR(200),
            assisting_provider_id INTEGER,
            clinical_notes TEXT,
            created_at TIMESTAMP
        )
    """)
    
    # =========================================================================
    # TABLE 10: VITAL SIGNS (Modern naming)
    # =========================================================================
    c.execute("""
        CREATE TABLE vital_signs (
            vital_sign_id INTEGER PRIMARY KEY,
            encounter_id INTEGER,
            patient_id INTEGER,
            measurement_datetime TIMESTAMP,
            systolic_blood_pressure INTEGER,
            diastolic_blood_pressure INTEGER,
            heart_rate_bpm INTEGER,
            respiratory_rate INTEGER,
            temperature_fahrenheit DECIMAL(6,2),
            oxygen_saturation_percent DECIMAL(6,2),
            weight_pounds DECIMAL(8,2),
            height_inches DECIMAL(6,2),
            body_mass_index DECIMAL(6,2),
            pain_scale_score INTEGER,
            recorded_by_user_id INTEGER,
            clinical_notes TEXT,
            created_at TIMESTAMP
        )
    """)
    
    # =========================================================================
    # TABLE 11: INSURANCE PROVIDERS (Modern naming)
    # =========================================================================
    c.execute("""
        CREATE TABLE insurance_providers (
            provider_id INTEGER PRIMARY KEY,
            company_name VARCHAR(300),
            insurance_type VARCHAR(100),
            address VARCHAR(500),
            city VARCHAR(100),
            state_code VARCHAR(10),
            zip_code VARCHAR(20),
            phone_number VARCHAR(30),
            fax_number VARCHAR(30),
            email_address VARCHAR(255),
            payer_identifier VARCHAR(100),
            is_active BOOLEAN,
            created_at TIMESTAMP
        )
    """)
    
    # =========================================================================
    # TABLE 12: BILLING CLAIMS (Modern naming)
    # =========================================================================
    c.execute("""
        CREATE TABLE billing_claims (
            claim_id INTEGER PRIMARY KEY,
            encounter_id INTEGER,
            patient_id INTEGER,
            insurance_provider_id INTEGER,
            claim_number VARCHAR(100),
            billing_date DATE,
            date_of_service DATE,
            claim_status VARCHAR(50),
            total_charge_amount DECIMAL(14,2),
            insurance_paid_amount DECIMAL(14,2),
            patient_paid_amount DECIMAL(14,2),
            adjustment_amount DECIMAL(14,2),
            outstanding_balance DECIMAL(14,2),
            payment_due_date DATE,
            payment_received_date DATE,
            billing_notes TEXT,
            submitted_datetime TIMESTAMP,
            created_at TIMESTAMP
        )
    """)
    
    # =========================================================================
    # TABLE 13: PATIENT ALLERGIES (Modern naming)
    # =========================================================================
    c.execute("""
        CREATE TABLE patient_allergies (
            allergy_id INTEGER PRIMARY KEY,
            patient_id INTEGER,
            allergen_name VARCHAR(300),
            allergen_category VARCHAR(100),
            reaction_description TEXT,
            severity_level VARCHAR(50),
            onset_date DATE,
            is_verified BOOLEAN DEFAULT FALSE,
            verified_by_user_id INTEGER,
            allergy_status VARCHAR(50),
            created_at TIMESTAMP
        )
    """)
    
    # =========================================================================
    # TABLE 14: STAFF MEMBERS (Modern naming)
    # =========================================================================
    c.execute("""
        CREATE TABLE staff_members (
            staff_id INTEGER PRIMARY KEY,
            employee_number VARCHAR(30) UNIQUE,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            email_address VARCHAR(255),
            phone_number VARCHAR(30),
            job_title VARCHAR(200),
            department_id INTEGER,
            supervisor_id INTEGER,
            hire_date DATE,
            termination_date DATE,
            employment_status VARCHAR(50),
            hourly_rate DECIMAL(12,2),
            created_at TIMESTAMP
        )
    """)
    
    # =========================================================================
    # TABLE 15: FACILITY ROOMS (Modern naming)
    # =========================================================================
    c.execute("""
        CREATE TABLE facility_rooms (
            room_id INTEGER PRIMARY KEY,
            room_number VARCHAR(30) UNIQUE,
            room_type VARCHAR(100),
            department_id INTEGER,
            floor_number INTEGER,
            bed_capacity INTEGER,
            availability_status VARCHAR(50),
            equipment_list TEXT,
            daily_rate DECIMAL(12,2),
            created_at TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    
    print(f"✅ Created TARGET database: {target_path}")
    print("   Tables: patients, healthcare_providers, departments, appointments,")
    print("           patient_encounters, clinical_diagnoses, medication_orders,")
    print("           laboratory_results, clinical_procedures, vital_signs,")
    print("           insurance_providers, billing_claims, patient_allergies,")
    print("           staff_members, facility_rooms")
    
    return target_path


def main():
    """Create both databases"""
    os.makedirs("data", exist_ok=True)
    
    print("="*70)
    print("   ENTERPRISE DATABASE CREATOR - Healthcare Management System")
    print("="*70)
    print()
    
    source_path = create_source_database()
    target_path = create_target_database()
    
    print("\n" + "="*70)
    print("   DATABASE CREATION COMPLETE!")
    print("="*70)
    print(f"\n📁 Source: {source_path}")
    print(f"📁 Target: {target_path}")
    print("\n🎯 Ready for AI-powered migration analysis!")
    print("   Run your DataForge application and upload these databases.")
    

if __name__ == "__main__":
    main()
