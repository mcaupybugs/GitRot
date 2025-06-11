import streamlit as st
import datetime
from app import ReadmeGeneratorApp

# Configure Streamlit page layout for wide mode
st.set_page_config(
    page_title="GitRot - README Generator",
    page_icon="📝",
    layout="wide",  # This is key for utilizing full width
    initial_sidebar_state="expanded"
)

# Custom CSS for wide layout with visible ad column
st.markdown("""
<style>
    /* Force full width and optimize layout */
    .main .block-container {
        padding: 0.5rem !important;
        margin: 0 !important;
        max-width: 100% !important;
        width: 100% !important;
    }
    
    /* Ensure columns are visible with minimal spacing */
    [data-testid="column"] {
        padding: 0.25rem !important;
        margin: 0 !important;
        border: none !important;
        min-width: 0 !important;
    }
    
    /* Reduce gaps but keep columns visible */
    .stHorizontalBlock, .row-widget, .stColumns {
        gap: 0.5rem !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Ensure all columns are properly displayed */
    .stColumn {
        padding: 0.25rem !important;
        margin: 0 !important;
        min-width: 0 !important;
        flex-shrink: 0 !important;
    }
    
    /* Make sure ad column (col3) is visible */
    .stColumn:nth-child(3) {
        background-color: #f8f9fa !important;
        border: 1px solid #e9ecef !important;
        border-radius: 8px !important;
        min-width: 250px !important;
    }
    
    /* Make sure content fills available space */
    .element-container {
        width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)

# Azure best practice: Initialize session state for persistent data
if 'readme_content' not in st.session_state:
    st.session_state.readme_content = None
if 'repo_url_generated' not in st.session_state:
    st.session_state.repo_url_generated = None
if 'generation_timestamp' not in st.session_state:
    st.session_state.generation_timestamp = None
if 'generation_method' not in st.session_state:
    st.session_state.generation_method = "Standard"

st.header("GitRot")
st.subheader("Get readme for your public github repo!!!")

# Sidebar for Azure monitoring and options
with st.sidebar:
    st.header("🔧 Azure OpenAI Settings")
    generation_method = st.selectbox(
        "Generation Method:",
        ["Standard README", "README with Examples"],
        key="gen_method"
    )
    
    if st.session_state.readme_content:
        st.success("✅ README Generated")
        st.info(f"📊 Length: {len(st.session_state.readme_content)} chars")
        if st.session_state.generation_timestamp:
            st.info(f"🕒 Generated: {st.session_state.generation_timestamp}")

# Create layout with persistent ad space on the right
main_col, ad_col = st.columns([7, 2])

with ad_col:
    # Google AdSense Advertisement Space - Always Visible
    st.markdown("### 📢 Sponsored")
    
    # Google AdSense code block - Replace with your actual AdSense code
    st.markdown("""
    <div style='text-align: center; margin: 20px 0; background: #ffeb3b; padding: 15px; border: 3px solid #ff9800; border-radius: 10px;'>
        <h3 style='color: #e65100; margin: 10px 0;'>🚀 ADVERTISEMENT SPACE 🚀</h3>
        <p style='color: #bf360c; font-weight: bold;'>Google AdSense will load here</p>
        
        <!-- Test Ad Unit - for development -->
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5478826702170077"
     crossorigin="anonymous"></script>
<script>
     (adsbygoogle = window.adsbygoogle || []).push({});
</script>
    </div>
    """, unsafe_allow_html=True)
    
    # Placeholder while setting up AdSense
    st.markdown("""
    <div style='border: 3px solid #4caf50; padding: 30px; text-align: center; background-color: #e8f5e8; border-radius: 8px; margin: 20px 0;'>
        <h4 style='color: #2e7d32; margin-bottom: 10px;'>📢 Advertisement</h4>
        <p style='color: #388e3c; font-size: 14px; margin-bottom: 15px;'>300x600 Sidebar Ad</p>
        <small style='color: #1b5e20;'>Replace AdSense code above with your publisher ID</small>
    </div>
    """, unsafe_allow_html=True)

with main_col:
    # Input field and generate button in main column
    repo_url = st.text_input("Enter the repo URL : ")
    readme_generator_app = ReadmeGeneratorApp()
    
    # Generate README button
    if repo_url and st.button("Generate README"):
        with st.spinner("Processing repository with Azure OpenAI..."):
            try:
                readme_content = readme_generator_app.generate_readme_from_repo_url(repo_url, generation_method)
                
                # Store in session state for persistence with proper timestamp
                st.session_state.readme_content = readme_content
                st.session_state.repo_url_generated = repo_url
                # Azure best practice: Use datetime for timestamp tracking
                st.session_state.generation_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.generation_method = generation_method
                
                st.success("README Generated Successfully!")
                
            except Exception as e:
                st.error(f"🚨 Azure OpenAI Error: {str(e)}")
                st.info("💡 Tip: Check your Azure OpenAI configuration and try again.")
                # Clear session state on error
                st.session_state.readme_content = None

# Display README content if it exists in session state
if st.session_state.readme_content:
    # Display within the main column (already created above)
    with main_col:
        # Display options for Azure monitoring - Layout within main column
        col1, col2 = st.columns([6, 1])
        
        with col2:
            # Azure best practice: Persistent display options
            display_option = st.selectbox(
                "Display Mode:",
                ["Rendered Markdown", "Raw Text", "Split View"],
                key="display_mode"
            )
            
            # Azure Application Insights tracking
            st.info(f"📊 Content Length: {len(st.session_state.readme_content)} chars")
            st.info(f"🔗 Repository: {st.session_state.repo_url_generated.split('/')[-1] if st.session_state.repo_url_generated else 'N/A'}")
            st.info(f"⚙️ Method: {st.session_state.generation_method}")
            
            # Clear content button for Azure session management
            if st.button("🗑️ Clear Content", help="Clear generated README and start fresh"):
                # Azure best practice: Clear all session state
                for key in ['readme_content', 'repo_url_generated', 'generation_timestamp']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()  # Use st.rerun() instead of st.experimental_rerun()
        
        with col1:
            # Azure best practice: Use session state content for all display modes
            readme_content = st.session_state.readme_content
            
            if display_option == "Rendered Markdown":
                # Best practice: Use st.markdown for proper rendering
                st.markdown("### 📋 Generated README Preview")
                st.markdown(readme_content, unsafe_allow_html=False)
                
            elif display_option == "Raw Text":
                # Fallback: Raw text display
                st.markdown("### 📝 Raw README Content")
                st.text_area(
                    "Generated README:", 
                    readme_content, 
                    height=600,
                    help="Raw markdown content - copy this to your repository"
                )
                
            elif display_option == "Split View":
                # Azure best practice: Side-by-side comparison
                st.markdown("### 📋 README Preview & Raw Content")
                col_rendered, col_raw = st.columns(2)
                
                with col_rendered:
                    st.markdown("#### Rendered")
                    # Use container for better scrolling in split view
                    with st.container():
                        st.markdown(readme_content, unsafe_allow_html=False)
                
                with col_raw:
                    st.markdown("#### Raw Markdown")
                    st.code(readme_content, language="markdown")
        
        # Azure monitoring: Download tracking (always visible when content exists)
        st.markdown("---")
        col_download1, col_download2, col_download3 = st.columns([1, 2, 1])
        
        with col_download2:
            # Azure best practice: Include timestamp in filename
            timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(
                label="📥 Download README.md",
                data=st.session_state.readme_content,
                file_name=f"README_{timestamp_str}.md",
                mime="text/markdown",
                help="Download the generated README for your repository",
                use_container_width=True
            )

# Azure best practice: Show usage instructions when no content
else:
    with main_col:
        st.info("👆 Enter a GitHub repository URL above and click 'Generate README' to get started!")
        
        # Azure monitoring: Show example usage
        with st.expander("📚 How to use GitRot", expanded=False):
            st.markdown("""
            **Azure OpenAI-Powered README Generation:**
            
            1. **Enter Repository URL**: Paste any public GitHub repository URL
            2. **Choose Method**: Select generation method in the sidebar
            3. **Generate**: Click 'Generate README' to process with Azure OpenAI
            4. **Review**: Use display modes to preview your README
            5. **Download**: Save the generated README.md file
            
            **Supported Repository Types:**
            - Python projects
            - JavaScript/Node.js applications
            - Documentation repositories
            - Multi-language codebases
            
            **Azure OpenAI Features:**
            - Intelligent code analysis
            - Professional documentation generation
            - Best practices compliance
            - Multiple display formats
            """)

# Azure best practice: Footer with session information
if st.session_state.readme_content:
    st.markdown("---")
    # Azure monitoring: Enhanced session metrics
    generation_time = st.session_state.generation_timestamp if st.session_state.generation_timestamp else "Unknown"
    repo_name = st.session_state.repo_url_generated.split('/')[-1] if st.session_state.repo_url_generated else "Unknown"
    
    st.markdown(
        f"<div style='text-align: center; color: #666; font-size: 0.8em;'>"
        f"🔵 Azure OpenAI Session Active | "
        f"📊 Content: {len(st.session_state.readme_content)} chars | "
        f"🕒 Generated: {generation_time} | "
        f"⚙️ Method: {st.session_state.generation_method} | "
        f"🔗 Repo: {repo_name}"
        f"</div>", 
        unsafe_allow_html=True
    )
