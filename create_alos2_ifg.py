#!/usr/bin/env python3 
import os, sys, re, requests, json, shutil, traceback, logging, hashlib, math
import math
from glob import glob
from UrlUtils import UrlUtils
from subprocess import check_call, CalledProcessError
from datetime import datetime
import xml.etree.cElementTree as ET
from xml.etree.ElementTree import Element, SubElement

log_format = "[%(asctime)s: %(levelname)s/%(funcName)s] %(message)s"
logging.basicConfig(format=log_format, level=logging.INFO)
logger = logging.getLogger('create_alos2_ifg.log')


BASE_PATH = os.path.dirname(__file__)

def updateXml(xml_file):
    print(xml_file)
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
                        print(n.text)
    print(tree)
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

def download_dem(SNWE):
    uu = UrlUtils()
    dem_user = uu.dem_u
    dem_pass = uu.dem_p
    srtm3_dem_url = uu.dem_url
    ned1_dem_url = uu.ned1_dem_url
    ned13_dem_url = uu.ned13_dem_url
   
    wd = os.getcwd()
    print("Working Directory : {}".format(wd))

    dem_url = srtm3_dem_url
    dem_cmd = [
                "/usr/local/isce/isce/applications/dem.py", "-a",
                "stitch", "-b", "{}".format(SNWE),
                "-k", "-s", "1", "-f", "-c", "-n", dem_user, "-w", dem_pass,
                "-u", dem_url
            ]
    dem_cmd_line = " ".join(dem_cmd)
    print("Calling dem.py: {}".format(dem_cmd_line))
    check_call(dem_cmd_line, shell=True)

    #cmd= ["rm", "*.zip",  *.dem *.dem.vrt *.dem.xml"
    #check_call(cmd, shell=True)

    dem_xml_file_1 = os.path.join(wd, glob("*.dem.wgs84.xml")[0])
    print("dem_xml_file_1 : {}".format(dem_xml_file_1))
    updateXml(dem_xml_file_1)

    cmd= ["mkdir", "3"]
    cmd_line = " ".join(cmd)
    check_call(cmd_line, shell=True)
    new_dir = os.path.join(wd, "3")

    os.chdir(new_dir)

    cmd= ["pwd"]
    cmd_line = " ".join(cmd)
    check_call(cmd_line, shell=True)
    
    dem_cmd = [
                "/usr/local/isce/isce/applications/dem.py", "-a",
                "stitch", "-b", "{}".format(SNWE),
                "-k", "-s", "3", "-f", "-c", "-n", dem_user, "-w", dem_pass,
                "-u", dem_url
            ]
    dem_cmd_line = " ".join(dem_cmd)
    print("Calling dem.py: {}".format(dem_cmd_line))
    check_call(dem_cmd_line, shell=True)

    #cmd= "rm *.zip *.log *.dem *.dem.vrt *.dem.xml"
    #check_call(cmd, shell=True)
    
    dem_xml_file_3 = os.path.join(new_dir, glob("*.dem.wgs84.xml")[0])
    print("dem_xml_file_3 : {}".format(dem_xml_file_3))
    updateXml(dem_xml_file_3)

    os.chdir(wd)
    cmd= ["pwd"]
    cmd_line = " ".join(cmd)
    check_call(cmd_line, shell=True)


def main():

    min_lon = 119.25384521484376
    max_lon = 120.58868408203126
    min_lat = -1.2749954674414934
    max_lat = 0.2822101626099863

    SNWE = get_SNWE(min_lon, max_lon, min_lat, max_lat)
    print(SNWE)
    download_dem(SNWE)
   

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
