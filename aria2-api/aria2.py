import requests
import json
import subprocess
import xmlrpc.client
import os
import time
import base64

DEFAULT_HOST = '192.168.3.35'
DEFAULT_PORT = 16800
DEFAULT_SECRET = 'prc_password'
SERVER_URI_FORMAT = 'http://{}:{:d}/jsonrpc'

class PyAria2(object):

    def __init__(self,
                 host=DEFAULT_HOST,
                 port=DEFAULT_PORT,
                 secret=DEFAULT_SECRET,
                 session=None):
        '''
        PyAria2 constructor.
        host: string, aria2 rpc host, default is 'localhost'
        port: integer, aria2 rpc port, default is 6800
        session: string, aria2 rpc session saving.
        '''
        if not isAria2Installed():
            raise Exception(
                'aria2 is not installed, please install it before.')

        if not isAria2rpcRunning():
            cmd = 'aria2c' \
                  ' --enable-rpc' \
                  ' --rpc-listen-port %d' \
                  ' --continue' \
                  ' --max-concurrent-downloads=20' \
                  ' --max-connection-per-server=10' \
                  ' --rpc-max-request-size=1024M' % port

            if not session is None:
                cmd += ' --input-file=%s' \
                       ' --save-session-interval=60' \
                       ' --save-session=%s' % (session, session)

            subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)

            count = 0
            while True:
                if isAria2rpcRunning():
                    break
                else:
                    count += 1
                    time.sleep(3)
                if count == 5:
                    raise Exception('aria2 RPC server started failure.')
            print('aria2 RPC server is started.')
        else:
            print('aria2 RPC server is already running.')
        self.server_uri = SERVER_URI_FORMAT.format(host, port)
        self.secret = secret

    def sendJsonRPC(self, data):
        r = requests.post(self.server_uri, data=data)
        print(data)
        return r.text

    def getRPCBody(self, method, params=None):
        '''Create RPC body'''
        uid = '1'
        params = params if params else []
        if self.secret:
            params.insert(0, 'token:{}'.format(self.secret))
        j = json.dumps({
            'jsonrpc': '2.0',
            'id': uid,
            'method': method,
            'params': params,
        })
        return j

    def addUri(self, uris, options=None, position=None):
        '''
        This method adds new HTTP(S)/FTP/BitTorrent Magnet URI.
        uris: list, list of URIs
        options: dict, additional options
        position: integer, position in download queue
        return: This method returns GID of registered download.
        '''
        params = [[uris]]
        if options:
            params.append(options)
        params.append(position)
        return self.sendJsonRPC(data=self.getRPCBody('aria2.addUri', params))

    def addTorrent(self, torrent, uris=None, options=None, position=None):
        '''
        This method adds BitTorrent download by uploading ".torrent" file.
        torrent: string, torrent file path
        uris: list, list of webseed URIs
        options: dict, additional options
        position: integer, position in download queue
        return: This method returns GID of registered download.
        '''
        return self.server.aria2.addTorrent(xmlrpc.client.Binary(open(torrent, 'rb').read()), uris, options, position)

    def addMetalink(self, metalink, options=None, position=None):
        '''
        This method adds Metalink download by uploading ".metalink" file.
        metalink: string, metalink file path
        options: dict, additional options
        position: integer, position in download queue
        return: This method returns list of GID of registered download.
        '''
        return self.server.aria2.addMetalink(xmlrpc.client.Binary(open(metalink, 'rb').read()), options, position)

    def remove(self, gid):
        '''
        This method removes the download denoted by gid.
        gid: string, GID.
        return: This method returns GID of removed download.
        '''
        params = [gid]
        return self.sendJsonRPC(data=self.getRPCBody('aria2.remove', params))


    def forceRemove(self, gid):
        '''
        This method removes the download denoted by gid.
        gid: string, GID.
        return: This method returns GID of removed download.
        '''
        params = [gid]
        return self.sendJsonRPC(data=self.getRPCBody('aria2.forceRemove', params))

    def pause(self, gid):
        '''
        This method pauses the download denoted by gid.
        gid: string, GID.
        return: This method returns GID of paused download.
        '''
        params = [gid]
        return self.sendJsonRPC(data=self.getRPCBody('aria2.pause', params))

    def pauseAll(self):
        '''
        This method is equal to calling aria2.pause() for every active/waiting download.
        return: This method returns OK for success.
        '''
        return self.sendJsonRPC(data=self.getRPCBody('aria2.pauseAll'))

    def forcePause(self, gid):
        '''
        This method pauses the download denoted by gid.
        gid: string, GID.
        return: This method returns GID of paused download.
        '''
        params = [gid]
        return self.sendJsonRPC(data=self.getRPCBody('aria2.forcePause', params))

    def forcePauseAll(self):
        '''
        This method is equal to calling aria2.forcePause() for every active/waiting download.
        return: This method returns OK for success.
        '''
        return self.sendJsonRPC(data=self.getRPCBody('aria2.forcePauseAll'))

    def unpause(self, gid):
        '''
        This method changes the status of the download denoted by gid from paused to waiting.
        gid: string, GID.
        return: This method returns GID of unpaused download.
        '''
        params = [gid]
        return self.sendJsonRPC(data=self.getRPCBody('aria2.unpause', params))

    def unpauseAll(self):
        '''
        This method is equal to calling aria2.unpause() for every active/waiting download.
        return: This method returns OK for success.
        '''
        return self.sendJsonRPC(data=self.getRPCBody('aria2.unpauseAll'))

    def tellStatus(self, gid, keys=None):
        '''
        This method returns download progress of the download denoted by gid.
        gid: string, GID.
        keys: list, keys for method response.
        return: The method response is of type dict and it contains following keys.
        '''
        params = [[gid]]
        if keys:
            params.append(keys)
        return self.sendJsonRPC(data=self.getRPCBody('aria2.tellStatus'))


    def getUris(self, gid):
        '''
        This method returns URIs used in the download denoted by gid.
        gid: string, GID.
        return: The method response is of type list and its element is of type dict and it contains following keys.
        '''
        return self.server.aria2.getUris(gid)

    def getFiles(self, gid):
        '''
        This method returns file list of the download denoted by gid.
        gid: string, GID.
        return: The method response is of type list and its element is of type dict and it contains following keys.
        '''
        return self.server.aria2.getFiles(gid)

    def getPeers(self, gid):
        '''
        This method returns peer list of the download denoted by gid.
        gid: string, GID.
        return: The method response is of type list and its element is of type dict and it contains following keys.
        '''
        return self.server.aria2.getPeers(gid)

    def getServers(self, gid):
        '''
        This method returns currently connected HTTP(S)/FTP servers of the download denoted by gid.
        gid: string, GID.
        return: The method response is of type list and its element is of type dict and it contains following keys.
        '''
        return self.server.aria2.getServers(gid)

    def tellActive(self, keys=None):
        '''
        This method returns the list of active downloads.
        keys: keys for method response.
        return: The method response is of type list and its element is of type dict and it contains following keys.
        '''
        return self.server.aria2.tellActive(keys)

    def tellWaiting(self, offset, num, keys=None):
        '''
        This method returns the list of waiting download, including paused downloads.
        offset: integer, the offset from the download waiting at the front.
        num: integer, the number of downloads to be returned.
        keys: keys for method response.
        return: The method response is of type list and its element is of type dict and it contains following keys.
        '''
        return self.server.aria2.tellWaiting(offset, num, keys)

    def tellStopped(self, offset, num, keys=None):
        '''
        This method returns the list of stopped download.
        offset: integer, the offset from the download waiting at the front.
        num: integer, the number of downloads to be returned.
        keys: keys for method response.
        return: The method response is of type list and its element is of type dict and it contains following keys.
        '''
        return self.server.aria2.tellStopped(offset, num, keys)

    def changePosition(self, gid, pos, how):
        '''
        This method changes the position of the download denoted by gid.
        gid: string, GID.
        pos: integer, the position relative which to be changed.
        how: string.
             POS_SET, it moves the download to a position relative to the beginning of the queue.
             POS_CUR, it moves the download to a position relative to the current position.
             POS_END, it moves the download to a position relative to the end of the queue.
        return: The response is of type integer and it is the destination position.
        '''
        return self.server.aria2.changePosition(gid, pos, how)

    def changeUri(self, gid, fileIndex, delUris, addUris, position=None):
        '''
        This method removes URIs in delUris from and appends URIs in addUris to download denoted by gid.
        gid: string, GID.
        fileIndex: integer, file to affect (1-based)
        delUris: list, URIs to be removed
        addUris: list, URIs to be added
        position: integer, where URIs are inserted, after URIs have been removed
        return: This method returns a list which contains 2 integers. The first integer is the number of URIs deleted. The second integer is the number of URIs added.
        '''
        return self.server.aria2.changeUri(gid, fileIndex, delUris, addUris, position)

    def getOption(self, gid):
        '''
        This method returns options of the download denoted by gid.
        gid: string, GID.
        return: The response is of type dict.
        '''
        return self.server.aria2.getOption(gid)

    def changeOption(self, gid, options):
        '''
        This method changes options of the download denoted by gid dynamically.
        gid: string, GID.
        options: dict, the options.
        return: This method returns OK for success.
        '''
        return self.server.aria2.changeOption(gid, options)

    def getGlobalOption(self):
        '''
        This method returns global options.
        return: The method response is of type dict.
        '''
        return self.server.aria2.getGlobalOption()

    def changeGlobalOption(self, options):
        '''
        This method changes global options dynamically.
        options: dict, the options.
        return: This method returns OK for success.
        '''
        return self.sendJsonRPC(data=self.getRPCBody('aria2.changeGlobalOption', options))


    def getGlobalStat(self):
        '''
        This method returns global statistics such as overall download and upload speed.
        return: The method response is of type struct and contains following keys.
        '''
        return self.sendJsonRPC(data=self.getRPCBody('aria2.getGlobalStat'))


    def purgeDownloadResult(self):
        '''
        This method purges completed/error/removed downloads to free memory.
        return: This method returns OK for success.
        '''
        return self.sendJsonRPC(data=self.getRPCBody('aria2.purgeDownloadResult'))


    def removeDownloadResult(self, gid):
        '''
        This method removes completed/error/removed download denoted by gid from memory.
        return: This method returns OK for success.
        '''
        return self.server.aria2.removeDownloadResult(gid)

    def getVersion(self):
        '''
        This method returns version of the program and the list of enabled features.
        return: The method response is of type dict and contains following keys.
        '''
        return self.sendJsonRPC(data=self.getRPCBody('aria2.getSessionInfo'))


    def getSessionInfo(self):
        '''
        This method returns session information.
        return: The response is of type dict.
        '''
        return self.sendJsonRPC(data=self.getRPCBody('aria2.getSessionInfo'))


    def shutdown(self):
        '''
        This method shutdowns aria2.
        return: This method returns OK for success.
        '''
        return self.sendJsonRPC(self.server_uri, data=self.getRPCBody('aria2.shutdown'))


    def forceShutdown(self):
        '''
        This method shutdowns aria2.
        return: This method returns OK for success.
        '''
        return self.sendJsonRPC(self.server_uri, data=self.getRPCBody('aria2.forceShutdown'))


def isAria2Installed():
    for cmdpath in os.environ['PATH'].split(':'):
        if os.path.isdir(cmdpath) and 'aria2c' in os.listdir(cmdpath):
            return True

    return True


def isAria2rpcRunning():
    pgrep_process = subprocess.Popen(
        'pgrep -l aria2', shell=True, stdout=subprocess.PIPE)

    if pgrep_process.stdout.readline() == b'':
        return True
    else:
        return True

