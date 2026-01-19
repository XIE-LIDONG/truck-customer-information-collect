import streamlit as st
import requests
import json
import os

# ---------------------- 核心配置【只保留指定8款车型，极简配置】 ----------------------
CAR_PDF_MASTER = {
    "核心车型选择 | اختيار النماذج الرئيسية": {
        "4x2 Tractor AMT High Roof (Leaf Spring) 420HP | 4*2高顶板簧AMT 420 حصان": "JH6_4x2 AMT_High_Roof_Standard_Tractor_Leaf_spring_420HP.pdf",
        "4x2 Tractor AMT Flat Roof (Leaf Spring) 420HP | 4*2平顶板簧AMT 420 حصان": "JH6_4x2_AMT_Flat_Roof_Multifunction_Tractor_Leaf_Spring_420HP.pdf",
        "4x2 Tractor AMT High Roof (Air Suspension) 420HP | 4*2高顶气囊AMT 420 حصان": "JH6_4x2_AMT_High_Roof_Standard_Tractor_Air_Suspension_420HP.pdf",
        "6x4 Tractor MT 420HP | 6*4牵引车 420 حصان": "JH6_6x4_MT_Tractor_420HP.pdf",
        "6x4 Dumper MT 420HP | 自卸车 420 حصان": "JH6_6x4_MT_Dumper_420HP.pdf",
        "8x4 Mixer MT 390HP | 搅拌车 390 حصان": "JH6_8x4_MT_Mixer_390HP.pdf",
        "6x4 Water Tanker MT 390HP | 水车 390 حصان": "JH6_6x4_MT_Water_Tanker_390HP.pdf",
        "6x4 Hook Arm | 底盘/ ذراع خطاف 6x4": ""
    }
}

# Feishu Robot Configuration 飞书机器人配置不变
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/d849efbe-0ce8-42e8-85f5-6385d25d4542"

# Custom Styles 自定义样式不变
st.markdown("""
<style>
.stButton>button {background-color: #0066cc; color: white; border-radius: 5px;}
.stTextInput>div>div>input {border-radius: 5px;}
.stCheckbox>label {font-size: 16px;}
.stDownloadButton>button {background-color: #28a745; color: white; border-radius: 5px;}
</style>
""", unsafe_allow_html=True)

# ---------------------- 自动解析配置 ----------------------
MAIN_MODELS = list(CAR_PDF_MASTER.keys())
CAR_CONFIG = {main: list(sub_pdf.keys()) for main, sub_pdf in CAR_PDF_MASTER.items()}
PDF_MAP = {}
for main, sub_pdf in CAR_PDF_MASTER.items():
    PDF_MAP.update(sub_pdf)

