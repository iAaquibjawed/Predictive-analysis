class AddIndexesToUsersForDeviseConfirmable < ActiveRecord::Migration[7.2]
  def change
    add_index :users, :confirmation_token, unique: true
  end
end
