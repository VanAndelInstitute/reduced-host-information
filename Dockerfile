#base python image
FROM python:3.12.4 AS compiler
ENV PYTHONBUFFERED=1

#specify where future commands will run and where the files are copied
WORKDIR /code/
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

#copy everything in current directory into working directory
COPY ./requirements.txt /code/requirements.txt
COPY ./requirements-dev.txt  /code/requirements-dev.txt

#install all requirements
RUN pip install --no-cache-dir -r ./requirements.txt
RUN pip install --no-cache-dir -r ./requirements-dev.txt

#create a runner
FROM python:3.12.4 AS runner
WORKDIR /code/
COPY --from=compiler /opt/venv /opt/venv

#copy everything in current directory into working directory
ENV PATH="/opt/venv/bin:$PATH"
COPY . /code/
CMD ["python","./modules/reduced_host_information.py"]