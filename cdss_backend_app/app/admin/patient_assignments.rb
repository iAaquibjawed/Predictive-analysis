ActiveAdmin.register PatientAssignment do
  menu parent: "Clinical Management", priority: 3

  permit_params :patient_id, :user_id, :active, :assigned_at

  # Filters
  filter :patient
  filter :user, label: "Doctor"
  filter :active
  filter :assigned_at

  # Index
  index do
    selectable_column
    id_column
    column "Patient" do |assignment|
      link_to assignment.patient.full_name, admin_patient_path(assignment.patient)
    end
    column "Doctor" do |assignment|
      assignment.user.full_name
    end
    column :active do |assignment|
      status_tag assignment.active? ? "Active" : "Inactive"
    end
    column :assigned_at
    column :created_at
    actions
  end

  # Form
  form do |f|
    f.inputs "Patient Assignment" do
      f.input :patient, as: :select, collection: Patient.joins(:user).includes(:user).map { |p| [p.full_name, p.id] }
      f.input :user, as: :select, collection: User.doctors.map { |d| [d.full_name, d.id] }, label: "Doctor"
      f.input :active
      f.input :assigned_at, as: :datetime_picker
    end
    f.actions
  end
end