class Ability
  include CanCan::Ability

  def initialize(user)
    user ||= User.new

    if user.admin?
      can :manage, :all
    elsif user.doctor?
      # Doctor permissions
      can :read, :all
      can :manage, :patients_assigned_to_them
    elsif user.pharmacist?
      # Pharmacist permissions
      can :read, [:drugs, :prescriptions]
      can :manage, :inventory
    elsif user.patient?
      # Patient permissions
      can :read, :own_data
    end
  end
end
