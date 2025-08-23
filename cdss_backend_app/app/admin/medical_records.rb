ActiveAdmin.register MedicalRecord do
  menu parent: "Clinical Management", priority: 2

  permit_params :patient_id, :created_by_id, :diagnosis, :symptoms, :treatment_plan,
                :notes, :visit_date

  # Filters
  filter :patient
  filter :created_by, label: "Doctor"
  filter :diagnosis
  filter :visit_date
  filter :created_at

  # Scopes
  scope :all, default: true
  scope :recent
  scope("This Month") { |scope| scope.where(visit_date: 1.month.ago..Date.current) }

  # Index
  index do
    selectable_column
    id_column
    column "Patient" do |record|
      link_to record.patient.full_name, admin_patient_path(record.patient)
    end
    column :diagnosis
    column :visit_date
    column "Doctor" do |record|
      record.created_by.full_name
    end
    column :symptoms do |record|
      truncate(record.symptoms, length: 50)
    end
    column :created_at
    actions
  end

  # Show
  show do
    attributes_table do
      row "Patient" do |record|
        link_to record.patient.full_name, admin_patient_path(record.patient)
      end
      row :diagnosis
      row :symptoms
      row :treatment_plan
      row :notes
      row :visit_date
      row "Doctor" do |record|
        record.created_by.full_name
      end
      row :created_at
      row :updated_at
    end
  end

  # Form
  form do |f|
    f.inputs "Medical Record" do
      f.input :patient, as: :select, collection: Patient.joins(:user).includes(:user).map { |p| [p.full_name, p.id] }
      f.input :created_by, as: :select, collection: User.doctors.map { |d| [d.full_name, d.id] }, label: "Doctor"
      f.input :visit_date, as: :date_picker
      f.input :diagnosis
      f.input :symptoms, as: :text
      f.input :treatment_plan, as: :text
      f.input :notes, as: :text
    end
    f.actions
  end
end