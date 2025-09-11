class AddConfirmableToAdminUsers < ActiveRecord::Migration[7.2]
  def change
    add_column :admin_users, :confirmed_at, :datetime
    add_column :admin_users, :confirmation_token, :string
    add_column :admin_users, :confirmation_sent_at, :datetime
    add_column :admin_users, :unconfirmed_email, :string
  end
end
