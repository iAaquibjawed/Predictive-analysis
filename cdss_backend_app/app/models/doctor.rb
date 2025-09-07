class Doctor < ApplicationRecord
    validates :name, presence: true
    validates :email, presence: true, uniqueness: true
    has_many :patients

    # Ransack searchable attributes
    def self.ransackable_attributes(auth_object = nil)
        ["created_at", "email", "id", "name", "phone_number", "specialty", "updated_at"]

        # EXCLUDE: address, etc.
    end

    def self.ransackable_associations(auth_object = nil)
        []
    end
end
