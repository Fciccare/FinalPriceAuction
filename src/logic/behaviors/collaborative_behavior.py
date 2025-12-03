import time
import random

from behaviors.pepper import *

GREETING = ['animations/Stand/Gestures/Hey_1', 'animations/Stand/Gestures/Hey_3'] #'animations/Stand/Gestures/BowShort_1',
POSITIVE = ['animations/Stand/Emotions/Positive/Happy_4', 'animations/Stand/Gestures/Enthusiastic_4', 'animations/Stand/Gestures/Yes_1', 'animations/Stand/Gestures/Yes_3']
YES = ['animations/Stand/Gestures/Yes_1',  'animations/Stand/Gestures/Yes_3']
NEGATIVE = ['animations/Stand/Gestures/Desperate_1', 'animations/Stand/Gestures/Desperate_2', 'animations/Stand/Gestures/Desperate_3', 'animations/Stand/Gestures/Desperate_5', 
            'animations/Stand/Gestures/IDontKnow_2', 'animations/Stand/Gestures/No_2','animations/Stand/Gestures/No_8']
NEUTRAL = ['animations/Stand/Gestures/But_1', 'animations/Stand/Gestures/CalmDown_6', 'animations/Stand/Gestures/Choice_1', 'animations/Stand/Gestures/Everything_2', 
           'animations/Stand/Gestures/Everything_3', 'animations/Stand/Gestures/Explain_1', 'animations/Stand/Gestures/Explain_10', 'animations/Stand/Gestures/Explain_11',  
           'animations/Stand/Gestures/Explain_8', 'animations/Stand/Gestures/Far_2', 'animations/Stand/Gestures/Give_4', 'animations/Stand/Gestures/Give_6', 
           'animations/Stand/Gestures/Thinking_1', 'animations/Stand/Gestures/Thinking_3'] 
POINT_LEFT = ['animations/Stand/Gestures/YouKnowWhat_5', 'animations/Stand/Gestures/Explain_2', 'animations/Stand/Gestures/Explain_3']
POINT_RIGHT = ['animations/Stand/Gestures/Give_3', 'animations/Stand/Gestures/Explain_4']
POINT_ALL = ['animations/Stand/Gestures/Everything_1', 'animations/Stand/Gestures/Everything_4', 'animations/Stand/Gestures/Give_5', 'animations/Stand/Gestures/Please_1']
SELF = ['animations/Stand/Gestures/Me_1', 'animations/Stand/Gestures/Me_2', 'animations/Stand/Gestures/Me_4', 'animations/Stand/Gestures/Me_7', 'animations/Stand/Gestures/ShowTablet_2', 
        'animations/Stand/Gestures/ShowTablet_3']
ANNOYED = ['animations/Stand/Gestures/YouKnowWhat_1', 'animations/Stand/Gestures/YouKnowWhat_3']


