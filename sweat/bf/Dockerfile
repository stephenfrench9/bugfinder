FROM stephenfrench9/base

COPY . /app
WORKDIR /app
RUN source env/bin/activate
RUN pip install elasticsearch

ENTRYPOINT ["python"]
CMD ["main.py"]
