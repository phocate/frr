from datetime import datetime
from src.db import db

# Agency-Committee mapping table
agency_committee = db.Table('agency_committee',
    db.Column('agency_id', db.Integer, db.ForeignKey('agency.id'), primary_key=True),
    db.Column('committee_id', db.Integer, db.ForeignKey('committee.id'), primary_key=True)
)

class Agency(db.Model):
    """Model for federal agencies"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    abbreviation = db.Column(db.String(20))
    description = db.Column(db.Text)
    
    regulations = db.relationship('Regulation', backref='agency', lazy='dynamic')
    committees = db.relationship('Committee', secondary=agency_committee,
                               backref=db.backref('agencies', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Agency {self.abbreviation or self.name}>'

class Committee(db.Model):
    """Model for congressional committees"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Committee {self.name}>'

class Regulation(db.Model):
    """Model for regulations"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    rin = db.Column(db.String(20), unique=True)
    agency_id = db.Column(db.Integer, db.ForeignKey('agency.id'))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    stages = db.relationship('RuleStage', backref='regulation', lazy='dynamic')
    documents = db.relationship('Document', backref='regulation', lazy='dynamic')
    
    def __repr__(self):
        return f'<Regulation {self.rin}: {self.title[:30]}...>'
    
    def current_stage(self):
        """Get the current stage of the regulation"""
        stages = self.stages.order_by(RuleStage.publication_date.desc()).all()
        if not stages:
            return None
        
        # Check for Final Rule
        final_stages = [s for s in stages if s.stage_type == 'Final']
        if final_stages:
            return final_stages[0]
        
        # Check for NPRM
        nprm_stages = [s for s in stages if s.stage_type == 'NPRM']
        if nprm_stages:
            return nprm_stages[0]
        
        # Check for ANPRM
        anprm_stages = [s for s in stages if s.stage_type == 'ANPRM']
        if anprm_stages:
            return anprm_stages[0]
        
        # Default to most recent stage
        return stages[0]

class RuleStage(db.Model):
    """Model for stages in the rulemaking process"""
    id = db.Column(db.Integer, primary_key=True)
    regulation_id = db.Column(db.Integer, db.ForeignKey('regulation.id'))
    stage_type = db.Column(db.String(20), nullable=False)  # ANPRM, NPRM, or Final
    publication_date = db.Column(db.Date)
    federal_register_id = db.Column(db.String(100))
    comment_end_date = db.Column(db.Date)
    
    def __repr__(self):
        return f'<RuleStage {self.stage_type} for Regulation {self.regulation_id}>'

class Document(db.Model):
    """Model for documents related to regulations"""
    id = db.Column(db.Integer, primary_key=True)
    regulation_id = db.Column(db.Integer, db.ForeignKey('regulation.id'))
    title = db.Column(db.String(255), nullable=False)
    document_type = db.Column(db.String(100))
    url = db.Column(db.String(255))
    publication_date = db.Column(db.Date)
    source = db.Column(db.String(50))  # federalregister.gov or regulations.gov
    
    def __repr__(self):
        return f'<Document {self.title[:30]}... for Regulation {self.regulation_id}>'
