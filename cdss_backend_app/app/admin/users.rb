ActiveAdmin.register User do
  menu parent: "User Management", priority: 1

  permit_params :email, :first_name, :last_name, :role, :active, :phone_number,
                :specialization, :license_number, :password, :password_confirmation

  # Filters
  filter :email
  filter :first_name
  filter :last_name
  filter :role, as: :select, collection: User.roles.map { |key, value| [key.humanize, key] }
  filter :active
  filter :created_at

  # Scopes
  scope :all, default: true
  scope :active
  scope :doctors
  scope("Pharmacists") { |scope| scope.where(role: :pharmacist) }

  # Index
  index do
    selectable_column
    id_column
    column :email
    column :full_name
    column :role do |user|
      status_tag user.role.humanize, class: user.role
    end
    column :active do |user|
      status_tag user.active? ? "Active" : "Inactive"
    end
    column :last_sign_in_at
    column :created_at
    actions
  end

  # Show
  show do
    attributes_table do
      row :email
      row :full_name
      row :role do |user|
        status_tag user.role.humanize
      end
      row :active
      row :phone_number
      row :specialization
      row :license_number
      row :sign_in_count
      row :current_sign_in_at
      row :last_sign_in_at
      row :created_at
    end

    # Role-specific panels
    if resource.doctor?
      panel "Assigned Patients" do
        table_for resource.assigned_patients.limit(10) do
          column "Patient" do |patient|
            link_to patient.full_name, admin_patient_path(patient)
          end
          column :nhs_number
          column :age
          column :created_at
        end
      end
    end

    if resource.patient?
      panel "Patient Record" do
        if resource.patient
          attributes_table_for resource.patient do
            row :nhs_number
            row :age
            row :gender
            row :medical_history
          end
        else
          "No patient record found"
        end
      end
    end
  end

  # Form
  form do |f|
    f.inputs "User Details" do
      f.input :email
      f.input :first_name
      f.input :last_name
      f.input :role, as: :select, collection: User.roles.map { |key, value| [key.humanize, key] }
      f.input :active
      f.input :phone_number
      f.input :specialization, hint: "For doctors and pharmacists"
      f.input :license_number, hint: "Professional license number"
    end

    f.inputs "Password (leave blank to generate random password)" do
      f.input :password
      f.input :password_confirmation
    end

    f.actions
  end

  # Controller configuration
  controller do
    def create
      Thread.current[:active_admin_creating_user] = true
      super
    ensure
      Thread.current[:active_admin_creating_user] = false
    end
  end

  # Batch actions
  batch_action :activate do |ids|
    User.where(id: ids).update_all(active: true)
    redirect_to collection_path, notice: "Users activated!"
  end

  batch_action :deactivate do |ids|
    User.where(id: ids).update_all(active: false)
    redirect_to collection_path, notice: "Users deactivated!"
  end
end