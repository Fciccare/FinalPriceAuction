import argparse
import sys
import numpy as np
import random
import math
import time
import os
import argparse
import cv2

import qi

class Pepper:
    
    port = str(5556)
    PATH = '/home/antimo/Documenti/Pepper'
    PATH = PATH + '/'
    trial = 10

    def __init__(self, session, ip, args, port):
        self.ip = ip
        self.people_detected = False
        self.people = None
        self.usr_id = []
        self.pitch_param = 0.4
        
        # people sensing
        self.tracker = session.service("ALTracker")
        self.people = session.service("ALPeoplePerception")
        self.people.setTimeBeforePersonDisappears(10)
        self.autonomus = session.service("ALAutonomousLife")

        
        # motion modules
        self.motion = session.service("ALMotion") 
        self.memory = session.service("ALMemory") 
        self.posture = session.service("ALRobotPosture") 
        
        # speech / audio modules
        self.tts = session.service("ALTextToSpeech")
        self.tts.setParameter("speed", 75)
        self.tts.setLanguage("English")
        self.asr = session.service("ALAnimatedSpeech") 
        self.audio = session.service("ALAudioRecorder")
        self.sounds = session.service("ALAudioPlayer") 
        self.animation_player_service = session.service("ALAnimationPlayer")
        self.behavior_player_service = session.service("ALBehaviorManager")
        
        # self.shutter = self.sounds.loadFile('/home/nao/recordings/camera_shutter.wav')
        self.speech = session.service("ALSpeechRecognition") 
        self.leds = session.service("ALLeds")
        
        # camera modules
        self.camera = session.service("ALVideoDevice")
        self.camera.setActiveCamera(0)  # 0 = top, 1 = bottom, 2 = depth
        # if not self.camera.hasDepthCamera():
        #     print 'Depth camera not available.'
        #     return False
        # else:
        #     print 'Depth camera is available.'
        #     self.camera.setResolution(2)
        #     self.camera.setColorSpace(11)
        #self.subscriberID = self.camera.subscribeCamera("DepthCamera", 2, 2, 11, 30)  # name, camera_id, resolution, color_space, fps
        
        self.photo = session.service("ALPhotoCapture")
        self.photo.setResolution(2)
        self.photo.setPictureFormat("png")
        self.photo_angles = [0.0, 0.0] 
        self.video = session.service("ALVideoRecorder") 
        self.video.setFrameRate(30)
        self.video.setVideoFormat("MJPG")
        if self.video.isRecording():
            print('Camera was still recording.')
            videoInfo = self.video.stopRecording()
            
        
    def take_picture(self, im_name='img_'+str(trial), path=PATH):
        # pepper.set_head(0, -0.1)
        # time.sleep(1)
        self.photo.takePicture('/home/nao/recordings/cameras/', 'image')
        n = len([x for x in os.listdir(path) if x[-4:] in ['.JPG','.jpg','.png'] and im_name in x])+1
        filename = path+im_name+'_'+str(n)+'.png'
        # print filename
        self.reset_eyes()
        cmd = 'sshpass -p nao scp nao@'+self.ip+':/home/nao/recordings/cameras/image.png '+filename
        os.system(cmd)
        return filename
    
    def reset_eyes(self):
        self.leds.reset('FaceLeds')
        
    def eyes_color(self, color):
        self.leds.fadeRGB('FaceLeds', color, 0.1)
        
    
    def point_at(self, x, y, z, effector_name, frame):
        """
        Point end-effector in cartesian space
        :Example:
        >>> pepper.point_at(1.0, 1.0, 0.0, "RArm", 0)
        :param x: X axis in meters
        :type x: float
        :param y: Y axis in meters
        :type y: float
        :param z: Z axis in meters
        :type z: float
        :param effector_name: `LArm`, `RArm` or `Arms`
        :type effector_name: string
        :param frame: 0 = Torso, 1 = World, 2 = Robot
        :type frame: integer
        """
        speed = 0.3     # 50 % of speed
        self.tracker.pointAt(effector_name, [x, y, z], frame, speed)
        
        
    def start_recording(self, filename='robot_video'):
        self.video.startRecording("/home/nao/recordings/cameras/", filename)
        time.sleep(1)
    
    def stop_recording(self, filename='robot_video'):
        self.video.stopRecording()
        cmd = 'sshpass -p nao scp nao@'+self.ip+':/home/nao/recordings/cameras/'+filename+'.avi /home/antimo/Documenti/Pepper/videos/'+filename+'.avi'
        os.system(cmd)
    
    def audio_start(self, filename='robot_audio'):
        self.audio.startMicrophonesRecording("/home/nao/recordings/"+filename, "wav", 48000, [0,0,1,0])
        
    def audio_stop(self):
        self.audio.stopMicrophonesRecording()
        
    def copy_audio(self, filename='robot_audio', path='/Users/lucarag/work/uom/data/cog_rob/'):
        n = len([x for x in os.listdir(path) if x[-4:] in ['.WAV','.wav']])+1
        filen = path+filename+'_'+str(n)+'.wav'
        # print filen
        cmd = 'sshpass -p nao scp nao@'+self.ip+':/home/nao/recordings/'+filename+'.wav '+filen
        os.system(cmd)
        return filen
    
    def on_word_recognized(self, value):
        print (value)
        self.speech_not_detected = False
                
    def start_listening(self, filename='robot_audio.wav'):
        self.reset_eyes()    
        vocabulary = ['bubble tea']
        self.speech.setVocabulary(vocabulary, False)
        self.speech_not_detected = True
        self.speech.subscribe("Test_ASR")
        self.subscriberSpeech = self.memory.subscriber("WordRecognized")
        self.subscriberSpeech.signal.connect(self.on_word_recognized)
        
        i = 0
        self.audio_start(filename)
        if args.robot == 'nao':
            self.leds.fadeRGB('FaceLeds', 'green', 1)
        while self.speech_not_detected:
            i = i+1
        # time.sleep(5)
        self.audio_stop()
        if args.robot == 'nao':
            self.leds.reset('FaceLeds')
        print ("hearing completed")
        self.speech.unsubscribe("Test_ASR") 
        return self.copy_audio()
    
    def on_human_tracked(self, value):
        if self.usr_id==[]:
            print (value[1][0][0])
            self.usr_id=value[1][0][0]
        self.people_detected = True
    
    
    def depth_camera(self):
        print ('depth camera ' + str(self.camera.hasDepthCamera()))
        # self.camera.setActiveCamera(2)  # 0 = top, 1 = bottom, 2 = depth
        # if not self.camera.hasDepthCamera():
        #     print 'Depth camera not available.'
        #     return False
        # else:
        #     print 'Depth camera is available.'
        #     self.camera.setResolution(2)
        #     self.camera.setColorSpace(11)  # 11 = depth
        self.camera.startCamera(2)
        no_image = True
        while no_image:
            image = self.camera.getImageRemote(self.subscriberID)
            if image is not None:
                no_image = False
            else:
                print ('No image received yet.')
                time.sleep(0.1)
        # image = self.camera.getImageRemote(self.subscriberID)  # name, camera_id, resolution, color_space, fps
        # print image
        width = image[0]
        height = image[1]
        channels = image[2]
        data = image[6]

        # Convert to OpenCV image
        image_array = np.frombuffer(data, dtype=np.uint8).reshape((height, width, channels))
        cv2.imwrite("camera.png", image_array)
        # cv2.waitKey(1)
        self.camera.releaseImage(self.subscriberID)
        self.camera.stopCamera(2)

    
    def start_tracking(self, just_distance=False):
        
        try:
            self.tracker.registerTarget("Face", 0.2)
            self.tracker.track("Face")

            print("[Thread] Tracker avviato, attendo 4 secondi...")
            time.sleep(4)  # Questo blocco è ora nel thread, non blocca il main

            dist = self.tracker.getTargetPosition()
            print("[Thread] Distanza iniziale:", dist)

            # Inizia a muoversi
            self.motion.moveToward(0.2, 0.0, 0.0)

            # Loop di polling (ora in background)
            while dist and dist[0] > 0.4:
                dist = self.tracker.getTargetPosition()
                print("[Thread] Distanza attuale:", dist)
                time.sleep(0.1) # Controlla 10 volte al secondo, è sufficiente

            print("[Thread] Target raggiunto o perso. Fermo il movimento.")
            
        except Exception as e:
            print(f"[Thread] Errore durante il tracking: {e}")
        
        finally:
            # Questo blocco 'finally' assicura che il robot si fermi
            # e pulisca il tracker ANCHE se il loop fallisce o si interrompe.
            print("[Thread] Pulizia in corso...")
            self.motion.stopMove()
            self.tracker.stopTracker()
            self.tracker.unregisterAllTargets()
            print("[Thread] Thread terminato.")
            # self.people_detected.unsubscribe("HumanDetected")
    
    def distance_from_person(self):
        dist = None
        if self.tracker.isActive():
            dist = self.tracker.getTargetPosition()     # robo-centric coordinates [x,y,z]
                                                        # robot is in coordinate [0.0, 0.0, 0.0]
        return dist
    
    def stop_tracking(self):
        if self.tracker.isActive():
            self.tracker.stopTracker()
            self.tracker.unregisterAllTargets()
        self.people.unsubscribe("HumanDetected")
    
    def stand_up(self, speed=0.2):
        self.posture.goToPosture("Stand", speed)
    
    def set_head(self, yaw = 0.0, pitch = 0.02, speed=0.2):
        self.motion.setAngles("HeadYaw", yaw, 0.1)
        self.motion.setAngles("HeadPitch", pitch, 0.1)
        
    def arms_angles(self, joints, angles, speed=0.2):
        self.motion.setAngles(joints, angles, speed)
        
    def get_arms_angles(self, joints):
        return self.motion.getAngles(joints, True)
    
    def photo_stance(self):
        self.stand_up()
        self.set_head(self.photo_angles[0], self.photo_angles[1])
    
    def soundSet(self, set_name):
        
        return self.sounds.getSoundSetFileNames(set_name)
    
    def play_sound(self, sound_name):
        self.sounds.playFile(sound_name)
    
    def stop(self):
        self.motion.stopMove()
        self.motion.setExternalCollisionProtectionEnabled('All', True)
        
