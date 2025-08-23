class Api::V1::PatientsController < ApplicationController
  before_action :set_patient, only: [:show, :update, :destroy, :compliance_report, :drug_interactions]

  def index
    @patients = Patient.accessible_by(current_ability)
                       .includes(:user, :assigned_doctors)
                       .page(params[:page])

    render json: PatientSerializer.new(@patients).serializable_hash
  end

  def show
    render json: PatientSerializer.new(@patient, include: [:medical_records, :prescriptions]).serializable_hash
  end

  def create
    @patient = Patient.new(patient_params)

    if @patient.save
      render json: PatientSerializer.new(@patient).serializable_hash, status: :created
    else
      render json: { errors: @patient.errors }, status: :unprocessable_entity
    end
  end

  def update
    if @patient.update(patient_params)
      render json: PatientSerializer.new(@patient).serializable_hash
    else
      render json: { errors: @patient.errors }, status: :unprocessable_entity
    end
  end

  def compliance_report
    # Generate compliance report by calling ML service
    ml_response = MlApiService.new.generate_compliance_report(@patient.id)
    render json: ml_response
  end

  def drug_interactions
    # Check for drug interactions using ML service
    current_drugs = @patient.current_medications.map(&:drug)
    ml_response = MlApiService.new.check_drug_interactions(current_drugs.pluck(:id))
    render json: ml_response
  end

  private

  def set_patient
    @patient = Patient.find(params[:id])
    authorize! :read, @patient
  end

  def patient_params
    params.require(:patient).permit(:nhs_number, :date_of_birth, :gender, :address, :phone_number, :emergency_contact)
  end
end