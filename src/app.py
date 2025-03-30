from flask import Flask, render_template, request, jsonify
import os
from src.app_config import get_config
from src.db import init_db, db
from src.models import Agency, Committee, Regulation, RuleStage, Document

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__,
                static_folder='../static',
                template_folder='../templates')
    
    # Load configuration
    app.config.from_object(get_config())
    
    # Initialize database
    init_db(app)
    
    # Register blueprints and routes
    register_routes(app)
    
    return app

def register_routes(app):
    """Register application routes"""
    
    @app.route('/')
    def index():
        # Fetch agencies and committees for filter dropdowns
        agencies = Agency.query.all()
        committees = Committee.query.all()
        return render_template('index.html', agencies=agencies, committees=committees)
    
    @app.route('/regulations')
    def regulations():
        """API endpoint for fetching regulations with filters"""
        agency_id = request.args.get('agency')
        committee_id = request.args.get('committee')
        stage = request.args.get('stage')
        search_query = request.args.get('query')
        
        # Build query
        query = Regulation.query
        
        if agency_id:
            query = query.filter_by(agency_id=agency_id)
        
        if committee_id:
            query = query.join(Agency).join(
                Agency.committees).filter(Committee.id == committee_id)
        
        if search_query:
            query = query.filter(Regulation.title.like(f'%{search_query}%'))
        
        # Execute query with pagination
        page = request.args.get('page', 1, type=int)
        per_page = app.config.get('ITEMS_PER_PAGE', 10)
        pagination = query.paginate(page=page, per_page=per_page)
        
        # Format results
        regulations = []
        for reg in pagination.items:
            reg_data = {
                'id': reg.id,
                'title': reg.title,
                'rin': reg.rin,
                'agency': reg.agency.name if reg.agency else 'Unknown',
                'stages': [],
                'documents': []
            }
            
            # Add stages
            for stage in reg.stages:
                reg_data['stages'].append({
                    'type': stage.stage_type,
                    'date': stage.publication_date.strftime('%Y-%m-%d') if stage.publication_date else None
                })
            
            # Add documents
            for doc in reg.documents:
                reg_data['documents'].append({
                    'title': doc.title,
                    'type': doc.document_type,
                    'url': doc.url
                })
            
            regulations.append(reg_data)
        
        return jsonify({
            'regulations': regulations,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page
        })
    
    @app.route('/regulation/<rin>')
    def regulation_detail(rin):
        """Detailed view for a specific regulation"""
        regulation = Regulation.query.filter_by(rin=rin).first_or_404()
        return render_template('regulation_detail.html', regulation=regulation)
    
    @app.route('/sync')
    def sync_data():
        """Endpoint to trigger data synchronization (for development)"""
        if app.config.get('DEBUG'):
            # This would be a command in production
            # Just a simple route for development
            from src.services.federal_register_service import FederalRegisterService
            fr_service = FederalRegisterService()
            result = fr_service.sync_data()
            return jsonify({"status": "success", "message": result})
        return jsonify({"status": "error", "message": "Only available in debug mode"})
    
    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

# Create the application instance
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=app.config.get('DEBUG', False))
