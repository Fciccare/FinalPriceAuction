import time
import random
from pepper import Pepper

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

        # self.pose_dictionary = {
        #         "power_pose": self.pose_power_pose,
        #         "crossed_arms": self.pose_crossed_arms,
        #         "strategist": self.pose_the_strategist,
        #         "forward_lean": self.pose_forward_lean,
        #         "pointing_finger": self.pose_pointing_finger,
        #         "intense_stare": self.pose_intense_stare,
        #         "take_space": self.pose_take_space,
        #         "gauntlet": self.pose_the_gauntlet
        #     }
        
    def talk_and_move(self, phrases):
        """
        Esegue una posa competitiva casuale
        e pronuncia una frase adatta.
        """
        #self.execute_random_competitive_pose()

        
        self.tts.say(phrases)
        
        # Pausa breve dopo aver parlato
        time.sleep(1)
        
        # Torna alla posa neutra
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
        print("1. Posa Ascolto Attivo (Testa inclinata)")
        
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
        print("2. Posa di Attesa (Mani giunte)")
        
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
        print("3. Posa Gesto di Offerta (Palmo in su)")
        
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
        print("4. Posa di Riflessione (Mano al mento)")
        
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


    def pose_5_incoraggiamento(self):
        """
        5. Incoraggiamento: Piccolo e contenuto "pugno" di esultanza.
        """
        print("5. Posa di Incoraggiamento (Forza!)")
        
        # Movimento 1: Pugni bassi
        self._execute_pose(
            ["LElbowRoll", "RElbowRoll", "LHand", "RHand", "LWristYaw", "RWristYaw"],
            [-0.8, 0.8, 0.1, 0.1, -1.0,1.0], 0.8)
        time.sleep(0.5)
        
        for i in range(3):
            # Movimento 2: Piccolo scatto verso l'alto
            self._execute_pose(
                ["LShoulderPitch", "RShoulderPitch"],
                [0.8, 0.8], 0.8)
            time.sleep(0.5)
            
            # Ritorno
            self._execute_pose(
                ["LShoulderPitch", "RShoulderPitch"],
                [1.2, 1.2], 0.8)
            time.sleep(0.5)
        


    def pose_6_incertezza(motion_service):
        """
        6. Incertezza: Solleva le "spalle" e apre le mani.
        """
        print("6. Posa di Incertezza (Non so...)")
        
        joint_names = [
            "LShoulderPitch", "LShoulderRoll", "LElbowRoll", "LHand",
            "RShoulderPitch", "RShoulderRoll", "RElbowRoll", "RHand",
            "HeadYaw"
        ]
        
        # LShoulderPitch/RShoulderPitch 0.8 = "spalle" su
        # LHand/RHand 1.0 = mani aperte
        angles = [
            0.8, 0.3, -0.5, 1.0,
            0.8, -0.3, 0.5, 1.0,
            0.0 # Testa dritta
        ]
        speed = 0.2
        motion_service.angleInterpolationWithSpeed(joint_names, angles, speed)
        
        # Aggiunge un leggero scuotimento della testa
        motion_service.angleInterpolationWithSpeed("HeadYaw", [-0.2, 0.2, 0.0], [0.3, 0.3, 0.3])


    def pose_7_orientamento(motion_service):
        """
        7. Orientamento: Ruota la base per seguire l'umano.
        Qui simuliamo una rotazione.
        """
        print("7. Posa di Orientamento (Ti seguo)")
        
        # Ruota sul posto (Theta = 0.4 radianti, circa 23 gradi)
        # moveTo è bloccante, useremo moveToward per un controllo più fluido
        
        # (Velocità X, Velocità Y, Velocità Theta)
        # Ruota a sinistra al 20% della velocità massima
        motion_service.moveToward(0.0, 0.0, 0.2) 
        time.sleep(1.5) # Ruota per 1.5 secondi
        motion_service.stopMove() # Ferma il movimento
        
        time.sleep(1)
        
        # Ruota indietro
        motion_service.moveToward(0.0, 0.0, -0.2)
        time.sleep(1.5)
        motion_service.stopMove()


    def pose_8_cenno_conferma(motion_service):
        """
        8. Cenno di Conferma: Lento "sì" con la testa.
        """
        print("8. Posa Cenno di Conferma (Sì)")
        
        # Movimento "Sì" (Su-Giù)
        # [Giù, Su, Centro]
        angles = [0.2, -0.1, 0.0]
        times = [0.8, 1.6, 2.2] # Tempi lenti e deliberati
        
        motion_service.angleInterpolation("HeadPitch", angles, times, True)


    def pose_9_cedere_spazio(motion_service):
        """
        9. Cedere Spazio: Fa un piccolo passo indietro.
        """
        print("9. Posa Cedere Spazio (Mi sposto)")
        
        # moveTo(x, y, theta)
        # x = -0.1 (10cm indietro)
        motion_service.moveTo(-0.1, 0.0, 0.0)


    def pose_10_proposta(motion_service):
        """
        10. Proposta: Indica un punto sul tavolo, dal basso.
        """
        print("10. Posa Proposta (Indicare basso)")
        
        # Usiamo il braccio sinistro
        joint_names = ["LShoulderPitch", "LShoulderRoll", "LElbowRoll", "LHand"]
        
        # Braccio basso (1.4), quasi dritto (LElbowRoll -0.2)
        # Mano quasi chiusa per "indicare" (LHand 0.1)
        angles = [1.4, 0.2, -0.2, 0.1]
        speed = 0.1
        
        motion_service.angleInterpolationWithSpeed(joint_names, angles, speed)

    def shutdown(self):
        """
        Rilascia la rigidità dei motori.
        """
        if not self.motion:
            return
        print("Rilascio i motori...")
        self.motion.setStiffnesses("Body", 0.0)
            