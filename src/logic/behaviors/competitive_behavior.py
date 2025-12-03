import random
import time

from behaviors.pepper import *

import argparse
import qi

class CompetitiveBehavior(Pepper):

    def __init__(self, session, ip, args, port):
        super().__init__(session, ip, args, port)
        
        self.tts.setLanguage("Italian")

        self.motion.setStiffnesses("Body", 1.0)

        self.pose_dictionary = {
                "power_pose": self.pose_power_pose,
                "crossed_arms": self.pose_crossed_arms,
                "strategist": self.pose_the_strategist,
                "forward_lean": self.pose_forward_lean,
                "pointing_finger": self.pose_pointing_finger,
                "intense_stare": self.pose_intense_stare,
                "take_space": self.pose_take_space,
                "gauntlet": self.pose_the_gauntlet
            }


    def talk_and_move(self, dialogo_robot):

        # azione = dialogo_robot.get("Azione")
        frase = dialogo_robot.get("Dialogo", "")
        # print("prima della move")
        self.execute_random_competitive_pose()
        # print("frase: ", frase)
        # if azione is not None:
        #     if azione == "PASSO":
        #         frase = frase + "Passo il turno."
        #     else:
        #         frase = frase + "Punto" + azione + "Monete."

        if frase:
            # print(f"Robot dice: {frase}")
            self.tts.say(frase)

        time.sleep(1)
        self.reset_pose()

    def execute_random_competitive_pose(self):
        """
        Chooses and executes a random competitive pose
        from the pose dictionary.
        """
        if not self.pose_dictionary:
            print("Pose dictionary is empty. Cannot choose.")
            return
            
        # 1. Get the list of keys (pose names)
        pose_keys = list(self.pose_dictionary.keys())
        
        # 2. Choose a key at random
        chosen_pose_name = random.choice(pose_keys)
        
        # 3. Retrieve the function ('value') from the dictionary
        chosen_pose_function = self.pose_dictionary[chosen_pose_name]
        
        #print("\n" + ("-"*30))
        # print(f"Random pose chosen: {chosen_pose_name.upper()}")
        #print(("-")*30)
        
        # 4. Execute the function
        chosen_pose_function()


    def reset_pose(self, speed=0.8):
        """
        Porta Pepper alla posa neutra "Stand".
        """
        if not self.posture:
            print("Servizio non inizializzato.")
            return
        # print("Torno alla posa 'Stand'...")
        self.posture.goToPosture("Stand", speed)

    def _execute_pose(self, joint_names, joint_angles, speed=0.3):
        """
        Funzione helper per eseguire un movimento.
        """
        if not self.motion:
            print("Servizio non inizializzato.")
            return
        
        # Usiamo angleInterpolationWithSpeed per un movimento fluido
        self.motion.angleInterpolationWithSpeed(
            joint_names, 
            joint_angles, 
            speed
        )
        

    def pose_power_pose(self):
        """
        1. La "Power Pose" (Mani sui Fianchi)
        Braccia piegate con i polsi vicino ai fianchi.
        """
        print("Eseguo: Power Pose")
        joints = [
            "LHand","LShoulderRoll", "LElbowRoll", "LShoulderPitch", "LWristYaw", "LElbowYaw",
            "RHand","RShoulderRoll", "RElbowRoll", "RShoulderPitch", "RWristYaw", "RElbowYaw"
        ]
        # Angoli in radianti
        angles = [
            -1.0, 0.7,   -2.0,  3.2, -0.2, -0.8,  # Braccio Sinistro
            -1.0, -0.7,   2.0,  3.2,  0.2, 0.8   # Braccio Destro
        ]

        self._execute_pose(joints, angles, speed=0.8)

    def pose_crossed_arms(self):
        """
        2. Le Braccia Conserte (L'Assertivo)
        Braccia incrociate sul petto, sotto il tablet.
        """
        print("Eseguo: Braccia Conserte")
        joints = [
            "LHand", 'LShoulderPitch', 'LElbowYaw', 'LElbowRoll', 
            "RHand", 'RShoulderPitch', 'RElbowYaw', 'RElbowRoll'
        ]
        angles = [-1.0, 0.25, 0.0, -2,     # Braccio Sinistro (attraverso il petto)
                  -1.0, -0.25, 0.0, 2]    # Braccio Destro (attraverso il petto)
        

        self._execute_pose(joints, angles, speed=0.2)

    def pose_the_strategist(self):
        """
        3. Lo Stratega (Mano al Mento)
        Mano destra al mento, testa leggermente inclinata.
        """
        print("Eseguo: Lo Stratega")
        joints = [
            "RShoulderPitch", "RShoulderRoll", "RElbowRoll", "RElbowYaw", "RHand","RWristYaw",
            "LShoulderPitch", "LShoulderRoll", # Braccio sinistro rilassato
            "HeadPitch"
        ]
        angles = [
            0.2, -0.2, 2.2, 0.58, 0.2, 1.2,   # Braccio Destro (al mento)
            1.5, 0.1,                  # Braccio Sinistro (rilassato)
            0.1                         # Testa (leggermente giù)
        ]
        self._execute_pose(joints, angles)

    def pose_forward_lean(self):
        """
        5. L'Inclinazione in Avanti (Il Predatore)
        Busto inclinato in avanti.
        """
        print("Eseguo: Inclinazione in Avanti")
        joints = ["HipPitch", "HeadPitch"]
        angles = [
            -0.4,  # Busto in avanti
            -0.2   # Testa su per mantenere lo sguardo
        ]
        self._execute_pose(joints, angles, speed=0.15)

    def pose_pointing_finger(self):
        """
        6. La Sfida (Dito Puntato)
        Braccio destro teso in avanti, mano chiusa a "indicare".
        """
        print("Eseguo: Dito Puntato")
        joints = [
            "RShoulderPitch", "RShoulderRoll", "RElbowRoll", "RHand"
        ]
        angles = [
            0.0, -0.1, 0.1, 0.0  # Braccio teso (RHand=0 è "dito")
        ]
        self._execute_pose(joints, angles, speed=0.8)

    def pose_intense_stare(self):
        """
        7. Lo Sguardo Intenso (Testa Bassa, Occhi Alti)
        Solo un movimento della testa.
        (Non mi convince)
        """
        print("Eseguo: Sguardo Intenso")
        joints = ["HeadPitch"]
        angles = [0.3]  # Testa giù (il tracking penserà a "occhi alti")
        self._execute_pose(joints, angles)


    def pose_take_space(self):
        """
        9. Presa di Spazio (Braccia Larghe)
        Braccia larghe con gomiti a 90 gradi.
        """
        print("Eseguo: Presa di Spazio")
        joints = [
            "LShoulderRoll", "LElbowRoll", "LShoulderPitch", "LHand",
            "RShoulderRoll", "RElbowRoll", "RShoulderPitch", "RHand"
        ]
        angles = [
            1.0, -1.57, 1.2, 1.0,  # Braccio Sinistro (largo, 90°, palmo aperto)
           -1.0,  1.57, 1.2, 1.0   # Braccio Destro (largo, 90°, palmo aperto)
        ]
        self._execute_pose(joints, angles, speed=0.25)

    def pose_the_gauntlet(self):
        """
        10. Il Guanto di Sfida (Palmi in Avanti)
        Braccia piegate in avanti con i palmi aperti.
        """
        print("Eseguo: Guanto di Sfida")
        joints = [
            "LShoulderPitch", "LElbowRoll", "LWristYaw", "LHand",
            "RShoulderPitch", "RElbowRoll", "RWristYaw", "RHand"
        ]
        angles = [
            0.5, -0.8, -1.57, 1.0,  # Braccio Sinistro (palmo avanti)
            0.5,  0.8,  1.57, 1.0   # Braccio Destro (palmo avanti)
        ]
        self._execute_pose(joints, angles)

    def shutdown(self):
        """
        Rilascia la rigidità dei motori.
        """
        if not self.motion:
            return
        print("Rilascio i motori...")
        self.motion.setStiffnesses("Body", 0.0)
            