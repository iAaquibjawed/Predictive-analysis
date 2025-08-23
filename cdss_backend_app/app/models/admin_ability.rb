class AdminAbility
  include CanCan::Ability

  def initialize(admin_user)
    admin_user ||= AdminUser.new

    if admin_user.persisted?
      # All admin users can manage everything for now
      can :manage, :all
    end
  end
end