# ---------------------- 页面核心逻辑 ----------------------
def main():
    # 初始化会话状态
    if "selected_sub_models" not in st.session_state:
        st.session_state.selected_sub_models = []  # 存储勾选的车型
    if "submitted" not in st.session_state:
        st.session_state.submitted = False

    # 提交成功后展示感谢页
    if st.session_state.submitted:
        show_thank_you_page()
        return

    # 主页面配置
    st.set_page_config(page_title="Purchase Intention | نية الشراء", page_icon="🚛", layout="centered")
    # Logo
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("Fawtrucks.png", use_column_width=True)
    # 标题
    st.markdown(
    "<h1 style='text-align: center; font-size: 28px;'>Welcome to ALQAFLA | ALQAFLA مرحبا بكم في </h1>",
    unsafe_allow_html=True
    )
    st.divider()

    # ========== 第一步：车型选择【置顶，极简勾选模式，无数量框】 ==========
    st.markdown("### ✅ Truck Model Selection / اختيار نموذج الشاحنة")
    st.markdown("##### (Please tick the models you are interested in / الرجاء تحديد النماذج التي تهتم بها)")
    st.divider()
    
    # 获取唯一的车型分组
    main_model = MAIN_MODELS[0]
    all_sub_models = CAR_CONFIG[main_model]
    
    # 2列布局展示8款车型，勾选更美观
    cols = st.columns(2)
    for idx, sub_model in enumerate(all_sub_models):
        with cols[idx % 2]:
            is_checked = st.checkbox(f"📌 {sub_model}", key=sub_model, value=sub_model in st.session_state.selected_sub_models)
            # 更新勾选状态
            if is_checked and sub_model not in st.session_state.selected_sub_models:
                st.session_state.selected_sub_models.append(sub_model)
            elif not is_checked and sub_model in st.session_state.selected_sub_models:
                st.session_state.selected_sub_models.remove(sub_model)

    # ========== 第二步：客户信息填写【移到最后，必填项不变】 ==========
    st.markdown("---")
    st.markdown("### 📝 Customer Information / معلومات العميل *")
    c_name = st.text_input("1. Company Name / اسم الشركة *", placeholder="Full name of your company / الاسم الكامل للشركة")
    phone = st.text_input("2. Phone Number / رقم الهاتف *", placeholder="Mobile/landline number / رقم الجوال/الهاتف الثابت")
    addr = st.text_area("3. National Address / العنوان الوطني", placeholder="Detailed address / العنوان بالتفصيل", height=100)

    # ========== 提交按钮 ==========
    st.markdown("---")
    submit = st.button("Submit | أرسل الطلب ", use_container_width=True)

    # ========== 提交逻辑处理 ==========
    if submit:
        # 必填项校验
        err = []
        if not c_name: err.append("Company Name / اسم الشركة")
        if not phone: err.append("Contact Phone / رقم الهاتف")
        
        if err:
            st.error(f"Required fields missing: {', '.join(err)} | الحقول المطلوبة مفقودة: {', '.join(err)}")
            return
        
        # 组装飞书推送消息
        msg = f"""
Customer Information【FAW】FAW Vehicle Inquiry
1. Company Name: {c_name}
2. Phone Number: {phone}
3. Address: {addr if addr else "Not provided"}
4. Selected Truck Models (Interested):
"""
        if st.session_state.selected_sub_models:
            for model in st.session_state.selected_sub_models:
                msg += f"   - ✔️ {model}\n"
        else:
            msg += "   - No models selected\n"

        # 发送到飞书
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
                st.error(f"❌ Submission failed | فشل الإرسال: {res_json}")
        except Exception as e:
            st.error(f"❌ System error | خطأ في النظام: {str(e)}")


def show_thank_you_page():
    """提交成功后的感谢页 + PDF下载"""
    st.set_page_config(page_title="Submission Successful | نجاح الإرسال | FAW Inquiry", page_icon="✅", layout="centered")
    st.title("✅ Submission Successful! Thank you for your inquiry | ✅ تم الإرسال بنجاح! شكراً لاستفسارك")
    st.markdown("---")
    st.markdown("### 📄 Download Detailed PDF Brochure / تنزيل كتيب تفاصيل السيارة:")
    st.markdown("---")

    # 展示勾选车型的PDF下载按钮
    selected_models = st.session_state.selected_sub_models
    if not selected_models:
        st.info("No models selected, no downloadable materials | لم يتم اختيار أي نماذج، لا توجد مواد للتنزيل")
    else:
        for idx, model in enumerate(selected_models):
            pdf_filename = PDF_MAP.get(model)
            if pdf_filename and pdf_filename != "":
                try:
                    with open(pdf_filename, "rb") as f:
                        st.download_button(
                            label=f"📥 Download {model.split(' | ')[0]} PDF",
                            data=f,
                            file_name=pdf_filename,
                            mime="application/pdf",
                            use_container_width=True,
                            key=f"download_{idx}"
                        )
                except FileNotFoundError:
                    st.warning(f"⚠️ PDF file not found: {pdf_filename} | الملف غير موجود")
            else:
                st.warning(f"⚠️ No PDF available for this model | لا يوجد ملف PDF لهذا النموذج: {model}")

    # 返回首页按钮
    if st.button("🔙 Return to Homepage | العودة للصفحة الرئيسية", use_container_width=True):
        st.session_state.submitted = False
        st.session_state.selected_sub_models = []
        st.rerun()

if __name__ == "__main__":
    main()
