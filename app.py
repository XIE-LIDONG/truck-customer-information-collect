import streamlit as st
import requests
import json
import os

# ---------------------- Core Configuration (Only modify this dict!) ----------------------
CAR_PDF_MASTER = {
    # 1. 4x2 Tractor
    "4x2 Tractor": {
        "4x2 Tractor AMT High Roof Standard (Leaf Spring) 420HP": "JH6_4x2 AMT_High_Roof_Standard_Tractor_Leaf_spring_420HP.pdf",
        "4x2 Tractor AMT High Roof Standard (Air Suspension) 420HP": "JH6_4x2_AMT_High_Roof_Standard_Tractor_Air_Suspension_420HP.pdf",
        "4x2 Tractor AMT High Roof Standard (Air Suspension) 460HP": "JH6_4x2_AMT_High_Roof_Standard_Tractor_Air_Suspension_460HP.pdf",
        "4x2 Tractor AMT Flat Roof Multifunction (Leaf Spring) 420HP": "JH6_4x2_AMT_Flat_Roof_Multifunction_Tractor_Leaf_Spring_420HP.pdf",
        "4x2 Tractor AMT High Roof Multifunction (Leaf Spring) 420HP": "JH6_4x2_AMT_High_Roof_Multifunction_Tractor_Leaf_Spring_420HP.pdf",
        "4x2 Tractor MT Flat Roof Multifunction (Leaf Spring) 420HP": "JH6_4x2_MT_Flat_Roof_Multifunction_Tractor_Leaf_Spring_420HP.pdf",  # 核心修复：加了逗号
        "4x2 Tractor MT Flat Roof Heavy Duty (Leaf Spring) 420HP (Double Reduction)": "JH6_4x2_MT_Flat_Roof_Heavy_Duty_Tractor_Leaf_Spring_420HP_Double_Reduction.pdf",
    },

    # 2. 6x4 Tractor
    "6x4 Tractor": {
        "6x4 Tractor MT (315 Tire)": "JH6_6x4_MT_Tractor_315_Tire.pdf",
        "6x4 Tractor MT 420HP": "JH6_6x4_MT_Tractor_420HP.pdf",
        "6x4 Tractor MT 550HP": "JH6_6x4_MT_Tractor_550HP.pdf"
    },

    # 3. 6x4 Dumper
    "6x4 Dumper": {
        "6x4 Dumper MT 390HP": "JH6_6x4_MT_Dumper_390HP.pdf",
        "6x4 Dumper MT 420HP": "JH6_6x4_MT_Dumper_420HP.pdf"
    },

    # 4. 6x4 Water Tanker
    "6x4 Water Tanker": {
        "6x4 Water Tanker MT 390HP": "JH6_6x4_MT_Water_Tanker_390HP.pdf"
    },

    # 5. 6x4 Boom Crane
    "6x4 Boom Crane": {
        "6x4 Boom Crane MT 390HP": "JH6_6x4_MT_Boom_Crane_390HP.pdf"
    },

    # 6. 8x4 Dumper
    "8x4 Dumper": {
        "8x4 Dumper MT 390HP": "JH6_8x4_MT_Dumper_390HP.pdf",
        "8x4 Dumper MT 420HP": "JH6_8x4_MT_Dumper_420HP.pdf"
    },

    # 7. 8x4 Mixer
    "8x4 Mixer": {
        "8x4 Mixer MT 390HP": "JH6_8x4_MT_Mixer_390HP.pdf"
    },
    # 8. 6✖4 hook Arm
    "Hook Arm":{
    "6x4 Hook Arm":""    
    }
}

# Feishu Robot Configuration
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/d849efbe-0ce8-42e8-85f5-6385d25d4542"

# Custom Styles
st.markdown("""
<style>
.stButton>button {background-color: #0066cc; color: white; border-radius: 5px;}
.stTextInput>div>div>input {border-radius: 5px;}
.stCheckbox>label {font-size: 16px;}
.stDownloadButton>button {background-color: #28a745; color: white; border-radius: 5px;}
</style>
""", unsafe_allow_html=True)

# ---------------------- Auto Parse Configuration ----------------------
MAIN_MODELS = list(CAR_PDF_MASTER.keys())
CAR_CONFIG = {main: list(sub_pdf.keys()) for main, sub_pdf in CAR_PDF_MASTER.items()}
PDF_MAP = {}
for main, sub_pdf in CAR_PDF_MASTER.items():
    PDF_MAP.update(sub_pdf)

