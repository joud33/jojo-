import io
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="تحليل درجات الطالبات", page_icon="📊", layout="wide")

st.title("📊 تحليل درجات الطالبات (Excel)")
st.caption("ارفعي ملف Excel للدرجات، واختاري عمود اسم الطالبة وعمود الدرجة، ثم البرنامج يحسب الإحصائيات تلقائيًا.")

with st.expander("✅ شكل الملف المطلوب", expanded=False):
    st.write("يفضل يكون عندك عمود للاسم وعمود للدرجة. مثال:")
    st.code("اسم الطالبة | الدرجة\nAisha | 78\nSara | 45\n...")

uploaded = st.file_uploader("ارفعي ملف Excel (.xlsx)", type=["xlsx"])

if uploaded is None:
    st.info("ارفعي ملف Excel للبدء.")
    st.stop()

try:
    df_raw = pd.read_excel(uploaded)
except Exception as e:
    st.error("ما قدرت أقرأ ملف الإكسل. تأكدي إنه .xlsx وغير تالف.")
    st.stop()

if df_raw.empty:
    st.error("الملف فاضي.")
    st.stop()

st.subheader("معاينة البيانات")
st.dataframe(df_raw, use_container_width=True)

cols = list(df_raw.columns)

st.subheader("اختيار الأعمدة")
col_name = st.selectbox("عمود اسم الطالبة (اختياري)", options=["(بدون)"] + cols, index=0)
col_score = st.selectbox("عمود الدرجة", options=cols, index=0)

max_score = st.number_input("الدرجة النهائية (من كم؟)", min_value=1.0, value=100.0, step=1.0)

# Clean and compute
df = df_raw.copy()

# Convert score column to numeric safely
df[col_score] = pd.to_numeric(df[col_score], errors="coerce")

valid_mask = df[col_score].notna()
invalid_count = int((~valid_mask).sum())

df_valid = df.loc[valid_mask].copy()
if df_valid.empty:
    st.error("ما لقيت أي درجات رقمية في العمود المختار.")
    st.stop()

df_valid["النسبة %"] = (df_valid[col_score] / max_score) * 100
df_valid["النسبة %"] = df_valid["النسبة %"].clip(lower=0, upper=100)

below_50_mask = df_valid["النسبة %"] < 50
below_50_count = int(below_50_mask.sum())
total_count = int(len(df_valid))
below_50_percent = (below_50_count / total_count) * 100

mean_score = float(df_valid[col_score].mean())
mean_percent = float(df_valid["النسبة %"].mean())

st.subheader("النتائج")
c1, c2, c3, c4 = st.columns(4)

c1.metric("عدد الطالبات (الدرجات الصحيحة)", f"{total_count}")
c2.metric("المتوسط الحسابي", f"{mean_score:.2f}")
c3.metric("متوسط النسبة من 100", f"{mean_percent:.2f}%")
c4.metric("أقل من 50%", f"{below_50_percent:.2f}% ({below_50_count})")

if invalid_count > 0:
    st.warning(f"تم تجاهل {invalid_count} صف/خانة لأن الدرجة غير رقمية أو فارغة.")

st.subheader("جدول النتائج (مع النسبة)")
show_cols = []
if col_name != "(بدون)":
    show_cols.append(col_name)
show_cols += [col_score, "النسبة %"]

st.dataframe(df_valid[show_cols].sort_values("النسبة %"), use_container_width=True)

st.subheader("تحميل ملف النتائج")
# Build output excel
out = io.BytesIO()
with pd.ExcelWriter(out, engine="openpyxl") as writer:
    df_valid.to_excel(writer, index=False, sheet_name="النتائج")
    summary = pd.DataFrame({
        "البند": ["عدد الطالبات", "المتوسط الحسابي", "متوسط النسبة %", "عدد أقل من 50%", "نسبة أقل من 50%"],
        "القيمة": [total_count, round(mean_score, 2), f"{mean_percent:.2f}%", below_50_count, f"{below_50_percent:.2f}%"]
    })
    summary.to_excel(writer, index=False, sheet_name="ملخص")

st.download_button(
    "⬇️ تنزيل Excel (النتائج + الملخص)",
    data=out.getvalue(),
    file_name="نتائج_الدرجات.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
