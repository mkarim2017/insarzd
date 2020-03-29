#!/usr/bin/env python3 
import os, sys, re, requests, json, shutil, traceback, logging, hashlib, math
import math
from glob import glob
from UrlUtils import UrlUtils
from subprocess import check_call, CalledProcessError
from datetime import datetime
import xml.etree.cElementTree as ET
from xml.etree.ElementTree import Element, SubElement
from zipfile import ZipFile
from create_input_xml import create_input_xml

log_format = "[%(asctime)s: %(levelname)s/%(funcName)s] %(message)s"
logging.basicConfig(format=log_format, level=logging.INFO)
logger = logging.getLogger('create_alos2_ifg.log')


BASE_PATH = os.path.dirname(__file__)

def fileContainsMsg(file_name, msg):
    with open(file_name, 'r') as f:
        datafile = f.readlines()
    for line in datafile:
        if msg in line:
            # found = True # Not necessary
            return True, line
    return False, None

def checkBurstError():
    msg = "cannot continue for interferometry applications"

    found, line = fileContainsMsg("alos2app.log", msg)
    if found:
        logger.info("checkBurstError : %s" %line.strip())
        raise RuntimeError(line.strip())
    if not found:
        msg = "Exception: Could not determine a suitable burst offset"
        found, line = fileContainsMsg("alos2app.log", msg)
        if found:
            logger.info("Found Error : %s" %line)
            raise RuntimeError(line.strip())

def updateXml(xml_file):
    logging.info(xml_file)
    path = os.path.split(xml_file)[0]
    tree = ET.parse(xml_file)
    root = tree.getroot()    


    for elem in root:
        if elem.tag == 'property':
            d = elem.attrib
            if 'name' in d.keys() and d['name'] == 'file_name':
       
                for n in elem:
                    if n.tag == 'value':
                        new_value = os.path.join(path, n.text)
                        n.text = new_value
                        logging.info(n.text)
    logging.info(tree)
    tree = ET.ElementTree(root)
    tree.write(xml_file) 

def get_SNWE(min_lon, max_lon, min_lat, max_lat):
    dem_S = min_lat
    dem_N = max_lat
    dem_W = min_lon
    dem_E = max_lon

    dem_S = int(math.floor(dem_S))
    dem_N = int(math.ceil(dem_N))
    dem_W = int(math.floor(dem_W))
    dem_E = int(math.ceil(dem_E))

    return "{} {} {} {}".format(dem_S, dem_N, dem_W, dem_E)

def run_command(cmd):
    cmd_line = " ".join(cmd)
    logging.info("calling : {}".format(cmd_line))
    check_call(cmd_line, shell=True)


def move_dem_separate_dir(dir_name):
    move_dem_separate_dir_SRTM(dir_name)
    move_dem_separate_dir_NED(dir_name)

def move_dem_separate_dir_SRTM(dir_name):
    logger.info("move_dem_separate_dir_SRTM : %s" %dir_name)
    create_dir(dir_name)

    move_cmd=["mv", "demLat*", dir_name]
    move_cmd_line=" ".join(move_cmd)
    logger.info("Calling {}".format(move_cmd_line))
    call_noerr(move_cmd_line)

def move_dem_separate_dir_NED(dir_name):
    logger.info("move_dem_separate_dir_NED : %s" %dir_name)
    create_dir(dir_name)
    move_cmd=["mv", "stitched.*", dir_name]
    move_cmd_line=" ".join(move_cmd)
    logger.info("Calling {}".format(move_cmd_line))
    call_noerr(move_cmd_line)

    move_cmd=["mv", "*DEM.vrt", dir_name]
    move_cmd_line=" ".join(move_cmd)
    logger.info("Calling {}".format(move_cmd_line))
    call_noerr(move_cmd_line)

