FROM python:3-alpine

RUN pip3 install requests beautifulsoup4 && mkdir -p /reachee

COPY . /reachee

CMD ["python","/reachee/reachee.py","/reachee/reachee.json"]