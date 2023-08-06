FROM fnndsc/centos-python3
LABEL MAINTAINER=caisd<caisd1@midea.com>

WORKDIR /apps

COPY requirements.txt aria2.py gotobt.py ./
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "gotobt.py" ]