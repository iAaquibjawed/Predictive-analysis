ActiveAdmin.register AuditLog do
  menu parent: "System & Analytics", priority: 1

  # Read-only
  actions :index, :show

  # Filters
  filter :user
  filter :action
  filter :resource_type
  filter :ip_address
  filter :performed_at

  # Scopes
  scope :all, default: true
  scope :recent
  scope("API Calls") { |scope| scope.where("action LIKE ?", "%API%") }
  scope("Admin Actions") { |scope| scope.where("action LIKE ?", "%admin%") }

  # Index
  index do
    id_column
    column :performed_at
    column :user do |log|
      log.user_name
    end
    column :action
    column :resource_type
    column :resource_id
    column :ip_address
    column :user_agent do |log|
      truncate(log.user_agent, length: 40) if log.user_agent
    end
    actions defaults: false do |log|
      link_to "View", admin_audit_log_path(log), class: "button"
    end
  end

  # Show
  show do
    attributes_table do
      row :performed_at
      row :user do |log|
        log.user_name
      end
      row :action
      row :resource_type
      row :resource_id
      row :ip_address
      row :user_agent
      row :change_data do |log|
        if log.change_data.present?
          pre log.formatted_changes
        else
          "No changes recorded"
        end
      end
    end
  end

  csv do
    column :id
    column :performed_at
    column("User") { |log| log.user_name }
    column :action
    column :resource_type
    column :resource_id
    column :ip_address
    column("Changes") { |log| log.formatted_changes }
  end
end