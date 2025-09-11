ActiveAdmin.register AdminUser do
  menu parent: "User Management", priority: 2

  permit_params :email, :password, :password_confirmation

  # Index
  index do
    selectable_column
    id_column
    column :email
    column :current_sign_in_at
    column :sign_in_count
    column :created_at
    actions
  end

  # Form
  form do |f|
    f.inputs "Admin Details" do
      f.input :email
      f.input :password
      f.input :password_confirmation
    end
    f.actions
  end

  # Controller configuration
  controller do
    def create
      Thread.current[:active_admin_creating_admin_user] = true
      super
    ensure
      Thread.current[:active_admin_creating_admin_user] = false
    end
  end
end