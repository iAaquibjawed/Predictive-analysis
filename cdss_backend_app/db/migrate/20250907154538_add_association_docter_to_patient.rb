class AddAssociationDocterToPatient < ActiveRecord::Migration[7.2]
  def change
    add_reference :patients, :doctor, foreign_key: true, null: true
  end
end
