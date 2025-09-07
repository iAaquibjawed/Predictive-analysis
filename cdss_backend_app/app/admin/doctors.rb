ActiveAdmin.register Doctor do
    menu parent: "Medical Staff", priority: 1

    permit_params :name, :specialty, :phone_number, :email, :address

    # Filters
    filter :name
    filter :specialty
    filter :email
    filter :created_at

    # Index
    index do
        selectable_column
        id_column
        column :name do |doctor|
        link_to doctor.name, admin_doctor_path(doctor)
        end
        column :specialty
        column :phone_number
        column :email
        column :created_at
        actions
    end

    # Show
    show do
        attributes_table do
        row :name
        row :specialty
        row :phone_number
        row :email
        row :address
        row :created_at
        end

        # Patients Panel
        panel "Assigned Patients" do
        table_for resource.patients.limit(10) do
            column :id do |patient|
            link_to patient.id, admin_patient_path(patient)
            end
            column :name
            column :nhs_number
            column :date_of_birth
            column :created_at
        end
        div do
            link_to "View All Patients", admin_patients_path(q: { doctor_id_eq: resource.id })
        end
        end
    end

    # Form
    form do |f|


        f.inputs "Doctor Details" do
        f.input :name, required: true
        f.input :specialty, as: :select, collection: [ "General Practitioner", "Cardiologist", "Dermatologist", "Neurologist", "Pediatrician", "Psychiatrist", "Radiologist", "Surgeon", "Other" ], include_blank: false
        f.input :phone_number
        f.input :email, required: true
        f.input :address, as: :text
        end

        f.actions
    end

    # Controller Customization for Ransack Searchable Attributes
    controller do
        def scoped_collection
        super.ransack(params[:q]).result(distinct: true)
        end
    end
end