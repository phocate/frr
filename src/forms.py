from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import Optional

class RegulationSearchForm(FlaskForm):
    """Form for searching regulations"""
    
    # Text search field
    q = StringField('Search Keywords', validators=[Optional()])
    
    # Agency dropdown
    agency = SelectField('Agency', choices=[
        ('', 'All Agencies'),
        ('federal-trade-commission', 'Federal Trade Commission'),
        ('transportation-department', 'Department of Transportation'),
        ('federal-communications-commission', 'Federal Communications Commission')
    ], validators=[Optional()])
    
    # Committee dropdown
    committee = SelectField('Committee of Jurisdiction', choices=[
        ('', 'All Committees'),
        ('commerce', 'Energy & Commerce'),
        ('agriculture', 'Agriculture'),
        ('transportation', 'Transportation & Infrastructure')
    ], validators=[Optional()])
    
    # Rulemaking stage dropdown
    status = SelectField('Rulemaking Stage', choices=[
        ('', 'All Stages'),
        ('nprm', 'Notice of Proposed Rulemaking'),
        ('final', 'Final Rule')
    ], validators=[Optional()])
    
    # Date range dropdown
    date = SelectField('Date Range', choices=[
        ('', 'All Time'),
        ('30', 'Last 30 days'),
        ('90', 'Last 90 days'),
        ('365', 'Last year')
    ], validators=[Optional()])
    
    # Submit button
    submit = SubmitField('Search Regulations')