def create_dir(dir_name):
    '''
    if os.path.isdir(dir_name):
        rmdir_cmd=["rm", "-rf", dir_name]
        rmdir_cmd_line=" ".join(rmdir_cmd)
        logger.info("Calling {}".format(rmdir_cmd_line))
        call_noerr(rmdir_cmd_line)
    '''
    if not os.path.isdir(dir_name):
        mkdir_cmd=["mkdir", dir_name]
        mkdir_cmd_line=" ".join(mkdir_cmd)
        logger.info("create_dir : Calling {}".format(mkdir_cmd_line))
        call_noerr(mkdir_cmd_line)

def call_noerr(cmd):
    """Run command and warn if exit status is not 0."""

    try: check_call(cmd, shell=True)
    except Exception as e:
        logger.warn("Got exception running {}: {}".format(cmd, str(e)))
        logger.warn("Traceback: {}".format(traceback.format_exc()))

def download_dem(SNWE):
    uu = UrlUtils()
    dem_user = uu.dem_u
    dem_pass = uu.dem_p
    srtm3_dem_url = uu.dem_url
    ned1_dem_url = uu.ned1_dem_url
    ned13_dem_url = uu.ned13_dem_url
    dem_type_simple = "SRTM3"
    preprocess_dem_dir="preprocess_dem"
    geocode_dem_dir="geocode_dem"
    dem_type = "SRTM3"
 
    wd = os.getcwd()
    logging.info("Working Directory : {}".format(wd))

    dem_url = srtm3_dem_url
    dem_cmd = [
                "/usr/local/isce/isce/applications/dem.py", "-a",
                "stitch", "-b", "{}".format(SNWE),
                "-k", "-s", "1", "-f", "-c", "-n", dem_user, "-w", dem_pass,
                "-u", dem_url
            ]
    dem_cmd_line = " ".join(dem_cmd)
    logging.info("Calling dem.py: {}".format(dem_cmd_line))
    check_call(dem_cmd_line, shell=True)
    preprocess_dem_file = glob("*.dem.wgs84")[0]

    #cmd= ["rm", "*.zip",  *.dem *.dem.vrt *.dem.xml"
    #check_call(cmd, shell=True)

    preprocess_dem_dir = "{}_{}".format(dem_type_simple, preprocess_dem_dir)


    logger.info("dem_type : %s preprocess_dem_dir : %s" %(dem_type, preprocess_dem_dir))
    if dem_type.startswith("NED"):
        move_dem_separate_dir_NED(preprocess_dem_dir)
    elif dem_type.startswith("SRTM"):
        move_dem_separate_dir_SRTM(preprocess_dem_dir)
    else:
        move_dem_separate_dir(preprocess_dem_dir)

    preprocess_dem_file = os.path.join(preprocess_dem_dir, preprocess_dem_file)
    logger.info("Using Preprocess DEM file: {}".format(preprocess_dem_file))

    #preprocess_dem_file = os.path.join(wd, glob("*.dem.wgs84")[0])
    #logging.info("preprocess_dem_file : {}".format(preprocess_dem_file))

    # fix file path in Preprocess DEM xml
    fix_cmd = [
        "/usr/local/isce/isce/applications/fixImageXml.py",
        "-i", preprocess_dem_file, "--full"
    ]
    fix_cmd_line = " ".join(fix_cmd)
    logger.info("Calling fixImageXml.py: {}".format(fix_cmd_line))
    check_call(fix_cmd_line, shell=True)

    preprocess_vrt_file=""
    if dem_type.startswith("SRTM"):
        preprocess_vrt_file = glob(os.path.join(preprocess_dem_dir, "*.dem.wgs84.vrt"))[0]
    elif dem_type.startswith("NED1"):
        preprocess_vrt_file = os.path.join(preprocess_dem_dir, "stitched.dem.vrt")
        logger.info("preprocess_vrt_file : %s"%preprocess_vrt_file)
    else: raise RuntimeError("Unknown dem type %s." % dem_type)

    if not os.path.isfile(preprocess_vrt_file):
        logger.info("%s does not exists. Exiting")
    
    preprocess_dem_xml = glob(os.path.join(preprocess_dem_dir, "*.dem.wgs84.xml"))[0]
    logging.info("preprocess_dem_xml : {}".format(preprocess_dem_xml))
    updateXml(preprocess_dem_xml)

    geocode_dem_dir = os.path.join(preprocess_dem_dir, "Coarse_{}_preprocess_dem".format(dem_type_simple))
    create_dir(geocode_dem_dir)
    dem_cmd = [
        "{}/applications/downsampleDEM.py".format(os.environ['ISCE_HOME']), "-i",
        "{}".format(preprocess_vrt_file), "-rsec", "3"
    ]
    dem_cmd_line = " ".join(dem_cmd)
    logger.info("Calling downsampleDEM.py: {}".format(dem_cmd_line))
    check_call(dem_cmd_line, shell=True)
    geocode_dem_file = ""

    logger.info("geocode_dem_dir : {}".format(geocode_dem_dir))
    if dem_type.startswith("SRTM"):
        geocode_dem_file = glob(os.path.join(geocode_dem_dir, "*.dem.wgs84"))[0]
    elif dem_type.startswith("NED1"):
        geocode_dem_file = os.path.join(geocode_dem_dir, "stitched.dem")
    logger.info("Using Geocode DEM file: {}".format(geocode_dem_file))

    checkBurstError()

    # fix file path in Geocoding DEM xml
    fix_cmd = [
        "{}/applications/fixImageXml.py".format(os.environ['ISCE_HOME']),
        "-i", geocode_dem_file, "--full"
    ]
    fix_cmd_line = " ".join(fix_cmd)
    logger.info("Calling fixImageXml.py: {}".format(fix_cmd_line))
    check_call(fix_cmd_line, shell=True)


    '''
    dem_xml_file_1 = os.path.join(wd, glob("*.dem.wgs84.xml")[0])
    logging.info("dem_xml_file_1 : {}".format(dem_xml_file_1))
    updateXml(dem_xml_file_1)

    preprocess_dem_dir = wd
    preprocess_vrt_file = glob(os.path.join(preprocess_dem_dir, "*.dem.wgs84.vrt"))[0]

    if not os.path.isfile(preprocess_vrt_file):
        logger.info("%s does not exists. Exiting")
    

    cmd= ["mkdir", "3"]
    cmd_line = " ".join(cmd)
    check_call(cmd_line, shell=True)
    new_dir = os.path.join(wd, "3")

    geocode_dem_dir=os.path.join(wd, "3")

    #os.chdir(geocode_dem_dir)

    cmd= ["pwd"]
    cmd_line = " ".join(cmd)
    check_call(cmd_line, shell=True)
    dem_cmd = [
        "/usr/local/isce/isce/applications/downsampleDEM.py", "-i",
        "{}".format(preprocess_vrt_file), "-rsec", "3"
    ]
    dem_cmd_line = " ".join(dem_cmd)
    logger.info("Calling downsampleDEM.py: {}".format(dem_cmd_line))
    check_call(dem_cmd_line, shell=True)
    geocode_dem_file = ""

    logger.info("geocode_dem_dir : {}".format(geocode_dem_dir))
    geocode_dem_file = glob(os.path.join(geocode_dem_dir, "*.dem.wgs84"))[0]
    logger.info("Using Geocode DEM file: {}".format(geocode_dem_file))

    checkBurstError()

    # fix file path in Geocoding DEM xml
    fix_cmd = [
        "/usr/local/isce/isce/applications/fixImageXml.py",
        "-i", geocode_dem_file, "--full"
    ]
    fix_cmd_line = " ".join(fix_cmd)
    logger.info("Calling fixImageXml.py: {}".format(fix_cmd_line))
    check_call(fix_cmd_line, shell=True)

    
    dem_cmd = [
                "/usr/local/isce/isce/applications/dem.py", "-a",
                "stitch", "-b", "{}".format(SNWE),
                "-k", "-s", "3", "-f", "-c", "-n", dem_user, "-w", dem_pass,
                "-u", dem_url
            ]
    dem_cmd_line = " ".join(dem_cmd)
    logging.info("Calling dem.py: {}".format(dem_cmd_line))
    check_call(dem_cmd_line, shell=True)

    #cmd= "rm *.zip *.log *.dem *.dem.vrt *.dem.xml"
    #check_call(cmd, shell=True)
    '''

    geocode_dem_xml = glob(os.path.join(geocode_dem_dir, "*.dem.wgs84.xml"))[0]
    logging.info("geocode_dem_xml : {}".format(geocode_dem_xml))
    updateXml(geocode_dem_xml)

    os.chdir(wd)
    cmd= ["pwd"]
    cmd_line = " ".join(cmd)
    check_call(cmd_line, shell=True)

    return preprocess_dem_xml, geocode_dem_xml

