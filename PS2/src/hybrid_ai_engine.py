"""
Hybrid AI Engine with Groq API Integration
Combines BERT embeddings, Groq LLM (Llama 3.3 70B), TF-IDF, and Domain knowledge
for intelligent column matching with explainability
"""

import os
import re
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import time
import requests

# Local models
try:
    from sentence_transformers import SentenceTransformer
    BERT_AVAILABLE = True
except ImportError:
    BERT_AVAILABLE = False
    print("Warning: sentence-transformers not installed. BERT matching disabled.")

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class MatchResult:
    """Result of column matching with scores from all models"""
    source_column: str
    target_column: str
    source_table: str
    target_table: str
    bert_score: float
    llm_score: float
    tfidf_score: float
    domain_score: float
    ensemble_score: float
    confidence_level: str  # high, medium, low
    mapping_type: str  # 1:1, 1:Many, Many:1
    transformation: Optional[str] = None
    explanation: str = ""
    why_mapped: str = ""
    why_not_others: str = ""
    data_type_source: str = ""
    data_type_target: str = ""


@dataclass 
class ValidationResult:
    """Result of data validation"""
    source_count: int
    target_count: int
    null_checks: Dict[str, int]
    duplicate_checks: Dict[str, int]
    failed_records: List[Dict]
    referential_integrity: List[Dict]
    is_valid: bool
    summary: str


