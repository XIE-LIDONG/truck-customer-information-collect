import streamlit as st
import requests
import json
import os
from datetime import datetime

CAR_PDF_MASTER = {
    "4x2 Tractor Head | رأس جرار 4x2": {
        "4x2 Tractor AMT Mega Air Suspension 420HP | رأس جرار 4x2 AMT ميجا مع تعليق هوائي 420 حصان": 
            "JH6_4x2_AMT_High_Roof_Standard_Tractor_Air_Suspension_420HP.pdf",

        "4x2 Tractor AMT Mega Leaf Spring 420HP | رأس جرار 4x2 AMT ميجا مع نوابض ورقية 420 حصان": 
            "JH6_4x2_AMT_High_Roof_Multifunction_Tractor_Leaf_Spring_420HP.pdf",

        "4x2 Tractor AMT Half Mega Leaf Spring 420HP | رأس جرار 4x2 AMT هاف ميجا مع نوابض ورقية 420 حصان": 
            "JH6_4x2_AMT_Flat_Roof_Multifunction_Tractor_Leaf_Spring_420HP.pdf",

        "4x2 Tractor MT Half Mega Leaf Spring 420HP | رأس جرار 4x2 MT هاف ميجا مع نوابض ورقية 420 حصان": 
            "JH6_4x2_MT_Flat_Roof_Multifunction_Tractor_Leaf_Spring_420HP.pdf"
    },

    "6x4 Tractor Head | رأس جرار 6x4": {
        "6x4 Tractor MT 420HP | رأس جرار 6x4 MT 420 حصان": 
            "JH6_6x4_MT_Tractor_420HP.pdf"
    },

    "6x4 Dumper | شاحنة قلابة 6x4": {
        "6x4 Dumper MT 390HP | شاحنة قلابة 6x4 MT 390 حصان": 
            "JH6_6x4_MT_Dumper_390HP.pdf"
    },

    "6x4 Water Tanker | شاحنة صهريج مياه 6x4": {
        "6x4 Water Tanker MT 390HP | شاحنة صهريج مياه 6x4 MT 390 حصان": 
            "JH6_6x4_MT_Water_Tanker_390HP.pdf"
    },

    "8x4 Mixer | شاحنة خلاطة 8x4": {
        "8x4 Mixer MT 390HP | شاحنة خلاطة 8x4 MT 390 حصان": 
            "JH6_8x4_MT_Mixer_390HP.pdf"
    }
}

FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/d849efbe-0ce8-42e8-85f5-6385d25d4542"

st.markdown("""
<style>
.stButton>button {background-color: #005a31; color: #fff; border-radius: 8px; font-weight: bold; border:1px solid #f1c40f;}
.stButton>button:hover {background-color: #004725; color: #f1c40f;}
.stTextInput>div>div>input {border-radius: 8px; border:1px solid #005a31; padding:8px;}
.stCheckbox>label {font-size: 15px; line-height: 1.6;}
.stDownloadButton>button {background-color: #f1c40f; color: #005a31; border-radius: 8px; font-weight: bold; border:1px solid #005a31;}
.stDownloadButton>button:hover {background-color: #d4ac0d; color: #fff;}
body {font-family: 'Segoe UI', Arabic, sans-serif;}
</style>
""", unsafe_allow_html=True)

ALL_MODELS = []
PDF_MAP = {}
for main_cat, sub_models in CAR_PDF_MASTER.items():
    for model_name, pdf_path in sub_models.items():
        ALL_MODELS.append(model_name)
        PDF_MAP[model_name] = pdf_path

