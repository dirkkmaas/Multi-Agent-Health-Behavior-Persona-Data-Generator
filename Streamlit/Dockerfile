# should be changed to slim in the future 
FROM python:3.11.10 

WORKDIR /streamlit

COPY Streamlit/requirements.txt /streamlit/requirements.txt
RUN pip install --no-cache-dir -r /streamlit/requirements.txt

COPY Streamlit/ /streamlit/

EXPOSE 8501

CMD ["streamlit", "run", "main.py", "--server.address", "0.0.0.0", "--server.port", "8501"]

