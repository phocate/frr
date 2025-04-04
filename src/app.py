from flask import Flask, render_template
import requests
from flask_wtf.csrf import CSRFProtect
from forms import RegulationSearchForm
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
csrf = CSRFProtect(app)

# Federal Register API configuration
FR_API_BASE_URL = "https://www.federalregister.gov/api/v1"

# Simple mapping of committees to agencies 
COMMITTEE_AGENCY_MAPPING = {
    "commerce": ["federal-trade-commission", "federal-communications-commission"],
    "agriculture": ["agriculture-department"],
    "transportation": ["transportation-department"]
}

@app.route('/', methods=['GET', 'POST'])
def index():
    """Main page with search form and results"""
    form = RegulationSearchForm()
    results = []
    total_count = 0
    error_message = None
    
    # If form is submitted and valid
    if form.validate_on_submit():
        try:
            # Get form data
            search_query = form.q.data or ''
            agency = form.agency.data or ''
            committee = form.committee.data or ''
            stage = form.status.data or ''
            date_range = form.date.data or ''
            
            # Build search parameters for Federal Register API
            conditions = {}
            
            # Handle agency or committee filter
            if committee and committee in COMMITTEE_AGENCY_MAPPING:
                conditions['agencies'] = COMMITTEE_AGENCY_MAPPING[committee]
            elif agency:
                conditions['agencies'] = [agency]
            
            # Handle date range filter
            if date_range:
                days = int(date_range)
                start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
                conditions['publication_date[gte]'] = start_date
            
            # Handle document type (rulemaking stage) filter
            if stage:
                doc_types = []
                if stage == 'nprm':
                    doc_types = ['PRORULE']
                elif stage == 'final':
                    doc_types = ['RULE']
                
                if doc_types:
                    conditions['type'] = doc_types
            else:
                # Default to show all rulemaking documents
                conditions['type'] = ['RULE', 'PRORULE']
            
            # Build search parameters
            params = {}
            for key, value in conditions.items():
                if isinstance(value, list):
                    for val in value:
                        params_key = f'conditions[{key}][]'
                        if params_key in params:
                            if isinstance(params[params_key], list):
                                params[params_key].append(val)
                            else:
                                params[params_key] = [params[params_key], val]
                        else:
                            params[params_key] = val
                else:
                    params[f'conditions[{key}]'] = value
            
            # Add text search if provided
            if search_query:
                params['conditions[term]'] = search_query
            
            # Add pagination
            params['page'] = 1
            params['per_page'] = 10
            params['format'] = 'json'
            
            # Make API request to Federal Register
            response = requests.get(f"{FR_API_BASE_URL}/documents", params=params)
            response.raise_for_status()
            data = response.json()
            
            # Process results
            results = process_federal_register_results(data.get('results', []))
            total_count = data.get('count', 0)
            
        except requests.exceptions.RequestException as e:
            error_message = f"Error fetching data from Federal Register API: {str(e)}"
        except Exception as e:
            error_message = f"An unexpected error occurred: {str(e)}"
    
    return render_template(
        'index.html', 
        form=form, 
        results=results, 
        total_count=total_count,
        error_message=error_message
    )

def process_federal_register_results(results):
    """Process Federal Register API results to a simplified format"""
    processed_results = []
    
    for item in results:
        # Determine rulemaking stage based on document type
        doc_type = item.get('type', '')
        stage = {
            'Proposed Rule': 'Notice of Proposed Rulemaking (NPRM)',
            'Rule': 'Final Rule',
        }.get(doc_type, doc_type)
        
        # Extract agency name
        agency = ''
        agencies = item.get('agencies', [])
        if agencies and isinstance(agencies, list) and len(agencies) > 0:
            agency = agencies[0].get('name', '')
        
        # Extract committee information (simplified mapping)
        committee = 'Unknown'
        if agencies and isinstance(agencies, list) and len(agencies) > 0:
            agency_slug = agencies[0].get('slug', '').lower()
            
            for comm, agency_list in COMMITTEE_AGENCY_MAPPING.items():
                if agency_slug in agency_list:
                    committee = comm.capitalize()
                    if committee == 'Commerce':
                        committee = 'Energy & Commerce'
                    elif committee == 'Transportation':
                        committee = 'Transportation & Infrastructure'
                    break
        
        # Create processed result
        processed_item = {
            'id': item.get('document_number', ''),
            'title': item.get('title', ''),
            'agency': agency,
            'committee': committee,
            'stage': stage,
            'publication_date': item.get('publication_date', ''),
            'abstract': item.get('abstract', ''),
            'html_url': item.get('html_url', ''),
            'pdf_url': item.get('pdf_url', '')
        }
        
        processed_results.append(processed_item)
    
    return processed_results

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0")
