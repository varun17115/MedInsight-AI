@echo off
echo Starting MedInsight AI Platform...

:: Use Python 3.11 since Python 3.14 breaks Streamlit's protobuf dependency
py -3.11 -m streamlit run app.py
pause
