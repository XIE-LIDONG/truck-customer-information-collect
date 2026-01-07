import streamlit as st
import requests
import json
import os

# ---------------------- Core Configuration (Only modify this dict!) ----------------------
# Format: {
#     "Main Category": {
#         "Sub-Model Display Name": "Corresponding PDF filename.pdf",
#         ...
#     },
#     ...
# }
CAR_PDF_MASTER = {
    # 1. 4x2 Tractor
    "4x2 Tractor": {
        "AMT High Roof Standard (Leaf Spring) 420HP": "JH6_4x2 AMT_High_Roof_Standard_Tractor_Leaf_spring_420HP.pdf",
        "AMT Flat Roof Multifunction (Leaf Spring) 420HP": "JH6_4x2_AMT_Flat_Roof_Multifunction_Tractor_Leaf_Spring_420HP.pdf",
        "AMT High Roof Multifunction (Leaf Spring) 420HP": "JH6_4x2_AMT_High_Roof_Multifunction_Tractor_Leaf_Spring_420HP.pdf",
        "AMT High Roof Standard (Air Suspension) 420HP": "JH6_4x2_AMT_High_Roof_Standard_Tractor_Air_Suspension_420HP.pdf",
        "AMT High Roof Standard (Air Suspension) 460HP": "JH6_4x2_AMT_High_Roof_Standard_Tractor_Air_Suspension_460HP.pdf",
        "MT Flat Roof Heavy Duty (Leaf Spring) 420HP (Double Reduction)": "JH6_4x2_MT_Flat_Roof_Heavy_Duty_Tractor_Leaf_Spring_420HP_Double_Reduction.pdf",
        "MT Flat Roof Multifunction (Leaf Spring) 420HP": "JH6_4x2_MT_Flat_Roof_Multifunction_Tractor_Leaf_Spring_420HP.pdf"
    },

    # 2. 6x4 Tractor
    "6x4 Tractor": {
        "MT Standard (315 Tire)": "JH6_6x4_MT_Tractor_315_Tire.pdf",
        "MT Standard 420HP": "JH6_6x4_MT_Tractor_420HP.pdf",
        "MT Standard 550HP": "JH6_6x4_MT_Tractor_550HP.pdf"
    },

    # 3. 6x4 Dumper
    "6x4 Dumper": {
        "MT Standard 390HP": "JH6_6x4_MT_Dumper_390HP.pdf",
        "MT Standard 420HP": "JH6_6x4_MT_Dumper_420HP.pdf"
    },

    # 4. 6x4 Water Tanker
    "6x4 Water Tanker": {
        "MT Standard 390HP": "JH6_6x4_MT_Water_Tanker_390HP.pdf"
    },

    # 5. 6x4 Boom Crane
    "6x4 Boom Crane": {
        "MT Standard 390HP": "JH6_6x4_MT_Boom_Crane_390HP.pdf"
    },

    # 6. 8x4 Dumper
    "8x4 Dumper": {
        "MT Standard 390HP": "JH6_8x4_MT_Dumper_390HP.pdf",
        "MT Standard 420HP": "JH6_8x4_MT_Dumper_420HP.pdf"
    },

    # 7. 8x4 Mixer
    "8x4 Mixer": {
        "MT Standard 390HP": "JH6_8x4_MT_Mixer_390HP.pdf"
    }
}

# Feishu Robot Configuration (No frequent modification needed)
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/d849efbe-0ce8-42e8-85f5-6385d25d4542"

# Custom Styles (No frequent modification needed)
st.markdown("""
<style>
.stButton>button {background-color: #0066cc; color: white; border-radius: 5px;}
.stTextInput>div>div>input {border-radius: 5px;}
.stCheckbox>label {font-size: 16px;}
.stDownloadButton>button {background-color: #28a745; color: white; border-radius: 5px;}
</style>
""", unsafe_allow_html=True)

# ---------------------- Auto Parse Configuration (No modification needed) ----------------------
# Extract from master dict: main model list, sub-model mapping, PDF mapping
# 1. Main model list (checkboxes displayed on page)
MAIN_MODELS = list(CAR_PDF_MASTER.keys())
# 2. Sub-model mapping (main → sub list)
CAR_CONFIG = {main: list(sub_pdf.keys()) for main, sub_pdf in CAR_PDF_MASTER.items()}
# 3. PDF mapping (sub-model → PDF filename)
PDF_MAP = {}
for main, sub_pdf in CAR_PDF_MASTER.items():
    PDF_MAP.update(sub_pdf)

