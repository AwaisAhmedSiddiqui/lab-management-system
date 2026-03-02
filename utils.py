"""
Utilities Module - Lab Management & Analytics System
Helper functions for validation, export, formatting, etc.
"""

import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
import re

# ==================== VALIDATION FUNCTIONS ====================

def validate_reference_no(reference_no):
    """Validate 14-digit reference number"""
    if not reference_no:
        return False, "Reference number is required"
    
    # Remove any spaces or dashes
    clean_ref = re.sub(r'[\s\-]', '', str(reference_no))
    
    if not clean_ref.isdigit():
        return False, "Reference number must contain only digits"
    
    if len(clean_ref) != 14:
        return False, f"Reference number must be exactly 14 digits (current: {len(clean_ref)} digits)"
    
    return True, clean_ref

def validate_numeric_field(value, field_name, allow_empty=True):
    """Validate numeric fields"""
    if not value and allow_empty:
        return True, 0
    
    try:
        num_value = float(value)
        return True, num_value
    except (ValueError, TypeError):
        return False, f"{field_name} must be a valid number"

# ==================== EXPORT FUNCTIONS ====================

def export_to_excel(df, filename="export"):
    """Export DataFrame to Excel"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
        
        # Auto-adjust column widths
        worksheet = writer.sheets['Data']
        for idx, col in enumerate(df.columns):
            max_length = max(
                df[col].astype(str).apply(len).max(),
                len(str(col))
            ) + 2
            worksheet.column_dimensions[chr(65 + idx)].width = min(max_length, 50)
    
    output.seek(0)
    return output

def export_to_pdf(df, title, filename="export"):
    """Export DataFrame to PDF"""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    
    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=landscape(letter), topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=20,
        alignment=1  # Center
    )
    elements.append(Paragraph(title, title_style))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Prepare data
    data = [df.columns.tolist()] + df.values.tolist()
    
    # Create table
    col_widths = [max(60, min(120, len(str(col)) * 8)) for col in df.columns]
    table = Table(data, colWidths=col_widths)
    
    # Style the table
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF4B4B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F5F5F5')),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F0F0')])
    ])
    table.setStyle(style)
    elements.append(table)
    
    doc.build(elements)
    output.seek(0)
    return output

def export_to_csv(df):
    """Export DataFrame to CSV"""
    return df.to_csv(index=False).encode('utf-8')

# ==================== FORMATTING FUNCTIONS ====================

def format_datetime(dt):
    """Format datetime for display"""
    if dt:
        if isinstance(dt, str):
            try:
                dt = datetime.fromisoformat(dt)
            except:
                return dt
        return dt.strftime('%d-%m-%Y %H:%M')
    return ''

def format_date(dt):
    """Format date for display"""
    if dt:
        if isinstance(dt, str):
            try:
                dt = datetime.fromisoformat(dt)
            except:
                return dt
        return dt.strftime('%d-%m-%Y')
    return ''

def format_number(num):
    """Format number for display"""
    if num is None:
        return '0'
    try:
        return f"{float(num):,.2f}"
    except:
        return str(num)

# ==================== UI HELPER FUNCTIONS ====================

def get_performa_list():
    """Get list of all performas"""
    return [
        'Data Retrieval Reports',
        'Lab Activity',
        'Special Checking in Lab',
        'Daily Checking Report',
        'Monthly Site Checking Report',
        'AMI MDI TCPs',
        'Audit Record',
        'Court Cases',
        'Log Book Record',
        'TA/DA Record'
    ]

def get_status_options():
    """Get status options"""
    return ['Active', 'Pending', 'Completed', 'Cancelled', 'Under Review']

def get_tariff_options():
    """Get tariff options"""
    return ['A-1', 'A-2', 'A-3', 'B-1', 'B-2', 'B-3', 'C-1', 'C-2', 'C-3', 'Industrial', 'Commercial', 'Domestic', 'Agriculture']

def get_sub_division_options():
    """Get sub-division options"""
    return [
        'Sub-Division 1',
        'Sub-Division 2', 
        'Sub-Division 3',
        'Sub-Division 4',
        'Sub-Division 5',
        'Sub-Division 6',
        'Sub-Division 7',
        'Sub-Division 8',
        'Sub-Division 9',
        'Sub-Division 10'
    ]

def apply_custom_css(theme):
    """Apply custom CSS based on theme settings"""
    css = f"""
    <style>
        :root {{
            --bg: {theme.get('background_color', '#0E1117')};
            --sidebar: {theme.get('sidebar_color', '#262730')};
            --text: {theme.get('text_color', '#FAFAFA')};
            --card: {theme.get('card_color', '#1E1E1E')};
            --primary: {theme.get('primary_color', '#FF4B4B')};
        }}

        /* Main background */
        .stApp {{
            background:
                radial-gradient(circle at 20% 0%, {theme.get('primary_color', '#FF4B4B')}22 0%, transparent 28%),
                radial-gradient(circle at 80% 100%, {theme.get('primary_color', '#FF4B4B')}1A 0%, transparent 30%),
                var(--bg);
        }}

        .block-container {{
            padding-top: 1rem;
            padding-bottom: 1.2rem;
        }}
        
        /* Sidebar */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, var(--sidebar), {theme.get('background_color', '#0E1117')});
            border-right: 1px solid {theme.get('primary_color', '#FF4B4B')}33;
        }}
        
        /* Text color */
        .stApp, .stApp p, .stApp span, .stApp label {{
            color: var(--text);
        }}
        
        /* Cards and containers */
        div[data-testid="stMetric"] {{
            background: linear-gradient(180deg, var(--card), {theme.get('background_color', '#0E1117')});
            padding: 1rem;
            border-radius: 12px;
            border: 1px solid {theme.get('primary_color', '#FF4B4B')}26;
            box-shadow: 0 6px 18px rgba(0, 0, 0, 0.18);
            transition: transform 0.18s ease, box-shadow 0.18s ease;
        }}

        div[data-testid="stMetric"]:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 22px rgba(0, 0, 0, 0.26);
        }}
        
        /* Primary color for buttons and accents */
        .stButton > button {{
            background: linear-gradient(135deg, var(--primary), {theme.get('primary_color', '#FF4B4B')}CC);
            color: white;
            border: 1px solid {theme.get('primary_color', '#FF4B4B')}80;
            border-radius: 10px;
            padding: 0.55rem 1rem;
            font-weight: 600;
            transition: transform 0.18s ease, box-shadow 0.18s ease, filter 0.18s ease;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 8px 20px {theme.get('primary_color', '#FF4B4B')}55;
            filter: brightness(1.05);
        }}

        .stButton > button:active {{
            transform: translateY(0);
        }}
        
        /* Remove number input spinners */
        input[type="number"]::-webkit-inner-spin-button,
        input[type="number"]::-webkit-outer-spin-button {{
            -webkit-appearance: none;
            margin: 0;
        }}
        input[type="number"] {{
            -moz-appearance: textfield;
        }}
        
        /* Custom metric cards */
        .metric-card {{
            background: linear-gradient(180deg, var(--card), {theme.get('background_color', '#0E1117')});
            border-radius: 12px;
            padding: 1.5rem;
            margin: 0.45rem 0;
            border: 1px solid {theme.get('primary_color', '#FF4B4B')}2E;
            border-left: 4px solid var(--primary);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.18);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}

        .metric-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 24px rgba(0, 0, 0, 0.24);
        }}
        
        /* Table styling */
        div[data-testid="stDataFrame"],
        .dataframe {{
            background: linear-gradient(180deg, var(--card), {theme.get('background_color', '#0E1117')});
            border-radius: 12px;
            border: 1px solid {theme.get('primary_color', '#FF4B4B')}22;
        }}
        
        /* Header styling */
        .main-header {{
            background: linear-gradient(100deg, var(--primary), {theme.get('primary_color', '#FF4B4B')}AA 52%, {theme.get('primary_color', '#FF4B4B')}70 100%);
            padding: 1.1rem 1.4rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 24px {theme.get('primary_color', '#FF4B4B')}3D;
        }}

        .main-header h1, .main-header p {{
            margin: 0;
            color: #FFFFFF;
        }}

        .main-header p {{
            opacity: 0.92;
            margin-top: 0.2rem;
        }}
        
        /* Status badges */
        .status-active {{ background: #28a745; color: white; padding: 2px 8px; border-radius: 4px; }}
        .status-pending {{ background: #ffc107; color: black; padding: 2px 8px; border-radius: 4px; }}
        .status-completed {{ background: #17a2b8; color: white; padding: 2px 8px; border-radius: 4px; }}
        .status-locked {{ background: #dc3545; color: white; padding: 2px 8px; border-radius: 4px; }}
        
        /* Mobile responsive */
        @media (max-width: 768px) {{
            .row-widget.stHorizontal {{
                flex-direction: column;
            }}
            
            .metric-card {{
                padding: 1rem;
            }}
        }}
        
        /* Sidebar navigation items */
        .nav-item {{
            padding: 0.75rem 1rem;
            margin: 0.25rem 0;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .nav-item:hover {{
            background: {theme.get('primary_color', '#FF4B4B')}33;
        }}
        
        .nav-item.active {{
            background: {theme.get('primary_color', '#FF4B4B')};
            color: white;
        }}
        
        /* Form styling */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > div,
        .stTextArea > div > div > textarea {{
            background-color: var(--card);
            border: 1px solid {theme.get('primary_color', '#FF4B4B')}33;
            border-radius: 10px;
        }}

        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {{
            border-color: var(--primary);
            box-shadow: 0 0 0 1px var(--primary);
        }}
        
        /* Locked record indicator */
        .locked-indicator {{
            background: #dc3545;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }}
        
        /* Activity log item */
        .activity-item {{
            background: var(--card);
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            border-left: 3px solid var(--primary);
        }}

        hr {{
            border: none;
            height: 1px;
            background: linear-gradient(90deg, transparent, {theme.get('primary_color', '#FF4B4B')}44, transparent);
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def show_metric_card(title, value, icon="📊", delta=None):
    """Display a custom metric card"""
    delta_html = ""
    if delta:
        color = "#28a745" if delta > 0 else "#dc3545"
        delta_html = f'<span style="color: {color}; font-size: 0.9rem;">{"+" if delta > 0 else ""}{delta}</span>'
    
    st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.9rem; color: #888; margin-bottom: 0.5rem;">{icon} {title}</div>
            <div style="font-size: 2rem; font-weight: bold;">{value}</div>
            {delta_html}
        </div>
    """, unsafe_allow_html=True)

def show_status_badge(status, is_locked=False):
    """Display status badge"""
    if is_locked:
        return '<span class="status-locked">🔒 Locked</span>'
    
    status_classes = {
        'Active': 'status-active',
        'Pending': 'status-pending',
        'Completed': 'status-completed'
    }
    css_class = status_classes.get(status, 'status-active')
    return f'<span class="{css_class}">{status}</span>'

def create_data_entry_form(form_key, existing_data=None, is_locked=False):
    """Create standardized data entry form"""
    data = existing_data or {}
    
    col1, col2 = st.columns(2)
    
    with col1:
        sub_division = st.selectbox(
            "Sub-Division *",
            options=[''] + get_sub_division_options(),
            index=0 if not data.get('sub_division') else get_sub_division_options().index(data.get('sub_division')) + 1 if data.get('sub_division') in get_sub_division_options() else 0,
            key=f"{form_key}_sub_division",
            disabled=is_locked
        )
        
        reference_no = st.text_input(
            "Reference No * (14 digits)",
            value=data.get('reference_no', ''),
            max_chars=14,
            key=f"{form_key}_reference_no",
            disabled=is_locked,
            help="Enter exactly 14 digits"
        )
        
        name = st.text_input(
            "Name *",
            value=data.get('name', ''),
            key=f"{form_key}_name",
            disabled=is_locked
        )
        
        tariff = st.selectbox(
            "Tariff",
            options=[''] + get_tariff_options(),
            index=0 if not data.get('tariff') else get_tariff_options().index(data.get('tariff')) + 1 if data.get('tariff') in get_tariff_options() else 0,
            key=f"{form_key}_tariff",
            disabled=is_locked
        )
        
        load_val = st.text_input(
            "Load",
            value=data.get('load', ''),
            key=f"{form_key}_load",
            disabled=is_locked
        )
        
        meter_no = st.text_input(
            "Meter No",
            value=data.get('meter_no', ''),
            key=f"{form_key}_meter_no",
            disabled=is_locked
        )
        
        make = st.text_input(
            "Make",
            value=data.get('make', ''),
            key=f"{form_key}_make",
            disabled=is_locked
        )
    
    with col2:
        mco_no = st.text_input(
            "MCO No",
            value=data.get('mco_no', ''),
            key=f"{form_key}_mco_no",
            disabled=is_locked
        )
        
        mco_date = st.date_input(
            "MCO Date",
            value=datetime.strptime(data['mco_date'], '%Y-%m-%d').date() if data.get('mco_date') else None,
            key=f"{form_key}_mco_date",
            disabled=is_locked
        )
        
        bill_reading = st.text_input(
            "Bill Reading",
            value=str(data.get('bill_reading', '')),
            key=f"{form_key}_bill_reading",
            disabled=is_locked
        )
        
        meter_reading = st.text_input(
            "Meter Reading",
            value=str(data.get('meter_reading', '')),
            key=f"{form_key}_meter_reading",
            disabled=is_locked
        )
        
        # Auto-calculate difference
        try:
            bill_val = float(bill_reading) if bill_reading else 0
            meter_val = float(meter_reading) if meter_reading else 0
            difference = meter_val - bill_val
        except:
            difference = 0
        
        st.text_input(
            "Difference (Auto-calculated)",
            value=f"{difference:.2f}",
            key=f"{form_key}_difference",
            disabled=True
        )
        
        status = st.selectbox(
            "Status",
            options=get_status_options(),
            index=get_status_options().index(data.get('status')) if data.get('status') in get_status_options() else 0,
            key=f"{form_key}_status",
            disabled=is_locked
        )
        
        remarks = st.text_area(
            "Remarks",
            value=data.get('remarks', ''),
            key=f"{form_key}_remarks",
            disabled=is_locked
        )
    
    return {
        'sub_division': sub_division,
        'reference_no': reference_no,
        'name': name,
        'tariff': tariff,
        'load': load_val,
        'meter_no': meter_no,
        'make': make,
        'mco_no': mco_no,
        'mco_date': str(mco_date) if mco_date else None,
        'bill_reading': bill_reading,
        'meter_reading': meter_reading,
        'status': status,
        'remarks': remarks
    }

def show_records_table(records, show_actions=True, on_edit=None, on_delete=None, on_print=None, on_unlock=None, is_admin=False):
    """Display records in a formatted table with actions"""
    if not records:
        st.info("No records found.")
        return
    
    # Convert to DataFrame for display
    df = pd.DataFrame(records)
    
    # Select columns for display
    display_cols = ['s_no', 'sub_division', 'reference_no', 'name', 'tariff', 'load', 
                   'meter_no', 'make', 'mco_no', 'mco_date', 'bill_reading', 
                   'meter_reading', 'difference', 'status', 'remarks']
    
    available_cols = [col for col in display_cols if col in df.columns]
    
    # Rename columns for display
    col_names = {
        's_no': 'S.No',
        'sub_division': 'Sub-Division',
        'reference_no': 'Reference No',
        'name': 'Name',
        'tariff': 'Tariff',
        'load': 'Load',
        'meter_no': 'Meter No',
        'make': 'Make',
        'mco_no': 'MCO No',
        'mco_date': 'MCO Date',
        'bill_reading': 'Bill Reading',
        'meter_reading': 'Meter Reading',
        'difference': 'Difference',
        'status': 'Status',
        'remarks': 'Remarks'
    }
    
    display_df = df[available_cols].rename(columns=col_names)
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    if show_actions:
        st.markdown("---")
        st.markdown("### Record Actions")
        
        for idx, record in enumerate(records):
            with st.expander(f"Record #{record.get('s_no', idx+1)} - {record.get('name', 'N/A')} ({record.get('reference_no', 'N/A')})"):
                is_locked = record.get('is_locked', False)
                
                if is_locked:
                    st.markdown('<span class="locked-indicator">🔒 This record is locked</span>', unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if not is_locked or is_admin:
                        if st.button("✏️ Edit", key=f"edit_{record['id']}_{idx}"):
                            if on_edit:
                                on_edit(record)
                
                with col2:
                    if is_admin:
                        if st.button("🗑️ Delete", key=f"delete_{record['id']}_{idx}"):
                            if on_delete:
                                on_delete(record)
                
                with col3:
                    if st.button("🖨️ Print", key=f"print_{record['id']}_{idx}"):
                        if on_print:
                            on_print(record)
                
                with col4:
                    if is_admin and is_locked:
                        if st.button("🔓 Unlock", key=f"unlock_{record['id']}_{idx}"):
                            if on_unlock:
                                on_unlock(record)

def generate_print_html(record, performa_name):
    """Generate printable HTML for a record"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{performa_name} - Print</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; }}
            .header {{ text-align: center; border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 20px; }}
            .header h1 {{ margin: 0; color: #FF4B4B; }}
            .record-table {{ width: 100%; border-collapse: collapse; }}
            .record-table th, .record-table td {{ 
                border: 1px solid #ddd; 
                padding: 10px; 
                text-align: left; 
            }}
            .record-table th {{ background: #FF4B4B; color: white; }}
            .footer {{ margin-top: 30px; text-align: center; color: #888; font-size: 0.9rem; }}
            @media print {{
                body {{ padding: 0; }}
                .no-print {{ display: none; }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Lab Management & Analytics System</h1>
            <h2>{performa_name}</h2>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <table class="record-table">
            <tr><th>S.No</th><td>{record.get('s_no', '')}</td></tr>
            <tr><th>Sub-Division</th><td>{record.get('sub_division', '')}</td></tr>
            <tr><th>Reference No</th><td>{record.get('reference_no', '')}</td></tr>
            <tr><th>Name</th><td>{record.get('name', '')}</td></tr>
            <tr><th>Tariff</th><td>{record.get('tariff', '')}</td></tr>
            <tr><th>Load</th><td>{record.get('load', '')}</td></tr>
            <tr><th>Meter No</th><td>{record.get('meter_no', '')}</td></tr>
            <tr><th>Make</th><td>{record.get('make', '')}</td></tr>
            <tr><th>MCO No</th><td>{record.get('mco_no', '')}</td></tr>
            <tr><th>MCO Date</th><td>{record.get('mco_date', '')}</td></tr>
            <tr><th>Bill Reading</th><td>{record.get('bill_reading', 0)}</td></tr>
            <tr><th>Meter Reading</th><td>{record.get('meter_reading', 0)}</td></tr>
            <tr><th>Difference</th><td>{record.get('difference', 0)}</td></tr>
            <tr><th>Status</th><td>{record.get('status', '')}</td></tr>
            <tr><th>Remarks</th><td>{record.get('remarks', '')}</td></tr>
        </table>
        
        <div class="footer">
            <p>Lab Management & Analytics System - Confidential Document</p>
        </div>
        
        <script>window.print();</script>
    </body>
    </html>
    """
    return html