class HybridAIEngine:
    """
    Hybrid AI Engine combining multiple models for intelligent column matching.
    
    Models and Weights:
    - BERT: Semantic similarity (35%)
    - LLM (Groq Llama 3.3 70B): Contextual understanding (35%)  
    - TF-IDF: Character pattern matching (10%)
    - Domain: Abbreviation knowledge (20%)
    """
    
    # Common prefixes to strip (e.g., cust_fname -> fname)
    COMMON_PREFIXES = ['cust_', 'customer_', 'usr_', 'user_', 'emp_', 'employee_', 
                       'ord_', 'order_', 'prod_', 'product_', 'inv_', 'invoice_',
                       'acct_', 'account_', 'item_', 'tbl_', 'src_', 'tgt_']
    
    # Common database abbreviations - EXPANDED
    ABBREVIATIONS = {
        # Customer/Person - EXPANDED
        'cust': 'customer', 'cust_id': 'customer_id', 'cid': 'customer_id', 'custid': 'customer_id',
        'fname': 'first_name', 'f_name': 'first_name', 'firstname': 'first_name', 'first': 'first_name',
        'lname': 'last_name', 'l_name': 'last_name', 'lastname': 'last_name', 'last': 'last_name',
        'mname': 'middle_name', 'm_name': 'middle_name', 'middlename': 'middle_name',
        'cust_fname': 'first_name', 'cust_lname': 'last_name', 'cust_name': 'customer_name',
        'dob': 'date_of_birth', 'bday': 'birthday', 'bd': 'birth_date', 'birthdate': 'date_of_birth',
        'ssn': 'social_security_number', 'sin': 'social_insurance_number',
        
        # Contact - EXPANDED
        'ph': 'phone', 'tel': 'telephone', 'mob': 'mobile', 'cell': 'cellphone',
        'phone_num': 'phone_number', 'phone_no': 'phone_number', 'phoneno': 'phone_number',
        'cust_ph': 'phone_number', 'cust_phone': 'phone_number',
        'addr': 'address', 'address1': 'address_line_1', 'address2': 'address_line_2',
        'addr1': 'address_line_1', 'addr2': 'address_line_2', 'street_addr': 'street_address',
        'cust_addr': 'street_address', 'cust_address': 'street_address',
        'zip': 'postal_code', 'zipcode': 'postal_code', 'zip_code': 'postal_code',
        'cust_zip': 'postal_code', 'postal': 'postal_code', 'pcode': 'postal_code',
        'email': 'email_address', 'e_mail': 'email_address', 'mail': 'email_address',
        'cust_email': 'email_address', 'emailaddr': 'email_address',
        
        # Location - EXPANDED
        'ctry': 'country', 'cntry': 'country', 'cnt': 'country', 'country_code': 'country',
        'prov': 'province', 'reg': 'region', 'st': 'state', 'state': 'state_code',
        'cust_state': 'state_code', 'cust_city': 'city',
        'lat': 'latitude', 'lng': 'longitude', 'lon': 'longitude',
        
        # Order/Transaction  
        'ord': 'order', 'ord_id': 'order_id', 'oid': 'order_id', 'order_no': 'order_number',
        'txn': 'transaction', 'trans': 'transaction', 'trx': 'transaction',
        'inv': 'invoice', 'inv_no': 'invoice_number', 'invno': 'invoice_number',
        'qty': 'quantity', 'amt': 'amount', 'tot': 'total', 'total_amt': 'total_amount',
        'disc': 'discount', 'pct': 'percent', 'percentage': 'percent',
        
        # Product
        'prod': 'product', 'prod_id': 'product_id', 'pid': 'product_id', 'prodid': 'product_id',
        'sku': 'stock_keeping_unit', 'cat': 'category', 'categ': 'category',
        'desc': 'description', 'descr': 'description', 'product_desc': 'product_description',
        'prod_name': 'product_name', 'item_name': 'product_name',
        
        # Financial
        'acct': 'account', 'acc': 'account', 'acct_no': 'account_number', 'accno': 'account_number',
        'bal': 'balance', 'curr': 'currency', 'ccy': 'currency',
        'cr': 'credit', 'dr': 'debit', 'pmt': 'payment', 'pymt': 'payment',
        
        # Date/Time - CRITICAL MAPPINGS
        'dt': 'date', 'tm': 'time', 'ts': 'timestamp', '_at': '_date',
        'yr': 'year', 'mo': 'month', 'dy': 'day',
        'created_dt': 'created_at', 'create_dt': 'created_at', 'createdt': 'created_at',
        'updated_dt': 'updated_at', 'update_dt': 'updated_at', 'updatedt': 'updated_at',
        'modified_dt': 'updated_at', 'modify_dt': 'updated_at', 'modifieddt': 'updated_at',
        'created_date': 'created_at', 'updated_date': 'updated_at', 'modified_date': 'updated_at',
        'create_date': 'created_at', 'update_date': 'updated_at', 'modify_date': 'updated_at',
        
        # Status - EXPANDED
        'sts': 'status', 'stat': 'status', 'flg': 'flag',
        'actv': 'active', 'inactv': 'inactive', 'is_active': 'active',
        'cust_status': 'is_active', 'cust_type': 'customer_type', 'status': 'is_active',
        'enabled': 'is_active', 'disabled': 'is_inactive',
        
        # Employee
        'emp': 'employee', 'emp_id': 'employee_id', 'eid': 'employee_id', 'empid': 'employee_id',
        'mgr': 'manager', 'dept': 'department', 'sal': 'salary', 'salary_amt': 'salary',
        
        # Technical
        'id': 'identifier', 'pk': 'primary_key', 'fk': 'foreign_key',
        'seq': 'sequence', 'num': 'number', 'no': 'number', 'nbr': 'number',
        'src': 'source', 'tgt': 'target', 'dest': 'destination',
        'ref': 'reference', 'cfg': 'configuration', 'config': 'configuration',
        'loc': 'location', 'geo': 'geography', 
        'img': 'image', 'pic': 'picture', 'photo': 'image',
        'msg': 'message', 'txt': 'text',
        'mid': 'member_id', 'sid': 'session_id', 'uid': 'user_id',
        'grp': 'group', 'cat': 'category', 'typ': 'type',
        'std': 'standard', 'ext': 'extension',
        
        # HEALTHCARE/MEDICAL DOMAIN - Enterprise Database Support
        # Patient/Person
        'pt': 'patient', 'pt_id': 'patient_id', 'pat': 'patient',
        'pt_fname': 'first_name', 'pt_lname': 'last_name', 'pt_mname': 'middle_name',
        'pt_dob': 'date_of_birth', 'pt_gender': 'gender', 'pt_ssn': 'social_security_number',
        'pt_email': 'email_address', 'pt_phone': 'phone_number', 'pt_cell': 'mobile_number',
        'pt_addr1': 'address_line_1', 'pt_addr2': 'address_line_2',
        'pt_city': 'city', 'pt_state': 'state_code', 'pt_zip': 'zip_code',
        'pt_mrn': 'medical_record_number', 'mrn': 'medical_record_number',
        'pt_emerg_contact': 'emergency_contact_name', 'pt_emerg_phone': 'emergency_contact_phone',
        'pt_blood_type': 'blood_type', 'pt_allergies': 'known_allergies',
        'pt_status': 'is_active',
        
        # Provider/Physician
        'dr': 'provider', 'dr_id': 'provider_id', 'doc': 'provider', 'phy': 'provider',
        'dr_npi': 'national_provider_identifier', 'npi': 'national_provider_identifier',
        'dr_fname': 'first_name', 'dr_lname': 'last_name', 'dr_suffix': 'credentials_suffix',
        'dr_specialty': 'specialty', 'dr_dept_id': 'department_id',
        'dr_email': 'email_address', 'dr_phone': 'phone_number',
        'dr_license_no': 'license_number', 'dr_license_state': 'license_state',
        'dr_license_exp': 'license_expiration_date', 'dr_dea_no': 'dea_number',
        'dr_status': 'is_active', 'dr_hire_dt': 'hire_date',
        
        # Department
        'dept_id': 'department_id', 'dept_code': 'department_code',
        'dept_name': 'department_name', 'dept_head_id': 'department_head_id',
        'dept_phone': 'phone_number', 'dept_location': 'location_description',
        'dept_floor': 'floor_number', 'dept_budget': 'annual_budget',
        'dept_status': 'is_active',
        
        # Appointments
        'appt': 'appointment', 'appt_id': 'appointment_id',
        'appt_dt': 'scheduled_datetime', 'appt_dur': 'duration_minutes',
        'appt_type': 'appointment_type', 'appt_reason': 'reason_for_visit',
        'appt_status': 'appointment_status', 'appt_notes': 'clinical_notes',
        'check_in_dt': 'check_in_time', 'check_out_dt': 'check_out_time',
        'no_show': 'is_no_show', 'room_no': 'room_number',
        
        # Encounter
        'enc': 'encounter', 'enc_id': 'encounter_id',
        'enc_type': 'encounter_type', 'enc_dt': 'encounter_start_datetime',
        'discharge_dt': 'discharge_datetime', 'chief_complaint': 'chief_complaint',
        'presenting_problem': 'present_illness_history', 'enc_status': 'encounter_status',
        'disposition': 'discharge_disposition', 'admit_src': 'admission_source',
        'bed_no': 'bed_number', 'acuity_level': 'acuity_score',
        
        # Diagnosis
        'diag': 'diagnosis', 'dx': 'diagnosis', 'dx_id': 'diagnosis_id',
        'dx_code': 'diagnosis_code', 'dx_code_type': 'code_system',
        'dx_desc': 'diagnosis_description', 'dx_type': 'diagnosis_classification',
        'dx_priority': 'priority_rank', 'onset_dt': 'onset_date',
        'resolved_dt': 'resolution_date', 'dx_status': 'diagnosis_status',
        'diagnosed_by': 'diagnosing_provider_id',
        
        # Medication
        'med': 'medication', 'rx': 'medication_order', 'rx_id': 'order_id',
        'med_name': 'medication_name', 'med_ndc': 'ndc_code',
        'med_dose': 'dosage_amount', 'med_unit': 'dosage_unit',
        'med_route': 'administration_route', 'med_freq': 'frequency_instructions',
        'rx_qty': 'quantity_prescribed', 'rx_refills': 'refills_authorized',
        'rx_start_dt': 'start_date', 'rx_end_dt': 'end_date',
        'rx_status': 'order_status', 'rx_notes': 'pharmacy_notes',
        'dispensed_dt': 'dispensed_datetime',
        
        # Lab
        'lab': 'laboratory', 'lab_id': 'result_id',
        'lab_code': 'test_code', 'lab_name': 'test_name',
        'lab_category': 'test_category', 'lab_value': 'result_value',
        'lab_unit': 'result_unit', 'lab_range_low': 'reference_range_low',
        'lab_range_high': 'reference_range_high', 'lab_flag': 'abnormal_flag',
        'specimen_type': 'specimen_type', 'collection_dt': 'collection_datetime',
        'result_dt': 'result_datetime', 'lab_status': 'result_status',
        'performed_by': 'performing_technician_id', 'verified_by': 'verifying_provider_id',
        'lab_notes': 'clinical_notes',
        
        # Procedure
        'proc': 'procedure', 'proc_id': 'procedure_id',
        'proc_code': 'procedure_code', 'proc_code_type': 'code_system',
        'proc_desc': 'procedure_description', 'proc_dt': 'procedure_datetime',
        'proc_duration': 'duration_minutes', 'proc_status': 'procedure_status',
        'proc_result': 'outcome_notes', 'proc_complications': 'complications',
        'anesthesia_type': 'anesthesia_type', 'proc_location': 'procedure_location',
        'assistant_id': 'assisting_provider_id', 'proc_notes': 'clinical_notes',
        
        # Vitals
        'vital': 'vital_sign', 'vital_id': 'vital_sign_id',
        'measured_dt': 'measurement_datetime',
        'bp_systolic': 'systolic_blood_pressure', 'bp_diastolic': 'diastolic_blood_pressure',
        'heart_rate': 'heart_rate_bpm', 'resp_rate': 'respiratory_rate',
        'temp_f': 'temperature_fahrenheit', 'o2_sat': 'oxygen_saturation_percent',
        'weight_lbs': 'weight_pounds', 'height_in': 'height_inches',
        'bmi': 'body_mass_index', 'pain_level': 'pain_scale_score',
        'measured_by': 'recorded_by_user_id', 'vital_notes': 'clinical_notes',
        
        # Insurance
        'ins': 'insurance', 'ins_id': 'provider_id',
        'ins_name': 'company_name', 'ins_type': 'insurance_type',
        'ins_addr': 'address', 'ins_city': 'city', 'ins_state': 'state_code',
        'ins_zip': 'zip_code', 'ins_phone': 'phone_number',
        'ins_fax': 'fax_number', 'ins_email': 'email_address',
        'ins_payer_id': 'payer_identifier', 'ins_status': 'is_active',
        'ins_policy_no': 'policy_number', 'ins_group_no': 'group_number',
        
        # Billing
        'bill': 'billing_claim', 'bill_id': 'claim_id', 'claim_no': 'claim_number',
        'bill_dt': 'billing_date', 'service_dt': 'date_of_service',
        'bill_status': 'claim_status', 'total_charges': 'total_charge_amount',
        'ins_payment': 'insurance_paid_amount', 'pt_payment': 'patient_paid_amount',
        'adjustments': 'adjustment_amount', 'balance_due': 'outstanding_balance',
        'due_dt': 'payment_due_date', 'paid_dt': 'payment_received_date',
        'bill_notes': 'billing_notes', 'submitted_dt': 'submitted_datetime',
        
        # Allergy
        'allergy': 'patient_allergy', 'allergy_id': 'allergy_id',
        'allergen': 'allergen_name', 'allergen_type': 'allergen_category',
        'reaction': 'reaction_description', 'severity': 'severity_level',
        'verified': 'is_verified', 'allergy_status': 'allergy_status',
        
        # Staff/Employee
        'emp_no': 'employee_number', 'emp_fname': 'first_name', 'emp_lname': 'last_name',
        'emp_email': 'email_address', 'emp_phone': 'phone_number',
        'emp_role': 'job_title', 'emp_dept_id': 'department_id',
        'emp_supervisor_id': 'supervisor_id', 'emp_hire_dt': 'hire_date',
        'emp_term_dt': 'termination_date', 'emp_status': 'employment_status',
        'emp_hourly_rate': 'hourly_rate',
        
        # Room/Facility
        'room': 'facility_room', 'room_id': 'room_id',
        'room_no': 'room_number', 'room_type': 'room_type',
        'floor_no': 'floor_number', 'bed_count': 'bed_capacity',
        'room_status': 'availability_status', 'equipment': 'equipment_list',
        'daily_rate': 'daily_rate',
    }
    
    # Semantic equivalents - EXPANDED with directional mappings
    SEMANTIC_GROUPS = {
        'name': ['name', 'title', 'label', 'designation', 'first_name', 'last_name', 'full_name'],
        'identifier': ['id', 'code', 'key', 'number', 'identifier', 'no', 'num'],
        'description': ['description', 'desc', 'details', 'notes', 'comments', 'remarks'],
        'created': ['created_at', 'created_date', 'created_dt', 'create_date', 'create_dt', 'createdt', 'creation_date'],
        'updated': ['updated_at', 'updated_date', 'updated_dt', 'modified_at', 'modified_date', 'modified_dt', 'update_date', 'modify_date'],
        'amount': ['amount', 'total', 'sum', 'value', 'price', 'cost', 'amt'],
        'status': ['status', 'state', 'condition', 'flag', 'is_active', 'active', 'enabled'],
        'email': ['email', 'mail', 'email_address', 'e_mail', 'emailaddr'],
        'phone': ['phone', 'telephone', 'mobile', 'cell', 'contact_number', 'phone_number', 'ph'],
        'address': ['address', 'location', 'street', 'addr', 'street_address'],
        'postal': ['zip', 'zip_code', 'postal_code', 'zipcode', 'postcode'],
        'customer': ['customer', 'cust', 'client', 'buyer', 'account_holder'],
        # Healthcare semantic groups
        'patient': ['patient', 'pt', 'pat', 'client', 'member'],
        'provider': ['provider', 'physician', 'doctor', 'dr', 'doc', 'clinician'],
        'encounter': ['encounter', 'visit', 'admission', 'admission', 'enc'],
        'diagnosis': ['diagnosis', 'diag', 'dx', 'condition', 'illness'],
        'medication': ['medication', 'med', 'rx', 'drug', 'prescription'],
        'procedure': ['procedure', 'proc', 'operation', 'surgery', 'intervention'],
        'laboratory': ['lab', 'laboratory', 'test', 'result'],
    }
    
    # Direct column mappings for common transformations
    DIRECT_MAPPINGS = {
        ('cust_id', 'customer_id'): 0.98,
        ('cust_fname', 'first_name'): 0.98,
        ('cust_lname', 'last_name'): 0.98,
        ('cust_email', 'email_address'): 0.98,
        ('cust_ph', 'phone_number'): 0.98,
        ('cust_addr', 'street_address'): 0.98,
        ('cust_city', 'city'): 0.98,
        ('cust_state', 'state_code'): 0.98,
        ('cust_zip', 'postal_code'): 0.98,
        ('cust_type', 'customer_type'): 0.98,
        ('cust_status', 'is_active'): 0.95,
        ('created_dt', 'created_at'): 0.98,
        ('modified_dt', 'updated_at'): 0.98,
        ('fname', 'first_name'): 0.98,
        ('lname', 'last_name'): 0.98,
        
        # HEALTHCARE ENTERPRISE DATABASE MAPPINGS
        # Patient table: pat -> patients
        ('pt_id', 'patient_id'): 0.98,
        ('pt_mrn', 'medical_record_number'): 0.98,
        ('pt_fname', 'first_name'): 0.98,
        ('pt_lname', 'last_name'): 0.98,
        ('pt_mname', 'middle_name'): 0.98,
        ('pt_dob', 'date_of_birth'): 0.98,
        ('pt_gender', 'gender'): 0.98,
        ('pt_ssn', 'social_security_number'): 0.98,
        ('pt_email', 'email_address'): 0.98,
        ('pt_phone', 'phone_number'): 0.98,
        ('pt_cell', 'mobile_number'): 0.98,
        ('pt_addr1', 'address_line_1'): 0.98,
        ('pt_addr2', 'address_line_2'): 0.98,
        ('pt_city', 'city'): 0.98,
        ('pt_state', 'state_code'): 0.98,
        ('pt_zip', 'zip_code'): 0.98,
        ('pt_emerg_contact', 'emergency_contact_name'): 0.98,
        ('pt_emerg_phone', 'emergency_contact_phone'): 0.98,
        ('pt_blood_type', 'blood_type'): 0.98,
        ('pt_allergies', 'known_allergies'): 0.98,
        ('pt_status', 'is_active'): 0.95,
        
        # Provider/Doctor table: doc -> healthcare_providers
        ('dr_id', 'provider_id'): 0.98,
        ('dr_npi', 'national_provider_identifier'): 0.98,
        ('dr_fname', 'first_name'): 0.98,
        ('dr_lname', 'last_name'): 0.98,
        ('dr_suffix', 'credentials_suffix'): 0.98,
        ('dr_specialty', 'specialty'): 0.98,
        ('dr_dept_id', 'department_id'): 0.98,
        ('dr_email', 'email_address'): 0.98,
        ('dr_phone', 'phone_number'): 0.98,
        ('dr_license_no', 'license_number'): 0.98,
        ('dr_license_state', 'license_state'): 0.98,
        ('dr_license_exp', 'license_expiration_date'): 0.98,
        ('dr_dea_no', 'dea_number'): 0.98,
        ('dr_status', 'is_active'): 0.95,
        ('dr_hire_dt', 'hire_date'): 0.98,
        
        # Department table: dept -> departments
        ('dept_id', 'department_id'): 0.98,
        ('dept_code', 'department_code'): 0.98,
        ('dept_name', 'department_name'): 0.98,
        ('dept_head_id', 'department_head_id'): 0.98,
        ('dept_phone', 'phone_number'): 0.98,
        ('dept_ext', 'extension'): 0.98,
        ('dept_location', 'location_description'): 0.98,
        ('dept_floor', 'floor_number'): 0.98,
        ('dept_budget', 'annual_budget'): 0.98,
        ('dept_status', 'is_active'): 0.95,
        
        # Appointment table: appt -> appointments
        ('appt_id', 'appointment_id'): 0.98,
        ('appt_dt', 'scheduled_datetime'): 0.98,
        ('appt_dur', 'duration_minutes'): 0.98,
        ('appt_type', 'appointment_type'): 0.98,
        ('appt_reason', 'reason_for_visit'): 0.98,
        ('appt_status', 'appointment_status'): 0.98,
        ('appt_notes', 'clinical_notes'): 0.98,
        ('check_in_dt', 'check_in_time'): 0.98,
        ('check_out_dt', 'check_out_time'): 0.98,
        ('no_show', 'is_no_show'): 0.95,
        ('room_no', 'room_number'): 0.98,
        
        # Encounter table: enc -> patient_encounters
        ('enc_id', 'encounter_id'): 0.98,
        ('enc_type', 'encounter_type'): 0.98,
        ('enc_dt', 'encounter_start_datetime'): 0.98,
        ('discharge_dt', 'discharge_datetime'): 0.98,
        ('chief_complaint', 'chief_complaint'): 0.98,
        ('presenting_problem', 'present_illness_history'): 0.98,
        ('enc_status', 'encounter_status'): 0.98,
        ('disposition', 'discharge_disposition'): 0.98,
        ('admit_src', 'admission_source'): 0.98,
        ('admit_dx', 'admitting_diagnosis'): 0.98,
        ('bed_no', 'bed_number'): 0.98,
        ('acuity_level', 'acuity_score'): 0.98,
        
        # Diagnosis table: diag -> clinical_diagnoses
        ('dx_id', 'diagnosis_id'): 0.98,
        ('dx_code', 'diagnosis_code'): 0.98,
        ('dx_code_type', 'code_system'): 0.98,
        ('dx_desc', 'diagnosis_description'): 0.98,
        ('dx_type', 'diagnosis_classification'): 0.98,
        ('dx_priority', 'priority_rank'): 0.98,
        ('onset_dt', 'onset_date'): 0.98,
        ('resolved_dt', 'resolution_date'): 0.98,
        ('dx_status', 'diagnosis_status'): 0.98,
        ('diagnosed_by', 'diagnosing_provider_id'): 0.98,
        
        # Medication table: med -> medication_orders
        ('rx_id', 'order_id'): 0.98,
        ('med_name', 'medication_name'): 0.98,
        ('med_ndc', 'ndc_code'): 0.98,
        ('med_dose', 'dosage_amount'): 0.98,
        ('med_unit', 'dosage_unit'): 0.98,
        ('med_route', 'administration_route'): 0.98,
        ('med_freq', 'frequency_instructions'): 0.98,
        ('rx_qty', 'quantity_prescribed'): 0.98,
        ('rx_refills', 'refills_authorized'): 0.98,
        ('rx_start_dt', 'start_date'): 0.98,
        ('rx_end_dt', 'end_date'): 0.98,
        ('rx_status', 'order_status'): 0.98,
        ('rx_notes', 'pharmacy_notes'): 0.98,
        ('dispensed_dt', 'dispensed_datetime'): 0.98,
        ('prescribed_by', 'prescribing_provider_id'): 0.98,
        
        # Lab table: lab -> laboratory_results
        ('lab_id', 'result_id'): 0.98,
        ('lab_code', 'test_code'): 0.98,
        ('lab_name', 'test_name'): 0.98,
        ('lab_category', 'test_category'): 0.98,
        ('lab_value', 'result_value'): 0.98,
        ('lab_unit', 'result_unit'): 0.98,
        ('lab_range_low', 'reference_range_low'): 0.98,
        ('lab_range_high', 'reference_range_high'): 0.98,
        ('lab_flag', 'abnormal_flag'): 0.98,
        ('specimen_type', 'specimen_type'): 0.98,
        ('collection_dt', 'collection_datetime'): 0.98,
        ('result_dt', 'result_datetime'): 0.98,
        ('lab_status', 'result_status'): 0.98,
        ('performed_by', 'performing_technician_id'): 0.98,
        ('verified_by', 'verifying_provider_id'): 0.98,
        ('lab_notes', 'clinical_notes'): 0.98,
        
        # Procedure table: proc -> clinical_procedures
        ('proc_id', 'procedure_id'): 0.98,
        ('proc_code', 'procedure_code'): 0.98,
        ('proc_code_type', 'code_system'): 0.98,
        ('proc_desc', 'procedure_description'): 0.98,
        ('proc_dt', 'procedure_datetime'): 0.98,
        ('proc_duration', 'duration_minutes'): 0.98,
        ('proc_status', 'procedure_status'): 0.98,
        ('proc_result', 'outcome_notes'): 0.98,
        ('proc_complications', 'complications'): 0.98,
        ('anesthesia_type', 'anesthesia_type'): 0.98,
        ('proc_location', 'procedure_location'): 0.98,
        ('assistant_id', 'assisting_provider_id'): 0.98,
        ('proc_notes', 'clinical_notes'): 0.98,
        
        # Vitals table: vitals -> vital_signs
        ('vital_id', 'vital_sign_id'): 0.98,
        ('measured_dt', 'measurement_datetime'): 0.98,
        ('bp_systolic', 'systolic_blood_pressure'): 0.98,
        ('bp_diastolic', 'diastolic_blood_pressure'): 0.98,
        ('heart_rate', 'heart_rate_bpm'): 0.98,
        ('resp_rate', 'respiratory_rate'): 0.98,
        ('temp_f', 'temperature_fahrenheit'): 0.98,
        ('o2_sat', 'oxygen_saturation_percent'): 0.98,
        ('weight_lbs', 'weight_pounds'): 0.98,
        ('height_in', 'height_inches'): 0.98,
        ('bmi', 'body_mass_index'): 0.98,
        ('pain_level', 'pain_scale_score'): 0.98,
        ('measured_by', 'recorded_by_user_id'): 0.98,
        ('vital_notes', 'clinical_notes'): 0.98,
        
        # Insurance table: ins -> insurance_providers
        ('ins_id', 'provider_id'): 0.98,
        ('ins_name', 'company_name'): 0.98,
        ('ins_type', 'insurance_type'): 0.98,
        ('ins_addr', 'address'): 0.98,
        ('ins_city', 'city'): 0.98,
        ('ins_state', 'state_code'): 0.98,
        ('ins_zip', 'zip_code'): 0.98,
        ('ins_phone', 'phone_number'): 0.98,
        ('ins_fax', 'fax_number'): 0.98,
        ('ins_email', 'email_address'): 0.98,
        ('ins_payer_id', 'payer_identifier'): 0.98,
        ('ins_status', 'is_active'): 0.95,
        
        # Billing table: bill -> billing_claims
        ('bill_id', 'claim_id'): 0.98,
        ('claim_no', 'claim_number'): 0.98,
        ('bill_dt', 'billing_date'): 0.98,
        ('service_dt', 'date_of_service'): 0.98,
        ('bill_status', 'claim_status'): 0.98,
        ('total_charges', 'total_charge_amount'): 0.98,
        ('ins_payment', 'insurance_paid_amount'): 0.98,
        ('pt_payment', 'patient_paid_amount'): 0.98,
        ('adjustments', 'adjustment_amount'): 0.98,
        ('balance_due', 'outstanding_balance'): 0.98,
        ('due_dt', 'payment_due_date'): 0.98,
        ('paid_dt', 'payment_received_date'): 0.98,
        ('bill_notes', 'billing_notes'): 0.98,
        ('submitted_dt', 'submitted_datetime'): 0.98,
        
        # Allergy table: allergy -> patient_allergies
        ('allergy_id', 'allergy_id'): 0.98,
        ('allergen', 'allergen_name'): 0.98,
        ('allergen_type', 'allergen_category'): 0.98,
        ('reaction', 'reaction_description'): 0.98,
        ('severity', 'severity_level'): 0.98,
        ('verified', 'is_verified'): 0.95,
        ('allergy_status', 'allergy_status'): 0.98,
        ('reported_dt', 'reported_date'): 0.98,
        
        # Employee table: emp -> staff_members
        ('emp_id', 'employee_id'): 0.98,
        ('emp_no', 'employee_number'): 0.98,
        ('emp_fname', 'first_name'): 0.98,
        ('emp_lname', 'last_name'): 0.98,
        ('emp_email', 'email_address'): 0.98,
        ('emp_phone', 'phone_number'): 0.98,
        ('emp_role', 'job_title'): 0.98,
        ('emp_dept_id', 'department_id'): 0.98,
        ('emp_supervisor_id', 'supervisor_id'): 0.98,
        ('emp_hire_dt', 'hire_date'): 0.98,
        ('emp_term_dt', 'termination_date'): 0.98,
        ('emp_status', 'employment_status'): 0.98,
        ('emp_hourly_rate', 'hourly_rate'): 0.98,
        
        # Room table: room -> facility_rooms
        ('room_id', 'room_id'): 0.98,
        ('room_no', 'room_number'): 0.98,
        ('room_type', 'room_type'): 0.98,
        ('floor_no', 'floor_number'): 0.98,
        ('bed_count', 'bed_capacity'): 0.98,
        ('room_status', 'availability_status'): 0.98,
        ('equipment', 'equipment_list'): 0.98,
        ('daily_rate', 'daily_rate'): 0.98,
    }
    
    def __init__(self, groq_api_key: Optional[str] = None):
        """Initialize the hybrid AI engine"""
        
        # Initialize BERT
        self.bert_model = None
        if BERT_AVAILABLE:
            try:
                self.bert_model = SentenceTransformer('all-MiniLM-L6-v2')
                print("✓ BERT model loaded successfully")
            except Exception as e:
                print(f"✗ Could not load BERT model: {e}")
        
        # Initialize Groq
        self.groq_api_key = groq_api_key or os.environ.get('GROQ_API_KEY', '')
        self.llm_available = bool(self.groq_api_key)
        
        if self.llm_available:
            print("✓ Groq LLM (Llama 3.3 70B) initialized")
        else:
            print("ℹ Groq API key not provided - using local models only")
        
        # Initialize TF-IDF
        self.tfidf_vectorizer = TfidfVectorizer(
            analyzer='char_wb',
            ngram_range=(2, 4),
            lowercase=True
        )
        
        # Model weights - OPTIMIZED: domain boosted since we have comprehensive mappings
        self.weights = {'bert': 0.25, 'llm': 0.30, 'tfidf': 0.10, 'domain': 0.35}
        
        # Embedding cache
        self._embedding_cache: Dict[str, np.ndarray] = {}
        
        # LLM response cache to reduce API calls
        self._llm_cache: Dict[str, Dict] = {}
        
        # Smart routing: skip LLM if local models are confident (lowered threshold)
        self._skip_llm_threshold = 0.70
    
    def _call_groq_api(self, prompt: str, max_retries: int = 2) -> Optional[str]:
        """Call Groq API with optimized settings for minimal token usage"""
        if not self.groq_api_key:
            return None
        
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        # Use smaller, faster model with minimal tokens
        data = {
            "model": "llama-3.1-8b-instant",  # Faster, cheaper model
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            "max_tokens": 400,  # Reduced from 2048
            "stop": ["\n\n", "```"]  # Stop early
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"]
                elif response.status_code == 429:
                    # Rate limited - wait with exponential backoff
                    wait_time = min(2 ** attempt, 10)
                    print(f"Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"Groq API error: {response.status_code}")
                    return None
            except Exception as e:
                print(f"Groq API call failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)
        
        return None
    
    def _normalize_column_name(self, name: str) -> str:
        """Normalize column name for comparison"""
        name = name.lower()
        name = re.sub(r'[_\-\.]', ' ', name)
        words = name.split()
        expanded = [self.ABBREVIATIONS.get(w, w) for w in words]
        return ' '.join(expanded)
    
    def _get_bert_embedding(self, text: str) -> Optional[np.ndarray]:
        """Get BERT embedding with caching"""
        if not self.bert_model:
            return None
        if text in self._embedding_cache:
            return self._embedding_cache[text]
        normalized = self._normalize_column_name(text)
        embedding = self.bert_model.encode(normalized, convert_to_numpy=True)
        self._embedding_cache[text] = embedding
        return embedding
    
    def calculate_bert_similarity(self, source: str, target: str) -> float:
        """Calculate BERT-based semantic similarity"""
        if not self.bert_model:
            return 0.0
        source_emb = self._get_bert_embedding(source)
        target_emb = self._get_bert_embedding(target)
        if source_emb is None or target_emb is None:
            return 0.0
        similarity = cosine_similarity([source_emb], [target_emb])[0][0]
        return float(max(0, min(1, similarity)))
    
    def calculate_tfidf_similarity(self, source: str, target: str) -> float:
        """Calculate TF-IDF based similarity"""
        source_norm = self._normalize_column_name(source)
        target_norm = self._normalize_column_name(target)
        try:
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([source_norm, target_norm])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(max(0, min(1, similarity)))
        except:
            return 0.0
    
    def _strip_common_prefix(self, name: str) -> str:
        """Strip common prefixes like cust_, usr_, prod_ etc."""
        name_lower = name.lower()
        for prefix in self.COMMON_PREFIXES:
            if name_lower.startswith(prefix):
                return name_lower[len(prefix):]
        return name_lower
    
    def _get_core_term(self, name: str) -> str:
        """Extract core term by removing prefix and normalizing"""
        stripped = self._strip_common_prefix(name)
        normalized = self._normalize_column_name(stripped)
        return normalized
    
    def calculate_domain_similarity(self, source: str, target: str) -> float:
        """Calculate domain-aware similarity - ENHANCED VERSION"""
        source_lower = source.lower().strip()
        target_lower = target.lower().strip()
        
        # 1. DIRECT MAPPING CHECK (highest priority) - exact known pairs
        pair = (source_lower, target_lower)
        if pair in self.DIRECT_MAPPINGS:
            return self.DIRECT_MAPPINGS[pair]
        
        # 2. Normalize both columns
        source_norm = self._normalize_column_name(source)
        target_norm = self._normalize_column_name(target)
        
        if source_norm == target_norm:
            return 0.98
        
        # 3. Strip prefix and compare core terms
        source_core = self._get_core_term(source)
        target_core = self._get_core_term(target)
        
        if source_core == target_core:
            return 0.95
        
        # 4. Check if source abbreviation expands to target
        if source_lower in self.ABBREVIATIONS:
            expanded = self.ABBREVIATIONS[source_lower]
            target_clean = target_lower.replace('_', '')
            expanded_clean = expanded.replace('_', '')
            if expanded_clean == target_clean or expanded == target_norm:
                return 0.95
        
        # 4b. Check stripped version in abbreviations
        source_stripped = self._strip_common_prefix(source)
        if source_stripped in self.ABBREVIATIONS:
            expanded = self.ABBREVIATIONS[source_stripped]
            target_clean = target_lower.replace('_', ' ').replace('_', '')
            expanded_clean = expanded.replace('_', ' ').replace('_', '')
            if expanded.replace('_', '') == target_lower.replace('_', '') or \
               expanded.replace('_', ' ') == target_lower.replace('_', ' '):
                return 0.95
        
        # 5. Check semantic groups - ENHANCED
        for group_name, terms in self.SEMANTIC_GROUPS.items():
            source_match = any(t in source_norm or source_norm in t or t in source_core for t in terms)
            target_match = any(t in target_norm or target_norm in t or t in target_core for t in terms)
            if source_match and target_match:
                return 0.88
        
        # 6. Suffix matching for date fields (_dt, _at, _date)
        date_suffixes = ['_dt', '_at', '_date', 'date', 'time']
        source_has_date = any(source_lower.endswith(s) or s in source_lower for s in date_suffixes)
        target_has_date = any(target_lower.endswith(s) or s in target_lower for s in date_suffixes)
        
        if source_has_date and target_has_date:
            # Extract base word (created, updated, modified)
            base_words = ['created', 'create', 'updated', 'update', 'modified', 'modify', 'deleted', 'delete']
            source_base = next((w for w in base_words if w in source_lower), None)
            target_base = next((w for w in base_words if w in target_lower), None)
            
            # Handle modified -> updated mapping
            if source_base in ['modified', 'modify'] and target_base in ['updated', 'update']:
                return 0.92
            if source_base and source_base.replace('d', '').replace('e', '') == target_base.replace('d', '').replace('e', '') if target_base else False:
                return 0.92
            if source_base == target_base:
                return 0.95
        
        # 7. Word overlap with intelligent matching
        source_words = set(source_norm.split())
        target_words = set(target_norm.split())
        
        # Expand abbreviations in source words
        expanded_source = set()
        for word in source_words:
            if word in self.ABBREVIATIONS:
                expanded_source.add(self.ABBREVIATIONS[word].replace('_', ' '))
                expanded_source.update(self.ABBREVIATIONS[word].split('_'))
            expanded_source.add(word)
        
        # Check overlap with expanded terms
        overlap = len(expanded_source & target_words)
        total = len(expanded_source | target_words)
        base_score = overlap / total if total > 0 else 0.0
        
        # 8. Partial match bonus
        if base_score > 0 and (source_core in target_core or target_core in source_core):
            base_score = max(base_score, 0.75)
        
        return base_score
    
    def get_llm_analysis(self, source_columns: List[str], target_columns: List[str],
                           source_table: str = "", target_table: str = "",
                           source_types: Dict[str, str] = None, 
                           target_types: Dict[str, str] = None,
                           source_samples: Dict[str, List] = None,
                           target_samples: Dict[str, List] = None) -> Dict[str, Any]:
        """Use Groq LLM to analyze column mappings - OPTIMIZED for minimal tokens"""
        
        # Check cache first
        cache_key = f"{source_table}_{target_table}"
        if cache_key in self._llm_cache:
            return self._llm_cache[cache_key]
        
        if not self.llm_available:
            return self._generate_local_mappings(source_columns, target_columns, source_types, target_types)
        
        # Pre-filter: only ask LLM about uncertain columns (saves tokens)
        uncertain_cols = []
        for src in source_columns:
            best_local = max(
                self.calculate_domain_similarity(src, tgt) * 0.5 + 
                self.calculate_tfidf_similarity(src, tgt) * 0.5
                for tgt in target_columns
            ) if target_columns else 0
            if best_local < self._skip_llm_threshold:
                uncertain_cols.append(src)
        
        # If all confident locally, skip LLM entirely
        if not uncertain_cols:
            print("✓ All columns matched locally, skipping LLM")
            return self._generate_local_mappings(source_columns, target_columns, source_types, target_types)
        
        # Ultra-compact prompt (minimal tokens)
        src_list = ",".join(uncertain_cols[:10])  # Limit to 10 cols
        tgt_list = ",".join(target_columns[:10])
        
        prompt = f'Map: {src_list} -> {tgt_list}. JSON:{{"m":[["src","tgt",0.9]]}}'
        
        response = self._call_groq_api(prompt)
        
        if response:
            try:
                text = response.strip()
                if text.startswith('```'):
                    text = text.split('```')[1]
                    if text.startswith('json'):
                        text = text[4:]
                text = text.strip()
                
                start_idx = text.find('{')
                end_idx = text.rfind('}')
                
                if start_idx != -1 and end_idx != -1:
                    raw = json.loads(text[start_idx:end_idx+1])
                    # Convert compact format to standard format
                    if 'm' in raw:
                        result = {"mappings": [
                            {"source": m[0], "target": m[1], "confidence": m[2], "why_mapped": f"{m[0]}->{m[1]}"}
                            for m in raw['m'] if len(m) >= 3
                        ]}
                    else:
                        result = raw
                    self._llm_cache[cache_key] = result
                    print(f"✓ LLM: {len(result.get('mappings', []))} mappings")
                    return result
            except json.JSONDecodeError as e:
                print(f"LLM parse error: {e}")
        
        # Fallback to local analysis
        return self._generate_local_mappings(source_columns, target_columns, source_types, target_types)
    
    def _generate_local_mappings(self, source_columns: List[str], target_columns: List[str],
                                  source_types: Dict[str, str] = None, 
                                  target_types: Dict[str, str] = None) -> Dict[str, Any]:
        """Generate mappings using local models when LLM is unavailable"""
        mappings = []
        
        for src_col in source_columns:
            best_target = None
            best_score = 0.0
            best_reason = ""
            
            src_norm = self._normalize_column_name(src_col)
            
            for tgt_col in target_columns:
                tgt_norm = self._normalize_column_name(tgt_col)
                
                bert = self.calculate_bert_similarity(src_col, tgt_col)
                domain = self.calculate_domain_similarity(src_col, tgt_col)
                tfidf = self.calculate_tfidf_similarity(src_col, tgt_col)
                
                score = bert * 0.5 + domain * 0.3 + tfidf * 0.2
                
                if score > best_score:
                    best_score = score
                    best_target = tgt_col
                    
                    if src_norm == tgt_norm:
                        best_reason = f"'{src_col}' expands to same meaning as '{tgt_col}'"
                    elif domain > 0.8:
                        best_reason = f"'{src_col}' is an abbreviation for '{tgt_col}'"
                    elif bert > 0.7:
                        best_reason = f"'{src_col}' is semantically similar to '{tgt_col}'"
                    else:
                        best_reason = f"Pattern matching suggests '{src_col}' maps to '{tgt_col}'"
            
            if best_score > 0.4:
                mappings.append({
                    "source": src_col,
                    "target": best_target,
                    "confidence": round(best_score, 2),
                    "why_mapped": best_reason,
                    "transformation": "none"
                })
            else:
                mappings.append({
                    "source": src_col,
                    "target": None,
                    "confidence": 0.0,
                    "why_mapped": f"No confident match found for '{src_col}'",
                    "transformation": "none"
                })
        
        return {"mappings": mappings}
    
    def match_columns(self, source_schema: Dict[str, Dict], 
                     target_schema: Dict[str, Dict],
                     threshold: float = 0.6) -> Tuple[List[MatchResult], Dict]:
        """
        Match columns between source and target schemas.
        
        Args:
            source_schema: {table_name: {column_name: data_type, ...}}
            target_schema: {table_name: {column_name: data_type, ...}}
            threshold: Minimum score for a valid match
        
        Returns:
            Tuple of (List[MatchResult], stats_dict)
        """
        results = []
        llm_cache = {}
        
        # Flatten schemas and extract samples if available
        source_flat = {}
        target_flat = {}
        source_types = {}
        target_types = {}
        source_samples = {}
        target_samples = {}
        
        def parse_col_info(columns_dict):
            types = {}
            samples = {}
            for col, info in columns_dict.items():
                if isinstance(info, dict):
                    types[col] = info.get('type', 'unknown')
                    samples[col] = info.get('samples', [])
                else:
                    types[col] = info
                    samples[col] = []
            return types, samples

        for table, columns in source_schema.items():
            s_types, s_samples = parse_col_info(columns)
            for col, dtype in s_types.items():
                key = f"{table}.{col}"
                source_flat[key] = col
                source_types[col] = dtype
                source_samples[col] = s_samples[col]
                
        for table, columns in target_schema.items():
            t_types, t_samples = parse_col_info(columns)
            for col, dtype in t_types.items():
                key = f"{table}.{col}"
                target_flat[key] = col
                target_types[col] = dtype
                target_samples[col] = t_samples[col]
        
        # Get LLM analysis (batched per table pair)
        for src_table in source_schema:
            for tgt_table in target_schema:
                key = f"{src_table}_{tgt_table}"
                src_cols_dict = source_schema[src_table]
                tgt_cols_dict = target_schema[tgt_table]
                
                src_cols = list(src_cols_dict.keys())
                tgt_cols = list(tgt_cols_dict.keys())
                
                curr_src_types = {c: source_types.get(c, 'unknown') for c in src_cols}
                curr_tgt_types = {c: target_types.get(c, 'unknown') for c in tgt_cols}
                
                llm_cache[key] = self.get_llm_analysis(
                    src_cols, tgt_cols, src_table, tgt_table,
                    curr_src_types, curr_tgt_types
                )
        
        # Match each source column
        for src_table, src_columns in source_schema.items():
            for src_col in src_columns:
                src_type = source_types.get(src_col, 'unknown')
                best_match = None
                best_score = 0.0
                
                for tgt_table, tgt_columns in target_schema.items():
                    llm_key = f"{src_table}_{tgt_table}"
                    llm_data = llm_cache.get(llm_key, {})
                    llm_mappings = {
                        m['source']: m for m in llm_data.get('mappings', [])
                    }
                    
                    llm_active = len(llm_mappings) > 0

                    for tgt_col in tgt_columns:
                        tgt_type = target_types.get(tgt_col, 'unknown')
                        
                        bert_score = self.calculate_bert_similarity(src_col, tgt_col)
                        tfidf_score = self.calculate_tfidf_similarity(src_col, tgt_col)
                        domain_score = self.calculate_domain_similarity(src_col, tgt_col)
                        
                        llm_score = 0.0
                        llm_info = llm_mappings.get(src_col, {})
                        
                        if llm_active:
                            llm_target = llm_info.get('target', '')
                            if llm_target:
                                llm_target_norm = llm_target.lower().replace('_', '').replace('-', '')
                                tgt_col_norm = tgt_col.lower().replace('_', '').replace('-', '')
                                
                                if llm_target == tgt_col or llm_target_norm == tgt_col_norm:
                                    try:
                                        llm_score = float(llm_info.get('confidence', 0.0))
                                    except:
                                        llm_score = 0.0
                        
                        # Ensemble calculation
                        if llm_active and llm_score > 0:
                            base = (
                                self.weights['bert'] * bert_score +
                                self.weights['llm'] * llm_score +
                                self.weights['tfidf'] * tfidf_score +
                                self.weights['domain'] * domain_score
                            )
                            if llm_score >= 0.8:
                                ensemble = base * 0.3 + llm_score * 0.7
                            else:
                                ensemble = base * 0.5 + llm_score * 0.5
                        else:
                            ensemble = (
                                0.45 * bert_score +
                                0.20 * tfidf_score +
                                0.35 * domain_score
                            )
                        
                        if ensemble > best_score:
                            best_score = ensemble
                            best_match = {
                                'target': tgt_col,
                                'target_table': tgt_table,
                                'bert': bert_score,
                                'llm': llm_score,
                                'tfidf': tfidf_score,
                                'domain': domain_score,
                                'llm_info': llm_info,
                                'target_type': tgt_type
                            }
                
                final_threshold = threshold if llm_active else max(0.4, threshold - 0.1)
                
                if best_match and best_score >= final_threshold:
                    confidence = 'high' if best_score >= 0.8 else 'medium' if best_score >= 0.6 else 'low'
                    
                    llm_info = best_match.get('llm_info', {})
                    why_mapped = llm_info.get('why_mapped', 
                        self._generate_explanation(src_col, best_match['target'], best_match))
                    
                    results.append(MatchResult(
                        source_column=src_col,
                        target_column=best_match['target'],
                        source_table=src_table,
                        target_table=best_match['target_table'],
                        bert_score=best_match['bert'],
                        llm_score=best_match['llm'],
                        tfidf_score=best_match['tfidf'],
                        domain_score=best_match['domain'],
                        ensemble_score=best_score,
                        confidence_level=confidence,
                        mapping_type=llm_info.get('mapping_type', '1:1'),
                        transformation=llm_info.get('transformation', 'none'),
                        explanation=why_mapped,
                        why_mapped=why_mapped,
                        why_not_others=llm_info.get('why_not_others', ''),
                        data_type_source=src_type,
                        data_type_target=best_match['target_type']
                    ))
        
        # Calculate statistics
        stats = {
            'total_mappings': len(results),
            'high_confidence': sum(1 for r in results if r.confidence_level == 'high'),
            'medium_confidence': sum(1 for r in results if r.confidence_level == 'medium'),
            'low_confidence': sum(1 for r in results if r.confidence_level == 'low'),
            'average_score': np.mean([r.ensemble_score for r in results]) if results else 0,
            'llm_enabled': self.llm_available,
            'bert_enabled': self.bert_model is not None
        }
        
        return results, stats
    
    def _generate_explanation(self, source: str, target: str, scores: Dict) -> str:
        """Generate human-readable explanation"""
        if scores['domain'] > 0.8:
            return f"'{source}' is a common abbreviation for '{target}' in database systems"
        elif scores['bert'] > 0.8:
            return f"'{source}' and '{target}' have very similar semantic meanings"
        elif scores['tfidf'] > 0.7:
            return f"'{source}' and '{target}' share similar naming patterns"
        else:
            return f"Multiple factors suggest '{source}' corresponds to '{target}'"
    
    def get_unmapped_columns(self, source_schema: Dict, target_schema: Dict,
                            mappings: List[MatchResult]) -> Dict[str, List[Dict]]:
        """Get unmapped columns with explanations"""
        mapped_sources = {(m.source_table, m.source_column) for m in mappings}
        mapped_targets = {(m.target_table, m.target_column) for m in mappings}
        
        unmapped = {'source': [], 'target': []}
        
        for table, columns in source_schema.items():
            for col in columns:
                if (table, col) not in mapped_sources:
                    unmapped['source'].append({
                        'table': table,
                        'column': col,
                        'reason': self._explain_unmapped_source(col)
                    })
        
        for table, columns in target_schema.items():
            for col in columns:
                if (table, col) not in mapped_targets:
                    unmapped['target'].append({
                        'table': table,
                        'column': col,
                        'reason': self._explain_unmapped_target(col)
                    })
        
        return unmapped
    
    def _explain_unmapped_source(self, col: str) -> str:
        """Explain why source column wasn't mapped"""
        col_lower = col.lower()
        if any(p in col_lower for p in ['created', 'updated', 'modified', '_at', '_by']):
            return "This appears to be an audit/tracking column not present in target schema"
        if any(p in col_lower for p in ['old_', 'legacy_', 'deprecated']):
            return "This appears to be a legacy column that has been retired"
        if any(p in col_lower for p in ['temp_', 'tmp_', 'backup_']):
            return "This appears to be a temporary/backup column not needed in target"
        return "No sufficiently similar column found in target schema"
    
    def _explain_unmapped_target(self, col: str) -> str:
        """Explain why target column has no source"""
        col_lower = col.lower()
        if any(p in col_lower for p in ['created', 'updated', 'modified', '_at']):
            return "This is likely an auto-generated audit column"
        if 'id' in col_lower and col_lower.endswith('id'):
            return "This appears to be a new identifier that will be auto-generated"
        return "This is a new column in the target schema - may need default value or manual mapping"


def create_engine(groq_api_key: str = None) -> HybridAIEngine:
    """Create hybrid AI engine with optional Groq API"""
    return HybridAIEngine(groq_api_key=groq_api_key)
