import streamlit as st
import requests
import json
import os

# ---------------------- 核心配置（仅需修改这个字典！） ----------------------
# 格式：{
#     "一级车型名": {
#         "二级车型名1": "对应的PDF文件名1.pdf",
#         "二级车型名2": "对应的PDF文件名2.pdf",
#         ...
#     },
#     ...
# }
# ---------------------- 核心配置（仅需修改这个字典！） ----------------------
CAR_PDF_MASTER = {
    # 1. 4x2 Tractor (4*2牵引车)
    "4x2 Tractor": {
        "AMT High Roof Standard (Leaf Spring) 420HP": "JH6_4x2 AMT_High_Roof_Standard_Tractor_Leaf_spring_420HP.pdf",
        "AMT Flat Roof Multifunction (Leaf Spring) 420HP": "JH6_4x2_AMT_Flat_Roof_Multifunction_Tractor_Leaf_Spring_420HP.pdf",
        "AMT High Roof Multifunction (Leaf Spring) 420HP": "JH6_4x2_AMT_High_Roof_Multifunction_Tractor_Leaf_Spring_420HP.pdf",
        "AMT High Roof Standard (Air Suspension) 420HP": "JH6_4x2_AMT_High_Roof_Standard_Tractor_Air_Suspension_420HP.pdf",
        "AMT High Roof Standard (Air Suspension) 460HP": "JH6_4x2_AMT_High_Roof_Standard_Tractor_Air_Suspension_460HP.pdf",
        "MT Flat Roof Heavy Duty (Leaf Spring) 420HP (Double Reduction)": "JH6_4x2_MT_Flat_Roof_Heavy_Duty_Tractor_Leaf_Spring_420HP_Double_Reduction.pdf",
        "MT Flat Roof Multifunction (Leaf Spring) 420HP": "JH6_4x2_MT_Flat_Roof_Multifunction_Tractor_Leaf_Spring_420HP.pdf"
    },

    # 2. 6x4 Tractor (6*4牵引车)
    "6x4 Tractor": {
        "MT Standard (315 Tire)": "JH6_6x4_MT_Tractor_315_Tire.pdf",
        "MT Standard 420HP": "JH6_6x4_MT_Tractor_420HP.pdf",
        "MT Standard 550HP": "JH6_6x4_MT_Tractor_550HP.pdf"
    },

    # 3. 6x4 Dumper (6*4自卸车)
    "6x4 Dumper": {
        "MT Standard 390HP": "JH6_6x4_MT_Dumper_390HP.pdf",
        "MT Standard 420HP": "JH6_6x4_MT_Dumper_420HP.pdf"
    },

    # 4. 6x4 Water Tanker (6*4水车)
    "6x4 Water Tanker": {
        "MT Standard 390HP": "JH6_6x4_MT_Water_Tanker_390HP.pdf"
    },

    # 5. 6x4 Boom Crane (6*4随车吊)
    "6x4 Boom Crane": {
        "MT Standard 390HP": "JH6_6x4_MT_Boom_Crane_390HP.pdf"
    },

    # 6. 8x4 Dumper (8*4自卸车)
    "8x4 Dumper": {
        "MT Standard 390HP": "JH6_8x4_MT_Dumper_390HP.pdf",
        "MT Standard 420HP": "JH6_8x4_MT_Dumper_420HP.pdf"
    },

    # 7. 8x4 Mixer (8*4搅拌车)
    "8x4 Mixer": {
        "MT Standard 390HP": "JH6_8x4_MT_Mixer_390HP.pdf"
    }
}

# 飞书机器人配置（无需频繁改）
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/d849efbe-0ce8-42e8-85f5-6385d25d4542"

# 自定义样式（无需频繁改）
st.markdown("""
<style>
.stButton>button {background-color: #0066cc; color: white; border-radius: 5px;}
.stTextInput>div>div>input {border-radius: 5px;}
.stCheckbox>label {font-size: 16px;}
.stDownloadButton>button {background-color: #28a745; color: white; border-radius: 5px;}
</style>
""", unsafe_allow_html=True)

# ---------------------- 自动解析配置（无需修改） ----------------------
# 从主字典自动提取：一级车型列表、二级车型映射、PDF映射
# 1. 一级车型列表（页面显示的复选框）
MAIN_MODELS = list(CAR_PDF_MASTER.keys())
# 2. 二级车型映射（一级→二级列表）
CAR_CONFIG = {main: list(sub_pdf.keys()) for main, sub_pdf in CAR_PDF_MASTER.items()}
# 3. PDF映射（二级车型→PDF文件名）
PDF_MAP = {}
for main, sub_pdf in CAR_PDF_MASTER.items():
    PDF_MAP.update(sub_pdf)

