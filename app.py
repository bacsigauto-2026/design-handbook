import streamlit as st
from supabase import create_client, Client
import pandas as pd
import time
import uuid

# --- App Configuration ---
st.set_page_config(
    page_title="Design Handbook",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Supabase Initialization ---
# Uses st.secrets to securely load credentials
try:
    SUPABASE_URL = st.secrets["supabase"]["url"]
    SUPABASE_KEY = st.secrets["supabase"]["key"]
except FileNotFoundError:
    st.error("Secrets not found. Please setup .streamlit/secrets.toml")
    st.stop()
except KeyError:
    st.error("Supabase credentials missing in secrets.toml")
    st.stop()

@st.cache_resource
def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase_client()

# --- Session State Management ---
if "user" not in st.session_state:
    st.session_state.user = None
if "role" not in st.session_state:
    st.session_state.role = None
if "auth_checked" not in st.session_state:
    st.session_state.auth_checked = False

# --- Helper Functions ---

def get_user_role(email, user_id=None):
    """Fetch user role from 'users' table or create if not exists."""
    try:
        # Check if user exists
        response = supabase.table("users").select("*").eq("email", email).execute()
        
        if response.data:
            return response.data[0]["role"]
        else:
            # Create new user with 'pending' role
            new_user_data = {"email": email, "role": "pending"}
            if user_id:
                new_user_data["id"] = user_id
            
            try:
                supabase.table("users").insert(new_user_data).execute()
            except Exception as e:
                # If ID is missing and no default, this will fail.
                st.warning(f"Note: User creation logic failed. Error: {e}")
                return None
            
            return "pending"
    except Exception as e:
        st.error(f"Database Error: {e}")
        return None

def login_with_google():
    """Trigger Google OAuth."""
    try:
        # Get the current URL to redirect back to
        # Note: 'redirect_to' requires site URL config in Supabase
        
        # 1. Get the OAuth provider URL
        data = supabase.auth.sign_in_with_oauth({
            "provider": "google", 
            "options": {
                "redirect_to": "http://localhost:8501" # Adjust for production
            }
        })
        
        # 2. Show the link/button
        if data.url:
            st.markdown(f'<a href="{data.url}" target="_self"><button style="background-color:#4285F4; color:white; padding:10px; border:none; border-radius:5px; cursor:pointer;">Login with Google</button></a>', unsafe_allow_html=True)
            st.info("Click the button above to sign in. (Requires Supabase Auth Config)")
    except Exception as e:
        st.error(f"Auth Error: {e}")

def check_auth_status():
    """Verify if user is logged in via Supabase Auth."""
    # Check for session in query params (Fragment based auth is standard in Supabase)
    # Streamlit doesn't handle hash fragments easily. 
    # We will rely on supabase client persistence or a 'Simulate' flow for this demo 
    # if actual OAuth flow is blocked by environment.
    
    session = supabase.auth.get_session()
    
    # DEV/DEMO OVERRIDE: 
    # Since OAuth callback handling in Streamlit requires URL fragment parsing (often handled by JS),
    # and we want a testable app, we might add a dev bypass or just rely on 'session' being present 
    # if the user manually managed it or if we are in environment supporting it.
    
    if session:
        return session.user
    return None

# --- UI Components ---

def render_access_denied():
    st.image("https://http.cat/403", width=400)
    st.error("🚫 Access Denied")
    st.write("Your account is currently **Pending Approval**.")
    st.write("Please contact the administrator.")

def get_sidebar_filters(df):
    st.sidebar.header("🔍 Filters")
    
    # Project Name
    projects = ["All"] + sorted(df["project_name"].unique().tolist())
    selected_project = st.sidebar.selectbox("Project Name", projects)
    
    # Cascade Filtering (Optional but requested)
    if selected_project != "All":
        df = df[df["project_name"] == selected_project]
    
    # Catalogue
    catalogues = ["All"] + sorted(df["catalogue"].dropna().unique().tolist())
    selected_catalogue = st.sidebar.selectbox("Catalogue", catalogues)
    
    if selected_catalogue != "All":
        df = df[df["catalogue"] == selected_catalogue]
    
    # Drawing Name
    drawings = ["All"] + sorted(df["drawing_name"].unique().tolist())
    selected_drawing = st.sidebar.selectbox("Drawing Name", drawings)
    
    if selected_drawing != "All":
        df = df[df["drawing_name"] == selected_drawing]
        
    return df

def render_main_dashboard():
    st.title("📘 Design Handbook")
    
    # specific_query
    query = supabase.table("design_docs").select("*").order("id", desc=False)
    response = query.execute()
    
    if not response.data:
        st.info("No design documents found.")
        return

    df = pd.DataFrame(response.data)
    
    # Apply Filters
    filtered_df = get_sidebar_filters(df)
    
    # Layout: Table Top, PDF Bottom
    
    st.subheader("Drawings List")
    # Configure dataframe with selection
    event = st.dataframe(
        filtered_df,
        use_container_width=True,
        on_select="rerun",
        selection_mode="single-row",
        hide_index=True
    )
    
    st.markdown("---")
    
    st.subheader("Drawing Viewer")
    if len(event.selection.rows) > 0:
        selected_row_index = event.selection.rows[0]
        # Since filtered_df might have different indices than original if we didn't reset,
        # we need to be careful. 'event.selection.rows' returns integer indices of the display.
        # Using iloc on filtered_df should work.
        
        try:
            selected_record = filtered_df.iloc[selected_row_index]
            pdf_link = selected_record.get("pdf_link")
            
            st.info(f"Viewing: **{selected_record.get('drawing_name')}**")
            
            if pdf_link:
                # PDF Embedding
                # Many sites block standard iframe embedding (X-Frame-Options). 
                # We will use <object> tag which is more standard for PDFs, 
                # and provide a fallback link.
                
                # Hack for Dropbox to ensure raw file is served
                if "dropbox.com" in pdf_link and "dl=0" in pdf_link:
                    pdf_link = pdf_link.replace("dl=0", "raw=1")
                
                # Hack for Google Drive to ensure preview is served
                if "drive.google.com" in pdf_link and "/view" in pdf_link:
                    pdf_link = pdf_link.replace("/view?usp=sharing", "/preview")
                    pdf_link = pdf_link.replace("/view", "/preview")
                
                # Add Full Screen Button
                st.link_button("Full Screen", pdf_link)

                # Add params to hide sidebar/toolbar
                # If there are existing fragments, this might need care, but usually just appending works for PDF viewers
                pdf_view_link = pdf_link
                if "drive.google.com" not in pdf_link:
                     pdf_view_link = pdf_link + "#toolbar=0&navpanes=0"

                pdf_display = f"""
                    <iframe src="{pdf_view_link}" width="100%" height="800px" type="application/pdf" style="border: none;">
                    </iframe>
                """
                st.markdown(pdf_display, unsafe_allow_html=True)
            else:
                st.warning("No PDF Link available for this record.")
        except Exception as e:
            st.error(f"Error loading viewer: {e}")
    else:
        st.info("👈 Select a drawing from the table to view.")

def render_admin_dashboard():
    st.title("🛡️ Admin Dashboard")
    
    st.subheader("User Management")
    
    # Fetch all users
    response = supabase.table("users").select("*").execute()
    
    if response.data:
        users_df = pd.DataFrame(response.data)
        
        # Display editable data editor for Roles
        # We can use st.data_editor to allow inline editing
        
        column_config = {
            "role": st.column_config.SelectboxColumn(
                "Role",
                help="User Role",
                options=["pending", "user", "admin"],
                required=True
            ),
            "id": st.column_config.TextColumn("ID", disabled=True),
            "email": st.column_config.TextColumn("Email", disabled=True),
            "created_at": st.column_config.DatetimeColumn("Created At", disabled=True, format="D MMM YYYY, h:mm a"),
        }
        
        edited_df = st.data_editor(
            users_df,
            column_config=column_config,
            use_container_width=True,
            key="user_editor",
            num_rows="dynamic" # Allow checking, though we primarily want to edit
        )
        
        # Detect Changes
        # This is a bit naive (comparing entire DF), but works for small user lists
        # In production, we'd use on_change callback or compare specific session state diffs.
        if st.button("Save Changes"):
            try:
                for index, row in edited_df.iterrows():
                    # Check against original data to find changes could be complex,
                    # easier to just upsert strictly needed fields if ID matches.
                    # Or finding diff:
                    original_row = users_df[users_df['id'] == row['id']].iloc[0]
                    if original_row['role'] != row['role']:
                        # Update DB
                        st.write(f"Updating {row['email']} to {row['role']}...")
                        supabase.table("users").update({"role": row['role']}).eq("id", row['id']).execute()
                
                st.success("Roles updated successfully!")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Error saving changes: {e}")
            
    else:
        st.info("No users found.")

# --- Main App Logic ---

def main():
    # 1. Check Login
    user = check_auth_status()
    
    # Check for Developer Override (if Auth not enabled)
    if not user and "temp_user_override" in st.session_state:
        user = st.session_state.temp_user_override

    # Sidebar Login Status
    with st.sidebar:
        if user:
            st.write(f"Logged in as: **{user.email}**")
            if st.button("Logout"):
                supabase.auth.sign_out()
                st.session_state.user = None
                st.session_state.role = None
                st.rerun()
        else:
            st.write("🔴 Not Logged In")

    if not user:
        # Show Login Screen
        st.title("Design Handbook Login")
        st.write("Please sign in to access the dashboard.")
        login_with_google()
        
        # --- DEBUG / DEMO HELPER ---
        # Since we can't easily click "Login with Google" in this simulated env
        # I will provide a dev bypass to demonstrate the logic works.
        with st.expander("Developer Login (Bypass default Auth)"):
            dev_email = st.text_input("Enter Email to Simulate Login")
            if st.button("Simulate Login"):
                if dev_email:
                    # Fake a user object
                    # generating a deterministic-ish UUID from email hash or just random is fine for simulation
                    fake_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, dev_email))
                    fake_user = type('obj', (object,), {'email': dev_email, 'id': fake_id})
                    # Set session directly (this won't persist actual Supabase session but works for app logic)
                    # For real app, we rely on Supabase returning session.
                    # We store in session_state to persist across reruns
                    st.session_state.temp_user_override = fake_user
                    st.rerun()

    # 2. if Logged In -> Check Role
    if user:
        # Check Role if not already in session
        if not st.session_state.role:
            role = get_user_role(user.email, getattr(user, 'id', None))
            st.session_state.role = role
        
        role = st.session_state.role
        
        # 3. Route based on Role
        if role == "pending":
            render_access_denied()
        elif role == "user":
            render_main_dashboard()
        elif role == "admin":
            st.sidebar.markdown("---")
            page = st.sidebar.radio("Navigate", ["Design Handbook", "Admin Dashboard"])
            if page == "Design Handbook":
                render_main_dashboard()
            else:
                render_admin_dashboard()
        else:
            st.error(f"Unknown role: {role}")

if __name__ == "__main__":
    main()