class CollaborativeBehavior(Pepper):

    def __init__(self, session, ip, args, port):
        super().__init__(session, ip, args, port)

        self.tts.setLanguage("Italian")

        self.motion.setStiffnesses("Body", 1.0)

        self.pose_dictionary = {
                "active_listening": self.pose_1_ascolto_attivo,
                "mani_giunte": self.pose_2_attesa_mani_giunte,
                "offerta": self.pose_3_gesto_offerta,
                "riflessione": self.pose_4_riflessione,
                "entusiasta": self.pose_7_entusiasta,
                "happy": self.pose_8_felice,
                "yes": self.pose_9_yes
            }
        
    def talk_and_move(self, dialogo_robot):

        azione = dialogo_robot.get("Azione")
        frase = dialogo_robot.get("Dialogo", "")

        self.execute_random_collaborative_pose()

        if azione is not None:
            if azione == "PASSO":
                frase = frase + "Passo il turno."
            else:
                frase = frase + "Punto" + azione + "Monete."

        if frase:
            print(f"Robot dice: {frase}")
            self.tts.say(frase)
        
        time.sleep(1)
        self.reset_pose()

    def execute_random_collaborative_pose(self):
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
        
        print("\n" + ("-"*30))
        print(f"Random pose chosen: {chosen_pose_name.upper()}")
        print(("-")*30)
        
        # 4. Execute the function
        chosen_pose_function()


    def reset_pose(self, speed=0.8):
        """
        Porta Pepper alla posa neutra "Stand".
        """
        if not self.posture:
            print("Servizio non inizializzato.")
            return
        print("Torno alla posa 'Stand'...")
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

    
    def pose_1_ascolto_attivo(self):
        """
        1. Ascolto Attivo: Inclina leggermente la testa di lato.
        """
        print("Eseguo: Posa Ascolto Attivo (Testa inclinata)")
        
        # Nomi dei giunti: [HeadYaw, HeadPitch]
        # HeadYaw: rotazione sinistra/destra
        # HeadPitch: rotazione su/giù
        joints = [
            "HeadYaw", "HeadPitch"
        ]
        
        # Angoli in radianti. 0.3 rad ~= 17 gradi
        angles = [
            0.3, 0.1
        ]

        self._execute_pose(joints, angles, 0.1)


    def pose_2_attesa_mani_giunte(self):
        """
        2. Attesa (Mani Giunte): Braccia piegate davanti, mani vicine.
        """
        print("Eseguo: Posa di Attesa (Mani giunte)")
        
        joints = [
            "LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll", "LWristYaw", "LHand",
            "RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw", "RHand"
        ]
        
        # Angoli per portare le mani davanti alla vita
        angles = [
            1.0, 0.1, -0.2, -0.8, -1.0, 0.5,  # Braccio Sinistro
            1.0, -0.1, 0.2, 0.8, 1.0, 0.5   # Braccio Destro (0.5 = mano semi-chiusa)
        ]
        
        self._execute_pose(joints, angles, 0.1)


    def pose_3_gesto_offerta(self):
        """
        3. Gesto di Offerta: Un braccio avanti, palmo in su.
        """
        print("Eseguo: Posa Gesto di Offerta (Palmo in su)")
        
        # Usiamo solo il braccio destro
        joints = ["RShoulderPitch", "RShoulderRoll", "RElbowRoll", "RWristYaw", "RHand"]
        
        # RHand 1.0 = mano completamente aperta
        # RWristYaw 1.5 ~= 85 gradi (palmo quasi verticale)
        angles = [0.8, -0.3, 0.6, 1.5, 1.0]
        
        self._execute_pose(joints, angles, 0.1)
        time.sleep(3)
        
        # Ritorno del braccio
        self.stand_up()


    def pose_4_riflessione(self):
        """
        4. Riflessione: Una mano vicino al mento e testa leggermente inclinata.
        """
        print("Eseguo: Posa di Riflessione (Mano al mento)")
        
        joints = [
            "RShoulderPitch", "RElbowRoll", "RElbowYaw", "RWristYaw", "RHand",
            "HeadYaw", "HeadPitch"
        ]
        
        # RHand 0.1 = mano quasi chiusa (pugno)
        angles = [
            0.7, 1.2, 1.0, 0.0, 0.1,  # Braccio
            0.2, -0.2                   # Testa (di lato e leggermente su)
        ]
        
        self._execute_pose(joints, angles, 0.1)


    def pose_7_entusiasta(self):
        """Apre le braccia in segno di accoglienza."""
        print("Eseguo: Entusiasta")
        self.animation_player_service.run("animations/Stand/Gestures/Enthusiastic_4")

    def pose_8_felice(self):
        print("Eseguo: Felice")
        self.animation_player_service.run("animations/Stand/Emotions/Positive/Happy_4")

    def pose_9_yes(self):
        print("Eseguo: Yes")
        self.animation_player_service.run("animations/Stand/Gestures/Yes_1")



    def shutdown(self):
        """
        Rilascia la rigidità dei motori.
        """
        if not self.motion:
            return
        print("Rilascio i motori...")
        self.motion.setStiffnesses("Body", 0.0)
            