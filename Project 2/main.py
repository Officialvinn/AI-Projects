import streamlit as st
import PyPDF2
import io
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Resume Critiquer", page_icon=":clipboard:", layout="centered")

st.title("Resume Critiquer")
st.markdown("Upload your resume and get feedback on how to improve it.")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

uploaded_file = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf", "txt"])
job_role = st.text_input("Enter the job role you are targeting (optional):")

analyze = st.button("Analyze Resume")


def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += (page.extract_text() or "") + "\n"
    return text


def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    return uploaded_file.read().decode("utf-8")


if analyze and not uploaded_file:
    st.warning("Please upload a resume first.")

if analyze and uploaded_file:
    if not OPENAI_API_KEY:
        st.error("OPENAI_API_KEY is not set. Add it to your .env file.")
        st.stop()

    try:
        file_content = extract_text_from_file(uploaded_file)

        if not file_content.strip():
            st.error("The uploaded file is empty or could not be read. Please upload a valid PDF or text file.")
            st.stop()

        prompt = f"""Please analyze this resume and provide constructive feedback.
Focus on the following aspects:
1. Content clarity and impact
2. Skill presentation
3. Experience descriptions
4. Specific improvements for the job role: {job_role if job_role else 'general job applications'}

Resume content:
{file_content}

Please provide your analysis in a clear, structured format with specific recommendations."""

        client = OpenAI(api_key=OPENAI_API_KEY)
        with st.spinner("Analyzing your resume..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert resume reviewer with years of experience in HR and recruitment."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=1000,
            )
        st.markdown("### Analysis Results")
        st.markdown(response.choices[0].message.content)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
