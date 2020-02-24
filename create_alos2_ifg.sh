#!/bin/bash
BASE_PATH=$(dirname "${BASH_SOURCE}")
BASE_PATH=$(cd "${BASE_PATH}"; pwd)

# source ISCE env
export PYTHONPATH=/usr/local/isce:$PYTHONPATH
export ISCE_HOME=/usr/local/isce/isce
export INSARZD_HOME=$HOME/insarzd
export PATH=$ISCE_HOME/applications:$ISCE_HOME/bin:/usr/local/gdal/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/gdal/lib:$LD_LIBRARY_PATH
export GDAL_DATA=/usr/local/gdal/share/gdal
export INSAR_ZERODOP_SCR=$HOME/insarzd/scripts
export INSAR_ZERODOP_BIN=$HOME/insarzd/bin
export PYTHONPATH=$INSAR_ZERODOP_SCR:$INSAR_ZERODOP_SCR/pac:$PYTHONPATH
export PATH=$INSAR_ZERODOP_SCR:$INSAR_ZERODOP_BIN:$PATH

# source environment
source $HOME/verdi/bin/activate

echo "##########################################" 1>&2
echo -n "Running ALOS2 interferogram generation : " 1>&2
date 1>&2
python3 $BASE_PATH/create_alos2_ifg.py > create_alos2_ifg.log 2>&1
#python3 $BASE_PATH/test.py > test.log 2>&1
STATUS=$?
echo -n "Finished running ALOS2 interferogram generation: " 1>&2
date 1>&2
if [ $STATUS -ne 0 ]; then
  echo "Failed to run ALOS2 interferogram generation." 1>&2
  echo "# ----- errors|exception found in log -----" >> _alt_traceback.txt && grep -i "error\|exception" create_alos2_ifg.log >> _alt_traceback.txt
  cat create_alos2_ifg.log 1>&2
  echo "{}"
  exit $STATUS
fi
