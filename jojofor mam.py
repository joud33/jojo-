import streamlit as st
import pandas as pd

st.set_page_config(page_title="تحليل الدرجات", page_icon="📊", layout="wide")

st.title("📊 برنامج تحليل درجات الطالبات")
st.write("ارفعي أي ملف Excel واختاري عمود الدرجات، والباقي علينا 😉")

uploaded = st.file_uploader("ارفعي ملف Excel", type=["xlsx", "xls"])

if uploaded is not None:
    try:
        df = pd.read_excel(uploaded)
    except:
        st.error("في مشكلة بقراءة الملف 😢 تأكدي إنه Excel صحيح")
        st.stop()

    if df.empty:
        st.error("الملف فاضي")
        st.stop()

    st.subheader("معاينة البيانات")
    st.dataframe(df.head())

    columns = df.columns.tolist()

    score_column = st.selectbox("اختاري عمود الدرجات", columns)

    max_score = st.number_input("الدرجة الكاملة (من كم؟)", min_value=1.0, value=100.0)

    # نحول القيم لأرقام
    df[score_column] = pd.to_numeric(df[score_column], errors="coerce")

    df = df.dropna(subset=[score_column])

    if len(df) == 0:
        st.error("ما فيه درجات رقمية في العمود المختار")
        st.stop()

    # نحسب النسبة
    df["النسبة %"] = (df[score_column] / max_score) * 100

    المتوسط = df[score_column].mean()
    متوسط_النسبة = df["النسبة %"].mean()

    اقل_من_50 = df[df["النسبة %"] < 50]
    نسبة_اقل_من_50 = (len(اقل_من_50) / len(df)) * 100

    st.subheader("📌 النتائج")

    col1, col2, col3 = st.columns(3)

    col1.metric("المتوسط الحسابي", f"{المتوسط:.2f}")
    col2.metric("متوسط النسبة من 100", f"{متوسط_النسبة:.2f}%")
    col3.metric("نسبة أقل من 50%", f"{نسبة_اقل_من_50:.2f}%")

    st.write(f"عدد الطالبات أقل من 50%: {len(اقل_من_50)}")

    st.subheader("📋 جدول بعد الحساب")
    st.dataframe(df)
