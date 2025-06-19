FROM python:3.11.10 

WORKDIR /hb_agent

COPY HB_Agent/requirements.txt /hb_agent/requirements.txt
RUN pip install --no-cache-dir -r /hb_agent/requirements.txt

COPY HB_Agent/ /hb_agent/
COPY Data /hb_agent/Data  

RUN apt-get update && \
    apt-get install -y dos2unix && \
    dos2unix /hb_agent/chroma_db.sh && \
    chmod +x /hb_agent/chroma_db.sh && \
    rm -rf /var/lib/apt/lists/*

EXPOSE 5000

CMD ["/hb_agent/chroma_db.sh"]