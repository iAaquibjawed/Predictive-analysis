# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# This file is the source Rails uses to define your schema when running `bin/rails
# db:schema:load`. When creating a new database, `bin/rails db:schema:load` tends to
# be faster and is potentially less error prone than running all of your
# migrations from scratch. Old migrations may fail to apply correctly if those
# migrations use external dependencies or application code.
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema[7.2].define(version: 2025_08_23_141131) do
  create_table "active_admin_comments", force: :cascade do |t|
    t.string "namespace"
    t.text "body"
    t.string "resource_type"
    t.integer "resource_id"
    t.string "author_type"
    t.integer "author_id"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["author_type", "author_id"], name: "index_active_admin_comments_on_author"
    t.index ["namespace"], name: "index_active_admin_comments_on_namespace"
    t.index ["resource_type", "resource_id"], name: "index_active_admin_comments_on_resource"
  end

  create_table "admin_users", force: :cascade do |t|
    t.string "email", default: "", null: false
    t.string "encrypted_password", default: "", null: false
    t.string "reset_password_token"
    t.datetime "reset_password_sent_at"
    t.datetime "remember_created_at"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["email"], name: "index_admin_users_on_email", unique: true
    t.index ["reset_password_token"], name: "index_admin_users_on_reset_password_token", unique: true
  end

  create_table "audit_logs", force: :cascade do |t|
    t.integer "user_id", null: false
    t.string "action"
    t.string "resource_type"
    t.integer "resource_id"
    t.string "ip_address"
    t.text "user_agent"
    t.datetime "performed_at"
    t.json "change_data"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["user_id"], name: "index_audit_logs_on_user_id"
  end

  create_table "drug_interactions", force: :cascade do |t|
    t.integer "drug_a_id", null: false
    t.integer "drug_b_id", null: false
    t.string "interaction_type"
    t.string "severity"
    t.text "description"
    t.text "mechanism"
    t.text "clinical_effect"
    t.text "management_recommendation"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["drug_a_id"], name: "index_drug_interactions_on_drug_a_id"
    t.index ["drug_b_id"], name: "index_drug_interactions_on_drug_b_id"
  end

  create_table "drugs", force: :cascade do |t|
    t.string "name"
    t.string "generic_name"
    t.string "dosage_form"
    t.string "strength"
    t.string "manufacturer"
    t.text "description"
    t.text "indications"
    t.text "contraindications"
    t.text "side_effects"
    t.boolean "active"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
  end

  create_table "io_t_readings", force: :cascade do |t|
    t.integer "patient_id", null: false
    t.integer "prescription_id", null: false
    t.string "device_id"
    t.string "event_type"
    t.datetime "recorded_at"
    t.json "data"
    t.integer "battery_level"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["patient_id"], name: "index_io_t_readings_on_patient_id"
    t.index ["prescription_id"], name: "index_io_t_readings_on_prescription_id"
  end

  create_table "medical_records", force: :cascade do |t|
    t.integer "patient_id", null: false
    t.integer "created_by_id", null: false
    t.string "diagnosis"
    t.text "symptoms"
    t.text "treatment_plan"
    t.text "notes"
    t.date "visit_date"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["created_by_id"], name: "index_medical_records_on_created_by_id"
    t.index ["patient_id"], name: "index_medical_records_on_patient_id"
  end

  create_table "patient_assignments", force: :cascade do |t|
    t.integer "patient_id", null: false
    t.integer "user_id", null: false
    t.datetime "assigned_at"
    t.boolean "active"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["patient_id"], name: "index_patient_assignments_on_patient_id"
    t.index ["user_id"], name: "index_patient_assignments_on_user_id"
  end

  create_table "patients", force: :cascade do |t|
    t.integer "user_id", null: false
    t.string "nhs_number", null: false
    t.date "date_of_birth", null: false
    t.string "gender", null: false
    t.text "address"
    t.string "phone_number"
    t.text "emergency_contact"
    t.text "medical_history"
    t.text "allergies"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["nhs_number"], name: "index_patients_on_nhs_number", unique: true
    t.index ["user_id"], name: "index_patients_on_user_id"
  end

  create_table "prescription_drugs", force: :cascade do |t|
    t.integer "prescription_id", null: false
    t.integer "drug_id", null: false
    t.string "dosage"
    t.string "frequency"
    t.string "duration"
    t.integer "daily_frequency"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["drug_id"], name: "index_prescription_drugs_on_drug_id"
    t.index ["prescription_id"], name: "index_prescription_drugs_on_prescription_id"
  end

  create_table "prescriptions", force: :cascade do |t|
    t.integer "patient_id", null: false
    t.integer "prescribing_doctor_id", null: false
    t.date "prescription_date"
    t.integer "status"
    t.text "notes"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["patient_id"], name: "index_prescriptions_on_patient_id"
    t.index ["prescribing_doctor_id"], name: "index_prescriptions_on_prescribing_doctor_id"
  end

  create_table "users", force: :cascade do |t|
    t.string "email", default: "", null: false
    t.string "encrypted_password", default: "", null: false
    t.string "first_name", null: false
    t.string "last_name", null: false
    t.integer "role", default: 0, null: false
    t.boolean "active", default: true, null: false
    t.string "phone_number"
    t.text "specialization"
    t.string "license_number"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["active"], name: "index_users_on_active"
    t.index ["email"], name: "index_users_on_email", unique: true
    t.index ["role"], name: "index_users_on_role"
  end

  add_foreign_key "audit_logs", "users"
  add_foreign_key "drug_interactions", "drug_as"
  add_foreign_key "drug_interactions", "drug_bs"
  add_foreign_key "io_t_readings", "patients"
  add_foreign_key "io_t_readings", "prescriptions"
  add_foreign_key "medical_records", "created_bies"
  add_foreign_key "medical_records", "patients"
  add_foreign_key "patient_assignments", "patients"
  add_foreign_key "patient_assignments", "users"
  add_foreign_key "patients", "users"
  add_foreign_key "prescription_drugs", "drugs"
  add_foreign_key "prescription_drugs", "prescriptions"
  add_foreign_key "prescriptions", "patients"
  add_foreign_key "prescriptions", "users", column: "prescribing_doctor_id"
end