# ---------------------- Page Logic ----------------------
def main():
    # Initialize session_state
    if "selected_main" not in st.session_state:
        st.session_state.selected_main = []
    if "submodel_qty" not in st.session_state:
        st.session_state.submodel_qty = {}  
    if "submitted" not in st.session_state:
        st.session_state.submitted = False

    # Show thank you page if submitted
    if st.session_state.submitted:
        show_thank_you_page()
        return

    # Form page
    st.set_page_config(page_title="FAW Vehicle Inquiry Form", page_icon="🚛", layout="centered")
    st.title("ALQAFLA&FAW Truck Form")
    st.divider()

    # 1. Basic Information
    c_name = st.text_input("1. Company Name *", placeholder="Full name of your company")
    phone = st.text_input("3. Phone NUmber *", placeholder="Mobile/landline number")
    addr = st.text_area("4. National Address", placeholder="Detailed address", height=100)

    # 2. Main Model Selection
    st.markdown("### Choose your favorite trucks model from below")
    cols = st.columns(3)
    for idx, m in enumerate(MAIN_MODELS):
        with cols[idx%3]:
            checked = st.checkbox(m, key=f"m_{m}", value=m in st.session_state.selected_main)
            if checked and m not in st.session_state.selected_main:
                st.session_state.selected_main.append(m)
            elif not checked and m in st.session_state.selected_main:
                st.session_state.selected_main.remove(m)

    # 3. Sub-model & Quantity
    if st.session_state.selected_main:
        st.markdown("### 5.1 Specific Models & Quantity ")
        st.markdown("---")
        for m in st.session_state.selected_main:
            st.subheader(m)
            for s in CAR_CONFIG[m]:
    
                unique_key = f"{m}_{s}"

                if unique_key not in st.session_state.submodel_qty:
                    st.session_state.submodel_qty[unique_key] = 0
                
                col1, col2 = st.columns([4,1])
                with col1: 
                    st.write(f"📌 {s}")
                with col2:
     
                    q = st.number_input(
                        "Quantity", 
                        min_value=0, 
                        value=st.session_state.submodel_qty[unique_key], 
                        step=1, 
                        key=f"q_{unique_key}"  # 唯一key：q_4x2 Tractor_AMT High Roof...
                    )
        
                    st.session_state.submodel_qty[unique_key] = q

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
2. Phone Number: {phone}
3. Address: {addr if addr else "Not provided"}
4. Vehicle Categories: {', '.join(st.session_state.selected_main) if st.session_state.selected_main else "Not selected"}
5. Purchase Details:
"""
        has_data = False

        for unique_key, q in st.session_state.submodel_qty.items():
            if q > 0:
            
                sub_model = unique_key.split("_", 1)[1]  # 从"4x2 Tractor_AMT High..."提取"AMT High..."
                msg += f"   - {sub_model}: {q} unit(s)\n"
                has_data = True
        if not has_data: 
            msg += "   - No specific models selected\n"

        # Send to Feishu
        try:
            res = requests.post(
                FEISHU_WEBHOOK,
                data=json.dumps({"msg_type":"text","content":{"text":msg.strip()}}),
                headers={"Content-Type":"application/json"}
            )
            res_json = res.json()
            if res.status_code == 200 and res_json.get("code") == 0:
                st.session_state.submitted = True
                st.rerun()
            else:
                st.error(f"❌ Submission failed: {res_json}")
        except Exception as e:
            st.error(f"❌ System error: {str(e)}")


def show_thank_you_page():
    st.set_page_config(page_title="Submission Successful | FAW Inquiry", page_icon="✅", layout="centered")
    st.title("✅ Submission Successful! Thank you for your inquiry")
    st.markdown("---")
    st.markdown("### 📄 You can download detailed information for selected models:")
    st.markdown("---")


    download_models = []
    for unique_key, q in st.session_state.submodel_qty.items():
        if q > 0:
            sub_model = unique_key.split("_", 1)[1]
            download_models.append(sub_model)

    if not download_models:
        st.info("No specific models selected, no downloadable materials available")
    else:
        for idx, model in enumerate(download_models):
            pdf_filename = PDF_MAP.get(model)
            if pdf_filename:
                try:
                    with open(pdf_filename, "rb") as f:
                        st.download_button(
                            label=f"📥 {pdf_filename}",
                            data=f,
                            file_name=pdf_filename,
                            mime="application/pdf",
                            use_container_width=True,
                            key=f"download_btn_{idx}" 
                        )
                except FileNotFoundError:
                    st.warning(f"⚠️ {pdf_filename} not found! Please check if the file is uploaded correctly.")
            else:
                st.warning(f"No PDF file configured for: {model}")

    # Return to homepage
    if st.button("Return to Inquiry Form", use_container_width=True):
        # 清空所有session_state
        st.session_state.submitted = False
        st.session_state.selected_main = []
        st.session_state.submodel_qty = {}
        st.rerun()

if __name__ == "__main__":
    main()
