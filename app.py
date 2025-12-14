import streamlit as st
from datetime import datetime
import pandas as pd
import os
import uuid

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="BAKEGOODBEGOOD",
    page_icon="🥤",
    layout="centered"
)

# พื้นหลังสีครีม
page_bg = """
<style>
[data-testid="stAppViewContainer"]{
    background: #A2C99F;
}
[data-testid="stSidebar"]{
    background: #A2C99F;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

ORDERS_FILE = "orders.csv"
SLIPS_DIR = "slips"

os.makedirs(SLIPS_DIR, exist_ok=True)

# เมนูเครื่องดื่ม + ราคา (เย็นทั้งหมด)
MENU_ITEMS = {
    "กาแฟเย็น 40 บาท": 40,
    "ชาไทยเย็น 35 บาท": 35,
    "ชาเขียวเย็น 35 บาท": 35,
    "โอวัลตินเย็น 40 บาท": 40,
    "เคลียร์มัจฉะเย็น 50 บาท": 50,
    "มัจฉะนมโอ็ตเย็น 60 บาท": 60,
    "มัจฉะนมสดเย็น 60 บาท": 60,
}

SWEETNESS_LEVEL = ["หวานน้อย", "หวานปกติ", "หวานมาก"]


# ---------------- HELPERS ----------------
def go_to_step(step_number: int):
    st.session_state.step = step_number


def load_orders():
    if os.path.exists(ORDERS_FILE):
        return pd.read_csv(ORDERS_FILE)
    return pd.DataFrame()


def save_order(order_data: dict):
    df_new = pd.DataFrame([order_data])
    if os.path.exists(ORDERS_FILE):
        df_old = pd.read_csv(ORDERS_FILE)
        df_all = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_all = df_new
    df_all.to_csv(ORDERS_FILE, index=False)


def show_qr_image():
    qr_files = ["qr_matcha.jpeg", "qr_matcha.jpg", "qr_matcha.png"]
    found = False
    for f in qr_files:
        if os.path.exists(f):
            st.image(f, caption="สแกนเพื่อชำระเงิน", use_column_width=True)
            found = True
            break
    if not found:
        st.warning("⚠️ ไม่พบไฟล์ QR Code (รองรับ qr_matcha.jpeg/.jpg/.png ในโฟลเดอร์เดียวกับ app.py)")


# ---------------- STATE INIT ----------------
if "step" not in st.session_state:
    st.session_state.step = 1
if "customer" not in st.session_state:
    st.session_state.customer = {}
if "order" not in st.session_state:
    st.session_state.order = {}

# ---------------- SIDEBAR ----------------
st.sidebar.title("BAKEGOODBEGOOD")

mode = st.sidebar.radio(
    "เลือกโหมด",
    ["ลูกค้าสั่งเครื่องดื่ม", "Admin ดูออเดอร์"]
)

# -------------------------------------------------
#                 CUSTOMER MODE
# -------------------------------------------------
if mode == "ลูกค้าสั่งเครื่องดื่ม":
    st.title("🥤 ระบบรับออเดอร์เครื่องดื่ม : ปิดรับออเดอร์ 9โมงค่ะ")

    st.sidebar.header("ขั้นตอนการสั่งซื้อ")
    st.sidebar.markdown(
        f"""
