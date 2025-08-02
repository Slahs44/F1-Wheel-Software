#include <Adafruit_ILI9341.h>
#include <Adafruit_GFX.h>
#include "Formula1_Display_Bold_allege7pt7b.h"


#define TFT_CS    8      // TFT CS  pin is connected to arduino pin 8
#define TFT_RST   9      // TFT RST pin is connected to arduino pin 9
#define TFT_DC    10     // TFT DC  pin is connected to arduino pin 10


void afficherTempsTours(float chrono, bool normal = true);



Adafruit_ILI9341 tft = Adafruit_ILI9341(TFT_CS, TFT_DC, TFT_RST);
int mode = 2;
long int time = millis();
bool already = true;


int vitesse = 139;
int gear = 2;
float tempsTourEnCours = 45.524;
int lastVitesse = vitesse;
int lastGear = gear;
String lastChrono = "0.00.000";



void setup() {
  Serial.begin(9600);
  tft.begin();
  tft.setRotation(1);
  affichage_init();
  Serial.println("o");


}

uint16_t fond = tft.color565(102, 102, 102);
uint16_t contour = tft.color565(255, 0, 0);


void loop() {
  // Lecture du bouton pour changer de mode
  Serial.println("f");
  

  afficherGear(gear);
  afficherVitesse(vitesse);
  
  if (vitesse == 320){
    vitesse = 0;
  }
  if (gear == 8){
    gear = 0;
  }
  gear = gear +1;
  vitesse = vitesse +1;

  tempsTourEnCours = tempsTourEnCours + 0.754;


  if (mode == 0){
    afficherTempsTours(tempsTourEnCours);
  }
  if(!already && mode == 1){
    afficherBandeau("SAFETY CAR EN PISTE", ILI9341_YELLOW, ILI9341_BLACK, 72);
    already = true;
  }
  if(already && mode == 2){
    afficherBandeau("VIRTUAL SAFETY CAR", ILI9341_YELLOW, ILI9341_BLACK, 74);
    already = false;
  }
  if (!already && mode == 3){
    afficherBandeau("Reprise de la course", ILI9341_GREEN, ILI9341_BLACK, 64);
    already = true;
  }
  if(already && mode == 4){
    afficherBandeau("", ILI9341_PURPLE, ILI9341_BLACK, 118);
    afficherTempsTours(70.584, false);
    already = false;
  }
  if (!already && mode == 5){
    afficherBandeau("DEPASSEMENT", ILI9341_BLUE, ILI9341_BLACK, 90);
    already = true;
  }
  if (already && mode == 6){
    afficherBandeau("ARRET COURSE", ILI9341_RED, ILI9341_BLACK, 85);
    already = false;
  }
  if (!already && mode == 7){
    mode++;
    already = true;
  }
  if (already && mode == 0){
    already = false;
    affichage_init();
  }

  

  if (millis() - time > 5000){
    mode++;
    time = millis();
    if (mode == 8){
      mode = 0;
    }
    Serial.println(mode);
  }

  delay(200);


  


}



void affichage_init(){
  tft.fillScreen(ILI9341_BLACK); // Nettoie l’écran pour le nouveau mode
  // Bloc Gear
  tft.fillRoundRect(108, 35, 108, 93, 10, fond); // fond centré, taille large
  tft.drawRoundRect(108, 35, 108, 93, 10, contour);
  // Bloc Speed
  tft.fillRoundRect(2, 35, 97, 70, 10, fond); // fond centré, taille large
  tft.drawRoundRect(2, 35, 97, 70, 10, contour);
  tft.setCursor(23, 47); // à gauche
  tft.setFont(&Formula1_Display_Bold_allege7pt7b);
  tft.setTextSize(1.5);
  tft.setTextColor(ILI9341_WHITE);
  tft.println("Speed");
  tft.fillRect(0,26,320,2, contour);


}

void afficherGear(int gear) {
  tft.setFont();
  tft.setTextColor(fond);
  tft.setTextSize(11); // très gros
  // Centrage vertical en deux lignes (approximatif selon police)
  tft.setCursor(135, 43);  // ligne du haut
  tft.print(lastGear);
  lastGear = gear;

  tft.setTextColor(ILI9341_WHITE);

  tft.setCursor(135, 43);  // ligne du haut
  tft.print(gear);
}


void afficherVitesse(int vitesse) {
  tft.setFont(&Formula1_Display_Bold_allege7pt7b);
  tft.setTextSize(2);
  tft.setCursor(20, 88); // à gauche
  tft.setTextColor(fond);
  tft.print(lastVitesse);
  lastVitesse = vitesse;
  tft.setCursor(20, 88);
  tft.setTextSize(2);
  tft.setTextColor(ILI9341_WHITE);
  tft.print(vitesse);
}



void afficherTempsTours(float chrono, bool normal = true) {
  // Normal est utile pour "le meilleur tour"
  // Traitement du chrono
  int minutes = 0;
    while (chrono >= 60.0) {
    minutes++;
    chrono -= 60.0;
  }

  // Maintenant reste contient les secondes avec centièmes
  int secondes = (int)chrono;
  int milliemes = (int)((chrono - secondes) * 1000);

  String milStr = String(milliemes);
  while (milStr.length() < 3) {
    milStr = "0" + milStr;
  }

  String temps = String(minutes) + ":"+ ((secondes < 10) ? "0" + String(secondes) : String(secondes)) + "." + milStr;

  tft.setFont(&Formula1_Display_Bold_allege7pt7b);
  tft.setTextSize(1.8);
  if (normal) {
    tft.setTextColor(ILI9341_BLACK);
    tft.setCursor(118, 19);
    tft.print(lastChrono);
  }
  tft.setCursor(118, 19);
  tft.setTextColor(ILI9341_WHITE);
  tft.print(temps);
  lastChrono = temps;
}


void afficherBandeau(String texte, uint16_t couleurFond, uint16_t couleurTexte, int pos) {
  tft.fillRect(0, 0, 320, 26, couleurFond);
  tft.setCursor(pos, 17);
  tft.setFont(&Formula1_Display_Bold_allege7pt7b);
  tft.setTextColor(couleurTexte);
  tft.setTextSize(1);
  tft.print(texte);
}



