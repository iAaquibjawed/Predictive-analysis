ActiveAdmin.register Prescription do
  menu parent: "Prescription Management", priority: 1

  permit_params :patient_id, :prescribing_doctor_id, :prescription_date, :status, :notes,
                prescription_drugs_attributes: [:id, :drug_id, :dosage, :frequency, :duration, :_destroy]

  # Filters
  filter :patient
  filter :prescribing_doctor, label: "Doctor"
  filter :prescription_date
  filter :status, as: :select, collection: Prescription.statuses
  filter :created_at

  # Scopes
  scope :all
  scope :active, default: true
  scope :pending
  scope :completed

  # Index
  index do
    selectable_column
    id_column
    column "Patient" do |prescription|
      link_to prescription.patient.full_name, admin_patient_path(prescription.patient)
    end
    column "Doctor" do |prescription|
      prescription.prescribing_doctor.full_name
    end
    column :prescription_date
    column "Medications" do |prescription|
      drugs = prescription.drugs.limit(3).pluck(:name)
      drugs.join(", ") + (prescription.drugs.count > 3 ? " (+#{prescription.drugs.count - 3} more)" : "")
    end
    column :status do |prescription|
      status_tag prescription.status.humanize
    end
    column "Adherence" do |prescription|
      "#{prescription.adherence_percentage}%"
    end
    column :created_at
    actions
  end

  # Show
  show do
    attributes_table do
      row "Patient" do |prescription|
        link_to prescription.patient.full_name, admin_patient_path(prescription.patient)
      end
      row "Doctor" do |prescription|
        prescription.prescribing_doctor.full_name
      end
      row :prescription_date
      row :status do |prescription|
        status_tag prescription.status.humanize
      end
      row "Adherence" do |prescription|
        "#{prescription.adherence_percentage}%"
      end
      row :notes
      row :created_at
    end

    # Medications Panel
    panel "Prescribed Medications" do
      table_for resource.prescription_drugs.includes(:drug) do
        column "Drug" do |pd|
          link_to pd.drug.name, admin_drug_path(pd.drug)
        end
        column :dosage
        column :frequency
        column :duration
        column "Daily Frequency" do |pd|
          pd.daily_frequency
        end
      end
    end
  end

  # Form with nested prescription_drugs
  form do |f|
    f.inputs "Prescription Details" do
      f.input :patient, as: :select, collection: Patient.joins(:user).includes(:user).map { |p| [p.full_name, p.id] }
      f.input :prescribing_doctor, as: :select, collection: User.doctors.map { |d| [d.full_name, d.id] }, label: "Doctor"
      f.input :prescription_date, as: :date_picker
      f.input :status, as: :select, collection: Prescription.statuses
      f.input :notes, as: :text
    end

    f.inputs "Medications" do
      f.has_many :prescription_drugs, heading: false, allow_destroy: true, new_record: true do |pd|
        pd.input :drug, as: :select, collection: Drug.active.map { |d| ["#{d.name} (#{d.strength})", d.id] }
        pd.input :dosage, placeholder: "e.g., 10mg"
        pd.input :frequency, placeholder: "e.g., twice daily"
        pd.input :duration, placeholder: "e.g., 30 days"
      end
    end

    f.actions
  end
end