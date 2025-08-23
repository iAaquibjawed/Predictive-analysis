ActiveAdmin.register Patient do
  menu parent: "Clinical Management", priority: 1

  permit_params :nhs_number, :date_of_birth, :gender, :address, :phone_number,
                :emergency_contact, :medical_history, :allergies,
                user_attributes: [:id, :first_name, :last_name, :email]

  # Scopes for filtering
  scope :all, default: true
  scope("Recent") { |scope| scope.where(created_at: 1.month.ago..Time.current) }
  scope("Adults") { |scope| scope.joins(:user).where("date_of_birth < ?", 18.years.ago) }
  scope("Pediatric") { |scope| scope.joins(:user).where("date_of_birth >= ?", 18.years.ago) }

  # Filters
  filter :user_first_name, as: :string, label: "First Name"
  filter :user_last_name, as: :string, label: "Last Name"
  filter :nhs_number
  filter :date_of_birth
  filter :gender, as: :select, collection: ['male', 'female', 'other', 'prefer_not_to_say']
  filter :created_at

  # Index page
  index do
    selectable_column
    id_column
    column :nhs_number
    column "Full Name" do |patient|
      link_to patient.full_name, admin_patient_path(patient)
    end
    column :age
    column :gender do |patient|
      status_tag patient.gender.humanize
    end
    column "Active Prescriptions" do |patient|
      patient.prescriptions&.active&.count || 0
    end
    column "Last Medical Record" do |patient|
      patient.medical_records&.recent&.first&.visit_date&.strftime("%d/%m/%Y") || "No records"
    end
    column :created_at
    actions
  end

  # Show page
  show do
    attributes_table do
      row :id
      row :nhs_number
      row "Full Name" do |patient|
        patient.full_name
      end
      row :age
      row :date_of_birth
      row :gender
      row :address
      row :phone_number
      row :emergency_contact
      row :medical_history
      row :allergies
      row :created_at
      row :updated_at
    end

    # Medical Records Panel
    panel "Medical Records" do
      table_for resource.medical_records.includes(:created_by).limit(10).order(visit_date: :desc) do
        column :visit_date
        column :diagnosis
        column :symptoms
        column :treatment_plan
        column "Doctor" do |record|
          record.created_by&.full_name
        end
        column :actions do |record|
          link_to "View", admin_medical_record_path(record), class: "button"
        end
      end

      div do
        link_to "View All Medical Records", admin_medical_records_path(q: { patient_id_eq: resource.id }), class: "button"
      end
    end

    # Current Prescriptions Panel
    panel "Current Prescriptions" do
      table_for resource.prescriptions.active.includes(:prescribing_doctor, :drugs) do
        column :prescription_date
        column "Medications" do |prescription|
          prescription.drugs.pluck(:name).join(", ")
        end
        column :status do |prescription|
          status_tag prescription.status.humanize
        end
        column "Doctor" do |prescription|
          prescription.prescribing_doctor.full_name
        end
        column :actions do |prescription|
          link_to "View", admin_prescription_path(prescription), class: "button"
        end
      end
    end
  end

  # Form
  form do |f|
    f.inputs "Patient Information" do
      f.has_many :user, heading: "Personal Details", allow_destroy: false do |user_form|
        user_form.input :first_name
        user_form.input :last_name
        user_form.input :email
      end

      f.input :nhs_number, hint: "10-digit NHS number"
      f.input :date_of_birth, as: :date_picker
      f.input :gender, as: :select, collection: ['male', 'female', 'other', 'prefer_not_to_say']
      f.input :address, as: :text
      f.input :phone_number
      f.input :emergency_contact, as: :text
    end

    f.inputs "Medical Information" do
      f.input :medical_history, as: :text
      f.input :allergies, as: :text
    end

    f.actions
  end

  # Custom actions
  member_action :compliance_report, method: :get do
    @compliance_data = {
      overall_adherence: 85.5,
      medications: resource.prescriptions.active.map do |prescription|
        {
          name: prescription.drugs.pluck(:name).join(", "),
          adherence: prescription.adherence_percentage
        }
      end
    }
    render "admin/patients/compliance_report"
  end

  action_item :compliance_report, only: :show do
    link_to "Compliance Report", compliance_report_admin_patient_path(resource), class: "button"
  end

  # CSV export
  csv do
    column :id
    column :nhs_number
    column("Name") { |patient| patient.full_name }
    column :age
    column :gender
    column :date_of_birth
    column("Active Prescriptions") { |patient| patient.prescriptions&.active&.count || 0 }
    column :created_at
  end
end