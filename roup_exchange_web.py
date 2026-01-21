import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ----------------------------
# File Paths for Persistence
# ----------------------------
STUDENTS_FILE = "students.csv"
REQUESTS_FILE = "requests.csv"
LOGS_FILE = "logs.csv"

# ----------------------------
# Page Configuration
# ----------------------------
st.set_page_config(
    page_title="Persistent Student Group Exchange",
    layout="centered"
)

st.title("🔄 Persistent Student Group Exchange")
st.write(
    "Students submit mutual requests. Exchanges happen **only if requests match and gender is same**. "
    "Data is saved automatically."
)

# ----------------------------
# Helper Functions
# ----------------------------
def load_csv(path, columns):
    if os.path.exists(path):
        return pd.read_csv(path)
    else:
        return pd.DataFrame(columns=columns)

def save_csv(df, path):
    df.to_csv(path, index=False)

def log_action(action, student1, student2=None):
    logs = load_csv(LOGS_FILE, ["Date", "Action", "Student1", "Student2"])
    logs = pd.concat([logs, pd.DataFrame([{
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Action": action,
        "Student1": student1,
        "Student2": student2 if student2 else ""
    }])], ignore_index=True)
    save_csv(logs, LOGS_FILE)

# ----------------------------
# Load Persistent Data
# ----------------------------
students = load_csv(STUDENTS_FILE, ["Name", "Gender", "Group"])
requests_df = load_csv(REQUESTS_FILE, ["Name", "TargetGroup"])

# ----------------------------
# Add Student Section
# ----------------------------
st.subheader("➕ Add Student")
with st.form("add_student_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input("Student Name")
    with col2:
        gender = st.selectbox("Gender", ["F","M"])
    with col3:
        group = st.number_input("Group", min_value=1, step=1)

    submitted = st.form_submit_button("Add Student")
    if submitted:
        if not name.strip():
            st.error("❌ Name cannot be empty.")
        elif name in students["Name"].values:
            st.error("❌ Student already exists.")
        else:
            students = pd.concat([students, pd.DataFrame([{"Name": name.strip(), "Gender": gender, "Group": group}])], ignore_index=True)
            save_csv(students, STUDENTS_FILE)
            log_action("Added Student", name)
            st.success(f"✅ {name} added successfully!")

# ----------------------------
# Display Students
# ----------------------------
st.subheader("📋 Current Students")
if students.empty:
    st.info("No students added yet.")
else:
    st.dataframe(students, use_container_width=True)

# ----------------------------
# Submit Exchange Request
# ----------------------------
st.subheader("📝 Submit Exchange Request")
if not students.empty:
    student_name = st.selectbox("Select student", students["Name"].tolist())
    current_group = students[students["Name"]==student_name]["Group"].iloc[0]
    target_group = st.number_input("Target Group", min_value=1, step=1, value=current_group)

    if st.button("Submit Request"):
        if target_group == current_group:
            st.warning("⚠ Already in this group.")
        elif student_name in requests_df["Name"].values:
            st.warning("⚠ You already submitted a request.")
        else:
            requests_df = pd.concat([requests_df, pd.DataFrame([{"Name": student_name, "TargetGroup": target_group}])], ignore_index=True)
            save_csv(requests_df, REQUESTS_FILE)
            log_action("Submitted Request", student_name)
            st.success(f"Request submitted: {student_name} → Group {target_group}")

# ----------------------------
# Show Pending Requests
# ----------------------------
st.subheader("📌 Pending Requests")
if requests_df.empty:
    st.info("No requests yet.")
else:
    st.dataframe(requests_df, use_container_width=True)

# ----------------------------
# Process Exchanges
# ----------------------------
st.subheader("🔁 Process Eligible Exchanges")
if st.button("Process Exchanges"):
    processed = []
    for _, req in requests_df.iterrows():
        student_name = req["Name"]
        target_group = req["TargetGroup"]
        student = students[students["Name"]==student_name].iloc[0]
        student_gender = student["Gender"]
        current_group = student["Group"]

        # Find reciprocal request from a student of same gender
        reciprocal = requests_df[
            (requests_df["TargetGroup"]==current_group) &
            (requests_df["Name"]!=student_name)
        ]
        reciprocal = reciprocal[
            reciprocal["Name"].apply(lambda n: students[students["Name"]==n]["Gender"].iloc[0]==student_gender)
        ]

        if not reciprocal.empty:
            partner_name = reciprocal.iloc[0]["Name"]
            partner_group = students[students["Name"]==partner_name]["Group"].iloc[0]

            # Swap groups
            students.loc[students["Name"]==student_name,"Group"] = partner_group
            students.loc[students["Name"]==partner_name,"Group"] = current_group
            processed.append(f"{student_name} ↔ {partner_name}")

            # Remove processed requests
            requests_df = requests_df[~requests_df["Name"].isin([student_name, partner_name])]
            log_action("Processed Exchange", student_name, partner_name)

    save_csv(students, STUDENTS_FILE)
    save_csv(requests_df, REQUESTS_FILE)

    if processed:
        st.success("✅ Exchanges processed:")
        for p in processed:
            st.write(f"🔁 {p}")
    else:
        st.info("No eligible exchanges found.")

# ----------------------------
# Logs Section
# ----------------------------
st.subheader("📜 Logs")
if os.path.exists(LOGS_FILE):
    logs = pd.read_csv(LOGS_FILE)
    if logs.empty:
        st.info("No logs yet.")
    else:
        st.dataframe(logs, use_container_width=True)
else:
    st.info("No logs yet.")

# ----------------------------
# Footer
# ----------------------------
st.markdown("---")
st.caption("Persistent Web App for classroom group management with mutual requests and logs")
