class AddIndexesToAdminUsersForDeviseConfirmable < ActiveRecord::Migration[7.2]
  def change
    add_index :admin_users, :confirmation_token, unique: true
  end
end