def unzip_slcs(slcs):
    for k, v in slcs.items():
        logging.info("Unzipping {} in {}".format(v, k))
        with ZipFile(v, 'r') as zf:
            zf.extractall(k)
        logging.info("Removing {}.".format(v))
        #try: os.unlink(v)
        #except: pass

def main():

    wd = os.getcwd()
    
    new_dir= "{}/src".format(BASE_PATH)
    logging.info(new_dir)
    os.chdir(new_dir)
    cmd = "./install.sh"
    os.system(cmd)

    os.chdir(wd)
    cmd= ["pwd"]
    run_command(cmd)

    min_lon = 119.25384521484376
    max_lon = 120.58868408203126
    min_lat = -1.2749954674414934
    max_lat = 0.2822101626099863

    SNWE = get_SNWE(min_lon, max_lon, min_lat, max_lat)

    SNWE = "14 25 -109 -91"
    logging.info("SNWE : {}".format(SNWE))
    dem_xml_file_1, dem_xml_file_3 = download_dem(SNWE)
   
    exit(0)
    slcs = {"reference" : "0000230036_001001_ALOS2227337160-180808.zip", "secondary" : "0000230039_001001_ALOS2235617160-181003.zip"}
    unzip_slcs(slcs)

    xml_file = "alos2app_scansar-stripmap.xml"
    tmpl_file = "alos2app_scansar-stripmap.xml.tmpl"
    ref_data_dir = os.path.join(wd, "reference")
    sec_data_dir = os.path.join(wd, "secondary")
    dem_file = os.path.splitext(dem_xml_file_1)[0]
    geocoded_dem_file = os.path.splitext(dem_xml_file_3)[0]
    start_subswath = 1
    end_subswath = 5
    burst_overlap = 85.0
    
    create_input_xml(os.path.join(BASE_PATH, tmpl_file), xml_file,
                     str(ref_data_dir), str(sec_data_dir),
                     str(dem_file), str(geocoded_dem_file), start_subswath, end_subswath, burst_overlap)


    alos2_start_time=datetime.now()
    logger.info("ALOS2 Start Time : {}".format(alos2_start_time)) 

    cmd = ["python3", "{}/scripts/alos2app.py".format(BASE_PATH), "-i", "{}".format(xml_file), "-e", "coherence"]
    run_command(cmd)

    cmd = ["python3", "{}/scripts/ion.py".format(BASE_PATH), "-i", "{}".format(xml_file)]
    run_command(cmd)

    cmd = ["python3", "{}/scripts/alos2app.py".format(BASE_PATH), "-i", "{}".format(xml_file), "-s", "filter"]
    run_command(cmd)




if __name__ == '__main__':
    complete_start_time=datetime.now()
    logger.info("TopsApp End Time : {}".format(complete_start_time))
    cwd = os.getcwd()

    ctx_file = os.path.abspath('_context.json')
    if not os.path.exists(ctx_file):
        raise RuntimeError("Failed to find _context.json.")
    with open(ctx_file) as f:
        ctx = json.load(f)

    main()
