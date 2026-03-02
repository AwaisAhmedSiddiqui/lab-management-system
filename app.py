"""
Lab Management & Analytics System
Main Application Entry Point
Version: 1.0.0
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import base64

# Import custom modules
from database import (
    init_database, create_default_users, get_table_name,
    add_record, update_record, delete_record, lock_record, unlock_record,
    get_record_by_id, get_all_records, get_record_count, get_next_sno,
    log_activity, get_recent_activities, get_activities_filtered,
    get_unique_sessions, get_theme_settings, update_theme_settings,
    get_dashboard_stats, backup_database, get_all_users
)
from auth import (
    init_session_state, is_authenticated, is_admin, is_staff,
    get_current_user, get_session_id, show_login_page, show_user_info,
    can_add, can_edit, can_delete, can_unlock, can_view_logs,
    can_change_theme, logout
)
from utils import (
    validate_reference_no, apply_custom_css, get_performa_list,
    export_to_excel, export_to_pdf, export_to_csv, format_datetime,
    create_data_entry_form, generate_print_html, show_metric_card
)
from config import (
    APP_NAME, APP_VERSION, MENU_ITEMS, PERFORMAS,
    THEME_PRESETS, DEFAULT_THEME
)

# Page Configuration
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database and session
init_database()
create_default_users()
init_session_state()

# Apply theme
theme = get_theme_settings()
apply_custom_css(theme)

def main():
    """Main application function"""
    
    if not is_authenticated():
        show_login_page()
        return
    
    # Show sidebar navigation
    show_sidebar()
    
    # Route to appropriate page
    current_page = st.session_state.get('current_page', 'Dashboard')
    
    if current_page == 'Dashboard':
        show_dashboard()
    elif current_page in get_performa_list():
        show_performa_page(current_page)
    elif current_page == 'Activity Logs':
        show_activity_logs()
    elif current_page == 'Theme Settings':
        show_theme_settings()
    elif current_page == 'User Management':
        show_user_management()
    elif current_page == 'Database Backup':
        show_database_backup()
    else:
        show_dashboard()

def show_sidebar():
    """Display sidebar navigation"""
    with st.sidebar:
        st.markdown(f"""
            <div style="text-align: center; padding: 1rem;">
                <h2 style="margin: 0;">🔬 Lab Management</h2>
                <p style="color: #888; font-size: 0.8rem;">v{APP_VERSION}</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # User info
        show_user_info()
        
        # Main Navigation
        st.markdown("### 📌 Main")
        if st.button("🏠 Dashboard", use_container_width=True, 
                    type="primary" if st.session_state.current_page == 'Dashboard' else "secondary"):
            st.session_state.current_page = 'Dashboard'
            st.rerun()
        
        # Performas Navigation
        st.markdown("### 📋 Performas")
        for item in MENU_ITEMS['performas']:
            btn_type = "primary" if st.session_state.current_page == item['name'] else "secondary"
            if st.button(f"{item['icon']} {item['name']}", use_container_width=True, type=btn_type, key=f"nav_{item['name']}"):
                st.session_state.current_page = item['name']
                st.rerun()
        
        # Admin Only Navigation
        if is_admin():
            st.markdown("### ⚙️ Admin")
            for item in MENU_ITEMS['admin']:
                btn_type = "primary" if st.session_state.current_page == item['name'] else "secondary"
                if st.button(f"{item['icon']} {item['name']}", use_container_width=True, type=btn_type, key=f"nav_admin_{item['name']}"):
                    st.session_state.current_page = item['name']
                    st.rerun()
        
        st.markdown("---")
        
        # Logout Button
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()

