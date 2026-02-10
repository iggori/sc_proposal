import streamlit as st
import json
from gateway import AIGateway
from templates import get_template, get_template_names, get_template_display_names, SAMPLE_INPUTS

# Initialize gateway (persists across reruns in session state)
if 'gateway' not in st.session_state:
    st.session_state.gateway = AIGateway()

gateway = st.session_state.gateway

# Page config
st.set_page_config(
    page_title="AI Platform MVP Demo",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 SC AI Platform MVP")
st.markdown("**One gateway, multiple use cases, shared guardrails**")

# Sidebar with stats
st.sidebar.header("📊 Platform Stats")
stats = gateway.get_stats()

st.sidebar.metric("Total Requests", stats['requests'])
st.sidebar.metric("Total Cost", f"${stats['total_cost']:.4f}")
if stats['requests'] > 0:
    st.sidebar.metric("Avg Cost/Request", f"${stats['avg_cost_per_request']:.6f}")
    st.sidebar.metric("Avg Confidence", f"{stats['avg_confidence']:.2%}")
    st.sidebar.metric("Avg Processing Time", f"{stats['avg_processing_time']:.2f}s")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.header("🎯 Try the Platform")

    # Template selection
    template_names = get_template_names()
    display_names = get_template_display_names()

    selected_template = st.selectbox(
        "Select Use Case",
        template_names,
        format_func=lambda x: display_names[x]
    )

    # Reset form state when template changes
    if 'last_selected_template' not in st.session_state:
        st.session_state.last_selected_template = selected_template

    if st.session_state.last_selected_template != selected_template:
        # Clear previous results and input when switching templates
        if 'last_result' in st.session_state:
            del st.session_state.last_result
        if 'input_text' in st.session_state:
            del st.session_state.input_text
        st.session_state.last_selected_template = selected_template

    # Input section
    st.subheader("Input")

    # Control buttons
    button_col1, button_col2 = st.columns(2)
    with button_col1:
        if st.button("📝 Load Sample Input"):
            # Clear any previous results when loading new sample
            if 'last_result' in st.session_state:
                del st.session_state.last_result
            st.session_state.input_text = SAMPLE_INPUTS[selected_template]

    with button_col2:
        if st.button("🗑️ Clear Form"):
            # Clear input and results
            if 'input_text' in st.session_state:
                del st.session_state.input_text
            if 'last_result' in st.session_state:
                del st.session_state.last_result

    # Text input
    input_text = st.text_area(
        "Enter your text:",
        value=st.session_state.get('input_text', ''),
        height=150,
        key="input_text"
    )

    # Process button
    if st.button("🚀 Process with AI Platform", type="primary"):
        if input_text.strip():
            if len(input_text) > 10000:
                st.error("Input too long (max 10,000 characters)")
            else:
                with st.spinner("Processing through AI Platform..."):
                    try:
                        config = get_template(selected_template)
                        result = gateway.process(selected_template, input_text, config)
                        # Store result for display
                        st.session_state.last_result = result
                    except Exception as e:
                        st.error(f"Processing failed: {str(e)}")
                        st.exception(e)  # Show full traceback in demo mode
        else:
            st.error("Please enter some text to process")

    # Display results
    if 'last_result' in st.session_state:
        result = st.session_state.last_result

        st.success("✅ Processed successfully!")

        # Show the platform pipeline
        st.subheader("🔧 Platform Pipeline")

        tab1, tab2, tab3, tab4 = st.tabs(["Input Processing", "Model Selection", "Output", "Audit Log"])

        with tab1:
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**Original Input:**")
                st.text_area("Original Input", result['original_input'], height=100, disabled=True, key="original_input_display")
            with col_b:
                st.markdown("**Tokenized Input (sent to LLM):**")
                st.text_area("Tokenized Input", result['tokenized_input'], height=100, disabled=True, key="tokenized_input_display")
            
            if result['pii_tokenized_count'] > 0:
                st.info(f"🔒 {result['pii_tokenized_count']} PII instance(s) tokenized: {', '.join(result['pii_tokens'][:3])}")
                st.caption("💡 Tokens are reversible - backend can retrieve original values, UI shows masked versions")

        with tab2:
            st.metric("Selected Model", result['model_used'])
            st.metric("Processing Cost", f"${result['cost']:.6f}")
            st.metric("Processing Time", f"{result['processing_time']:.2f}s")

        with tab3:
            st.markdown("**Structured Output:**")
            output = result['output']
            if isinstance(output, dict) and 'data' in output:
                # New validation format
                final_output = output['data']
                validation_passed = output.get('validation_passed', False)
                missing_fields = output.get('missing_fields', [])

                # Show validation status
                if validation_passed:
                    st.success("✅ Schema validation passed")
                else:
                    st.warning(f"⚠️ Schema validation failed - missing fields: {missing_fields}")
            else:
                # Fallback for old format
                final_output = output

            # Show both backend and display versions
            col_backend, col_display = st.columns(2)
            
            with col_backend:
                st.markdown("**Backend Output (full PII):**")
                st.caption("Used by system for actions")
                backend_data = result.get('backend_output', {}).get('data', {}) if isinstance(result.get('backend_output'), dict) else {}
                st.json(backend_data if backend_data else final_output)
            
            with col_display:
                st.markdown("**UI Output (masked PII):**")
                st.caption("Shown to users for privacy")
                st.json(final_output)

            # Show confidence if available
            if isinstance(final_output, dict) and 'confidence' in final_output:
                confidence = final_output['confidence']
                if confidence < 0.8:
                    st.warning(f"⚠️ Low confidence ({confidence:.2%}) - would trigger human review")
                else:
                    st.success(f"✅ High confidence ({confidence:.2%})")

            # Show PII tokenization count
            if result.get('pii_tokenized_count', 0) > 0:
                st.success(f"🔒 PII tokenization demonstrated: {result['pii_tokenized_count']} instance(s)")
                st.caption("Notice: Backend has full values, UI shows masked versions")

        with tab4:
            st.markdown("**Audit Trail Entry:**")
            audit_entries = gateway.get_audit_log(1)
            if audit_entries:
                st.json(audit_entries[0])

with col2:
    st.header("📋 Platform Benefits")

    st.markdown("""
    **🎯 One Gateway, Multiple Use Cases**
    - Support tickets → routing
    - Documents → extraction
    - Questions → answers

    **🛡️ Built-in Guardrails**
    - PII anonymization
    - Schema validation
    - Confidence scoring
    - Cost tracking

    **📊 Shared Infrastructure**
    - Audit logging
    - Model routing
    - Cost optimization
    - Compliance ready
    """)

    st.header("🔍 Recent Activity")
    audit_log = gateway.get_audit_log(5)

    if audit_log:
        for entry in reversed(audit_log[-3:]):  # Show last 3
            with st.expander(f"{entry['use_case']} - {entry['timestamp'][:19]}"):
                st.write(f"**Model:** {entry.get('model_used', 'N/A')}")
                st.write(f"**Cost:** ${entry['cost']:.6f}")
                st.write(f"**Confidence:** {entry.get('confidence', 0):.2%}")
                st.write(f"**Time:** {entry['processing_time']:.2f}s")
    else:
        st.info("No activity yet. Try processing some text!")

# Footer
st.markdown("---")
st.markdown("*This MVP demonstrates platform thinking: reusable infrastructure that makes AI adoption safe and efficient at scale.*")

# Instructions
with st.expander("ℹ️ How to Use"):
    st.markdown("""
    1. **Select a use case** from the dropdown
    2. **Load sample input** or enter your own text
    3. **Click "Process"** to see the platform in action
    4. **Explore the tabs** to understand the processing pipeline

    **Key Demo Points:**
    - Same gateway code handles different use cases
    - PII is automatically masked
    - Models are routed based on complexity
    - All interactions are logged for compliance
    - Costs are tracked in real-time
    """)

# Add OpenAI API key input (optional)
st.sidebar.markdown("---")
st.sidebar.subheader("🔑 OpenAI API (Optional)")
api_key = st.sidebar.text_input("API Key", type="password", help="Add your OpenAI API key to use real models instead of mock responses")
if api_key:
    gateway.set_api_key(api_key)  # Securely store in gateway instance
    st.sidebar.success("✅ API key set - using real OpenAI models!")
else:
    st.sidebar.info("Using mock responses for demo")