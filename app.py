import streamlit as st
import requests
import json
import os

# ---------------------- Core Configuration (✅ 你的原版完整字典 一字未改) ----------------------
CAR_PDF_MASTER = {
    # 1. 4x2 Tractor - 4x2 رأس جرار
    "4x2 Tractor Head | 4x2 رأس جرار": {
       
        "4x2 Tractor AMT High Roof Air Suspension 420HP | جرار 4x2 AMT سقف عالي قياسي (تعليق هوائي) 420 حصان": "JH6_4x2_AMT_High_Roof_Standard_Tractor_Air_Suspension_420HP.pdf",
        "4x2 Tractor AMT High Roof Leaf Spring 420HP | جرار 4x2 AMT سقف عالي متعدد الوظائف (نوابض ورقية) 420 حصان": "JH6_4x2_AMT_High_Roof_Multifunction_Tractor_Leaf_Spring_420HP.pdf",
        "4x2 Tractor AMT Flat Roof Leaf Spring 420HP | جرار 4x2 AMT سقف مسطح متعدد الوظائف (نوابض ورقية) 420 حصان": "JH6_4x2_AMT_Flat_Roof_Multifunction_Tractor_Leaf_Spring_420HP.pdf",
        "4x2 Tractor MT Flat Roof Leaf Spring 420HP | جرار 4x2 MT سقف مسطح متعدد الوظائف (نوابض ورقية) 420 حصان": "JH6_4x2_MT_Flat_Roof_Multifunction_Tractor_Leaf_Spring_420HP.pdf"
      
    },
    # 2. 6x4 Tractor - 6x4 رأس جرار
    "6x4 Tractor Head | 6x4 رأس جرار": {
       
        "6x4 Tractor MT 420HP | جرار 6x4 MT 420 حصان": "JH6_6x4_MT_Tractor_420HP.pdf"
       
    },

    # 3. 6x4 Dumper - 6x4 قلابة
    "6x4 Dumper | 6x4 قلابة": {
        "6x4 Dumper MT 390HP | قلابة 6x4 MT 390 حصان": "JH6_6x4_MT_Dumper_390HP.pdf",
        "6x4 Dumper MT 420HP | قلابة 6x4 MT 420 حصان": "JH6_6x4_MT_Dumper_420HP.pdf"
    },
    

    # 6. 6x4 Water Tanker - 6x4 صهريج مياه
    "6x4 Water Tanker | 6x4 صهريج مياه": {
        "6x4 Water Tanker MT 390HP | صهريج مياه 6x4 MT 390 حصان": "JH6_6x4_MT_Water_Tanker_390HP.pdf"
    },

    # 8. 8x4 Mixer - 8x4 خلاطة
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
.stCheckbox>label {font-size: 15px;}
.stDownloadButton>button {background-color: #28a745; color: white; border-radius: 5px;}
</style>
""", unsafe_allow_html=True)

# ---------------------- Auto Parse 自动提取【所有车型平铺，无分级】 ----------------------
ALL_MODELS = []  # 所有车型平铺列表
PDF_MAP = {}     # 车型和PDF的映射关系
for main_cat, sub_models in CAR_PDF_MASTER.items():
    for model_name, pdf_path in sub_models.items():
        ALL_MODELS.append(model_name)
        PDF_MAP[model_name] = pdf_path

# ---------------------- Page Logic ----------------------
def main():
    # Initialize session_state
    if "selected_models" not in st.session_state:
        st.session_state.selected_models = []
    if "submitted" not in st.session_state:
        st.session_state.submitted = False

    # Show thank you page if submitted
    if st.session_state.submitted:
        show_thank_you_page()
        return

    # Form page
    st.set_page_config(page_title="Purchase Intention | نية الشراء", page_icon="🚛", layout="centered")
    # ====== Logo ======
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("Fawtrucks.png", use_column_width=True)
    # ====== Title ======
    st.markdown(
    "<h1 style='text-align: center; font-size: 28px;'>Welcome to ALQAFLA | مرحبا بكم في ALQAFLA</h1>",
    unsafe_allow_html=True
    )
    st.divider()

    # ✅ 核心修改：无分级、所有车型直接平铺勾选 双列布局 美观紧凑
    st.markdown("### ✅ Select Vehicle Models | اختر نماذج السيارات")
    st.markdown("##### (Tick the models you are interested in / اضغط على النماذج التي تهتم بها)")
    st.divider()
    cols = st.columns(2)
    for idx, model in enumerate(ALL_MODELS):
        with cols[idx % 2]:
            is_checked = st.checkbox(model, key=f"model_{idx}", value=model in st.session_state.selected_models)
            if is_checked and model not in st.session_state.selected_models:
                st.session_state.selected_models.append(model)
            elif not is_checked and model in st.session_state.selected_models:
                st.session_state.selected_models.remove(model)

    # ✅ Customer Information (删除地址栏，只有公司名+手机号 两个必填项，纯英阿双语)
    st.markdown("---")
    st.markdown("### 📝 Customer Information | معلومات العميل *")
    c_name = st.text_input("1. Company Name / اسم الشركة *", placeholder="Full name of your company / الاسم الكامل للشركة")
    phone = st.text_input("2. Phone Number / رقم الهاتف *", placeholder="Mobile/landline number / رقم الجوال/الهاتف الثابت")

    # Submit Button
    st.markdown("---")
    submit = st.button("Submit Inquiry | أرسل الاستفسار", use_container_width=True)

    # Submission Logic
    if submit:
        # Validate required fields
        err = []
        if not c_name: err.append("Company Name / اسم الشركة")
        if not phone: err.append("Phone Number / رقم الهاتف")
        
        if err:
            st.error(f"Required fields missing: {', '.join(err)} | الحقول المطلوبة مفقودة: {', '.join(err)}")
            return

        # Construct Feishu message
        msg = f"""
New Purchase Inquiry Received [ALQAFLA]
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
                st.error(f"❌ Submission failed | فشل الإرسال: {res_json.get('msg','Unknown Error')}")
        except Exception as e:
            st.error(f"❌ System error | خطأ في النظام: {str(e)}")

def show_thank_you_page():
    st.set_page_config(page_title="Thank You | شكرًا", page_icon="✅", layout="centered")
    st.title("✅ Submission Successful | تم الإرسال بنجاح")
    st.header("Thank you for your inquiry | شكرًا لاستفسارك")
    st.markdown("We will contact you as soon as possible | سنقوم بالتواصل معك في أقرب وقت")
    st.markdown("---")

    # PDF Download Section
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

    # Return to homepage
    st.markdown("---")
    if st.button("🔙 Back to Homepage | العودة للصفحة الرئيسية", use_container_width=True):
        st.session_state.submitted = False
        st.session_state.selected_models = []
        st.rerun()

if __name__ == "__main__":
    main()
