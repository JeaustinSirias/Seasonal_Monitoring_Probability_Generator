#############################################################
#							                                #
#         Seasonal Monitoring & Probability Generator	    #
#	                Jeaustin Sirias Chacón 		            #
#                    Copyright (C) 2020		                #
#							                                #
#############################################################

FROM python:3.7

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "make", "run"]





