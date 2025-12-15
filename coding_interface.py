# save as: coding_interface.py

"""
Phillips Curve Classification Human Coding Interface
=====================================================
Streamlit application for human validation of Claude's Phillips curve
slope classifications from FOMC transcripts.

Following Mullainathan et al. (2024) framework for LLM output validation.

Usage:
    streamlit run coding_interface.py

Changelog:
    v1.1 - Fixed session resume widget state bug (widget_version pattern)
         - Added resume CSV validation
         - Locked coder name after first save to prevent inconsistencies
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import io


def get_script_directory():
    """Get the directory where this script is located."""
    return Path(__file__).resolve().parent


SCRIPT_DIR = get_script_directory()

# Page configuration
st.set_page_config(
    page_title="Phillips Curve Classification",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_data
def load_coding_data_from_file(file_content):
    """Load the coding sample data from uploaded file."""
    return pd.read_csv(io.StringIO(file_content.decode('utf-8')))


@st.cache_data
def load_default_coding_data():
    """Load the default coding data from the repo."""
    coding_file = SCRIPT_DIR / 'validation_samples' / 'production' / 'coding_phillips.csv'
    if coding_file.exists():
        return pd.read_csv(coding_file)
    return None


def get_results_csv(results):
    """Convert results to CSV for download."""
    df = pd.DataFrame(results)
    return df.to_csv(index=False).encode('utf-8')


def get_previous_coding(coding_id, results):
    """Get previous coding values for a specific coding_id."""
    for result in results:
        if result.get('coding_id') == coding_id:
            return result
    return None


def validate_resume_csv(resume_df, coding_df):
    """
    Validate that a resume CSV is compatible with the current coding data.
    
    Returns:
        tuple: (is_valid, message, matching_ids)
    """
    required_cols = {'coding_id', 'coder_name', 'classification'}
    if not required_cols.issubset(resume_df.columns):
        missing = required_cols - set(resume_df.columns)
        return False, f"Missing required columns: {missing}", set()
    
    resume_ids = set(resume_df['coding_id'].tolist())
    coding_ids = set(coding_df['coding_id'].tolist())
    
    matching_ids = resume_ids.intersection(coding_ids)
    unmatched_ids = resume_ids - coding_ids
    
    if len(matching_ids) == 0:
        return False, "No coding_ids in resume file match current data source", set()
    
    if len(unmatched_ids) > 0:
        return True, f"Warning: {len(unmatched_ids)} coding_ids in resume file not found in current data (will be ignored)", matching_ids
    
    return True, f"Successfully validated {len(matching_ids)} coded arguments", matching_ids


def initialize_session_state():
    """Initialize all session state variables."""
    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0
    if 'results' not in st.session_state:
        st.session_state.results = []
    if 'coded_ids' not in st.session_state:
        st.session_state.coded_ids = set()
    if 'widget_version' not in st.session_state:
        st.session_state.widget_version = 0
    if 'locked_coder_name' not in st.session_state:
        st.session_state.locked_coder_name = None


def main():
    st.title("Phillips Curve Classification")
    st.markdown("**Human Validation of LLM Classifications**")
    st.markdown("---")

    # Initialize session state
    initialize_session_state()

    # Sidebar setup
    with st.sidebar:
        st.header("Setup")

        # Coder identification
        # If name is locked (user has saved at least once), show it as locked
        if st.session_state.locked_coder_name is not None:
            st.text_input(
                "Your Name (locked)",
                value=st.session_state.locked_coder_name,
                disabled=True,
                help="Name is locked after first save to ensure consistency"
            )
            coder_name = st.session_state.locked_coder_name
        else:
            coder_name = st.text_input(
                "Your Name",
                placeholder="Enter your name",
                help="Used to identify your coding results. Will be locked after first save."
            )

        if not coder_name:
            st.warning("Please enter your name to begin")
            st.stop()

        # Data source selection
        st.markdown("---")
        st.subheader("Data Source")

        data_source = st.radio(
            "Choose data source:",
            ["Use default sample", "Upload custom file"],
            help="Use the pre-loaded sample or upload your own CSV"
        )

        coding_df = None

        if data_source == "Use default sample":
            coding_df = load_default_coding_data()
            if coding_df is None:
                st.error("Default coding file not found. Please upload a file.")
                st.stop()
            else:
                st.success(f"Loaded {len(coding_df)} arguments")
        else:
            uploaded_file = st.file_uploader(
                "Upload Coding File",
                type=['csv'],
                help="Upload a coding CSV file"
            )
            if uploaded_file:
                coding_df = load_coding_data_from_file(uploaded_file.getvalue())
                st.success(f"Loaded {len(coding_df)} arguments")
            else:
                st.info("Please upload a coding file")
                st.stop()

    total_arguments = len(coding_df)
    current_index = st.session_state.current_index
    
    # Get current widget version for keying
    v = st.session_state.widget_version

    # Progress tracking in sidebar
    with st.sidebar:
        st.markdown("---")
        st.header("Progress")

        n_coded = len(st.session_state.coded_ids)
        progress_pct = n_coded / total_arguments if total_arguments > 0 else 0
        st.progress(progress_pct)
        st.write(f"Coded: {n_coded} / {total_arguments}")
        st.write(f"Current: Argument {current_index + 1}")

        # Download results button
        st.markdown("---")
        st.subheader("Save Results")

        if st.session_state.results:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_name = coder_name.lower().replace(' ', '_')
            filename = f"coded_{safe_name}_phillips_{timestamp}.csv"

            st.download_button(
                label="📥 Download Results CSV",
                data=get_results_csv(st.session_state.results),
                file_name=filename,
                mime="text/csv",
                help="Download your coding results"
            )
            st.caption(f"{len(st.session_state.results)} arguments coded")
        else:
            st.info("Code some arguments to enable download")

        # Load previous session via upload
        st.markdown("---")
        st.subheader("Resume Session")

        resume_file = st.file_uploader(
            "Upload previous session",
            type=['csv'],
            key="resume_upload",
            help="Upload a previously downloaded results file to continue"
        )

        if resume_file:
            if st.button("Load Session"):
                try:
                    resume_df = pd.read_csv(resume_file)
                    
                    # Validate the resume CSV
                    is_valid, message, matching_ids = validate_resume_csv(resume_df, coding_df)
                    
                    if not is_valid:
                        st.error(f"Cannot load session: {message}")
                    else:
                        if "Warning" in message:
                            st.warning(message)
                        
                        # Filter to only matching IDs
                        valid_results = resume_df[resume_df['coding_id'].isin(matching_ids)].to_dict('records')
                        
                        st.session_state.results = valid_results
                        st.session_state.coded_ids = set(r['coding_id'] for r in valid_results)
                        
                        # Lock the coder name from the resume file
                        if len(valid_results) > 0:
                            st.session_state.locked_coder_name = valid_results[0].get('coder_name', coder_name)
                        
                        # INCREMENT WIDGET VERSION to force fresh widget state
                        # This is critical - without this, widgets show cached values
                        # instead of values from the loaded CSV
                        st.session_state.widget_version += 1

                        # Jump to first uncoded argument
                        found_uncoded = False
                        for idx in range(len(coding_df)):
                            if coding_df.iloc[idx]['coding_id'] not in st.session_state.coded_ids:
                                st.session_state.current_index = idx
                                found_uncoded = True
                                break
                        
                        if not found_uncoded:
                            # All are coded, go to last one
                            st.session_state.current_index = len(coding_df) - 1

                        st.success(f"Loaded {len(valid_results)} coded arguments")
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"Error loading session: {e}")

    # Main coding area
    if current_index < total_arguments:
        current_row = coding_df.iloc[current_index]
        coding_id = current_row['coding_id']
        quotation = current_row['quotation']
        description = current_row.get('description', '')
        explanation = current_row.get('explanation', '')
        variable = current_row.get('variable', '')

        is_coded = coding_id in st.session_state.coded_ids
        previous_coding = get_previous_coding(coding_id, st.session_state.results) if is_coded else None

        # Two-column layout
        col1, col2 = st.columns([3, 2])

        with col1:
            st.subheader(f"Argument {coding_id}")

            if variable:
                st.caption(f"Economic Variable: **{variable}**")

            if is_coded:
                st.success("✓ Already coded - you can update or skip")

            # Quotation
            st.markdown("**Quotation:**")
            st.markdown(
                f"""<div style="background-color: #f0f2f6; padding: 20px;
                border-radius: 10px; font-size: 16px; line-height: 1.6;">
                {quotation}
                </div>""",
                unsafe_allow_html=True
            )

            # Description
            if pd.notna(description) and str(description).strip():
                st.markdown("**Description:**")
                st.markdown(
                    f"""<div style="background-color: #e8f4f8; padding: 15px;
                    border-radius: 8px; font-size: 14px; margin-top: 10px;">
                    {description}
                    </div>""",
                    unsafe_allow_html=True
                )

            # Explanation
            if pd.notna(explanation) and str(explanation).strip():
                st.markdown("**Explanation:**")
                st.markdown(
                    f"""<div style="background-color: #fff4e6; padding: 15px;
                    border-radius: 8px; font-size: 14px; margin-top: 10px;">
                    {explanation}
                    </div>""",
                    unsafe_allow_html=True
                )

        with col2:
            st.subheader("Classification")

            st.markdown("""
            **Does this speaker express a belief about how labor market
            conditions affect inflation (Phillips curve)?**
            """)

            # Get default value from previous coding
            categories = ['steep', 'flat', 'moderate', 'none']
            category_labels = {
                'steep': 'STEEP - Labor markets SIGNIFICANTLY affect inflation',
                'flat': 'FLAT - Labor markets have LITTLE/NO effect on inflation',
                'moderate': 'MODERATE - Qualified/partial relationship',
                'none': 'NONE - No Phillips curve belief expressed'
            }

            default_idx = 3  # Default to none
            if previous_coding:
                prev_cat = previous_coding.get('classification', 'none')
                if prev_cat in categories:
                    default_idx = categories.index(prev_cat)

            # IMPORTANT: Widget key includes version number
            # This forces Streamlit to create a fresh widget after session resume,
            # using the index/value parameters instead of cached state
            classification = st.radio(
                "Select classification:",
                options=categories,
                format_func=lambda x: category_labels[x],
                index=default_idx,
                key=f"classification_{current_index}_v{v}"
            )

            # Optional notes
            st.markdown("---")
            notes_default = ''
            if previous_coding:
                notes_val = previous_coding.get('notes', '')
                if isinstance(notes_val, str) and pd.notna(notes_val):
                    notes_default = notes_val
            
            # IMPORTANT: Widget key includes version number
            notes = st.text_area(
                "Notes (optional):",
                value=notes_default,
                max_chars=500,
                key=f"notes_{current_index}_v{v}",
                help="Any observations or issues with this argument"
            )

            # Classification guide
            with st.expander("📖 Classification Guide"):
                st.markdown("""
                **STEEP**: The speaker indicates labor market conditions
                SIGNIFICANTLY affect inflation.
                - Causal language: "drives", "causes", "leads to"
                - Concern: "will feed into", "translate to"
                - Example: "Tight labor markets are driving wage pressures
                  that will feed into core inflation"

                **FLAT**: The speaker indicates labor markets have
                LITTLE or NO effect on inflation.
                - Disconnection: "despite", "hasn't translated"
                - Skepticism: "broken", "dead", "no longer valid"
                - Example: "Despite unemployment below 4%, we've seen
                  no acceleration in inflation"

                **MODERATE**: The speaker indicates a QUALIFIED or
                PARTIAL relationship.
                - Hedging: "some", "modest", "limited"
                - Example: "Tight labor may generate some inflation
                  pressure, but effects are modest"

                **NONE** (default): No Phillips curve belief expressed.
                - Mentions labor OR inflation, but not both
                - Mentions both but no causal connection
                - Pure description without interpreting relationship
                """)

        # Navigation
        st.markdown("---")
        col_prev, col_save, col_next, col_jump = st.columns([1, 2, 1, 2])

        with col_prev:
            if st.button("◀ Previous", disabled=(current_index == 0), use_container_width=True):
                st.session_state.current_index -= 1
                st.rerun()

        with col_save:
            if st.button("💾 Save & Continue", type="primary", use_container_width=True):
                # Lock coder name on first save
                if st.session_state.locked_coder_name is None:
                    st.session_state.locked_coder_name = coder_name
                
                result = {
                    'coding_id': coding_id,
                    'coder_name': st.session_state.locked_coder_name,
                    'classification': classification,
                    'notes': notes,
                    'coded_at': datetime.now().isoformat()
                }

                # Update or append
                existing_idx = None
                for i, r in enumerate(st.session_state.results):
                    if r['coding_id'] == coding_id:
                        existing_idx = i
                        break

                if existing_idx is not None:
                    st.session_state.results[existing_idx] = result
                else:
                    st.session_state.results.append(result)

                st.session_state.coded_ids.add(coding_id)

                st.success(f"Saved! ({len(st.session_state.results)} total)")

                # Move to next
                if current_index < total_arguments - 1:
                    st.session_state.current_index += 1
                    st.rerun()

        with col_next:
            if st.button("Skip ▶", disabled=(current_index == total_arguments - 1), use_container_width=True):
                st.session_state.current_index += 1
                st.rerun()

        with col_jump:
            # IMPORTANT: Widget key includes version number
            jump_to = st.number_input(
                "Jump to:",
                min_value=1,
                max_value=total_arguments,
                value=current_index + 1,
                step=1,
                key=f"jump_{current_index}_v{v}"
            )
            if st.button("Go", use_container_width=True):
                st.session_state.current_index = jump_to - 1
                st.rerun()

    else:
        st.success("🎉 All arguments have been reviewed!")
        st.info(f"Total coded: {len(st.session_state.coded_ids)} / {total_arguments}")

        st.markdown("### Download your results:")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_name = coder_name.lower().replace(' ', '_')
        filename = f"coded_{safe_name}_phillips_{timestamp}.csv"

        st.download_button(
            label="📥 Download Results CSV",
            data=get_results_csv(st.session_state.results),
            file_name=filename,
            mime="text/csv",
            type="primary"
        )

        if st.button("Return to Start"):
            st.session_state.current_index = 0
            st.rerun()


if __name__ == "__main__":
    main()