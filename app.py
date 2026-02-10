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

st.title("🤖 Scalable Capital AI Platform MVP")
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

    # Input section
    st.subheader("Input")

    # Load sample data button
    if st.button("📝 Load Sample Input"):
        st.session_state.input_text = SAMPLE_INPUTS[selected_template]

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
            with st.spinner("Processing through AI Platform..."):
                config = get_template(selected_template)
                result = gateway.process(selected_template, input_text, config)

            # Store result for display
            st.session_state.last_result = result
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
                st.text_area("", result['original_input'], height=100, disabled=True)
            with col_b:
                st.markdown("**PII Masked Input:**")
                st.text_area("", result['cleaned_input'], height=100, disabled=True)

        with tab2:
            st.metric("Selected Model", result['model_used'])
            st.metric("Processing Cost", f"${result['cost']:.6f}")
            st.metric("Processing Time", f"{result['processing_time']:.2f}s")

        with tab3:
            st.markdown("**Structured Output:**")
            output = result['output']
            if isinstance(output, dict) and 'output' in output:
                # Nested structure from gateway
                final_output = output['output']
            else:
                final_output = output

            st.json(final_output)

            # Show confidence if available
            if isinstance(final_output, dict) and 'confidence' in final_output:
                confidence = final_output['confidence']
                if confidence < 0.8:
                    st.warning(f"⚠️ Low confidence ({confidence:.2%}) - would trigger human review")
                else:
                    st.success(f"✅ High confidence ({confidence:.2%})")

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
    import os
    os.environ['OPENAI_API_KEY'] = api_key
    st.sidebar.success("✅ API key set - using real OpenAI models!")
else:
    st.sidebar.info("Using mock responses for demo")