- {'✅' if st.session_state.step > 1 else '👉'} **Step 1:** ลงทะเบียน  
- {'✅' if st.session_state.step > 2 else '👉'} **Step 2:** เลือกเมนู  
- {'✅' if st.session_state.step > 3 else '👉'} **Step 3:** เลือกความหวาน  
- {'👉'} **Step 4:** ชำระเงิน
"""
    )

    # STEP 1 – ลงทะเบียนลูกค้า
    if st.session_state.step == 1:
        st.subheader("Step 1: ลงทะเบียนลูกค้า")

        name = st.text_input("ชื่อลูกค้า", placeholder="เช่น กัส, มิ้นท์, ตาล ฯลฯ")
        phone = st.text_input("เบอร์โทรศัพท์", placeholder="เช่น 0812345678")
        st.caption("ชื่อและเบอร์ลูกค้ามีผลต่อระบบสมาชิกและโปรโมชั่นต่างๆค่ะ รบกวนใส่ชื่อและเบอร์โทรให้เหมือนกันในทุกครั้งของการสั่งซื้อ")

        if st.button("ไป Step 2 ➡️"):
            if not name.strip() or not phone.strip():
                st.error("กรุณากรอกชื่อและเบอร์โทรศัพท์ให้ครบก่อนนะคะ")
            else:
                st.session_state.customer = {
                    "name": name.strip(),
                    "phone": phone.strip(),
                    "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                go_to_step(2)

    

# STEP 2 – เลือกเมนู + เลือกความหวาน + สรุปออเดอร์ (รวมหน้าเดียว)
    elif st.session_state.step == 2:
        st.subheader("Step 2: เลือกเมนูเครื่องดื่ม + เลือกความหวาน")
    
        DELIVERY_FEE = 5  # ค่าจัดส่ง
    
        # ----------------------------
        # เลือกเมนู
        # ----------------------------
        st.markdown("### 🥤 เลือกเมนู")
        menu_choice = st.radio(
            "",
            options=list(MENU_ITEMS.keys()),
            index=0
        )
        price = MENU_ITEMS[menu_choice]
    
        # ----------------------------
        # เลือกระดับความหวาน
        # ----------------------------
        st.markdown("### 🍬 เลือกระดับความหวาน")
        sweetness = st.radio(
            "",
            options=SWEETNESS_LEVEL,
            horizontal=True
        )
    
        # ----------------------------
        # คำนวณราคารวม
        # ----------------------------
        total_price = price + DELIVERY_FEE
    
        # ----------------------------
        # สรุปรายการในหน้าเดียวกัน
        # ----------------------------
        st.markdown("---")
        st.markdown("### 📋 สรุปรายการที่เลือก")
    
        st.write(f"**ราคาเครื่องดื่ม:** {price} บาท")
        st.write(f"**ค่าจัดส่ง:** {DELIVERY_FEE} บาท")
        st.write(f"**ราคารวมทั้งหมด:** 💸 {total_price} บาท")
    
        # เก็บค่าลง session
        st.session_state.order = {
            "menu": menu_choice,
            "sweetness": sweetness,
            "price": price,
            "delivery_fee": DELIVERY_FEE,
            "total_price": total_price,
        }
    
        st.markdown("---")
    
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ ย้อนกลับไปแก้ข้อมูลลูกค้า"):
                go_to_step(1)
    
        with col2:
            if st.button("ไป Step 3 – ชำระเงิน ➡️"):
                go_to_step(4)


    # STEP 4 – ชำระเงิน + แนบสลิป
    elif st.session_state.step == 4:
        st.subheader("Step 4: ชำระเงิน & แนบสลิป")

        customer = st.session_state.customer
        order = st.session_state.order

        st.markdown("### 👤 ข้อมูลลูกค้า")
        st.write(f"**ชื่อ:** {customer.get('name', '-')}")
        st.write(f"**เบอร์โทรศัพท์:** {customer.get('phone', '-')}")

        st.markdown("### 🥤 รายการที่สั่ง")
        st.write(f"**เมนู:** {order.get('menu', '-')}")
        st.write(f"**ความหวาน:** {order.get('sweetness', '-')}")
        st.write(f"**ค่าจัดส่ง:** {order.get('delivery_fee', 0)} บาท")
        st.write(f"**ราคารวม:** 💸 {order.get('price', 0)} บาท")

        st.markdown("---")
        st.markdown("### 📲 สแกน QR เพื่อชำระเงิน")
        show_qr_image()

        st.markdown("### 🧾 แนบสลิปโอนเงิน")
        slip_file = st.file_uploader(
            "อัปโหลดสลิปโอนเงิน (ไฟล์รูป)",
            type=["png", "jpg", "jpeg"]
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ ย้อนกลับไปแก้ความหวาน"):
                go_to_step(3)

        with col2:
            confirm_btn = st.button("✅ ยืนยันออเดอร์")

        if confirm_btn:
            if slip_file is None:
                st.error("กรุณาอัปโหลดสลิปโอนเงินก่อนกดยืนยันออเดอร์นะคะ")
            else:
                # เซฟไฟล์สลิปลงโฟลเดอร์ slips/
                ext = os.path.splitext(slip_file.name)[1].lower()
                if ext == "":
                    ext = ".jpg"
                slip_name = f"slip_{uuid.uuid4().hex}{ext}"
                slip_path = os.path.join(SLIPS_DIR, slip_name)
                with open(slip_path, "wb") as f:
                    f.write(slip_file.getbuffer())

                now = datetime.now()
                # จัดการชื่อให้ไม่มีช่องว่าง / ตัวพิมพ์เล็ก
                clean_name = customer.get("name", "").strip().replace(" ", "").lower()
                clean_phone = customer.get("phone", "").strip()
                
                # timestamp
                timestamp = now.strftime("%Y%m%d%H%M%S")
                
                # สร้าง order_id ใหม่
                order_id = f"{clean_name}-{clean_phone}-{timestamp}"

                order_data = {
                    "order_id": order_id,
                    "created_at": now.strftime("%Y-%m-%d %H:%M:%S"),
                    "name": customer.get("name", ""),
                    "phone": customer.get("phone", ""),
                    "menu": order.get("menu", ""),
                    "sweetness": order.get("sweetness", ""),
                    "price": order.get("price", 0),
                    "slip_file": slip_name,
                }

                save_order(order_data)

                st.success(f"🎉 รับออเดอร์เรียบร้อยแล้ว! (Order ID: {order_id})")
                st.info("กำลังจัดเตรียมเครื่องดื่ม🥤")

                if st.button("เริ่มออเดอร์ใหม่ 🆕"):
                    st.session_state.step = 1
                    st.session_state.customer = {}
                    st.session_state.order = {}

# -------------------------------------------------
#                 ADMIN MODE
# -------------------------------------------------
else:
    st.title("🛠 Admin Login")

    # ใส่รหัสผ่านก่อนเข้า Admin
    password = st.text_input("กรุณาใส่รหัสผ่านเพื่อเข้าหน้า Admin", type="password")

    if password != "goggag1112":
        st.warning("รหัสผ่านไม่ถูกต้องหรือยังไม่ได้กรอก")
        st.stop()
    else:
        st.success("เข้าสู่ระบบสำเร็จ ✔️")
        st.title("📦 Admin – จัดการออเดอร์")

        df = load_orders()

        if df.empty:
            st.info("ยังไม่มีออเดอร์เข้ามาในระบบ")
        else:
            st.subheader("ลิสต์ออเดอร์ทั้งหมด")
            st.dataframe(df)

            st.markdown("---")
            st.subheader("🧾 ดู / พิมพ์ Slip")

            order_ids = df["order_id"].astype(str).tolist()
            selected_id = st.selectbox("เลือก Order ID", order_ids)

            if selected_id:
                row = df[df["order_id"].astype(str) == selected_id].iloc[0]

                st.markdown("### ตัวอย่าง Slip สำหรับปริ้น")
                st.markdown(
                    f"""
