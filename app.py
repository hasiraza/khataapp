import streamlit as st
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import os
import tempfile

SRC_FOLDER = "src"
os.makedirs(SRC_FOLDER, exist_ok=True)

def create_csv_files():
    persons = ["Ali", "Umer", "Haseeb", "Talha"]
    for person in persons:
        file = os.path.join(SRC_FOLDER, f"{person}.csv")
        if not os.path.exists(file):
            df = pd.DataFrame(columns=["Date", "Time", "Amount"])
            df.to_csv(file, index=False)

create_csv_files()

def convert_csv_to_pdf(csv_file, total):
    df = pd.read_csv(csv_file)
    pdf_path = tempfile.mktemp(".pdf")
    pdf = SimpleDocTemplate(pdf_path, pagesize=letter)
    data = [df.columns.tolist()] + df.values.tolist()
    table = Table(data)
    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold')
    ])
    table.setStyle(style)
    styles = getSampleStyleSheet()
    summary = Paragraph(f"<b>Total Amount:</b> {total}", styles["Normal"])
    pdf.build([table, summary])
    return pdf_path

def send_email(receiver_email, pdf_path, person_name, total):
    sender_email = "khataapp45@gmail.com"
    sender_password = "aymp ottt dktf cnpt"
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = f"{person_name}'s Report (Total: {total})"
    msg.attach(MIMEText(f"Attached is {person_name}'s data report.\nTotal Amount: {total}", 'plain'))
    with open(pdf_path, "rb") as file:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={person_name}_report.pdf")
        msg.attach(part)
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)

st.set_page_config(page_title="Person Amount Tracker", page_icon="💰")
st.title(" Person Amount Tracker App")

person = st.selectbox("Select a Person", ["Ali", "Umer", "Haseeb", "Talha"])
file_path = os.path.join(SRC_FOLDER, f"{person}.csv")

if os.path.exists(file_path):
    df = pd.read_csv(file_path)
else:
    df = pd.DataFrame(columns=["Date", "Time", "Amount"])
    df.to_csv(file_path, index=False)

st.write(f"📋 {person}'s Current Data:")
st.dataframe(df)

amount = st.number_input("Enter Amount to Add", min_value=0.0, step=1.0)

if st.button("➕ Add Amount"):
    now = datetime.now()
    new_row = {"Date": now.strftime("%Y-%m-%d"), "Time": now.strftime("%H:%M:%S"), "Amount": amount}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(file_path, index=False)
    st.success(f"✅ Added {amount} for {person}")

total = df["Amount"].sum() if not df.empty else 0
st.info(f"💵 Total Amount for {person}: {total}")

email = st.selectbox('Select mail',['umarwatto02828@gmail.com','hasiraza511@gmail.com','alimaqbool0306@gmail.com'])

if st.button("📤 Save & Send Email"):
    if not email:
        st.error("Please enter a valid email!")
    else:
        pdf_path = convert_csv_to_pdf(file_path, total)
        send_email(email, pdf_path, person, total)
        st.success(f"✅ Email sent successfully to {email} with {person}'s PDF report!")
