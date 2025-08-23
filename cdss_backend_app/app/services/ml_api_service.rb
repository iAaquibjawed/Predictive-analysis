class MlApiService
  include HTTParty

  base_uri ENV.fetch('ML_API_URL', 'http://localhost:8001')

  def initialize
    @options = {
      headers: {
        'Content-Type' => 'application/json',
        'Authorization' => "Bearer #{ENV['ML_API_TOKEN']}"
      },
      timeout: 30
    }
  end

  def analyze_symptoms(symptoms_data)
    post('/api/v1/analyze_symptoms', symptoms_data)
  end

  def check_drug_interactions(drug_ids)
    post('/api/v1/drug_interactions', { drug_ids: drug_ids })
  end

  def generate_compliance_report(patient_id)
    get("/api/v1/compliance/#{patient_id}")
  end

  def forecast_demand(inventory_data)
    post('/api/v1/forecast/demand', inventory_data)
  end

  def get_treatment_recommendations(patient_data)
    post('/api/v1/recommendations', patient_data)
  end

  private

  def post(endpoint, data)
    response = self.class.post(endpoint, @options.merge(body: data.to_json))
    handle_response(response)
  end

  def get(endpoint)
    response = self.class.get(endpoint, @options)
    handle_response(response)
  end

  def handle_response(response)
    case response.code
    when 200..299
      JSON.parse(response.body)
    when 400..499
      { error: 'Client error', details: response.body }
    when 500..599
      { error: 'Server error', details: 'ML service unavailable' }
    else
      { error: 'Unknown error', details: response.body }
    end
  rescue JSON::ParserError
    { error: 'Invalid response format' }
  end
end