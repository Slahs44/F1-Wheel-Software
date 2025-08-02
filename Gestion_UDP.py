import socket
import struct
import serial
import time
import Write_in_csvortxt as wr


class F1_data_UDP():
    def __init__(self):
        
        self.header_size = 29  # taille header packet F1 2024

        self.code = {'T': ["Car Telemetry", 0, 4], 
                     'C': ["Car Status", 4, 6],
                     'E': ["Race Event", 10, 3],
                     'S': ["Session Data", 13, 1],
                     'L': ["Lap Data", 14, 6] } # 'Lettre_code' : ["Nom du module", 'ID de la première valeur dans data_send', 'nbr de valeurs récupérées dans le paquet']
        
        # Taille et format supposés, 
        self.PACKET_SIZE = {'Telemetry' : (1352, self.parse_car_telemetry),
                            'Car_Status' : (1239, self.parse_car_status),
                            'Race_Event' : (45, self.parse_event_packet),
                            'Lap_Data' : (1285, self.parse_lap_data),
                            'Session_Data' : (753, self.parse_session_data)} 
        
        self.Id_unpacked_telemetry = [0, 5, 6, 7]
        self.Id_unpacked_status = [4, 11, 12, 16, 19, 20]
        self.Id_unpacked_lapData = [0, 1, 6, 12, 13, 14]
        # self.Id_unpacked_event = [] # car methode différentes
        # self.Id_unpacked_SessionData = [] # car unique valeur récupérée
        self.Id_unpacked_lapData = [0, 1, 6, 12, 13, 14]


        self.nbr_data = 20 # Nombre de données totales envoyées vers l'arduino

        self.title = ["Vitesse",
                      "Rapport",
                      "Tour Moteur",
                      "DRS Status",
                      "Pit Limiteur Status",
                      "DRS Allowed",
                      "DRS Distance",
                      "FIA Flag",                    #// -1 = invalid/ unknown, 0 = none, 1 = green  2 = blue, 3 = yellow, 4 = red
                      "ERS Energy",
                      "ERS Mode",
                      "Fatest Lap",
                      "Safety Car Status",          # 0 = No Safety Car, 1 = Full Safety Car, 2 = Virtual Safety Car, 3 = Formation Lap Safety Car
                      "Total de Tour",
                      "Temps dernier tour",
                      "Temps tour actuel",
                      "Delta devant",
                      "Delta SC",
                      "Position",
                      "Current Lap"
                      ]
        
        # Configuration réseau
        self.UDP_IP = "127.0.0.1"
        self.UDP_PORT = 20777
        self.sock ='' # Varibla pour l'objet UDP

        # Configuration Arduino
        self.temps_demarage = 8 # temps en sec
        self.arduino_port = 'COM3'
        self.baud = 112500
        self.arduino = '' # Variable pour l'objet de la carte arduino

        self.demarrage()

        self.data_send = [0 for k in range(self.nbr_data)]


    def demarrage(self):
        # Connexion à la carte Arduino (remplace COM3 par le bon port)
        self.arduino = serial.Serial(self.arduino_port, self.baud, timeout=1)
        time.sleep(self.temps_demarage)  # attendre que l'Arduino redémarre

        # Exemple réception UDP (simplifiée)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.UDP_IP, self.UDP_PORT))
        print(f"📡 En écoute sur {self.UDP_IP}:{self.UDP_PORT}...")

    def lecture_adresse(self):
         return self.sock.recvfrom(2048)

    def send_number(self, numbers :list):
        data = ""
        for k in range(len(numbers)):
            values = str(numbers[k])
            if k == len(numbers) -1:
                data += values + "\n"
            else:
                data += values +  ", "
            
        self.arduino.write(data.encode())
        #print(f"✅ Envoyé à l'Arduino : ", data)


