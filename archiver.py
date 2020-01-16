import oss2
import sys
import json
import argparse
import os
import fnmatch
import logging
import time
from datetime import datetime


config={}


def main():
    parser = argparse.ArgumentParser(description='Ship configured logs into aliyun oss bucket')
    parser.add_argument("--config", required=True, help="config file of %(prog) program")
    args=parser.parse_args()

    loadConfig(args.config)
    process()
    
    return 0

def loadConfig(configFile):
    global config
    logLevelDict= {"CRITICAL":50, "ERROR":40, "WARNING":30, "INFO":20, "DEBUG":10, "NOTSET":0}

    try:
        with open(configFile, 'r') as content_file:
            content = content_file.read()
    except IOError:
        sys.stderr.write("Cannot open the config file %s \n" % config)
        sys.exit(1)

    config=json.loads(content)    

    logLevel=config["LogLevel"].upper()
    if not logLevel in logLevelDict.keys():
        sys.stderr.write("Invalid log level defined in config: %s \n" % logLevel)
        sys.exit(2)

    logging.basicConfig(filename=config["LogFile"],level=logLevelDict[logLevel], format="%(asctime)s - %(levelname)s - %(message)s")

def process():
    logPathes=config["Collectors"]["LogPath"]
    for logPath in logPathes:
        logging.debug("Traversing %s" % logPath)
        pattern=logPath.split("/")[-1]
        basedir="/".join(logPath.split("/")[0:-1])
        files=findFiles(pattern, basedir)
        for file in files:
            fileRoot=file["root"]
            fileName=file["name"]
            fileFullPath=file["fullpath"]
            fileINode=file["inode"]
            logging.debug("Checking file: %s" % file)
            
            lastFileInodeProcessed=getLastFileInode(fileFullPath)

            if fileINode == lastFileInodeProcessed:
                logging.info("Skipping %s, it's already processed." % fileFullPath)
                continue

            upload(file)

def findFiles(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                item={}
                item["root"]=root
                item["name"]=name
                item["fullpath"]=os.path.join(root, name)
                item["inode"]=os.stat(item["fullpath"]).st_ino
                item["size"]=os.stat(item["fullpath"]).st_size
                result.append(item)
    return result

def getLastFileInode(filePath):
    global config
    datadir=config["DataDir"]
    datadir=datadir+"/" if datadir[-1] != "/" else datadir
    filePath=filePath.replace("/","_")
    
    if not os.path.exists(datadir + filePath):
        logging.debug("%s doesn't exists so return 0 as inode" % (datadir+filePath))
        return 0

    with open(datadir + filePath, 'r') as content_file:
        content = content_file.read()

    logging.debug("%s found so return %s as inode" % (datadir+filePath, content))
    return int(content)

def now():
    return datetime.now().strftime('%Y%m%d')

def upload(file):
    global config

    filePath=file["fullpath"]
    fileName=file["name"]
    size=file["size"]
    inode=file["inode"]
    datadir=config["DataDir"]
    datadir=datadir+"/" if datadir[-1] != "/" else datadir
    disarmedFilePath=filePath.replace("/","_")
    accessKeyId=config["Aliyun"]["AccessKeyID"]
    accessKeySecret=config["Aliyun"]["AccessKeySecret"]
    bucketName=config["Aliyun"]["BucketName"]
    endpoint=config["Aliyun"]["Endpoint"]
    prefix=config["Aliyun"]["Prefix"]
    prefix=prefix if prefix[-1]=="/" else prefix+"/"
    appendDateTime=True if config["AppendDataTimeToNameOfFile"] == "true" else False
    fileKey=prefix+fileName
    fileKey=fileKey+"-"+now() if appendDateTime else fileKey

    if not os.path.exists(datadir):
        os.mkdir(datadir)

    logging.info("uploading %s with %s in size" % (filePath, size))

    startTime=time.time()
    auth=oss2.Auth(accessKeyId, accessKeySecret)
    bucket=oss2.Bucket(auth, endpoint, bucketName)
    bucket.put_object_from_file(fileKey, filePath)
    elapsedTime=time.time()-startTime
    logging.info("uploading of %s took %s seconds" % (filePath, elapsedTime))

    with open(datadir + disarmedFilePath, 'w') as fd:
        fd.write(str(inode))

    return    

if __name__ == "__main__":
    sys.exit(main())
