import streamlit as st
import requests
import json
import os

# ---------------------- Core Configuration (Only modify this dict!) ----------------------
CAR_PDF_MASTER = {
    # 1. 4x2 Tractor - 4x2 رأس جرار
    "4x2 Tractor Head | 4x2 رأس جرار": {
        "4x2 Tractor AMT High Roof Standard (Leaf Spring) 420HP | جرار 4x2 AMT سقف عالي قياسي (نوابض ورقية) 420 حصان": "JH6_4x2 AMT_High_Roof_Standard_Tractor_Leaf_spring_420HP.pdf",
        "4x2 Tractor AMT High Roof Standard (Air Suspension) 420HP | جرار 4x2 AMT سقف عالي قياسي (تعليق هوائي) 420 حصان": "JH6_4x2_AMT_High_Roof_Standard_Tractor_Air_Suspension_420HP.pdf",
        "4x2 Tractor AMT High Roof Standard (Air Suspension) 460HP | جرار 4x2 AMT سقف عالي قياسي (تعليق هوائي) 460 حصان": "JH6_4x2_AMT_High_Roof_Standard_Tractor_Air_Suspension_460HP.pdf",
        "4x2 Tractor AMT Flat Roof Multifunction (Leaf Spring) 420HP | جرار 4x2 AMT سقف مسطح متعدد الوظائف (نوابض ورقية) 420 حصان": "JH6_4x2_AMT_Flat_Roof_Multifunction_Tractor_Leaf_Spring_420HP.pdf",
        "4x2 Tractor AMT High Roof Multifunction (Leaf Spring) 420HP | جرار 4x2 AMT سقف عالي متعدد الوظائف (نوابض ورقية) 420 حصان": "JH6_4x2_AMT_High_Roof_Multifunction_Tractor_Leaf_Spring_420HP.pdf",
        "4x2 Tractor MT Flat Roof Multifunction (Leaf Spring) 420HP | جرار 4x2 MT سقف مسطح متعدد الوظائف (نوابض ورقية) 420 حصان": "JH6_4x2_MT_Flat_Roof_Multifunction_Tractor_Leaf_Spring_420HP.pdf",
        "4x2 Tractor MT Flat Roof Heavy Duty (Leaf Spring) 420HP (Double Reduction) | جرار 4x2 MT سقف مسطح للخدمة الشاقة (نوابض ورقية) 420 حصان (تخفيض مزدوج)": "JH6_4x2_MT_Flat_Roof_Heavy_Duty_Tractor_Leaf_Spring_420HP_Double_Reduction.pdf",
    },

    # 2. 6x4 Tractor - 6x4 رأس جرار
    "6x4 Tractor Head | 6x4 رأس جرار": {
        "6x4 Tractor MT (315 Tire) | جرار 6x4 MT (إطار 315)": "JH6_6x4_MT_Tractor_315_Tire.pdf",
        "6x4 Tractor MT 420HP | جرار 6x4 MT 420 حصان": "JH6_6x4_MT_Tractor_420HP.pdf",
        "6x4 Tractor MT 550HP | جرار 6x4 MT 550 حصان": "JH6_6x4_MT_Tractor_550HP.pdf"
    },

    # 3. 6x4 Dumper - 6x4 قلابة
    "6x4 Dumper | 6x4 قلابة": {
        "6x4 Dumper MT 390HP | قلابة 6x4 MT 390 حصان": "JH6_6x4_MT_Dumper_390HP.pdf",
        "6x4 Dumper MT 420HP | قلابة 6x4 MT 420 حصان": "JH6_6x4_MT_Dumper_420HP.pdf"
    },
    
    # 4. 6x4 Boom Crane - 6x4 رافعة
    "6x4 Boom Crane | 6x4 رافعة": {
        "6x4 Boom Crane MT 390HP | رافعة 6x4 MT 390 حصان": "JH6_6x4_MT_Boom_Crane_390HP.pdf"
    },
    
    # 5. 6x4 Hook Arm - 6x4 ذراع خطاف
    "Hook Arm | ذراع خطاف": {
        "6x4 Hook Arm | ذراع خطاف 6x4": ""    
    },

    # 6. 6x4 Water Tanker - 6x4 صهريج مياه
    "6x4 Water Tanker | 6x4 صهريج مياه": {
        "6x4 Water Tanker MT 390HP | صهريج مياه 6x4 MT 390 حصان": "JH6_6x4_MT_Water_Tanker_390HP.pdf"
    },

    # 7. 8x4 Dumper - 8x4 قلابة
    "8x4 Dumper | 8x4 قلابة": {
        "8x4 Dumper MT 390HP | قلابة 8x4 MT 390 حصان": "JH6_8x4_MT_Dumper_390HP.pdf",
        "8x4 Dumper MT 420HP | قلابة 8x4 MT 420 حصان": "JH6_8x4_MT_Dumper_420HP.pdf"
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
.stCheckbox>label {font-size: 16px;}
.stDownloadButton>button {background-color: #28a745; color: white; border-radius: 5px;}
.stSelectbox>div>div>select {font-size: 16px;}
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
    st.set_page_config(page_title="Purchase Intention | نية الشراء", page_icon="🚛", layout="centered")
    
    # ====== Logo ======
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("Fawtrucks.png", use_column_width=True)
    # ====== Logo End ======
    
    st.markdown(
        "<h1 style='text-align: center; font-size: 28px;'>Welcome to ALQAFLA | مرحبا بكم في القفلة</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<h3 style='text-align: center; font-size: 20px; color: #666;'>FAW Trucks Purchase Inquiry | استفسار شراء شاحنات فاو</h3>",
        unsafe_allow_html=True
    )
    st.divider()

    # 1. Basic Information - المعلومات الأساسية
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 1. Basic Information | المعلومات الأساسية")
    with col2:
        st.markdown("<h3 style='text-align: right;'>المعلومات الأساسية | Basic Information</h3>", unsafe_allow_html=True)
    
    c_name = st.text_input(
        "Company Name * | اسم الشركة *", 
        placeholder="Enter your company name | أدخل اسم شركتك"
    )
    
    phone = st.text_input(
        "Phone Number * | رقم الهاتف *", 
        placeholder="Enter your phone number | أدخل رقم هاتفك"
    )
    
    addr = st.text_area(
        "National Address | العنوان الوطني", 
        placeholder="Enter your address | أدخل عنوانك",
        height=100
    )

    # 2. Main Model Selection - اختيار الموديل الرئيسي
    st.markdown("### 2. Select Vehicle Type | اختر نوع المركبة")
    st.markdown("<h3 style='text-align: right;'>اختر نوع المركبة | Select Vehicle Type</h3>", unsafe_allow_html=True)
    
    st.info("Please select one or more vehicle types below | الرجاء اختيار نوع أو أكثر من المركبات أدناه")
    
    cols = st.columns(3)
    for idx, m in enumerate(MAIN_MODELS):
        with cols[idx%3]:
            checked = st.checkbox(m, key=f"m_{m}", value=m in st.session_state.selected_main)
            if checked and m not in st.session_state.selected_main:
                st.session_state.selected_main.append(m)
            elif not checked and m in st.session_state.selected_main:
                st.session_state.selected_main.remove(m)

    # 3. Sub-model & Quantity - الموديل الفرعي والكمية
    if st.session_state.selected_main:
        st.markdown("### 3. Specific Models & Quantity | النماذج التفصيلية والكمية")
        st.markdown("<h3 style='text-align: right;'>النماذج التفصيلية والكمية | Specific Models & Quantity</h3>", unsafe_allow_html=True)
        
        st.warning("Enter quantity for each model (0 means not selected) | أدخل الكمية لكل موديل (0 يعني غير محدد)")
        st.markdown("---")
        
        for m in st.session_state.selected_main:
            st.subheader(f"📋 {m}")
            
            for s in CAR_CONFIG[m]:
                unique_key = f"{m}_{s}"
                
                if unique_key not in st.session_state.submodel_qty:
                    st.session_state.submodel_qty[unique_key] = 0
                
                # Extract English and Arabic parts for display
                if " | " in s:
                    eng_part, ar_part = s.split(" | ", 1)
                    display_text = f"**{eng_part}**<br><span style='color: #666; text-align: right; direction: rtl;'>{ar_part}</span>"
                else:
                    display_text = f"**{s}**"
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(display_text, unsafe_allow_html=True)
                with col2:
                    q = st.number_input(
                        "Qty | الكمية",
                        min_value=0,
                        value=st.session_state.submodel_qty[unique_key],
                        step=1,
                        key=f"q_{unique_key}",
                        label_visibility="collapsed"
                    )
                    st.session_state.submodel_qty[unique_key] = q
                st.divider()

    # 4. Submit Button - زر الإرسال
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        submit = st.button(
            "🚚 Submit Order | أرسل الطلب 🚚", 
            use_container_width=True,
            type="primary"
        )

    # 5. Submission Logic - منطق الإرسال
    if submit:
        # Validate required fields - التحقق من الحقول المطلوبة
        err = []
        if not c_name: 
            err.append("Company Name | اسم الشركة")
        if not phone: 
            err.append("Phone Number | رقم الهاتف")
        
        if err:
            error_msg = f"**Required fields missing | الحقول المطلوبة مفقودة:**\n\n"
            for e in err:
                error_msg += f"• {e}\n"
            st.error(error_msg)
            return

        # Check if at least one model is selected - التحقق من اختيار نموذج واحد على الأقل
        has_selected = any(q > 0 for q in st.session_state.submodel_qty.values())
        if not has_selected:
            st.warning("⚠️ Please select at least one vehicle model | ⚠️ الرجاء اختيار نموذج مركبة واحد على الأقل")
            return

        # Construct Feishu message - بناء رسالة Feishu
        msg = f"""
🚛 **New FAW Vehicle Inquiry Received | تم استلام استفسار جديد لشاحنات فاو** 🚛

**Customer Information | معلومات العميل:**
1. **Company Name | اسم الشركة:** {c_name}
2. **Phone Number | رقم الهاتف:** {phone}
3. **Address | العنوان:** {addr if addr else "Not provided | لم يتم تقديمه"}
4. **Selected Vehicle Types | أنواع المركبات المختارة:** {', '.join(st.session_state.selected_main) if st.session_state.selected_main else "Not selected | لم يتم الاختيار"}

**📊 Purchase Details | تفاصيل الشراء:**
"""
        total_units = 0
        
        for unique_key, q in st.session_state.submodel_qty.items():
            if q > 0:
                # Extract model name without quantity display part
                model_display = unique_key.split("_", 1)[1]
                # Get only English part for Feishu message
                if " | " in model_display:
                    model_for_msg = model_display.split(" | ")[0]
                else:
                    model_for_msg = model_display
                    
                msg += f"   • **{model_for_msg}:** {q} unit(s) | وحدة\n"
                total_units += q
        
        msg += f"\n**📈 Total Units | إجمالي الوحدات:** {total_units}"

        # Send to Feishu - إرسال إلى Feishu
        try:
            with st.spinner("Sending your inquiry... | جاري إرسال استفسارك..."):
                res = requests.post(
                    FEISHU_WEBHOOK,
                    data=json.dumps({
                        "msg_type": "text",
                        "content": {
                            "text": msg.strip()
                        }
                    }),
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                res_json = res.json()
                
                if res.status_code == 200 and res_json.get("code") == 0:
                    st.session_state.submitted = True
                    st.rerun()
                else:
                    st.error(f"❌ Submission failed | فشل الإرسال: {res_json.get('msg', 'Unknown error')}")
        except requests.exceptions.Timeout:
            st.error("⏰ Request timeout. Please try again. | ⏰ انتهت مهلة الطلب. يرجى المحاولة مرة أخرى.")
        except Exception as e:
            st.error(f"❌ System error | خطأ في النظام: {str(e)}")


def show_thank_you_page():
    st.set_page_config(
        page_title="Submission Successful | نجاح الإرسال", 
        page_icon="✅", 
        layout="centered"
    )
    
    # Success message - رسالة النجاح
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("Fawtrucks.png", use_column_width=True)
    
    st.title("✅ Thank You! | ✅ شكرًا لك!")
    st.markdown("""
    <div style='text-align: center;'>
        <h3>Your inquiry has been successfully submitted | تم إرسال استفسارك بنجاح</h3>
        <p>Our sales team will contact you within 24 hours | سيتصل بك فريق المبيعات خلال 24 ساعة</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.balloons()
    st.markdown("---")
    
    # Download section - قسم التنزيل
    st.markdown("### 📄 Download Specifications | تنزيل المواصفات")
    st.markdown("<h3 style='text-align: right;'>تنزيل المواصفات | Download Specifications</h3>", unsafe_allow_html=True)
    
    download_models = []
    for unique_key, q in st.session_state.submodel_qty.items():
        if q > 0:
            sub_model = unique_key.split("_", 1)[1]
            download_models.append(sub_model)

    if not download_models:
        st.info("""
        ℹ️ No specific models selected for download | ℹ️ لم يتم اختيار أي نماذج للتنزيل
        
        You can return to the form to select models | يمكنك العودة إلى النموذج لاختيار النماذج
        """)
    else:
        st.success(f"📥 Download materials for {len(download_models)} selected model(s) | 📥 مواد التنزيل لـ {len(download_models)} نموذج محدد")
        
        for idx, model_display in enumerate(download_models):
            pdf_filename = PDF_MAP.get(model_display)
            if pdf_filename:
                try:
                    with open(pdf_filename, "rb") as f:
                        # Display model name nicely
                        if " | " in model_display:
                            eng_name, ar_name = model_display.split(" | ", 1)
                            button_label = f"📥 {eng_name} | {ar_name}"
                        else:
                            button_label = f"📥 {model_display}"
                            
                        st.download_button(
                            label=button_label,
                            data=f,
                            file_name=pdf_filename,
                            mime="application/pdf",
                            use_container_width=True,
                            key=f"download_btn_{idx}"
                        )
                except FileNotFoundError:
                    st.warning(f"""
                    ⚠️ File not found | ⚠️ الملف غير موجود: {pdf_filename}
                    
                    Please contact support | يرجى الاتصال بالدعم
                    """)
            else:
                st.warning(f"""
                ⚠️ No PDF available | ⚠️ لا يوجد ملف PDF: {model_display.split(' | ')[0]}
                
                Specifications coming soon | المواصفات قريبًا
                """)

    # Return to homepage - العودة للصفحة الرئيسية
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(
            "🏠 Return to Homepage | العودة للصفحة الرئيسية 🏠", 
            use_container_width=True,
            type="secondary"
        ):
            st.session_state.submitted = False
            st.session_state.selected_main = []
            st.session_state.submodel_qty = {}
            st.rerun()


if __name__ == "__main__":
    main()
