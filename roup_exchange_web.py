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
st.write("Exchange students between groups **only if gender matches**.")

# ----------------------------
# Initial Data (Session State)
# ----------------------------
if "students" not in st.session_state:
    st.session_state.students = pd.DataFrame([
        {"Name": "Amina", "Gender": "F", "Group": 1},
        {"Name": "Sara", "Gender": "F", "Group": 2},
        {"Name": "Fatima", "Gender": "F", "Group": 2},
        {"Name": "Youssef", "Gender": "M", "Group": 1},
        {"Name": "Omar", "Gender": "M", "Group": 2},
        {"Name": "Hamza", "Gender": "M", "Group": 3},
    ])

df = st.session_state.students

# ----------------------------
# Display Table
# ----------------------------
st.subheader("📋 Current Students")
st.dataframe(df, use_container_width=True)

# ----------------------------
# Exchange Section
# ----------------------------
st.subheader("🔁 Request an Exchange")

student_name = st.selectbox(
    "Select student",
    df["Name"].tolist()
)

target_group = st.selectbox(
    "Target group",
    sorted(df["Group"].unique())
)

# ----------------------------
# Exchange Logic
# ----------------------------
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

            # Swap groups
            df.loc[df["Name"] == student_name, "Group"] = target_group
            df.loc[df["Name"] == partner["Name"], "Group"] = student["Group"]

            st.success(
                f"✅ Exchange successful!\n\n"
                f"🔁 {student_name} ↔ {partner['Name']}"
            )

            st.session_state.students = df
            st.rerun()

# ----------------------------
# Footer
# ----------------------------
st.markdown("---")
st.caption("Designed for classroom group management")
