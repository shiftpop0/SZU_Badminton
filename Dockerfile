FROM python:3.9-slim
 
WORKDIR /TicketRobber
 
ADD . /TicketRobber
 
RUN python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple && pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
 
EXPOSE 8501

CMD ["/usr/local/bin/streamlit","run", "web_ui.py"]
