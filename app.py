import streamlit as st
import requests
import json
import os

# ---------------------- Core Configuration (✅ 你的原版字典，无任何修改) ----------------------
CAR_PDF_MASTER = {
    "4x2 Tractor Head | 4x2 رأس جرار": {
        "4x2 Tractor AMT High Roof Standard (Leaf Spring) 420HP | جرار 4x2 AMT سقف عالي قياسي (نوابض ورقية) 420 حصان": "JH6_4x2 AMT_High_Roof_Standard_Tractor_Leaf_spring_420HP.pdf",
        "4x2 Tractor AMT High Roof Standard (Air Suspension) 420HP | جرار 4x2 AMT سقف عالي قياسي (تعليق هوائي) 420 حصان": "JH6_4x2_AMT_High_Roof_Standard_Tractor_Air_Suspension_420HP.pdf",
        "4x2 Tractor AMT High Roof Standard (Air Suspension) 460HP | جرار 4x2 AMT سقف عالي قياسي (تعليق هوائي) 460 حصان": "JH6_4x2_AMT_High_Roof_Standard_Tractor_Air_Suspension_460HP.pdf",
        "4x2 Tractor AMT Flat Roof Multifunction (Leaf Spring) 420HP | جرار 4x2 AMT سقف مسطح متعدد الوظائف (نوابض ورقية) 420 حصان": "JH6_4x2_AMT_Flat_Roof_Multifunction_Tractor_Leaf_Spring_420HP.pdf",
        "4x2 Tractor AMT High Roof Multifunction (Leaf Spring) 420HP | جرار 4x2 AMT سقف عالي متعدد الوظائف (نوابض ورقية) 420 حصان": "JH6_4x2_AMT_High_Roof_Multifunction_Tractor_Leaf_Spring_420HP.pdf",
        "4x2 Tractor MT Flat Roof Multifunction (Leaf Spring) 420HP | جرار 4x2 MT سقف مسطح متعدد الوظائف (نوابض ورقية) 420 حصان": "JH6_4x2_MT_Flat_Roof_Multifunction_Tractor_Leaf_Spring_420HP.pdf",
        "4x2 Tractor MT Flat Roof Heavy Duty (Leaf Spring) 420HP (Double Reduction) | جرار 4x2 MT سقف مسطح للخدمة الشاقة (نوابض ورقية) 420 حصان (تخفيض مزدوج)": "JH6_4x2_MT_Flat_Roof_Heavy_Duty_Tractor_Leaf_Spring_420HP_Double_Reduction.pdf",
    },
    "6x4 Tractor Head | 6x4 رأس جرار": {
        "6x4 Tractor MT (315 Tire) | جرار 6x4 MT (إطار 315)": "JH6_6x4_MT_Tractor_315_Tire.pdf",
        "6x4 Tractor MT 420HP | جرار 6x4 MT 420 حصان": "JH6_6x4_MT_Tractor_420HP.pdf",
        "6x4 Tractor MT 550HP | جرار 6x4 MT 550 حصان": "JH6_6x4_MT_Tractor_550HP.pdf"
    },
    "6x4 Dumper | 6x4 قلابة": {
        "6x4 Dumper MT 390HP | قلابة 6x4 MT 390 حصان": "JH6_6x4_MT_Dumper_390HP.pdf",
        "6x4 Dumper MT 420HP | قلابة 6x4 MT 420 حصان": "JH6_6x4_MT_Dumper_420HP.pdf"
    },
    "6x4 Boom Crane | 6x4 رافعة": {
        "6x4 Boom Crane MT 390HP | رافعة 6x4 MT 390 حصان": "JH6_6x4_MT_Boom_Crane_390HP.pdf"
    },
    "Hook Arm | ذراع خطاف": {
        "6x4 Hook Arm | ذراع خطاف 6x4": ""    
    },
    "6x4 Water Tanker | 6x4 صهريج مياه": {
        "6x4 Water Tanker MT 390HP | صهريج مياه 6x4 MT 390 حصان": "JH6_6x4_MT_Water_Tanker_390HP.pdf"
    },
    "8x4 Dumper | 8x4 قلابة": {
        "8x4 Dumper MT 390HP | قلابة 8x4 MT 390 حصان": "JH6_8x4_MT_Dumper_390HP.pdf",
        "8x4 Dumper MT 420HP | قلابة 8x4 MT 420 حصان": "JH6_8x4_MT_Dumper_420HP.pdf"
    },
    "8x4 Mixer | 8x4 خلاطة": {
        "8x4 Mixer MT 390HP | خلاطة 8x4 MT 390 حصان": "JH6_8x4_MT_Mixer_390HP.pdf"
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
    if "selected_main" not in st.session_state:
        st.session_state.selected_main = []
    if "selected_sub_models" not in st.session_state:
        st.session_state.selected_sub_models = []
    if "submitted" not in st.session_state:
        st.session_state.submitted = False

    if st.session_state.submitted:
        show_thank_you_page()
        return

    st.set_page_config(page_title="Purchase Intention | نية الشراء", page_icon="🚛", layout="centered")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("Fawtrucks.png", use_column_width=True)
    st.markdown("<h1 style='text-align: center; font-size: 28px;'>Welcome to ALQAFLA | مرحبا بكم في ALQAFLA</h1>",unsafe_allow_html=True)
    st.divider()

    # 1. Main Category Selection
    st.markdown("### ✅ Vehicle Category | فئة السيارة")
    st.markdown("##### (Tick the vehicle type you need / اضغط على نوع السيارة المطلوبة)")
    cols = st.columns(3)
    for idx, m in enumerate(MAIN_MODELS):
        with cols[idx%3]:
            checked = st.checkbox(m, key=f"m_{m}", value=m in st.session_state.selected_main)
            if checked and m not in st.session_state.selected_main:
                st.session_state.selected_main.append(m)
            elif not checked and m in st.session_state.selected_main:
                st.session_state.selected_main.remove(m)

    # 2. Sub Model Selection (Checkbox Only / No Quantity)
    if st.session_state.selected_main:
        st.markdown("### ✅ Specific Vehicle Model | نموذج السيارة التفصيلي")
        st.markdown("##### (Tick the specific model / اضغط على النموذج التفصيلي)")
        st.markdown("---")
        for m in st.session_state.selected_main:
            st.subheader(m)
            for s in CAR_CONFIG[m]:
                is_checked = st.checkbox(f"📌 {s}", key=f"s_{s}", value=s in st.session_state.selected_sub_models)
                if is_checked and s not in st.session_state.selected_sub_models:
                    st.session_state.selected_sub_models.append(s)
                elif not is_checked and s in st.session_state.selected_sub_models:
                    st.session_state.selected_sub_models.remove(s)

    # 3. Customer Info (✅ Delete National Address，only 2 fields)
    st.markdown("---")
    st.markdown("### 📝 Customer Information | معلومات العميل *")
    c_name = st.text_input("1. Company Name / اسم الشركة *", placeholder="Full name of your company / الاسم الكامل للشركة")
    phone = st.text_input("2. Phone Number / رقم الهاتف *", placeholder="Mobile/landline number / رقم الجوال/الهاتف الثابت")

    # 4. Submit Button
    st.markdown("---")
    submit = st.button("Submit Inquiry | أرسل الاستفسار", use_container_width=True)

    # 5. Submit Logic
    if submit:
        err = []
        if not c_name: err.append("Company Name / اسم الشركة")
        if not phone: err.append("Phone Number / رقم الهاتف")
        if err:
            st.error(f"Required fields missing: {', '.join(err)} | الحقول المطلوبة مفقودة: {', '.join(err)}")
            return

        msg = f"""
New Purchase Inquiry [ALQAFLA]
1. Company Name: {c_name}
2. Phone Number: {phone}
3. Selected Vehicle Models:
"""
        if st.session_state.selected_sub_models:
            for model in st.session_state.selected_sub_models:
                msg += f"   - {model.split(' | ')[0]}\n"
        else:
            msg += "   - No models selected\n"

        try:
            res = requests.post(FEISHU_WEBHOOK,data=json.dumps({"msg_type":"text","content":{"text":msg.strip()}}),headers={"Content-Type":"application/json"})
            res_json = res.json()
            if res.status_code == 200 and res_json.get("code") == 0:
                st.session_state.submitted = True
                st.rerun()
            else:
                st.error(f"❌ Submission failed | فشل الإرسال: {res_json.get('msg','Error')}")
        except Exception as e:
            st.error(f"❌ System error | خطأ في النظام: {str(e)}")

def show_thank_you_page():
    st.set_page_config(page_title="Thank You | شكرًا", page_icon="✅", layout="centered")
    st.title("✅ Submission Successful | تم الإرسال بنجاح")
    st.header("Thank you for your inquiry | شكرًا لاستفسارك")
    st.markdown("We will contact you as soon as possible | سنقوم بالتواصل معك في أقرب وقت")
    st.markdown("---")

    st.subheader("📄 Download Brochures | تنزيل الكتيبات")
    selected_models = st.session_state.selected_sub_models
    if not selected_models:
        st.info("No models selected | لم يتم تحديد أي نماذج")
    else:
        for idx, model in enumerate(selected_models):
            pdf_filename = PDF_MAP.get(model)
            if pdf_filename and pdf_filename.strip():
                try:
                    with open(pdf_filename, "rb") as f:
                        st.download_button(label=f"📥 Download: {model.split(' | ')[0]}",data=f,file_name=pdf_filename,mime="application/pdf",use_container_width=True,key=f"dl_{idx}")
                except FileNotFoundError:
                    st.warning(f"⚠️ File not found | الملف غير موجود : {pdf_filename}")
            else:
                st.warning(f"⚠️ No brochure available | لا يوجد كتيب متاح : {model.split(' | ')[0]}")

    st.markdown("---")
    if st.button("🔙 Back to Homepage | العودة للصفحة الرئيسية", use_container_width=True):
        st.session_state.submitted = False
        st.session_state.selected_main = []
        st.session_state.selected_sub_models = []
        st.rerun()

if __name__ == "__main__":
    main()