# ----------------------------------------------------------------------------------------------------------------------- #
# --------------------------------   Gestion des différents paquets de télémetry F1 24   -------------------------------- #
# ----------------------------------------------------------------------------------------------------------------------- #
    def parse_car_telemetry(self, data, index=19):
        Format = '<HfffBbhBBH4H4B4BH4f4B'
        carTelemetrySize = struct.calcsize(Format)
        offset = self.header_size + index * carTelemetrySize
        slice_data = data[offset:offset + carTelemetrySize]
        

        
        unpacked = struct.unpack(Format, slice_data)
        

        # Extraction des données :
        i = self.code['T'][1] # increment de la boucle
        for k in self.Id_unpacked_telemetry:
            self.data_send[i] = unpacked[k]
            i += 1


        telemetry = {
            'Speed': unpacked[0],
            #'throttle': unpacked[1],
            #'steer': unpacked[2],
            #'brake': unpacked[3],
            #'clutch': unpacked[4],
            'Gear': unpacked[5],
            'RPM': unpacked[6],
            'DRS': unpacked[7],
            #'revLightsPercent': unpacked[8],
            #'revLightsBitValue': unpacked[9],
            #'brakesTemperature': list(unpacked[10:14]),
            #'tyresSurfaceTemperature': list(unpacked[14:18]),
            #'tyresInnerTemperature': list(unpacked[18:22]),
            #'engineTemperature': unpacked[22],
            #'tyresPressure': list(unpacked[23:27]),
            #'surfaceType': list(unpacked[27:31]),
        }
        
        return telemetry


    def parse_car_status(self, data, index=19):
        Format = "<BBBBBfffHHBBHBBBbfffBfffB"
        carStatusSize = struct.calcsize(Format)
        offset = self.header_size + index * carStatusSize
        slice_data = data[offset:offset + carStatusSize]


        unpacked = struct.unpack(Format, slice_data)

        # Extraction des données :
        i = self.code['C'][1]# increment de la boucle
        for k in self.Id_unpacked_status:
            self.data_send[i] = unpacked[k]
            i += 1

        car_status = {
            #"tractionControl": unpacked[0],
            #"antiLockBrakes": unpacked[1],
            #"fuelMix": unpacked[2],
            #"frontBrakeBias": unpacked[3],
            "pitLimiterStatus": unpacked[4],
            #"fuelInTank": unpacked[5],
            #"fuelCapacity": unpacked[6],
            #"fuelRemainingLaps": unpacked[7],
            #"maxRPM": unpacked[8],
            #"idleRPM": unpacked[9],
            #"maxGears": unpacked[10],
            "drsAllowed": unpacked[11],
            "drsActivationDistance": unpacked[12],
            #"actualTyreCompound": unpacked[13],
            #"visualTyreCompound": unpacked[14],
            #"tyresAgeLaps": unpacked[15],
            "vehicleFiaFlags": unpacked[16], #// -1 = invalid/ unknown, 0 = none, 1 = green  2 = blue, 3 = yellow, 4 = red
            #"enginePowerICE": unpacked[17],
            #"enginePowerMGUK": unpacked[18],
            "ersStoreEnergy": unpacked[19],
            "ersDeployMode": unpacked[20],
            #"ersHarvestedThisLapMGUK": unpacked[21],
            #"ersHarvestedThisLapMGUH": unpacked[22],
            #"ersDeployedThisLap": unpacked[23],
            #"networkPaused": unpacked[24],
        }

        return car_status
    

    def parse_event_packet(self, data, index = 19):
        EVENT_CODES = {"FTLP": "Fastest Lap", # 1
                       "RTMT": "Retirement",
                       "PENA": "Penalty",
                       "OVTK": "Overtake",
                       "SCAR": "Safety Car"} # 3,4

        event_code_bytes = data[self.header_size:self.header_size + 4]
        event_code = event_code_bytes.decode("ascii")
        result = {
            "event_code": event_code,
            "event_name": EVENT_CODES.get(event_code, "Unknown")
        }

        offset = self.header_size + 4

        if event_code == "FTLP":
            vehicle_idx, lap_time = struct.unpack_from("<Bf", data, offset)
            result.update({"vehicle_idx": vehicle_idx, "lap_time ": lap_time})
            if vehicle_idx == index:
                self.data_send[10] = lap_time

        elif event_code == "RTMT":
            (vehicle_idx,) = struct.unpack_from("<B", data, offset)
            result.update({"vehicle_idx": vehicle_idx})

        elif event_code == "PENA":
            values = struct.unpack_from("<BBBBBBB", data, offset)
            result.update({
                "penalty_type": values[0],
                "infringement_type": values[1],
                "vehicle_idx": values[2],
                "other_vehicle_idx": values[3],
                "time": values[4],
                "lap_num": values[5],
                "places_gained": values[6]
            })

        elif event_code == "OVTK":
            overtaker, overtaken = struct.unpack_from("<BB", data, offset)
            result.update({"overtaking_vehicle_idx": overtaker, "being_overtaken_vehicle_idx": overtaken})

        elif event_code == "SCAR":
            sc_type, sc_event = struct.unpack_from("<BB", data, offset)
            result.update({"safety_car_type": sc_type, "event_type": sc_event})
            self.data_send[11] = sc_type     # 0 = No Safety Car, 1 = Full Safety Car, 2 = Virtual Safety Car, 3 = Formation Lap Safety Car
            # self.data_send[XX] = sc_event    # 0 = Deployed, 1 = Returning, 2 = Returned, 3 = Resume Race

        return result


    def parse_session_data(self, data, index = 19):
        # Définition du format du paquet
        Format = "<BbbBHBbBHBBBBBHHBBBBBBB"

        sessionDataSize = struct.calcsize(Format)
        offset = self.header_size + index * sessionDataSize
        slice_data = data[offset:offset + sessionDataSize]

        
        unpacked = struct.unpack(Format, slice_data)

        session_data = {
            #"weather": unpacked[0],
            #"trackTemperature": unpacked[1],
            #"airTemperature": unpacked[2],
            "totalLaps": unpacked[3],
            #"trackLength": unpacked[4],
            #"sessionType": unpacked[5],
            #"trackId": unpacked[6],
            #"formula": unpacked[7],
            #"sessionTimeLeft": unpacked[8],
            #"sessionDuration": unpacked[9],
            #"pitSpeedLimit": unpacked[10],
            #"gamePaused": unpacked[11],
            #"isSpectating": unpacked[12],
            #"spectatorCarIndex": unpacked[13],
            #"sliProNativeSupport": unpacked[14],
            #"numMarshalZones": unpacked[15],
            #"safetyCarStatus": unpacked[16],
            #"networkGame": unpacked[17],
            #"numWeatherForecastSamples": unpacked[18],
            #"sessionType": unpacked[19],
            #"timeOffset": unpacked[20],
            #"weather": unpacked[21],
            #"trackTemp": unpacked[22],
            #"trackTempChange": unpacked[23],
            #"airTemp": unpacked[24],
            #"airTempChange": unpacked[25],
            #"rainPercentage": unpacked[26],
        }

        self.data_send[12] = unpacked[3]

        return session_data


    def parse_lap_data(self, data, index = 19):
        Format = "<IIHBHBHBHBfffBBBBBBBBBBBBBBBHHBfB"
        lapDataSize = struct.calcsize(Format)
        offset = self.header_size + index * lapDataSize
        slice_data = data[offset:offset + lapDataSize]

        unpacked = struct.unpack(Format, slice_data)

                # Extraction des données :
        i = self.code['L'][1] # increment de la boucle
        for k in self.Id_unpacked_telemetry:
            self.data_send[i] = unpacked[k]
            i += 1
        
        lap_data = {
            "last_lap_time_ms": unpacked[0],        
            "current_lap_time_ms": unpacked[1],     
            #"sector1_ms": unpacked[2],
            #"sector1_min": unpacked[3],
            #"sector2_ms": unpacked[4],
            #"sector2_min": unpacked[5],
            "delta_front_ms": unpacked[6],          
            #"delta_front_min": unpacked[7],
            #"delta_leader_ms": unpacked[8],
            #"delta_leader_min": unpacked[9],
            #"lap_distance": unpacked[10],
            #"total_distance": unpacked[11],
            "safety_car_delta": unpacked[12],       
            "car_position": unpacked[13],           
            "current_lap_num": unpacked[14],        
            #"pit_status": unpacked[15],
            #"num_pit_stops": unpacked[16],
            #"sector": unpacked[17],
            #"current_lap_invalid": unpacked[18],
            #"penalties": unpacked[19],
            #"total_warnings": unpacked[20],
            #"corner_cutting_warnings": unpacked[21],
            #"unserved_drive_throughs": unpacked[22],
            #"unserved_stop_go_pens": unpacked[23],
            #"grid_position": unpacked[24],
            #"driver_status": unpacked[25],
            #"result_status": unpacked[26],
            #"pit_lane_timer_active": unpacked[27],
            #"pit_lane_time_ms": unpacked[28],
            #"pit_stop_timer_ms": unpacked[29],
            #"pit_stop_should_serve_pen": unpacked[30],
            #"speed_trap_fastest_speed": unpacked[31],
            #"speed_trap_fastest_lap": unpacked[32],
        }
        return lap_data
    
    def __repr__(self):
        out = ""
        for k in range(len(self.title)):
            out += self.title[k] + ":" + str(self.data_send[k]) + " // "
        return out

    
    
    





    
F1 = F1_data_UDP()
adresse = r'Record_data.csv'
wr.ajout_ligne(F1.title, adresse)




while True:
    player_data_modify = "No data"

    data, addr = F1.lecture_adresse()
    for key in F1.PACKET_SIZE.keys():
        if len(data) == F1.PACKET_SIZE[key][0]:
            player_data_modify = F1.PACKET_SIZE[key][1](data)
            #print("Télémetrie voiture joueur : ", player_data_modify)
            F1.send_number(F1.data_send)
            #wr.ajout_ligne(F1.data_send, adresse)
            print(key)
            print(F1)


