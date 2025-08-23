migrations = [
  "rails generate model Patient user:references nhs_number:string:uniq date_of_birth:date gender:string address:text phone_number:string emergency_contact:text medical_history:text allergies:text",
  "rails generate model PatientAssignment patient:references user:references assigned_at:datetime active:boolean",
  "rails generate model Drug name:string generic_name:string dosage_form:string strength:string manufacturer:string description:text indications:text contraindications:text side_effects:text active:boolean",
  "rails generate model Prescription patient:references prescribing_doctor:references prescription_date:date status:integer notes:text",
  "rails generate model PrescriptionDrug prescription:references drug:references dosage:string frequency:string duration:string daily_frequency:integer",
  "rails generate model MedicalRecord patient:references created_by:references diagnosis:string symptoms:text treatment_plan:text notes:text visit_date:date",
  "rails generate model IoTReading patient:references prescription:references device_id:string event_type:string recorded_at:datetime data:json battery_level:integer",
  "rails generate model DrugInteraction drug_a:references drug_b:references interaction_type:string severity:string description:text mechanism:text clinical_effect:text management_recommendation:text",
  "rails generate model AuditLog user:references action:string resource_type:string resource_id:integer ip_address:string user_agent:string performed_at:datetime changes:json"
]

puts "Run these commands to generate all models:"
migrations.each { |cmd| puts cmd }