#!/usr/bin/env python
import rospy
import socket
import requests
import json
import numpy as np
from geometry_msgs.msg import Pose, Point, Quaternion, PoseArray

def checkState(IP_ADDRESS, PORT, API_KEY, SMARTSUIT_NAME, COUNTDOWN_DELAY):
    data = {
    'smartsuit_name': SMARTSUIT_NAME,
    'countdown_delay': COUNTDOWN_DELAY
  }
    request = requests.post("http://{}:{}/v1/{}/calibrate".format(IP_ADDRESS, PORT, API_KEY),  data=json.dumps(data))
    if request.status_code != 200:
        print("The suit may not be connected... Status code != 200")
    print("Wait until connection...")
    while requests.post("http://{}:{}/v1/{}/calibrate".format(IP_ADDRESS, PORT, API_KEY),  data=json.dumps(data)).status_code != 200:
        continue
    print("Connection identified")
      

def makeMsg(data):
    pointMsg = Point()
    quatMsg = Quaternion()
    poseMsg = Pose()
    pointMsg.x = data['position']['x']
    pointMsg.y = data['position']['y']
    pointMsg.z = data['position']['z']
    quatMsg.x = data['rotation']['x']
    quatMsg.y = data['rotation']['y']
    quatMsg.z = data['rotation']['z']
    quatMsg.w = data['rotation']['w']

    poseMsg.position = pointMsg
    poseMsg.orientation = quatMsg
    return poseMsg

IP_ADDRESS = '192.169.0.2' # Replace with actual ip address
PORT = '14041' # Replace with actual port
API_KEY = 'dgps' # Replace with actual api key
SMARTSUIT_NAME = 'U94' # Optional
COUNTDOWN_DELAY = 1 # Optional

# Head : head
# Shoulder : shoulder bone
# Upper Arm: upper arm bone
# Lower Arm : lower arm bone 
# back Hand : back hand 
# Hip : pelvis bone (calculated through two sensors at pelvis' each bone)
# Up Leg : upper leg bone 
# Lower Leg : lower leg bone 
# back foot : back foot

if __name__ == "__main__":
    rospy.init_node("EXOSUIT")
    # Internal loop back socket communication
    server_addr = ("127.0.0.1", 10000)
    
    # socket.SOCK_DGRAM ,  this argument depends  whether communication protocol is UDP or TCP 
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.bind(server_addr)
    posesPub = rospy.Publisher("/exosuit", PoseArray, queue_size=1000)
    
    checkState(IP_ADDRESS, PORT, API_KEY, SMARTSUIT_NAME, COUNTDOWN_DELAY)
    
    while not rospy.is_shutdown():
        data, addr = client.recvfrom(1024000)
        data = json.loads(data)
        
        #print(data)
        #print(data['actors'][0]['leftShoulder']['position'])
        #print(data['actors'][0]['leftUpperArm']['position'])
        #print(data['actors'][0]['leftLowerArm']['position'])
        #print(data['actors'][0]['leftHand']['position'])
        #print(data['actors'][0]['leftFoot']['position'])
        #print(data['actors'][0]['head']) 

        headMsg = makeMsg(data['actors'][0]['head'])
        leftShoulderboneMsg = makeMsg(data['actors'][0]['leftShoulder'])
        leftUpperArmboneMsg = makeMsg(data['actors'][0]['leftUpperArm'])
        leftLowerArmboneMsg = makeMsg(data['actors'][0]['leftLowerArm'])
        leftBackhandMsg = makeMsg(data['actors'][0]['leftHand'])
        rightShoulderboneMsg = makeMsg(data['actors'][0]['rightShoulder'])
        rightUpperArmboneMsg = makeMsg(data['actors'][0]['rightUpperArm'])
        rightLowerArmboneMsg = makeMsg(data['actors'][0]['rightLowerArm'])
        rightBackhandMsg = makeMsg(data['actors'][0]['rightHand'])
        
        pelvisBoneMsg = makeMsg(data['actors'][0]['hip'])
        spineboneMsg = makeMsg(data['actors'][0]['spine'])
        chestboneMsg = makeMsg(data['actors'][0]['chest'])
        leftUpLegboneMsg = makeMsg(data['actors'][0]['leftUpLeg'])
        leftLowerLegboneMsg = makeMsg(data['actors'][0]['leftLeg'])
        leftBackFootMsg = makeMsg(data['actors'][0]['leftFoot'])
        rightUpLegboneMsg = makeMsg(data['actors'][0]['rightUpLeg'])
        rightLowerLegboneMsg = makeMsg(data['actors'][0]['rightLeg'])
        rightBackFootMsg = makeMsg(data['actors'][0]['rightFoot'])

        posesMsg = PoseArray()
        posesMsg.poses.append(headMsg)  
        posesMsg.poses.append(leftShoulderboneMsg)
        posesMsg.poses.append(leftUpperArmboneMsg)
        posesMsg.poses.append(leftLowerArmboneMsg)
        posesMsg.poses.append(leftBackhandMsg)
        posesMsg.poses.append(rightShoulderboneMsg)
        posesMsg.poses.append(rightUpperArmboneMsg)
        posesMsg.poses.append(rightLowerArmboneMsg)
        posesMsg.poses.append(rightBackhandMsg)
        
        posesMsg.poses.append(pelvisBoneMsg)
        posesMsg.poses.append(spineboneMsg)
        posesMsg.poses.append(chestboneMsg)
        posesMsg.poses.append(leftUpLegboneMsg)
        posesMsg.poses.append(leftLowerLegboneMsg)
        posesMsg.poses.append(leftBackFootMsg)
        posesMsg.poses.append(rightUpLegboneMsg)
        posesMsg.poses.append(rightLowerLegboneMsg)
        posesMsg.poses.append(rightBackFootMsg)


        posesPub.publish(posesMsg)