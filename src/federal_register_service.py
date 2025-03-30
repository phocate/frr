import requests
import logging
from datetime import datetime
from flask import current_app
from src.db import db
from src.models import Agency, Regulation, RuleStage, Document

class FederalRegisterService:
    """Service for interacting with the Federal Register API"""
    BASE_URL = "https://www.federalregister.gov/api/v1"
    
    def __init__(self):
       pass 
    def search_documents(self, params=None):
        """
        Search for documents in the Federal Register
        
        params: dict of query parameters
        """
        endpoint = f"{self.BASE_URL}/documents"
        default_params = {
            'fields[]': ['title', 'type', 'document_number', 'publication_date', 
                         'agencies', 'rin', 'docket_ids', 'abstract'],
            'per_page': 20,
            'order': 'newest'
        }
        
        # Combine default params with custom params
        if params:
            default_params.update(params)
            
        try:
            response = requests.get(endpoint, params=default_params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching data from Federal Register API: {e}")
            return None
            
    def sync_data(self):
        """Sync data from Federal Register API to database"""
        # Fetch documents with type 'RULE' or 'PRORULE' or 'PROPOSED RULE'
        params = {
            'conditions[type][]': ['RULE', 'PRORULE', 'PROPOSED RULE'],
            'per_page': 50
        }
        
        results = self.search_documents(params)
        
        if not results:
            return "No results found or API error occurred."
        
        processed_count = 0
        
        for doc in results.get('results', []):
            # Process each document
            rin = doc.get('rin', '')
            
            if not rin:
                continue
                
            # Find or create agency
            agency_data = doc.get('agencies', [{}])[0]
            agency = Agency.query.filter_by(name=agency_data.get('name')).first()
            
            if not agency:
                agency = Agency(
                    name=agency_data.get('name'),
                    abbreviation=agency_data.get('acronym', '')
                )
                db.session.add(agency)
                db.session.commit()
            
            # Find or create regulation
            regulation = Regulation.query.filter_by(rin=rin).first()
            
            if not regulation:
                regulation = Regulation(
                    title=doc.get('title'),
                    rin=rin,
                    agency=agency,
                    description=doc.get('abstract')
                )
                db.session.add(regulation)
                db.session.commit()
            
            # Determine stage type
            doc_type = doc.get('type')
            stage_type = None
            
            if doc_type == 'PRORULE' or doc_type == 'PROPOSED RULE':
                stage_type = 'NPRM'
            elif doc_type == 'RULE':
                stage_type = 'Final'
            else:
                # Assume ANPRM for other types
                stage_type = 'ANPRM'
            
            if stage_type:
                # Parse publication date
                publication_date = None
                if doc.get('publication_date'):
                    try:
                        publication_date = datetime.strptime(
                            doc.get('publication_date'), '%Y-%m-%d'
                        ).date()
                    except ValueError:
                        pass
                
                # Check if this stage already exists
                document_number = doc.get('document_number')
                existing_stage = RuleStage.query.filter_by(
                    regulation=regulation,
                    federal_register_id=document_number
                ).first()
                
                if not existing_stage:
                    stage = RuleStage(
                        regulation=regulation,
                        stage_type=stage_type,
                        publication_date=publication_date,
                        federal_register_id=document_number
                    )
                    db.session.add(stage)
                    
                    # Also add document
                    document = Document(
                        regulation=regulation,
                        title=f"{stage_type} Document",
                        document_type=stage_type,
                        url=doc.get('html_url'),
                        publication_date=publication_date,
                        source='federalregister.gov'
                    )
                    db.session.add(document)
                    
                    processed_count += 1
            
            db.session.commit()
        
        return f"Sync completed. Processed {processed_count} new documents."