def show_dashboard():
    """Display main dashboard"""
    st.markdown(f"""
        <div class="main-header">
            <h1>🏠 Dashboard</h1>
            <p>Welcome back, {get_current_user()['full_name']}!</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Get statistics
    stats = get_dashboard_stats()
    
    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Records", stats.get('total_records', 0))
    
    with col2:
        st.metric("📝 Today's Entries", stats.get('today_entries', 0))
    
    with col3:
        st.metric("👥 Active Users Today", stats.get('active_users_today', 0))
    
    with col4:
        st.metric("📋 Total Performas", len(PERFORMAS))
    
    st.markdown("---")
    
    # Admin: Show Recent Activities
    if is_admin():
        st.markdown("### 🔔 Last 10 User Activities")
        activities = get_recent_activities(10)
        
        if activities:
            activity_data = []
            for act in activities:
                activity_data.append({
                    'Date & Time': format_datetime(act['timestamp']),
                    'Username': act['username'],
                    'Performa': act['performa_name'],
                    'Action': act['action_type'],
                    'Reference No': act['reference_no'] or '-'
                })
            
            df = pd.DataFrame(activity_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No recent activities found.")
    
    st.markdown("---")
    
    # Performa Record Counts
    st.markdown("### 📊 Records by Performa")
    
    col1, col2 = st.columns(2)
    
    performa_list = list(PERFORMAS.keys())
    
    with col1:
        for performa in performa_list[:5]:
            count = stats.get(PERFORMAS[performa], 0)
            st.markdown(f"""
                <div class="metric-card">
                    <strong>{performa}</strong>
                    <div style="font-size: 1.5rem; color: {theme.get('primary_color', '#FF4B4B')};">{count}</div>
                </div>
            """, unsafe_allow_html=True)
    
    with col2:
        for performa in performa_list[5:]:
            count = stats.get(PERFORMAS[performa], 0)
            st.markdown(f"""
                <div class="metric-card">
                    <strong>{performa}</strong>
                    <div style="font-size: 1.5rem; color: {theme.get('primary_color', '#FF4B4B')};">{count}</div>
                </div>
            """, unsafe_allow_html=True)

def show_performa_page(performa_name):
    """Display performa data entry and management page"""
    table_name = get_table_name(performa_name)
    
    st.markdown(f"""
        <div class="main-header">
            <h1>📋 {performa_name}</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Initialize edit mode state
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False
    if 'edit_record_id' not in st.session_state:
        st.session_state.edit_record_id = None
    
    # Action tabs
    tab1, tab2, tab3 = st.tabs(["📋 View Records", "➕ Add New", "📊 Export"])
    
    with tab1:
        show_records_view(performa_name, table_name)
    
    with tab2:
        show_add_form(performa_name, table_name)
    
    with tab3:
        show_export_options(performa_name, table_name)

def show_records_view(performa_name, table_name):
    """Display records view with search and filters"""
    
    # Search and Filter Section
    st.markdown("### 🔍 Search & Filter")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_term = st.text_input("🔎 Search (Name, Meter No, Reference No)", key=f"search_{table_name}")
    
    with col2:
        start_date = st.date_input("📅 From Date", value=None, key=f"start_date_{table_name}")
    
    with col3:
        end_date = st.date_input("📅 To Date", value=None, key=f"end_date_{table_name}")
    
    # Get records
    records = get_all_records(
        table_name, 
        search_term=search_term if search_term else None,
        start_date=str(start_date) if start_date else None,
        end_date=str(end_date) if end_date else None
    )
    
    st.markdown(f"**Total Records: {len(records)}**")
    
    if not records:
        st.info("No records found. Add new records using the 'Add New' tab.")
        return
    
    # Display records in a table
    df = pd.DataFrame(records)
    
    # Select columns for display
    display_cols = ['s_no', 'sub_division', 'reference_no', 'name', 'tariff', 'load', 
                   'meter_no', 'bill_reading', 'meter_reading', 'difference', 'status', 'is_locked']
    
    available_cols = [col for col in display_cols if col in df.columns]
    display_df = df[available_cols].copy()
    
    # Rename columns
    col_names = {
        's_no': 'S.No', 'sub_division': 'Sub-Division', 'reference_no': 'Reference No',
        'name': 'Name', 'tariff': 'Tariff', 'load': 'Load', 'meter_no': 'Meter No',
        'bill_reading': 'Bill Reading', 'meter_reading': 'Meter Reading',
        'difference': 'Difference', 'status': 'Status', 'is_locked': 'Locked'
    }
    display_df = display_df.rename(columns=col_names)
    
    # Format locked column
    if 'Locked' in display_df.columns:
        display_df['Locked'] = display_df['Locked'].apply(lambda x: '🔒' if x else '🔓')
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Record Actions
    st.markdown("---")
    st.markdown("### ⚡ Record Actions")
    
    # Select record for action
    record_options = [f"#{r['s_no']} - {r['name']} ({r['reference_no']})" for r in records]
    selected_record = st.selectbox("Select Record", options=record_options, key=f"select_record_{table_name}")
    
    if selected_record:
        selected_idx = record_options.index(selected_record)
        record = records[selected_idx]
        is_locked = record.get('is_locked', False)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Edit button
            edit_allowed = is_admin() or (is_staff() and not is_locked)
            if st.button("✏️ Edit", disabled=not edit_allowed, key=f"edit_btn_{table_name}"):
                st.session_state[f'edit_record_{table_name}'] = record
                st.session_state[f'show_edit_form_{table_name}'] = True
                st.rerun()
        
        with col2:
            # Delete button (Admin only)
            if st.button("🗑️ Delete", disabled=not is_admin(), key=f"delete_btn_{table_name}"):
                if is_admin():
                    delete_record(table_name, record['id'])
                    log_activity(
                        username=get_current_user()['username'],
                        role=get_current_user()['role'],
                        session_id=get_session_id(),
                        performa_name=performa_name,
                        action_type='Delete',
                        reference_no=record['reference_no'],
                        record_id=record['id']
                    )
                    st.success("Record deleted successfully!")
                    st.rerun()
        
        with col3:
            # Print button
            if st.button("🖨️ Print", key=f"print_btn_{table_name}"):
                # Lock record after print (for staff)
                if is_staff() and not is_locked:
                    lock_record(table_name, record['id'])
                
                log_activity(
                    username=get_current_user()['username'],
                    role=get_current_user()['role'],
                    session_id=get_session_id(),
                    performa_name=performa_name,
                    action_type='Print',
                    reference_no=record['reference_no'],
                    record_id=record['id']
                )
                
                # Generate print HTML
                print_html = generate_print_html(record, performa_name)
                b64 = base64.b64encode(print_html.encode()).decode()
                href = f'<a href="data:text/html;base64,{b64}" target="_blank">🖨️ Click here to Print</a>'
                st.markdown(href, unsafe_allow_html=True)
                st.success("Print document generated! Record has been locked.")
        
        with col4:
            # Unlock button (Admin only)
            if is_locked and is_admin():
                if st.button("🔓 Unlock", key=f"unlock_btn_{table_name}"):
                    unlock_record(table_name, record['id'])
                    log_activity(
                        username=get_current_user()['username'],
                        role=get_current_user()['role'],
                        session_id=get_session_id(),
                        performa_name=performa_name,
                        action_type='Unlock',
                        reference_no=record['reference_no'],
                        record_id=record['id']
                    )
                    st.success("Record unlocked successfully!")
                    st.rerun()
    
    # Show edit form if active
    if st.session_state.get(f'show_edit_form_{table_name}', False):
        show_edit_form(performa_name, table_name)

def show_add_form(performa_name, table_name):
    """Display add new record form"""
    st.markdown("### ➕ Add New Record")
    
    with st.form(f"add_form_{table_name}"):
        form_data = create_data_entry_form(f"add_{table_name}")
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("💾 Save Record", use_container_width=True)
        with col2:
            save_print = st.form_submit_button("💾🖨️ Save & Print", use_container_width=True)
        
        if submit or save_print:
            # Validate reference number
            is_valid, result = validate_reference_no(form_data['reference_no'])
            
            if not is_valid:
                st.error(result)
                return
            
            form_data['reference_no'] = result
            
            # Validate required fields
            if not form_data.get('name'):
                st.error("Name is required!")
                return
            
            if not form_data.get('sub_division'):
                st.error("Sub-Division is required!")
                return
            
            # Add record
            record_id = add_record(table_name, form_data, get_current_user()['username'])
            
            # Log activity
            log_activity(
                username=get_current_user()['username'],
                role=get_current_user()['role'],
                session_id=get_session_id(),
                performa_name=performa_name,
                action_type='Add',
                reference_no=form_data['reference_no'],
                record_id=record_id
            )
            
            if save_print:
                # Lock record after save & print
                lock_record(table_name, record_id)
                
                log_activity(
                    username=get_current_user()['username'],
                    role=get_current_user()['role'],
                    session_id=get_session_id(),
                    performa_name=performa_name,
                    action_type='Print',
                    reference_no=form_data['reference_no'],
                    record_id=record_id
                )
                
                record = get_record_by_id(table_name, record_id)
                print_html = generate_print_html(record, performa_name)
                b64 = base64.b64encode(print_html.encode()).decode()
                href = f'<a href="data:text/html;base64,{b64}" target="_blank">🖨️ Click here to Print</a>'
                st.markdown(href, unsafe_allow_html=True)
                st.success("Record saved, printed and locked!")
            else:
                st.success("Record saved successfully!")
            
            st.rerun()

def show_edit_form(performa_name, table_name):
    """Display edit record form"""
    record = st.session_state.get(f'edit_record_{table_name}')
    
    if not record:
        return
    
    st.markdown("---")
    st.markdown("### ✏️ Edit Record")
    
    is_locked = record.get('is_locked', False)
    can_edit_record = is_admin() or (is_staff() and not is_locked)
    
    if is_locked and not is_admin():
        st.warning("🔒 This record is locked. Only Admin can edit locked records.")
        if st.button("❌ Cancel Edit", key="cancel_edit"):
            st.session_state[f'show_edit_form_{table_name}'] = False
            st.rerun()
        return
    
    with st.form(f"edit_form_{table_name}"):
        form_data = create_data_entry_form(f"edit_{table_name}", existing_data=record, is_locked=False)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            update_btn = st.form_submit_button("💾 Update Record", use_container_width=True)
        
        with col2:
            update_print = st.form_submit_button("💾🖨️ Update & Print", use_container_width=True)
        
        with col3:
            cancel_btn = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if cancel_btn:
            st.session_state[f'show_edit_form_{table_name}'] = False
            st.rerun()
        
        if update_btn or update_print:
            # Validate reference number
            is_valid, result = validate_reference_no(form_data['reference_no'])
            
            if not is_valid:
                st.error(result)
                return
            
            form_data['reference_no'] = result
            
            # Validate required fields
            if not form_data.get('name'):
                st.error("Name is required!")
                return
            
            # Update record
            update_record(table_name, record['id'], form_data, get_current_user()['username'])
            
            # Log activity
            log_activity(
                username=get_current_user()['username'],
                role=get_current_user()['role'],
                session_id=get_session_id(),
                performa_name=performa_name,
                action_type='Edit',
                reference_no=form_data['reference_no'],
                record_id=record['id']
            )
            
            if update_print:
                # Lock record after update & print
                lock_record(table_name, record['id'])
                
                log_activity(
                    username=get_current_user()['username'],
                    role=get_current_user()['role'],
                    session_id=get_session_id(),
                    performa_name=performa_name,
                    action_type='Print',
                    reference_no=form_data['reference_no'],
                    record_id=record['id']
                )
                
                updated_record = get_record_by_id(table_name, record['id'])
                print_html = generate_print_html(updated_record, performa_name)
                b64 = base64.b64encode(print_html.encode()).decode()
                href = f'<a href="data:text/html;base64,{b64}" target="_blank">🖨️ Click here to Print</a>'
                st.markdown(href, unsafe_allow_html=True)
                st.success("Record updated, printed and locked!")
            else:
                st.success("Record updated successfully!")
            
            st.session_state[f'show_edit_form_{table_name}'] = False
            st.rerun()

def show_export_options(performa_name, table_name):
    """Display export options"""
    st.markdown("### 📊 Export Data")
    
    # Filters
    col1, col2 = st.columns(2)
    
    with col1:
        export_start = st.date_input("From Date", value=None, key=f"export_start_{table_name}")
    
    with col2:
        export_end = st.date_input("To Date", value=None, key=f"export_end_{table_name}")
    
    # Get records
    records = get_all_records(
        table_name,
        start_date=str(export_start) if export_start else None,
        end_date=str(export_end) if export_end else None
    )
    
    st.info(f"📊 {len(records)} records will be exported")
    
    if not records:
        st.warning("No records to export.")
        return
    
    # Prepare DataFrame
    df = pd.DataFrame(records)
    
    # Select columns for export
    export_cols = ['s_no', 'sub_division', 'reference_no', 'name', 'tariff', 'load',
                  'meter_no', 'make', 'mco_no', 'mco_date', 'bill_reading',
                  'meter_reading', 'difference', 'status', 'remarks', 'entry_date']
    
    available_cols = [col for col in export_cols if col in df.columns]
    export_df = df[available_cols].copy()
    
    # Rename columns
    col_names = {
        's_no': 'S.No', 'sub_division': 'Sub-Division', 'reference_no': 'Reference No',
        'name': 'Name', 'tariff': 'Tariff', 'load': 'Load', 'meter_no': 'Meter No',
        'make': 'Make', 'mco_no': 'MCO No', 'mco_date': 'MCO Date',
        'bill_reading': 'Bill Reading', 'meter_reading': 'Meter Reading',
        'difference': 'Difference', 'status': 'Status', 'remarks': 'Remarks',
        'entry_date': 'Entry Date'
    }
    export_df = export_df.rename(columns=col_names)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Excel Export
        excel_data = export_to_excel(export_df, performa_name)
        st.download_button(
            label="📥 Download Excel",
            data=excel_data,
            file_name=f"{performa_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col2:
        # PDF Export
        try:
            pdf_data = export_to_pdf(export_df, performa_name)
            st.download_button(
                label="📥 Download PDF",
                data=pdf_data,
                file_name=f"{performa_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.warning("PDF export requires reportlab. Install with: pip install reportlab")
    
    with col3:
        # CSV Export
        csv_data = export_to_csv(export_df)
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"{performa_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

def show_activity_logs():
    """Display activity logs (Admin only)"""
    if not is_admin():
        st.error("Access denied. Admin only feature.")
        return
    
    st.markdown("""
        <div class="main-header">
            <h1>📜 Activity Logs</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Filters
    st.markdown("### 🔍 Filter Activities")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        users = get_all_users()
        user_options = ['All Users'] + [u['username'] for u in users]
        selected_user = st.selectbox("Filter by User", options=user_options)
    
    with col2:
        start_date = st.date_input("From Date", value=datetime.now().date() - timedelta(days=7), key="log_start")
    
    with col3:
        end_date = st.date_input("To Date", value=datetime.now().date(), key="log_end")
    
    with col4:
        performa_options = ['All Performas'] + list(PERFORMAS.keys()) + ['System']
        selected_performa = st.selectbox("Filter by Performa", options=performa_options)
    
    # Session filter
    sessions = get_unique_sessions()
    session_options = ['All Sessions'] + [f"{s['session_id'][:8]}... ({s['username']})" for s in sessions]
    selected_session = st.selectbox("Filter by Session", options=session_options)
    
    # Get filtered activities
    activities = get_activities_filtered(
        username=selected_user if selected_user != 'All Users' else None,
        start_date=str(start_date) if start_date else None,
        end_date=str(end_date) if end_date else None,
        performa=selected_performa if selected_performa != 'All Performas' else None,
        session_id=sessions[session_options.index(selected_session) - 1]['session_id'] if selected_session != 'All Sessions' else None
    )
    
    st.markdown(f"**Total Activities: {len(activities)}**")
    
    if activities:
        # Display table
        activity_data = []
        for act in activities:
            activity_data.append({
                'Log ID': act['log_id'],
                'Date & Time': format_datetime(act['timestamp']),
                'Username': act['username'],
                'Role': act['role'],
                'Performa': act['performa_name'],
                'Action': act['action_type'],
                'Reference No': act['reference_no'] or '-',
                'Session ID': act['session_id'][:8] + '...'
            })
        
        df = pd.DataFrame(activity_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Export option
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            excel_data = export_to_excel(df, "Activity_Logs")
            st.download_button(
                label="📥 Export to Excel",
                data=excel_data,
                file_name=f"Activity_Logs_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    else:
        st.info("No activities found for the selected filters.")

def show_theme_settings():
    """Display theme settings (Admin only)"""
    if not is_admin():
        st.error("Access denied. Admin only feature.")
        return
    
    st.markdown("""
        <div class="main-header">
            <h1>🎨 Theme Settings</h1>
        </div>
    """, unsafe_allow_html=True)
    
    current_theme = get_theme_settings()
    
    # Theme Presets
    st.markdown("### 🎯 Quick Theme Presets")
    
    preset_cols = st.columns(len(THEME_PRESETS))
    for idx, (preset_name, preset_theme) in enumerate(THEME_PRESETS.items()):
        with preset_cols[idx]:
            if st.button(preset_name, use_container_width=True, key=f"preset_{preset_name}"):
                update_theme_settings(
                    preset_theme['background_color'],
                    preset_theme['sidebar_color'],
                    preset_theme['text_color'],
                    preset_theme['card_color'],
                    preset_theme['primary_color'],
                    get_current_user()['username']
                )
                st.success(f"Theme changed to {preset_name}!")
                st.rerun()
    
    st.markdown("---")
    
    # Custom Theme Settings
    st.markdown("### ⚙️ Custom Theme")
    
    with st.form("theme_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            background_color = st.color_picker(
                "Background Color",
                value=current_theme.get('background_color', '#0E1117')
            )
            
            sidebar_color = st.color_picker(
                "Sidebar Color",
                value=current_theme.get('sidebar_color', '#262730')
            )
            
            text_color = st.color_picker(
                "Text Color",
                value=current_theme.get('text_color', '#FAFAFA')
            )
        
        with col2:
            card_color = st.color_picker(
                "Card Color",
                value=current_theme.get('card_color', '#1E1E1E')
            )
            
            primary_color = st.color_picker(
                "Primary/Accent Color",
                value=current_theme.get('primary_color', '#FF4B4B')
            )
        
        # Preview
        st.markdown("### 👁️ Preview")
        st.markdown(f"""
            <div style="background: {background_color}; padding: 1rem; border-radius: 10px; margin: 1rem 0;">
                <div style="display: flex; gap: 1rem;">
                    <div style="background: {sidebar_color}; padding: 1rem; border-radius: 8px; width: 150px;">
                        <p style="color: {text_color}; margin: 0;">Sidebar</p>
                    </div>
                    <div style="flex: 1;">
                        <div style="background: {card_color}; padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem;">
                            <p style="color: {text_color}; margin: 0;">Card Content</p>
                        </div>
                        <button style="background: {primary_color}; color: white; border: none; padding: 0.5rem 1rem; border-radius: 5px;">
                            Button
                        </button>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.form_submit_button("💾 Save Theme", use_container_width=True):
            update_theme_settings(
                background_color, sidebar_color, text_color,
                card_color, primary_color,
                get_current_user()['username']
            )
            st.success("Theme updated successfully!")
            st.rerun()

def show_user_management():
    """Display user management (Admin only)"""
    if not is_admin():
        st.error("Access denied. Admin only feature.")
        return
    
    st.markdown("""
        <div class="main-header">
            <h1>👥 User Management</h1>
        </div>
    """, unsafe_allow_html=True)
    
    users = get_all_users()
    
    # Display users
    st.markdown("### 📋 System Users")
    
    user_data = []
    for user in users:
        user_data.append({
            'User ID': user['user_id'],
            'Username': user['username'],
            'Full Name': user['full_name'],
            'Role': '👑 Admin' if user['role'] == 'admin' else '👤 Staff',
            'Status': '✅ Active' if user['is_active'] else '❌ Inactive',
            'Created': format_datetime(user['created_at'])
        })
    
    df = pd.DataFrame(user_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.info("""
        **User Credentials:**
        - Admin: `admin` / `Admin@123`
        - Staff 1: `staff1` / `Staff@123`
        - Staff 2: `staff2` / `Staff@123`
    """)

def show_database_backup():
    """Display database backup options (Admin only)"""
    if not is_admin():
        st.error("Access denied. Admin only feature.")
        return
    
    st.markdown("""
        <div class="main-header">
            <h1>💾 Database Backup</h1>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📦 Backup Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class="metric-card">
                <h4>🔄 Create Backup</h4>
                <p>Create a backup of the entire database including all records and settings.</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("💾 Create Backup Now", use_container_width=True):
            try:
                backup_path = backup_database()
                
                # Read backup file
                with open(backup_path, 'rb') as f:
                    backup_data = f.read()
                
                st.download_button(
                    label="📥 Download Backup",
                    data=backup_data,
                    file_name=f"lab_management_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db",
                    mime="application/octet-stream",
                    use_container_width=True
                )
                
                st.success(f"Backup created successfully!")
            except Exception as e:
                st.error(f"Backup failed: {str(e)}")
    
    with col2:
        st.markdown("""
            <div class="metric-card">
                <h4>📊 Database Info</h4>
            </div>
        """, unsafe_allow_html=True)
        
        stats = get_dashboard_stats()
        st.write(f"**Total Records:** {stats.get('total_records', 0)}")
        st.write(f"**Total Performas:** {len(PERFORMAS)}")
        st.write(f"**Database File:** lab_management.db")

# Run the application
if __name__ == "__main__":
    main()
