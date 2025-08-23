class AuditLog < ApplicationRecord
  belongs_to :user, optional: true

  validates :action, presence: true
  validates :performed_at, presence: true

  scope :recent, -> { where(performed_at: 1.month.ago..Time.current) }
  scope :by_user, ->(user_id) { where(user_id: user_id) }
  scope :by_action, ->(action) { where(action: action) }
  scope :by_resource, ->(type, id = nil) do
    scope = where(resource_type: type)
    scope = scope.where(resource_id: id) if id
    scope
  end

  # Ransack searchable attributes - be careful with sensitive data
  def self.ransackable_attributes(auth_object = nil)
    [
      "action", "created_at", "id", "ip_address",
      "performed_at", "resource_id", "resource_type", "updated_at", "user_id"
    # EXCLUDE: user_agent (might contain sensitive info), change_data (might contain sensitive data)
    ]
  end

  def self.ransackable_associations(auth_object = nil)
    ["user"]
  end

  # Helper methods
  def user_name
    user&.full_name || 'System'
  end

  def resource_name
    return 'N/A' unless resource_type && resource_id
    "#{resource_type} ##{resource_id}"
  end

  # Use change_data instead of changes
  def formatted_changes
    return 'No changes recorded' unless change_data.present?

    change_data.map do |field, values|
      if values.is_a?(Array) && values.length == 2
        "#{field}: #{values[0]} → #{values[1]}"
      else
        "#{field}: #{values}"
      end
    end.join(', ')
  end

  # Class method to create audit log entries
  def self.log_action(user:, action:, resource: nil, ip_address: nil, user_agent: nil, changes: nil)
    create!(
      user: user,
      action: action,
      resource_type: resource&.class&.name,
      resource_id: resource&.id,
      ip_address: ip_address,
      user_agent: user_agent,
      performed_at: Time.current,
      change_data: changes  # Store in change_data column
    )
  end
end