# ---------------------- 页面逻辑（无需修改） ----------------------
def main():
    # 初始化session_state
    if "selected_main" not in st.session_state:
        st.session_state.selected_main = []
    if "submodel_qty" not in st.session_state:
        st.session_state.submodel_qty = {}
    if "submitted" not in st.session_state:
        st.session_state.submitted = False  # 提交成功标记

    # 提交成功 → 显示感谢页
    if st.session_state.submitted:
        show_thank_you_page()
        return

    # 未提交 → 填写页面
    st.set_page_config(page_title="FAW 购车问卷", page_icon="🚛", layout="centered")
    st.title("🚛 FAW 购车信息收集问卷")
    st.divider()

    # 1. 基础信息
    c_name = st.text_input("1. 公司名称 *", placeholder="贵公司全称")
    u_name = st.text_input("2. 联系人姓名", placeholder="您的姓名")
    phone = st.text_input("3. 联系电话 *", placeholder="手机号/座机")
    addr = st.text_area("4. 公司地址", placeholder="详细地址", height=100)

    # 2. 一级车型选择（自动从MAIN_MODELS读取，无需改代码）
    st.markdown("### 5. 意向车型大类（勾选）")
    cols = st.columns(3)
    for idx, m in enumerate(MAIN_MODELS):
        with cols[idx%3]:
            checked = st.checkbox(m, key=f"m_{m}", value=m in st.session_state.selected_main)
            if checked and m not in st.session_state.selected_main:
                st.session_state.selected_main.append(m)
            elif not checked and m in st.session_state.selected_main:
                st.session_state.selected_main.remove(m)

    # 3. 二级车型+数量（自动从CAR_CONFIG读取，无需改代码）
    if st.session_state.selected_main:
        st.markdown("### 5.1 具体车型及数量（默认0）")
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
                        f"{s} 数量", min_value=0, value=st.session_state.submodel_qty[s], step=1, key=f"q_{s}"
                    )
                    st.session_state.submodel_qty[s] = q

    # 4. 提交按钮
    st.markdown("---")
    submit = st.button("提交购车信息", use_container_width=True)

    # 5. 提交逻辑
    if submit:
        # 校验必填项
        err = []
        if not c_name: err.append("公司名称")
        if not phone: err.append("联系电话")
        if err:
            st.error(f"必填项缺失：{', '.join(err)}")
            return

        # 构造飞书消息
        msg = f"""
客户信息【FAW】FAW 购车意向
1. 公司名称：{c_name}
2. 联系人：{u_name if u_name else "未填写"}
3. 电话：{phone}
4. 地址：{addr if addr else "未填写"}
5. 车型大类：{', '.join(st.session_state.selected_main) if st.session_state.selected_main else "未选择"}
6. 采购明细：
"""
        has_data = False
        for s, q in st.session_state.submodel_qty.items():
            if q > 0:
                msg += f"   - {s}：{q} 台\n"
                has_data = True
        if not has_data: msg += "   - 无\n"

        # 飞书推送
        try:
            res = requests.post(
                FEISHU_WEBHOOK,
                data=json.dumps({"msg_type":"text","content":{"text":msg.strip()}}),
                headers={"Content-Type":"application/json"}
            )
            res_json = res.json()
            if res.status_code == 200 and res_json.get("code") == 0:
                st.session_state.submitted = True  # 标记提交成功
                st.rerun()  # 跳转感谢页
            else:
                st.error(f"❌ 推送失败：{res_json}")
        except Exception as e:
            st.error(f"❌ 系统错误：{str(e)}")

# ---------------------- 感谢页（PDF下载自动从PDF_MAP读取，无需改代码） ----------------------
def show_thank_you_page():
    st.set_page_config(page_title="提交成功 | FAW购车问卷", page_icon="✅", layout="centered")
    st.title("✅ 提交成功！感谢您的咨询")
    st.markdown("---")
    st.markdown("### 📞 我们会尽快与您取得联系")
    st.markdown("### 📄 您可下载选中车型的详细资料：")
    st.markdown("---")

    # 筛选数量>0的车型，生成下载按钮
    download_models = [s for s, q in st.session_state.submodel_qty.items() if q > 0]
    if not download_models:
        st.info("您未选择具体车型，暂无可下载的资料")
    else:
        for model in download_models:
            pdf_filename = PDF_MAP.get(model)
            if pdf_filename:
                # 检查文件是否存在（本地测试用）
                if os.path.exists(pdf_filename):
                    with open(pdf_filename, "rb") as f:
                        st.download_button(
                            label=f"📥 下载 {model} 详细资料",
                            data=f,
                            file_name=pdf_filename,
                            mime="application/pdf",
                            use_container_width=True
                        )
                else:
                    st.warning(f"⚠️ 未找到 {pdf_filename} 文件，请确认文件已上传")
            else:
                st.warning(f"{model} 暂无对应的资料文件")

    # 返回首页按钮
    if st.button("返回问卷首页", use_container_width=True):
        st.session_state.submitted = False
        st.session_state.selected_main = []
        st.session_state.submodel_qty = {}
        st.rerun()

if __name__ == "__main__":
    main()
