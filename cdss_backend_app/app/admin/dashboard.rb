ActiveAdmin.register_page "Dashboard" do
  menu priority: 1, label: proc { I18n.t("active_admin.dashboard") }

  content title: proc { I18n.t("active_admin.dashboard") } do
    div class: "blank_slate_container", id: "dashboard_default_message" do
      span class: "blank_slate" do
        span "Welcome to CDSS Admin"
        small "Clinical Decision Support System Administration"
      end
    end

    # System Overview Section
    panel "System Overview" do
      columns do
        column do
          attributes_table_for nil do
            row("Total Patients") { Patient.count }
            row("Active Users") { User.active.count }
            row("Total Prescriptions") { Prescription.count }
            row("Active Drugs") { Drug.active.count }
          end
        end

        column do
          attributes_table_for nil do
            row("Today's Records") { MedicalRecord.where(visit_date: Date.current).count }
            row("Drug Alerts") { DrugInteraction.high_risk.count }
            row("IoT Devices") { IoTReading.distinct.count(:device_id) }
            row("Audit Entries Today") { AuditLog.where(performed_at: Date.current.all_day).count }
          end
        end
      end
    end

    # Recent Activity Section
    panel "Recent Activity" do
      table_for AuditLog.includes(:user).limit(10).order(created_at: :desc) do
        column :performed_at
        column :user do |log|
          log.user_name
        end
        column :action
        column :resource_type
        column :ip_address
      end
    end
  end
end