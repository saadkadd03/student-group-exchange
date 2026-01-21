import streamlit as st
import pandas as pd

# ----------------------------
# Page Configuration
# ----------------------------
st.set_page_config(
    page_title="Student Group Exchange",
    page_icon="🔄",
    layout="centered"
)

st.title("🔄 Student Group Exchange System")
st.write("Manage student groups and exchange students **based on gender**.")

# ----------------------------
# Session State Initialization
# ----------------------------
if "students" not in st.session_state:
    st.session_state.students = pd.DataFrame(
        columns=["Name", "Gender", "Group"]
    )

df = st.session_state.students

# ----------------------------
# Add Student Section
# ----------------------------
st.subheader("➕ Add a Student")

with st.form("add_student_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        name = st.text_input("Student Name")

    with col2:
        gender = st.selectbox("Gender", ["F", "M"])

    with col3:
        group = st.number_input("Group", min_value=1, step=1)

    submitted = st.form_submit_button("Add Student")

    if submitted:
        if not name.strip():
            st.error("❌ Student name cannot be empty.")
        elif name in df["Name"].values:
            st.error("❌ Student already exists.")
        else:
            new_student = pd.DataFrame(
                [{"Name": name.strip(), "Gender": gender, "Group": group}]
            )
            st.session_state.students = pd.concat(
                [df, new_student], ignore_index=True
            )
            st.success(f"✅ {name} added successfully!")
            st.rerun()

# ----------------------------
# Display Students
# ----------------------------
st.subheader("📋 Current Students")

if df.empty:
    st.info("No students added yet.")
else:
    st.dataframe(df, use_container_width=True)

# ----------------------------
# Exchange Section
# ----------------------------
st.subheader("🔁 Exchange Students")

if df.empty:
    st.warning("Please add students first.")
else:
    student_name = st.selectbox(
        "Select student",
        df["Name"].tolist()
    )

    target_group = st.number_input(
        "Target Group",
        min_value=1,
        step=1
    )

    if st.button("Exchange"):
        student = df[df["Name"] == student_name].iloc[0]

        if student["Group"] == target_group:
            st.warning("⚠ Student is already in this group.")
        else:
            candidates = df[
                (df["Group"] == target_group) &
                (df["Gender"] == student["Gender"])
            ]

            if candidates.empty:
                st.error("❌ No student of the same gender found in target group.")
            else:
                partner = candidates.iloc[0]

                df.loc[df["Name"] == student_name, "Group"] = target_group
                df.loc[df["Name"] == partner["Name"], "Group"] = student["Group"]

                st.session_state.students = df
                st.success(
                    f"✅ Exchange successful!\n\n"
                    f"🔁 {student_name} ↔ {partner['Name']}"
                )
                st.rerun()

# ----------------------------
# Footer
# ----------------------------
st.markdown("---")
st.caption("Web app for classroom group management")
