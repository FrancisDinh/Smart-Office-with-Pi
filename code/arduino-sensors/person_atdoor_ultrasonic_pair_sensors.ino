const int trig1 = 8;    
const int echo1 = 7;   
const int trig2 = 9;
const int echo2 = 10;  
 
void setup()
{
    Serial.begin(115200);     
    pinMode(trig1,OUTPUT);   
    pinMode(echo1,INPUT);    
    pinMode(trig2,OUTPUT);
    pinMode(echo2,INPUT);
}

void loop()
{
    int distance1 = Distance_func(trig1,echo1);
    /*Serial.println(distance1);*/
    int distance2 = Distance_func(trig2,echo2);
    /*Serial.println(distance2);*/
    if (distance1 <= 50 || distance2 <= 50){
      Serial.println(true);
    }
    else{
      Serial.println(false);
    }
    delay(10);             
}
int Distance_func(int trig,int echo){
  
    unsigned long duration; 
    int distance;  
    
    digitalWrite(trig,0);   
    delayMicroseconds(2);
    digitalWrite(trig,1);   
    delayMicroseconds(5);   
    digitalWrite(trig,0);   
    
  
    duration = pulseIn(echo,HIGH);  

    distance = int(duration/2/29.412);
    
    delay(200);
  return distance;
}