# ---------------------- Page Logic (No modification needed) ----------------------
def main():
    # Initialize session_state
    if "selected_main" not in st.session_state:
        st.session_state.selected_main = []
    if "submodel_qty" not in st.session_state:
        st.session_state.submodel_qty = {}
    if "submitted" not in st.session_state:
        st.session_state.submitted = False  # Submission success flag

    # Show thank you page if submitted successfully
    if st.session_state.submitted:
        show_thank_you_page()
        return

    # Show form page if not submitted
    st.set_page_config(page_title="FAW Vehicle Inquiry Form", page_icon="🚛", layout="centered")
    st.title("🚛 FAW Vehicle Inquiry Form")
    st.divider()

    # 1. Basic Information
    c_name = st.text_input("1. Company Name *", placeholder="Full name of your company")
    u_name = st.text_input("2. Contact Person", placeholder="Your name")
    phone = st.text_input("3. Contact Phone *", placeholder="Mobile/landline number")
    addr = st.text_area("4. Company Address", placeholder="Detailed address", height=100)

    # 2. Main Model Selection (auto read from MAIN_MODELS)
    st.markdown("### 5. Intended Vehicle Categories (Check applicable)")
    cols = st.columns(3)
    for idx, m in enumerate(MAIN_MODELS):
        with cols[idx%3]:
            checked = st.checkbox(m, key=f"m_{m}", value=m in st.session_state.selected_main)
            if checked and m not in st.session_state.selected_main:
                st.session_state.selected_main.append(m)
            elif not checked and m in st.session_state.selected_main:
                st.session_state.selected_main.remove(m)

    # 3. Sub-model & Quantity (auto read from CAR_CONFIG)
    if st.session_state.selected_main:
        st.markdown("### 5.1 Specific Models & Quantity (Default: 0)")
        st.markdown("---")
        for m in st.session_state.selected_main:
            st.subheader(m)
            for s in CAR_CONFIG[m]:
                if s not in st.session_state.submodel_qty:
                    st.session_state.submodel_qty[s] = 0
                col1, col2 = st.columns([4,1])
                with col1: st.write(f"📌 {s}")
                with col2:
                    q = st.number_input(
                        f"{s} Quantity", min_value=0, value=st.session_state.submodel_qty[s], step=1, key=f"q_{s}"
                    )
                    st.session_state.submodel_qty[s] = q

    # 4. Submit Button
    st.markdown("---")
    submit = st.button("Submit Inquiry", use_container_width=True)

    # 5. Submission Logic
    if submit:
        # Validate required fields
        err = []
        if not c_name: err.append("Company Name")
        if not phone: err.append("Contact Phone")
        
        if err:
            st.error(f"Required fields missing: {', '.join(err)}")
            return

        # Construct Feishu message
        msg = f"""
Customer Information【FAW】FAW Vehicle Inquiry
1. Company Name: {c_name}
2. Contact Person: {u_name if u_name else "Not provided"}
3. Phone Number: {phone}
4. Address: {addr if addr else "Not provided"}
5. Vehicle Categories: {', '.join(st.session_state.selected_main) if st.session_state.selected_main else "Not selected"}
6. Purchase Details:
"""
        has_data = False
        for s, q in st.session_state.submodel_qty.items():
            if q > 0:
                msg += f"   - {s}: {q} unit(s)\n"
                has_data = True
        if not has_data: msg += "   - No specific models selected\n"

        # Send to Feishu
        try:
            res = requests.post(
                FEISHU_WEBHOOK,
                data=json.dumps({"msg_type":"text","content":{"text":msg.strip()}}),
                headers={"Content-Type":"application/json"}
            )
            res_json = res.json()
            if res.status_code == 200 and res_json.get("code") == 0:
                st.session_state.submitted = True  # Mark submission success
                st.rerun()  # Redirect to thank you page
            else:
                st.error(f"❌ Submission failed: {res_json}")
        except Exception as e:
            st.error(f"❌ System error: {str(e)}")

# ---------------------- Thank You Page (PDF download auto read from PDF_MAP) ----------------------
def show_thank_you_page():
    st.set_page_config(page_title="Submission Successful | FAW Inquiry", page_icon="✅", layout="centered")
    st.title("✅ Submission Successful! Thank you for your inquiry")
    st.markdown("---")
    st.markdown("### 📞 We will contact you shortly")
    st.markdown("### 📄 You can download detailed information for selected models:")
    st.markdown("---")

    # Filter models with quantity > 0 and generate download buttons
    download_models = [s for s, q in st.session_state.submodel_qty.items() if q > 0]
    if not download_models:
        st.info("No specific models selected, no downloadable materials available")
    else:
        for model in download_models:
            pdf_filename = PDF_MAP.get(model)
            if pdf_filename:
                # Check file existence (for local testing)
                if os.path.exists(pdf_filename):
                    with open(pdf_filename, "rb") as f:
                        st.download_button(
                            label=f"📥 Download {model} Details",
                            data=f,
                            file_name=pdf_filename,
                            mime="application/pdf",
                            use_container_width=True
                        )
                else:
                    st.warning(f"⚠️ {pdf_filename} not found, please confirm the file is uploaded")
            else:
                st.warning(f"No materials available for {model}")

    # Return to homepage button
    if st.button("Return to Inquiry Form", use_container_width=True):
        st.session_state.submitted = False
        st.session_state.selected_main = []
        st.session_state.submodel_qty = {}
        st.rerun()

if __name__ == "__main__":
    main()
