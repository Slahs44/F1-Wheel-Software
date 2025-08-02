#include <Joystick.h>

// Création de la manette HID avec 1 bouton
Joystick_ Joystick(JOYSTICK_DEFAULT_REPORT_ID, JOYSTICK_TYPE_GAMEPAD,
                  1,     // 1 bouton
                  0,     // aucun hat switch
                  false, false, true,  // pas d'axes X/Y/Z
                  false, false, false,  // pas de rotations
                  false, false, false,  // pas de rudder/throttle/etc.
                  false);               // pas de steering

const int boutonPin = 2;  // Le bouton est branché sur la pin D2
const int potPin = A0; // Pin test

// Data Discussion Python
const int dataSizePC_IN = 14;
const int dataSizeNano_IN = 2;
const int dataSizePC_OUT = 2;
const int dataSizeNano_OUT= 10;
long int receivedDataPC[dataSizePC_IN];
long int receivedDataNano[dataSizeNano_IN];
long int DataToPC[dataSizePC_OUT];
long int DataToNano[dataSizeNano_OUT];
String input = ""; // à conserver globalement pour maintenir l'état entre les appels

void setup() {
  Serial.begin(115200);     // USB vers PC (Python + HID)
  Serial1.begin(9600);      // UART vers la Nano
  pinMode(boutonPin, INPUT);  // Pas de résistance interne
  Joystick.begin();           // Initialisation HID
}


Stream& pc = Serial;
Stream& nano = Serial1;


void loop() {
  int potValue = analogRead(potPin); // 0 à 1023
  int zValue = map(potValue, 0, 1023, 0, 1023); // adapter la plage si nécessaire
  Joystick.setZAxis(zValue);

  readAndParsePCData();
  //readAndParseNanoData();
  pc.println("");
  sendDataNano(receivedDataPC);

  bool etatBouton = digitalRead(boutonPin);  // HIGH = appuyé
  Joystick.setButton(0, etatBouton);
  delay(5);
  

}



void sendDataPC(long int* data){
  pc.print(arrayIntTOString(data, dataSizePC_OUT));
}

void sendDataNano(long int* data){
  Serial1.print(arrayIntTOString(data, dataSizeNano_OUT));
}

String arrayIntTOString(long int* array, int size) {
  String result = "";
  for (int i = 0; i < size; i++) {
    result += String(array[i]);
    if (i < size - 1) {
      result += ",";
    }
  }
  result += "\n";
  return result;
}




void readAndParseNanoData(){
  while (nano.available()) {
    char c = nano.read();

    if (c == '\n') {
      long int* temp = parseData(input, dataSizeNano_IN);
      input = ""; // Réinitialise
      for (int i = 0; i < dataSizeNano_IN; i++) {
        receivedDataNano[i] = temp[i];
      }
      delete[] temp;

    } else {
      input += c;
    }
  }
}

void readAndParsePCData() {
  while (pc.available()) {
    char c = pc.read();

    if (c == '\n') {
      long int* temp = parseData(input, dataSizePC_IN);
      input = ""; // Réinitialise
      for (int i = 0; i < dataSizePC_IN; i++) {
        receivedDataPC[i] = temp[i];
      }
      delete[] temp;

    } else {
      input += c;
    }
  }
}

long int* parseData(String data, int dataSize) {
  long int* result = new long int[dataSize];  // Allocation dynamique
  int index = 0;
  int start = 0;

  for (int i = 0; i < data.length(); i++) {
    if (data[i] == ',' || i == data.length() - 1) {
      String val = data.substring(start, (i == data.length() - 1) ? i + 1 : i);
      result[index] = val.toInt();
      index++;
      if (index >= dataSize) break;
      start = i + 1;
    }
  }

  return result;
}




