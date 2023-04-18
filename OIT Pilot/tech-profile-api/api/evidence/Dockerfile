FROM public.ecr.aws/lambda/python:3.8

COPY requirements.txt ./
COPY model /opt/ml/model
RUN pip install -r requirements.txt
RUN python3.8 -m pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_trf-3.4.1/en_core_web_trf-3.4.1-py3-none-any.whl
RUN python3.8 -m pip install sentence_transformers

COPY index.py entity_linker.py ./
CMD ["index.handler"]
