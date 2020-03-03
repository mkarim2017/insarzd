FROM hysds/pge-isce_giant

MAINTAINER aria-ops "aria-ops@list.jpl.nasa.gov"
LABEL description="ALOS2 PGE container"


USER root

#RUN pip3 install 'pyproj==1.9.6'
#RUN pip install 'pyproj==1.9.6'

USER ops


# copy insarzd code ensure proper permissions, and move dependencies to final locations
COPY . /home/ops/insarzd
RUN set -ex \
 && sudo /usr/bin/pip3 install joblib netcdf4 \
 && sudo rm -rf /root/.cache \
 && sudo chown -R ops:ops /home/ops/insarzd 

# set entrypoint
WORKDIR /home/ops
CMD ["/bin/bash", "--login"]
