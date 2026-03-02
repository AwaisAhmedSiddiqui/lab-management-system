"""
Authentication Module - Lab Management & Analytics System
Handles user authentication, session management, and permissions
"""

import streamlit as st
from database import verify_user, create_session, end_session, log_activity

def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'Dashboard'

def login(username, password):
    """Authenticate user and create session"""
    user = verify_user(username, password)
    
    if user:
        st.session_state.authenticated = True
        st.session_state.user = user
        st.session_state.session_id = create_session(user['user_id'])
        
        # Log login activity
        log_activity(
            username=user['username'],
            role=user['role'],
            session_id=st.session_state.session_id,
            performa_name='System',
            action_type='Add',
            details='User logged in'
        )
        return True
    return False

def logout():
    """End session and logout user"""
    if st.session_state.session_id:
        # Log logout activity
        if st.session_state.user:
            log_activity(
                username=st.session_state.user['username'],
                role=st.session_state.user['role'],
                session_id=st.session_state.session_id,
                performa_name='System',
                action_type='Add',
                details='User logged out'
            )
        end_session(st.session_state.session_id)
    
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.session_id = None
    st.session_state.current_page = 'Dashboard'

def is_authenticated():
    """Check if user is authenticated"""
    return st.session_state.get('authenticated', False)

def is_admin():
    """Check if current user is admin"""
    user = st.session_state.get('user')
    return user and user.get('role') == 'admin'

def is_staff():
    """Check if current user is staff"""
    user = st.session_state.get('user')
    return user and user.get('role') == 'staff'

def get_current_user():
    """Get current logged in user"""
    return st.session_state.get('user')

def get_session_id():
    """Get current session ID"""
    return st.session_state.get('session_id')

def can_add():
    """Check if user can add records"""
    return is_authenticated()

def can_edit(record=None):
    """Check if user can edit records"""
    if is_admin():
        return True  # Admin can edit any record
    
    if is_staff() and record:
        # Staff can only edit unlocked records
        return not record.get('is_locked', False)
    
    return False

def can_delete():
    """Check if user can delete records"""
    return is_admin()

def can_unlock():
    """Check if user can unlock records"""
    return is_admin()

def can_view_logs():
    """Check if user can view activity logs"""
    return is_admin()

def can_change_theme():
    """Check if user can change system theme"""
    return is_admin()

def require_auth(func):
    """Decorator to require authentication"""
    def wrapper(*args, **kwargs):
        if not is_authenticated():
            st.error("Please login to access this feature.")
            return None
        return func(*args, **kwargs)
    return wrapper

def require_admin(func):
    """Decorator to require admin role"""
    def wrapper(*args, **kwargs):
        if not is_admin():
            st.error("This feature is only available to administrators.")
            return None
        return func(*args, **kwargs)
    return wrapper

def show_login_page():
    """Display login page"""
    st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
        }
        .login-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        .login-header h1 {
            color: #FF4B4B;
            font-size: 2rem;
        }
        .cred-box {
            margin-top: 0.75rem;
            padding: 0.9rem;
            border-radius: 10px;
            border: 1px solid rgba(255, 75, 75, 0.55);
            background: rgba(14, 17, 23, 0.85);
            color: #F8FAFC;
        }
        .cred-box p {
            color: #FFFFFF;
            font-size: 0.98rem;
        }
        .cred-box table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }
        .cred-box th, .cred-box td {
            text-align: left;
            padding: 0.35rem 0.25rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.18);
            color: #F8FAFC;
        }
        .cred-box th {
            font-weight: 700;
            color: #FFFFFF;
            background: rgba(255, 75, 75, 0.16);
        }
        .role-pill {
            display: inline-block;
            padding: 0.2rem 0.55rem;
            border-radius: 999px;
            font-weight: 700;
            font-size: 0.78rem;
            letter-spacing: 0.2px;
        }
        .role-admin {
            color: #FFF7ED;
            background: linear-gradient(135deg, #F97316, #EA580C);
        }
        .role-staff {
            color: #ECFEFF;
            background: linear-gradient(135deg, #0891B2, #0E7490);
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-header">', unsafe_allow_html=True)
        st.markdown("# 🔬 Lab Management System")
        st.markdown("### Login to Continue")
        st.markdown('</div>', unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("👤 Username", placeholder="Enter username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter password")
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                submit = st.form_submit_button("🔐 Login", use_container_width=True)
            
            if submit:
                if username and password:
                    if login(username, password):
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                else:
                    st.warning("Please enter both username and password")
        
        st.markdown("---")
        st.markdown("""
            <div class="cred-box">
                <p style="margin: 0 0 0.55rem 0;"><strong>Default Login Credentials</strong></p>
                <table>
                    <thead>
                        <tr>
                            <th>Role</th>
                            <th>Username</th>
                            <th>Password</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><span class="role-pill role-admin">Admin</span></td>
                            <td>admin</td>
                            <td>Admin@123</td>
                        </tr>
                        <tr>
                            <td><span class="role-pill role-staff">Staff</span></td>
                            <td>staff1</td>
                            <td>Staff@123</td>
                        </tr>
                        <tr>
                            <td><span class="role-pill role-staff">Staff</span></td>
                            <td>staff2</td>
                            <td>Staff@123</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        """, unsafe_allow_html=True)

def show_user_info():
    """Display current user info in sidebar"""
    user = get_current_user()
    if user:
        is_admin_role = user['role'] == 'admin'
        role_badge = "👑 Admin" if is_admin_role else "👤 Staff"
        card_bg = "linear-gradient(135deg, rgba(249,115,22,0.24), rgba(234,88,12,0.24))" if is_admin_role else "linear-gradient(135deg, rgba(8,145,178,0.24), rgba(14,116,144,0.24))"
        card_border = "1px solid rgba(249,115,22,0.55)" if is_admin_role else "1px solid rgba(8,145,178,0.55)"
        badge_bg = "#EA580C" if is_admin_role else "#0E7490"
        st.sidebar.markdown(f"""
            <div style="padding: 1rem; background: {card_bg}; border: {card_border}; border-radius: 12px; margin-bottom: 1rem;">
                <p style="margin: 0 0 0.5rem 0; color: #FFFFFF; font-weight: 700; font-size: 0.95rem;">{user['full_name']}</p>
                <span style="display: inline-block; background: {badge_bg}; color: #FFFFFF; padding: 0.22rem 0.58rem; border-radius: 999px; font-size: 0.8rem; font-weight: 700;">
                    {role_badge}
                </span>
            </div>
        """, unsafe_allow_html=True)
