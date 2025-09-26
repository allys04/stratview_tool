FROM python:3.12.3
WORKDIR /api_app
COPY requirements.txt ./requirements.txt
COPY stratapi.py ./stratapi.py
COPY stratdata.db ./stratdata.db
RUN pip3 install -r api_requirements.txt
COPY . .
CMD [ "sh", "-c", "uvicorn stratapi:api_app --host=0.0.0.0 --port=$PORT" ]

WORKDIR /frontend_app
COPY pages/1_Data_Visualisation.py ./pages/1_Data_Visualisation.py
COPY pages/2_Model_Information.py ./pages/2_Model_Information.py
COPY http_verbs.py ./http_verbs.py
COPY Introduction.py ./Introduction.py
RUN pip3 install -r frontend_requirements.txt
COPY . .
CMD streamlit run --server.port $PORT Introduction.py