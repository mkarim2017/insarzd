FROM hysds/pge-isce_giant

MAINTAINER aria-ops "aria-ops@list.jpl.nasa.gov"
LABEL description="ALOS2 PGE container"


USER root

#RUN pip3 install 'pyproj==1.9.6'
#RUN pip install 'pyproj==1.9.6'

USER ops


# copy insarzd code ensure proper permissions, and move dependencies to final locations
COPY . /home/ops/verdi/ops/insarzd
RUN set -ex \
 && sudo /usr/bin/pip3 install joblib netcdf4 \
 && sudo rm -rf /root/.cache \
 && sudo chown -R ops:ops /home/ops/verdi/ops/insarzd \
 #&& mv /home/ops/verdi/ops/insarzd/spyddder-man /home/ops/verdi/ops/ \
 #&& mv /home/ops/verdi/ops/insarzd/slcp2pm /home/ops/verdi/ops/ \
 #&& mv /home/ops/verdi/ops/insarzd/slcp2cor /home/ops/verdi/ops/ \
 #&& cd /home/ops/verdi/ops/slcp2pm/src \
 #&& ./compile.sh \
 #&& cd /home/ops/verdi/ops/slcp2cor/src \
 #&& ./compile.sh

# set entrypoint
WORKDIR /home/ops
CMD ["/bin/bash", "--login"]