def main():
    if "selected_models" not in st.session_state:
        st.session_state.selected_models = []
    if "submitted" not in st.session_state:
        st.session_state.submitted = False

    if st.session_state.submitted:
        show_thank_you_page()
        return

    st.set_page_config(page_title="Purchase Intention | نية الشراء", page_icon="🚛", layout="centered")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("Fawtrucks.png", use_column_width=True)
    
    st.markdown("<h3 style='text-align:center; color:#005a31;'>بسم الله الرحمن الرحيم</h3>", unsafe_allow_html=True)
    st.markdown(
    "<h1 style='text-align: center; font-size: 28px; color:#005a31;'>Welcome to ALQAFLA | مرحبا بكم في شركة القافلة</h1>",
    unsafe_allow_html=True
    )
    st.markdown("<h4 style='text-align:center; color:#d4ac0d;'>اللهم بارك فينا و في أعمالنا</h4>", unsafe_allow_html=True)
    st.divider()

    st.markdown("### ✅ Select your trucks | اختر شاحناتك")

    st.divider()
    for idx, model in enumerate(ALL_MODELS):
        is_checked = st.checkbox(model, key=f"model_{idx}", value=model in st.session_state.selected_models)
        if is_checked and model not in st.session_state.selected_models:
            st.session_state.selected_models.append(model)
        elif not is_checked and model in st.session_state.selected_models:
            st.session_state.selected_models.remove(model)

    st.markdown("---")

    c_name = st.text_input("1. Name / الاسم *", placeholder="Fill in your name  / أدخل اسمك")
    phone = st.text_input("2. Phone Number / رقم الهاتف *", placeholder="Mobile/landline number / رقم الجوال/الهاتف الثابت")

    st.markdown("---")
    submit = st.button("Submit | أرسل", use_container_width=True)

    if submit:
        err = []
        if not c_name: err.append("Company Name / اسم الشركة")
        if not phone: err.append("Phone Number / رقم الهاتف")
        
        if err:
            st.error(f"Required fields missing: {', '.join(err)} | الحقول المطلوبة مفقودة: {', '.join(err)}")
            return
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"""
New Purchase Inquiry Received [ALQAFLA]
📅 Submission Time: {current_time}
1. Company Name: {c_name}
2. Contact Phone Number: {phone}
3. Selected Vehicle Models:
"""
        has_data = False
        if st.session_state.selected_models:
            for model in st.session_state.selected_models:
                msg += f"   - {model.split(' | ')[0]}\n"
                has_data = True
        if not has_data: 
            msg += "   - No specific models selected\n"

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
                st.error(f"❌ Submission failed | فشل الإرسال: {res_json.get('msg','Unknown Error')}")
        except Exception as e:
            st.error(f"❌ System error | خطأ في النظام: {str(e)}")

def show_thank_you_page():
    st.set_page_config(page_title="Thank You | شكرًا", page_icon="✅", layout="centered")
    st.markdown("<h2 style='text-align:center; color:#005a31;'>الحمد لله على النجاح ✅</h2>", unsafe_allow_html=True)
    st.title("✅ Submission Successful | تم الإرسال بنجاح")
    st.header("Thank you for your inquiry | شكرًا لاستفسارك الكريم")
    st.markdown("<h4 style='text-align:center; color:#d4ac0d;'>اللهم حفظك و بارك فيك</h4>", unsafe_allow_html=True)
    st.markdown("---")

    st.subheader("📄 Download Vehicle Brochures | تنزيل كتيبات السيارات")
    selected_models = st.session_state.selected_models

    if not selected_models:
        st.info("No models selected | لم يتم تحديد أي نماذج")
    else:
        for idx, model in enumerate(selected_models):
            pdf_filename = PDF_MAP.get(model)
            if pdf_filename and pdf_filename.strip():
                try:
                    with open(pdf_filename, "rb") as f:
                        st.download_button(
                            label=f"📥 {model.split(' | ')[0]}",
                            data=f,
                            file_name=pdf_filename,
                            mime="application/pdf",
                            use_container_width=True,
                            key=f"download_btn_{idx}"
                        )
                except FileNotFoundError:
                    st.warning(f"⚠️ File not found | الملف غير موجود : {pdf_filename}")
            else:
                st.warning(f"⚠️ No brochure available | لا يوجد كتيب متاح : {model.split(' | ')[0]}")

    st.markdown("---")
    if st.button("🔙 Back to Homepage | العودة للصفحة الرئيسية بإذن الله", use_container_width=True):
        st.session_state.submitted = False
        st.session_state.selected_models = []
        st.rerun()

if __name__ == "__main__":
    main()