**Drink Cafe – ใบรับออเดอร์**

- Order ID: `{row['order_id']}`
- วันที่: {row['created_at']}
- ชื่อลูกค้า: {row['name']}
- เบอร์โทร: {row['phone']}

**รายการเครื่องดื่ม**

- เมนู: {row['menu']}
- ความหวาน: {row['sweetness']}
- ราคารวม: 💸 {row['price']} บาท
"""
                )

                slip_file = row.get("slip_file", None)
                if isinstance(slip_file, str):
                    slip_path = os.path.join(SLIPS_DIR, slip_file)
                    if os.path.exists(slip_path):
                        st.markdown("**สลิปโอนเงิน (จากลูกค้า):**")
                        st.image(slip_path, use_column_width=True)
                    else:
                        st.warning("ไม่พบไฟล์สลิปที่บันทึกไว้")

                slip_html = f"""
<html>
  <head>
    <meta charset="utf-8" />
    <title>Order {row['order_id']}</title>
  </head>
  <body style="font-family: sans-serif; max-width: 400px; margin: 0 auto;">
    <h2>BAKEGOODBEGOOD – ใบรับออเดอร์</h2>
    <p><strong>Order ID:</strong> {row['order_id']}<br/>
       <strong>วันที่:</strong> {row['created_at']}<br/>
       <strong>ชื่อลูกค้า:</strong> {row['name']}<br/>
       <strong>เบอร์โทร:</strong> {row['phone']}</p>
    <hr/>
    <h3>รายการเครื่องดื่ม</h3>
    <p>
       เมนู: {row['menu']}<br/>
       ความหวาน: {row['sweetness']}<br/>
       ราคารวม: {row['price']} บาท
    </p>
    <hr/>
    <p style="text-align:center;">ขอบคุณที่อุดหนุนค่ะ 🥤</p>
  </body>
</html>
"""
                slip_bytes = slip_html.encode("utf-8")

                st.download_button(
                    "⬇️ ดาวน์โหลด Slip (HTML สำหรับ Print)",
                    data=slip_bytes,
                    file_name=f"order_{row['order_id']}.html",
                    mime="text/html"
                )
