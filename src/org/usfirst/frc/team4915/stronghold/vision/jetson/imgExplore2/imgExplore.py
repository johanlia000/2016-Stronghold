#!/usr/bin/python
#
#
# imgExplore.py
#   a python/opencv utility for perusing video or image streams.
#   Performance issues can be resolved by migrating algorithms to
#   gpu. (VisionWorks, Cuda, etc are available optimization avenues)
#
#   db: 1/28/16, for spartronics 4915
#
#
from __future__ import print_function
import cv2
import os.path
import sys, traceback
import argparse
import numpy as np
import math
from multiprocessing.pool import ThreadPool
from collections import deque

import robotCnx
import planeTracker
import common

class App:
    def __init__(self):
        self.args = self.parseArgs()
        # args is argparser.Namespace: an object whose members are 
        # accessed as:  self.args.cannedimages

        self.robotCnx = robotCnx.RobotCnx(self.args.fakerobot)

        self.vsrc = None
        if self.args.cannedimages:
            self.fnpat = '../../pictures/RealFullField/%d.jpg'
        else:
            self.fnpat = None
        self.index = 0
        self.lastFn = None
        self.mainImg = None
        self.algostate = {}  # stores persistant objects depending on cmode
        self.threadn = cv2.getNumberOfCPUs()
        self.pool = ThreadPool(processes = self.threadn)
        self.pending = deque()
        self.threadedMode = True
        self.update = False
        self.latency = common.StatValue()   
        self.frameT = common.StatValue() 
        self.lastFrameTime = common.clock()
        self.zeros = (0,0,0,0,0,0)

        self.indent = ' ' * 50
        self.lastStatus = ""

        # cmodelist maps a number [0, len] to an cmode/algorithm
        self.cmodelist = [
            'rgb',
            'adaptiveThreshold',
            'threshold',
            'huerange*valrange',
            'canny',
            'simpleblob',
            'houghlines',
            'contours',
            'ORB',

            'b',
            'g',
            'h',
            'r',
            's',
            'v',
        ]

        # cmodeValueCache stores the edited values associated with each cmode.
        # It starts empty, then builds up state as cmode changes.
        self.cmodeValueCache = {
            'adaptiveThreshold': [-4, 0, 0, 0, 0, 0],
            'threshold':         [75, 0, 0, 0, 0, 0],
            'huerange*valrange': [79, 91, 100, 255, 0, 0],
            'canny':             [10, 200, 0, 0, 0, 0],
            'simpleblob':        [75, 150, 5, 150, 0, 0], 
                          # minThresh
                          # maxThresh
                          # thresStep
                          # minSize (maxsize is 'large')
            'houghlines':        [2, 5, 10, 30, 2, 0], 
                          # rho is distance resolution in pixels
                          # theta is angle in degress (larger -> more lines)
                          # threshold is measured in 'votes', higher -> fewer 
                          # minLineLength
                          # maxLineGap
            'contours':          [1, 0, 0, -1, 1, 0],
                          # mode: [0-3]
                          # method: [CHAIN_APPROX_NONE,_SIMPLE,_TC89_L1, KOS]
                          # offset shift for contour
                          # unused
                          # which contour to draw, -1 is all
                          # which level of the contours to draw
            'ORB':              [40, 10, 8, 31, 0, 0],
                          # nfeatures
                          # scaleFactor [1 -> 2  (0->255)]
                          # nlevels
                          # patchSizea == edgeThreshold
            'r': self.zeros,
            'g': self.zeros,
            'b': self.zeros,
            'h': self.zeros,
            's': self.zeros,
            'v': self.zeros,
            'rgb': self.zeros
        }

        #keyToCmode maps a key to a cmod
        self.keyToCmode = {
            49: self.cmodelist[1], # adaptiveThreshold on '1' key
            50: self.cmodelist[2],
            51: self.cmodelist[3],
            52: self.cmodelist[4],
            53: self.cmodelist[5],
            54: self.cmodelist[6], # houghlines
            55: self.cmodelist[7], # contours
            56: self.cmodelist[8], # ORB

            98: 'b',
            99: 'rgb',
            103: 'g',
            104: 'h',
            114: 'r',
            115: 's',
            118: 'v',
        }

        self.keyToFrameChange = {
            81: 'b',
            83: 'n',
        }

        self.algoValueChange = {
            127: ("reset",  self.zeros),  # keypad clear

            190: ("v1Down",  (-1, 0, 0, 0, 0, 0)), # f1
            191: ("v1Up  ",  (1, 0, 0, 0, 0, 0)),  # f2

            84: ("v1Down",  (-1, 0, 0, 0, 0, 0)), # downarrow
            82: ("v1Up  ",  (1, 0, 0, 0, 0, 0)),  # uparrow

            191: ("v1Up  ",  (1, 0, 0, 0, 0, 0)),  # downarrow

            192: ("v2Down",  (0, -1, 0, 0, 0, 0)), # f3
            193: ("v2Up  ",  (0, 1, 0, 0, 0, 0)),  # f4

            194: ("v3Down",  (0, 0, -1, 0, 0, 0)), # f5
            195: ("v3Up  ",  (0, 0, 1, 0, 0, 0)),  # f6

            196: ("v4Down",  (0, 0, 0, -1, 0, 0)), # f7
            197: ("v4Up  ",  (0, 0, 0, 1, 0, 0)), # f8

            198: ("v5Down",  (0, 0, 0, 0, -1, 0)), # f9
            199: ("v5Up  ",  (0, 0, 0, 0, 1, 0)), # f10

            200: ("v6Down",  (0, 0, 0, 0, 0, -1)), # f10
            201: ("v6Up  ",  (0, 0, 0, 0, 0, 1)),  # f11
        }

        self.cmode = self.getCmode(self.args.algorithm)
        self.values = self.getCmodeValues(self.cmode)

    # end of __init__

    # -----------------------------------------------------------------
    def Run(self):
        print("\n\nkeys:\n" \
      "  ESC: exit\n\n" \
      "  c: rgb\n" \
      "  r: red\n" \
      "  g: green\n" \
      "  b: blue,\n" \
      "  h: hue\n" \
      "  s: sat\n"\
      "  v: val\n" \
      "  1: adaptive threshold (thresh,inv)\n"\
      "  2: threshold          (thresh,inv)\n"\
      "  3: huerange*valrange  (hmin,hmax,vmin,vmax)\n"\
      "  4: canny edges        (thresh/10, range)\n"\
      "  5: simple blobs       (thresh0,thresh1,minA,aMult,colorthresh)\n"\
      "  6: houghlines         (rho,theta,thresh,minlen,maxgap)\n"\
      "  7: contours           (mode:0-3,method:0-3,offset,id(-1:all),depth)\n"\
      "  8: ORB features       (nfeatures,scaleFactor(0->255)],patchSize)\n"\
      "  9: PlaneTracker       (unimplemented)\n"\
      "\n"\
      "  F1,F2:            -/+ v1\n"\
      "  F3,F4:            -/+ v2\n"\
      "  F5,F6:            -/+ v3\n"\
      "  F7,F8:            -/+ v4\n"\
      "  F9,F10:           -/+ v5\n"\
      "  F10,F11:          -/+ v6\n"\
      "\n"\
      "  <right arrow>:    increase img seq frame\n"\
      "  <left arrow>:     decrease img seq frame\n"\
          )

        if not self.fnpat:
            vsrc = cv2.VideoCapture(0)
            if not vsrc or not vsrc.isOpened():
                print("Problem opening video source")
                vsrc = None
                exit(1)
            else:
                w = vsrc.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
                h = vsrc.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
                self.putNotice("video is %dx%d" % (w, h))
                if 0:
                    vsrc.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, w)
                    vsrc.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, h)
        else:
            vsrc = None

        self.update = False
        while True:
            while len(self.pending) > 0 and self.pending[0].ready():
                frame,t0,keypoints,lines,contours = self.pending.popleft().get()
                self.latency.update(common.clock() - t0)
                self.robotCnx.SetFPS(int(1/self.frameT.value))

                if not self.args.nodisplay:
                    self.drawStr(frame, (20, 20), 
                        "latency       : %.1f ms" % (self.latency.value*1000))
                    self.drawStr(frame, (20, 40), 
                        "frame interval: %.1f ms" % (self.frameT.value*1000))
                    self.showImg(frame, keypoints, lines, contours)

            if vsrc:
                # Here we have a video source... Capture the image in the 
                # main thread, process it in other threads.
                if len(self.pending) < self.threadn:
                    # we have threads available to perform work for us
                    ret, self.mainImg = vsrc.read() # <---can take some time
                    t = common.clock()
                    self.frameT.update(t - self.lastFrameTime)
                    self.lastFrameTime = t
                    # pass a copy of the new frame to another thread for 
                    # processing this alows us to get back to the 
                    # time-consuming task of capturing the next video frame.
                    task = self.pool.apply_async(processFrameCB, 
                                            (self, self.mainImg.copy(), t))
                    self.pending.append(task)

                ret = self.checkKey(1, self.cmode, self.index, self.values)
                done,self.update,self.cmode,self.index,self.values,msg=ret

                if msg:
                    self.putStatus(msg)

                if done:
                    break
            else:
                # Here we don't have a video source, rather rely on 'canned' 
                #  images. Thus, we don't use multiple threads... just do it 
                #  all right here.
                if self.index < 0:
                    # index < 0 signals user's intent to go bkd in framelist
                    goback = True
                    self.index = abs(self.index)
                else:
                    goback = False
                fn = self.fnpat % self.index
                base = os.path.basename(fn)
                if not os.path.isfile(fn) and self.index >= 0:
                    # image sequence may be missing some frames..
                    self.putNotice(base+" not found")
                    if goback:
                        self.index = -(self.index-1)
                    else:
                        self.index = self.index+1
                    continue

                if fn != self.lastFn or self.update:
                    if not self.update:
                        # update the current filename status field
                        self.putNotice(base)

                    self.mainImg = cv2.imread(fn, cv2.IMREAD_ANYCOLOR)
                    (img, t0, keypts, lines, contours) = self.processFrame(
                                                        self.mainImg.copy(), 
                                                        common.clock())
                    self.frameT.update(common.clock() - t0)
                    self.robotCnx.SetFPS(int(1 / self.frameT.value))

                    if not self.args.nodisplay:
                        if self.cmode == 'rgb':
                            str = "%s     (%.2f ms)" % \
                                    (base,self.frameT.value*1000)
                        else:
                            str = "%s[%s] (%.2f ms)" % \
                                    (base,self.cmode,self.frameT.value*1000)
                        self.drawStr(img, (20, 20), str)
                        self.showImg(img, keypts, lines, contours)

                    self.lastFn = fn

                ret = self.checkKey(10, self.cmode, self.index, self.values)
                done,self.update,self.cmode,self.index,self.values,msg = ret
                if msg:
                    self.putStatus(msg)

                if done:
                    break
        # end of while
        self.robotCnx.Shutdown()
    # end of Run()

    # --------------------------------------------------------------------
    def parseArgs(self):
        # perhaps we should bundle all this behavior into -runmode
        #   runmode: production == nodisplay, realrobot, video
        #   debugi:  display, fakerobot, novideo
        #   debugv:  display, fakerobot, video
        parser = argparse.ArgumentParser()
        parser.add_argument("-c", "--cannedimages",
                            help="use canned images instead of video", 
                            action='store_true')
        parser.add_argument("-n", "--nodisplay",
                            help="disable display of images to screen",
                            action='store_true')
        parser.add_argument("-f", "--fakerobot",
                            help="connect to fake robot on localhost", 
                            action='store_true')
        parser.add_argument("-a", "--algorithm",
                            default=0,
                            type=int,
                            help="select an algorithm between 0 and 6")
        return parser.parse_args()

    def simpleThreshold(self, frame, vals=None):
        if vals:
            tvals = vals
        else:
            tvals = self.getCmodeValues('threshold')
        if tvals[1] == 0:
            thresh = cv2.THRESH_BINARY
        else:
            thresh = cv2.THRESH_BINARY_INV
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        (ret,gray) = cv2.threshold(gray, tvals[0],
                                  200, # value to draw
                                  thresh)
        return gray

    def hvRange(self, frame):
        hvvals = self.getCmodeValues('huerange*valrange')
        # threshold value (want bright areas)
        # multiply result by hue in range
        mode = cv2.COLOR_BGR2HSV # or: cv2.COLOR_HSV2BGR)
        hsv = cv2.cvtColor(frame, mode)
        h,s,v = cv2.split(hsv)
        himg = cv2.inRange(h, hvvals[0], hvvals[1])
        vimg = cv2.inRange(v, hvvals[2], hvvals[3])
        return cv2.multiply(vimg, himg, scale=1.0/255)

    def processFrame(self, frame, t0):
        keypoints = None
        lines = None
        contours = None
        cmode = self.cmode
        values = self.values
        if cmode != 'rgb':
            if cmode in ['h', 's', 'v']:
                #mode = (cv2.COLOR_BGR2HLS, cv2.COLOR_HLS2BGR)
                mode = (cv2.COLOR_BGR2HSV, cv2.COLOR_HSV2BGR)
                hsv = cv2.cvtColor(frame, mode[0])
                if cmode == 'h':
                    if mode[0] == cv2.COLOR_BGR2HSV: 
                        hsv[:,:,1] = 255 # s = 1
                        hsv[:,:,2] = 128 # v = .5
                    else:
                        hsv[:,:,1] = 128 # l = .5 
                        hsv[:,:,2] = 255 # s = 1
                    frame = cv2.cvtColor(hsv, mode[1])
                elif cmode == 's':
                    # extract the s as grayscale
                    if mode[0] == cv2.COLOR_BGR2HSV: 
                        h,frame,v = cv2.split(hsv)
                    else:
                        h,l,frame = cv2.split(hsv)
                elif cmode == 'v':
                    if mode[0] == cv2.COLOR_BGR2HSV: 
                        h,s,frame = cv2.split(hsv)
                    else:
                        h,frame,s = cv2.split(hsv)
            elif cmode in ['r', 'g', 'b']:
                if cmode == 'r':
                    b,g,frame = cv2.split(frame)
                elif cmode == 'g':
                    b,frame,r = cv2.split(frame)
                elif cmode == 'b':
                    frame,g,r = cv2.split(frame)
            elif cmode == 'adaptiveThreshold':
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                if values[1] == 0:
                    thresh = cv2.THRESH_BINARY
                else:
                    thresh = cv2.THRESH_BINARY_INV
                frame = cv2.adaptiveThreshold(gray, 
                                            200, # value to draw
                                            cv2.ADAPTIVE_THRESH_MEAN_C,
                                            thresh,
                                            5, 
                                            values[0])
            elif cmode == 'threshold':
                frame = self.simpleThreshold(frame, values)
            elif cmode == 'huerange*valrange':
                frame = self.hvRange(frame)
            elif cmode == 'canny': 
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                v1 = values[0]*200
                v2 = v1 + values[1]
                frame = cv2.Canny(frame, v1, v2, apertureSize=5)
            elif cmode == 'simpleblob':
                if not "blobdetector" in self.algostate or self.update:
                    bp = cv2.SimpleBlobDetector_Params()

                    if values[4] >= 0:
                        bp.filterByColor = True
                        bp.blobColor = values[4]  # 0 or 255  (?)
                    else:
                        bp.filterByColor = False
                        bp.blobColor = 0 

                    # Change thresholds
                    bp.minThreshold = values[0]  # 50
                    bp.maxThreshold = values[1]  # 150
                    bp.thresholdStep = values[2] # 5

                    # Filter by Area.
                    bp.filterByArea = True
                    bp.minArea = values[3]       # 500
                    bp.maxArea = (640 * 480) / 3   

                    # Filter by Circularity
                    bp.filterByCircularity = False
                    bp.minCircularity = 0.1

                    # Filter by Convexity
                    bp.filterByConvexity = False
                    bp.minConvexity = 0.87

                    # Filter by Inertia
                    bp.filterByInertia = False
                    bp.minInertiaRatio = 0.01
                    
                    detector = cv2.SimpleBlobDetector(bp)
                    self.algostate["blobdetector"] = detector
                else:
                    detector = self.algostate["blobdetector"] 

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                keypoints = detector.detect(frame) # we'll draw them
                keypoints = self.robotCnx.NewKeypoints(keypoints)
            elif cmode == "houghlines":
                cv = self.getCmodeValues('canny')
                bwf = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                v1 = cv[0]*200
                v2 = v1 + cv[1]
                bwf = cv2.Canny(bwf, v1, v2, apertureSize=5)
                rho = max(values[0], 1)
                theta = max(math.radians(values[1]), 0)
                threshold = max(values[2], 1) # votes needed to accept a line
                minlen = values[3]
                maxgap = values[4]
                lines = cv2.HoughLinesP(bwf, 
                                        rho,  # distance res of accum in pixels
                                        theta,
                                        threshold,
                                        minLineLength=minlen,
                                        maxLineGap=maxgap)
                lines = self.robotCnx.NewLines(lines)
            elif cmode == 'contours':
                gray = self.simpleThreshold(frame)
                mode = cv2.RETR_TREE  #values[0]
                method = cv2.CHAIN_APPROX_SIMPLE  #values[1]
                off = (values[2], values[3])
                contours = cv2.findContours(gray, mode, method, offset=off)
                # NB: contours may be tuple (contours, hierarchy)
            elif cmode == 'ORB':
                if not "ORB" in self.algostate or self.update:
                    sf = max(1, min(2, 1. + values[1]/255.)) # [1->2]
                    self.algostate["ORB"] = cv2.ORB( nfeatures=values[0],
                                                scaleFactor=sf,
                                                nlevels=values[2],
                                                patchSize=values[3],
                                                edgeThreshold=values[3])
                                            # could add: 
                                            #   WTA_K: 2
                                            #   scoreType ORB_HARRIS_SCORE
                                            #  patchSize ~= edgeThreshold

                orb = self.algostate["ORB"]
                #keypoints,descrs = orb.detectAndCompute(frame, None)
                #gray = self.simpleThreshold(frame)
                gray = self.hvRange(frame)
                keypoints = orb.detect(gray, None)
                self.putNotice('ORB features: %d' % len(keypoints))
                frame = gray
            else:
                print("unknown cmode: " + cmode)
        return frame, t0, keypoints, lines, contours

    def showImg(self, frame, keypoints, lines, contours):
        if not self.args.nodisplay:
            if keypoints:
                frame = cv2.drawKeypoints(frame, [keypoints[0]],
                                   np.array([]),
                                   (0,0,255), 
                                   cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS) 
                if len(keypoints) > 1:
                    frame = cv2.drawKeypoints(frame, keypoints[1:],
                                   np.array([]),
                                   (255,205,25), 
                                   cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS) 
            if lines != None:
                for l in lines[0]:
                    cv2.line(frame, (l[0], l[1]), (l[2], l[3]), (20,255,255))

            if contours != None:
                contours0,hier = contours
                cindex = self.values[3] # if -1, all are drawn
                maxlevel = self.values[4]
                if len(contours0) <= cindex:
                    self.putNotice("reset contour id")
                    values[3] = -1
                    cindex = -1
                cv2.drawContours(frame, contours0, cindex,
                                (128,255,255), 
                                thickness=1, 
                                lineType=cv2.CV_AA,
                                hierarchy=hier, 
                                maxLevel=maxlevel)
                
            cv2.imshow("img", frame)


    def getCmode(self, num):
        return self.cmodelist[num]

    def getCmodeValues(self, cmode):
        if cmode in self.cmodeValueCache:
            return self.cmodeValueCache[cmode]
        else:
            print("%s not cached, ..." % cmode)
        return self, zeros

    def setCmodeValues(self, cmode, values):
        self.cmodeValueCache[cmode] = values 

    def checkKey(self, waitMS, cmode, index, values):
        done=False
        forceUpdate=False
        msg = None
        key = 0xFF & cv2.waitKey(waitMS)
        if key == 27: # ESC
            done=True
        elif key == 255:
            pass
        elif key in self.keyToCmode:
            # change cmode requested
            self.setCmodeValues(cmode, values) # stash values for last cmode
            cmode = self.keyToCmode[key]
            values = self.getCmodeValues(cmode)
            msg = "%s:%s          " % (cmode, str(values))
            forceUpdate = True
        elif key in self.keyToFrameChange:
            if self.keyToFrameChange[key] == 'n':
                index = (index + 1)
            else:
                index = -(index - 1)
        elif key in self.algoValueChange:
            dv = self.algoValueChange[key]
            if dv[0] == "reset":
                values = dv[1]
            else:
                values = map(sum, zip(values, dv[1]))
            forceUpdate = True
        else:
            self.putNotice("unbound key %d '%s'" % (key, chr(key)))

        if forceUpdate:
            msg = "%s %s" % (cmode, str(values))

        return done,forceUpdate,cmode,index,values,msg

    def putStatus(self, msg):
        if msg:
            self.lastStatus = (msg + self.indent)[:49]
        sys.stdout.write(' ' + self.lastStatus + '\r')
        sys.stdout.flush()

    def putNotice(self, msg):
        sys.stdout.write((self.indent + msg + self.indent)[:78] + '\r')
        self.putStatus(None)
        sys.stdout.flush()

    def drawStr(self, img, pos, str):
        cv2.putText(img, str, pos, cv2.FONT_HERSHEY_PLAIN, 1, 
                    (0, 0, 0), thickness=2)  # colors arb bgr
        cv2.putText(img, str, pos, cv2.FONT_HERSHEY_PLAIN, 1, 
                    (244, 100, 100))  # colors arb bgr

def processFrameCB(o, frame, t0):
    return o.processFrame(frame, t0)

if __name__ == '__main__':
    App().Run()

