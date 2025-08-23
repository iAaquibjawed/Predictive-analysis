class CreateAuditLogs < ActiveRecord::Migration[7.2]
  def change
    create_table :audit_logs do |t|
      t.references :user, null: false, foreign_key: true
      t.string :action
      t.string :resource_type
      t.integer :resource_id
      t.string :ip_address
      t.text :user_agent
      t.datetime :performed_at
      t.json :change_data

      t.timestamps
    end
  end
end
