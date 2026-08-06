# app.py – MockTest.pro (Level 99 Ultimate Edition - Fixed)
import os, json, datetime, random, hashlib
from io import BytesIO
from flask import Flask, request, jsonify, render_template_string, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mocktest.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'change-in-production'
db = SQLAlchemy(app)

EXPORT_PASSWORD_HASH = hashlib.sha256('121520'.encode()).hexdigest()

# ====================== MODELS ======================
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), index=True)
    topic = db.Column(db.String(100))
    question = db.Column(db.Text)
    options = db.Column(db.Text)
    correct = db.Column(db.Integer)
    explanation = db.Column(db.Text, default='')

class TestAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), index=True)
    category = db.Column(db.String(50))
    topic = db.Column(db.String(100))
    total = db.Column(db.Integer)
    correct = db.Column(db.Integer)
    wrong = db.Column(db.Integer)
    skipped = db.Column(db.Integer)
    pct = db.Column(db.Float)
    time_sec = db.Column(db.Integer)
    mode = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class WeakQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), index=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    wrong_count = db.Column(db.Integer, default=1)
    last_wrong = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class UserStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), index=True, unique=True)
    xp = db.Column(db.Integer, default=0)
    streak = db.Column(db.Integer, default=0)
    last_active = db.Column(db.Date, default=datetime.date.utcnow)

with app.app_context():
    db.create_all()
    if Question.query.count() == 0:
        samples = {
            "GK": {
                "World Geography": [
                    {"question":"भारत की राजधानी क्या है?","options":["मुंबई","नई दिल्ली","कोलकाता","चेन्नई"],"correct":1,"explanation":"नई दिल्ली भारत की राजधानी है।"},
                    {"question":"टॉरस पर्वत किस देश में है?","options":["भारत","तुर्की","पाकिस्तान","ईरान"],"correct":1,"explanation":"टॉरस पर्वत तुर्की में है।"},
                    {"question":"नील नदी किस महाद्वीप में है?","options":["एशिया","अफ्रीका","यूरोप","ऑस्ट्रेलिया"],"correct":1,"explanation":"नील नदी अफ्रीका में है।"},
                    {"question":"विश्व का सबसे बड़ा महाद्वीप कौन सा है?","options":["अफ्रीका","एशिया","यूरोप","उत्तरी अमेरिका"],"correct":1,"explanation":"एशिया क्षेत्रफल में सबसे बड़ा है।"},
                    {"question":"माउंट एवरेस्ट की ऊँचाई कितनी है?","options":["8848 मी","8611 मी","7850 मी","9200 मी"],"correct":0,"explanation":"8848 मीटर।"},
                    {"question":"विश्व का सबसे बड़ा महासागर कौन सा है?","options":["अटलांटिक","हिंद","आर्कटिक","प्रशांत"],"correct":3,"explanation":"प्रशांत महासागर सबसे बड़ा है।"},
                    {"question":"भारत की सबसे लंबी नदी कौन सी है?","options":["गंगा","यमुना","गोदावरी","ब्रह्मपुत्र"],"correct":0,"explanation":"गंगा भारत की सबसे लंबी नदी है।"},
                    {"question":"थार मरुस्थल कहाँ स्थित है?","options":["राजस्थान","गुजरात","पंजाब","हरियाणा"],"correct":0,"explanation":"मुख्यतः राजस्थान में।"},
                    {"question":"सुंडा खाड़ी किन दो द्वीपों के बीच है?","options":["जावा और सुमात्रा","बोर्नियो और सुलावेसी","जावा और बाली","सुमात्रा और कालीमंतन"],"correct":0,"explanation":"जावा और सुमात्रा के बीच।"},
                    {"question":"गोबी रेगिस्तान किस देश में है?","options":["भारत","चीन","मंगोलिया","रूस"],"correct":2,"explanation":"मंगोलिया और चीन में।"},
                    {"question":"अरब सागर किसके दक्षिण में स्थित है?","options":["भारत","पाकिस्तान","ईरान","अरब प्रायद्वीप"],"correct":3,"explanation":"अरब प्रायद्वीप के दक्षिण में।"},
                    {"question":"डेन्यूब नदी किस सागर में गिरती है?","options":["काला सागर","भूमध्य सागर","कैस्पियन सागर","अटलांटिक"],"correct":0,"explanation":"काला सागर में।"},
                    {"question":"एशिया और अफ्रीका को जोड़ने वाला स्थलडमरूमध्य?","options":["स्वेज","पनामा","जिब्राल्टर","बोस्पोरस"],"correct":0,"explanation":"स्वेज स्थलडमरूमध्य।"},
                    {"question":"उत्तरी अमेरिका की सबसे लंबी नदी?","options":["मिसिसिपी","मिसौरी","अमेज़न","कोलोराडो"],"correct":1,"explanation":"मिसौरी-मिसिसिपी प्रणाली।"},
                    {"question":"किलिमंजारो पर्वत किस देश में है?","options":["केन्या","तंजानिया","युगांडा","रवांडा"],"correct":1,"explanation":"तंजानिया में।"},
                    {"question":"विश्व की सबसे बड़ी झील?","options":["कैस्पियन सागर","सुपीरियर","विक्टोरिया","बैकाल"],"correct":0,"explanation":"कैस्पियन सागर।"},
                    {"question":"एंजिल जलप्रपात किस नदी पर है?","options":["नील","अमेज़न","कांगो","ओरिनोको"],"correct":1,"explanation":"अमेज़न की सहायक नदी पर।"},
                    {"question":"ग्रेट बैरियर रीफ किस देश के पास है?","options":["ऑस्ट्रेलिया","न्यूजीलैंड","फिजी","पापुआ न्यू गिनी"],"correct":0,"explanation":"ऑस्ट्रेलिया के पूर्वी तट पर।"},
                    {"question":"यूरोप का सबसे ऊँचा पर्वत शिखर?","options":["एल्ब्रुस","मोंट ब्लांक","मैटरहॉर्न","ग्रॉसग्लॉकनर"],"correct":0,"explanation":"माउंट एल्ब्रुस।"},
                    {"question":"कर्क रेखा कितने देशों से होकर गुजरती है?","options":["12","16","18","20"],"correct":1,"explanation":"16 देशों से।"}
                ],
                "Indian History": [
                    {"question":"भारत का पहला प्रधानमंत्री कौन था?","options":["जवाहरलाल नेहरू","महात्मा गांधी","सरदार पटेल","डॉ. राजेंद्र प्रसाद"],"correct":0,"explanation":"जवाहरलाल नेहरू।"},
                    {"question":"ताजमहल किसने बनवाया?","options":["अकबर","शाहजहां","बाबर","औरंगजेब"],"correct":1,"explanation":"शाहजहां ने।"},
                    {"question":"1857 का विद्रोह किस वर्ष हुआ?","options":["1856","1857","1858","1859"],"correct":1,"explanation":"1857 में।"},
                    {"question":"भारत को स्वतंत्रता कब मिली?","options":["1945","1946","1947","1948"],"correct":2,"explanation":"15 अगस्त 1947।"},
                    {"question":"अशोक किस वंश के थे?","options":["मौर्य","गुप्त","चोल","मुगल"],"correct":0,"explanation":"मौर्य वंश।"},
                    {"question":"भारत का संविधान कब लागू हुआ?","options":["26 नवंबर 1949","26 जनवरी 1950","15 अगस्त 1947","2 अक्टूबर 1950"],"correct":1,"explanation":"26 जनवरी 1950।"},
                    {"question":"सिख धर्म के संस्थापक कौन थे?","options":["गुरु नानक","गुरु गोबिंद सिंह","गुरु अंगद","गुरु अर्जुन"],"correct":0,"explanation":"गुरु नानक।"},
                    {"question":"पानीपत का पहला युद्ध किस वर्ष लड़ा गया?","options":["1526","1556","1761","1857"],"correct":0,"explanation":"1526 में।"},
                    {"question":"दीन-ए-इलाही किसने चलाया?","options":["अकबर","जहाँगीर","शाहजहाँ","औरंगज़ेब"],"correct":0,"explanation":"अकबर ने।"},
                    {"question":"भारत छोड़ो आंदोलन कब शुरू हुआ?","options":["1940","1942","1945","1947"],"correct":1,"explanation":"1942 में।"},
                    {"question":"महात्मा गांधी का जन्म कब हुआ?","options":["1869","1879","1889","1899"],"correct":0,"explanation":"2 अक्टूबर 1869।"},
                    {"question":"अकबर का संरक्षक कौन था?","options":["बैरम खान","टोडरमल","मानसिंग","अबुल फजल"],"correct":0,"explanation":"बैरम खान।"},
                    {"question":"हड़प्पा सभ्यता किस नदी के किनारे विकसित हुई?","options":["गंगा","यमुना","सिंधु","गोदावरी"],"correct":2,"explanation":"सिंधु नदी।"},
                    {"question":"भारत में ब्रिटिश ईस्ट इंडिया कंपनी की स्थापना कब हुई?","options":["1600","1605","1610","1620"],"correct":0,"explanation":"1600 में।"},
                    {"question":"स्वराज्य की स्थापना किसने की?","options":["गोखले","तिलक","शिवाजी","राणा प्रताप"],"correct":2,"explanation":"शिवाजी ने।"},
                    {"question":"भारत में पहला सूती कपड़ा मिल कहाँ लगा?","options":["मुंबई","अहमदाबाद","कानपुर","सूरत"],"correct":0,"explanation":"1854 में मुंबई में।"},
                    {"question":"बंगाल विभाजन कब हुआ?","options":["1905","1906","1907","1908"],"correct":0,"explanation":"1905 में।"},
                    {"question":"साइमन कमीशन का भारत आगमन?","options":["1927","1928","1929","1930"],"correct":1,"explanation":"1928 में।"},
                    {"question":"जलियांवाला बाग हत्याकांड कब हुआ?","options":["1917","1918","1919","1920"],"correct":2,"explanation":"1919 में।"},
                    {"question":"भारत का राष्ट्रगान 'जन गण मन' किसने लिखा?","options":["रवींद्रनाथ टैगोर","बंकिमचंद्र","सुभाषचंद्र","महात्मा गांधी"],"correct":0,"explanation":"रवींद्रनाथ टैगोर।"}
                ]
            },
            "Maths": {
                "Arithmetic": [
                    {"question":"15 × 12 = ?","options":["150","170","180","200"],"correct":2,"explanation":"180।"},
                    {"question":"√144 = ?","options":["10","11","12","14"],"correct":2,"explanation":"12।"},
                    {"question":"25% of 200 = ?","options":["25","50","75","100"],"correct":1,"explanation":"50।"},
                    {"question":"125 ÷ 5 = ?","options":["20","25","30","35"],"correct":1,"explanation":"25।"},
                    {"question":"7² + 3² = ?","options":["49","58","67","70"],"correct":1,"explanation":"58।"},
                    {"question":"10% of 500 = ?","options":["50","60","70","80"],"correct":0,"explanation":"50।"},
                    {"question":"2000 का 5% कितना होगा?","options":["50","100","150","200"],"correct":1,"explanation":"100।"},
                    {"question":"यदि एक वस्तु का मूल्य 300 रु से 360 रु हो जाए तो % वृद्धि?","options":["10%","15%","20%","25%"],"correct":2,"explanation":"20%।"},
                    {"question":"यदि किसी संख्या का 40%, 80 है तो संख्या क्या है?","options":["120","160","200","240"],"correct":2,"explanation":"200।"},
                    {"question":"300 का 33⅓% कितना?","options":["100","110","120","130"],"correct":0,"explanation":"100।"},
                    {"question":"एक संख्या का 15% यदि 45 हो तो संख्या?","options":["200","250","300","350"],"correct":2,"explanation":"300।"},
                    {"question":"₹500 का 20% लाभ कितना?","options":["₹50","₹75","₹100","₹125"],"correct":2,"explanation":"₹100।"},
                    {"question":"यदि A का 25% = 50 हो, तो A = ?","options":["100","150","200","250"],"correct":2,"explanation":"200।"},
                    {"question":"एक घंटे का कितना % 15 मिनट है?","options":["15%","20%","25%","30%"],"correct":2,"explanation":"25%।"},
                    {"question":"250 का 8% कितना?","options":["15","18","20","22"],"correct":2,"explanation":"20।"},
                    {"question":"यदि संख्या 800 है और 20% घटे तो नई संख्या?","options":["600","620","640","660"],"correct":2,"explanation":"640।"},
                    {"question":"10% वार्षिक ब्याज पर 2 वर्ष का साधारण ब्याज ₹400 है तो मूलधन?","options":["₹1500","₹2000","₹2500","₹3000"],"correct":1,"explanation":"₹2000।"},
                    {"question":"15 पुस्तकों का मूल्य ₹1200 है तो 5 का मूल्य?","options":["₹300","₹350","₹400","₹450"],"correct":2,"explanation":"₹400।"},
                    {"question":"80 किमी/घंटा से 240 किमी दूरी तय करने में समय?","options":["2 h","3 h","4 h","5 h"],"correct":1,"explanation":"3 घंटे।"},
                    {"question":"12 आदमी 15 दिन में काम खत्म करते हैं, 20 आदमी कितने दिन लेंगे?","options":["7","8","9","10"],"correct":2,"explanation":"9 दिन।"}
                ],
                "Geometry": [
                    {"question":"त्रिभुज के तीनों कोणों का योग?","options":["90°","180°","270°","360°"],"correct":1,"explanation":"180°।"},
                    {"question":"एक वृत्त का परिमाप सूत्र?","options":["2πr","πr²","πd","4r²"],"correct":0,"explanation":"2πr।"},
                    {"question":"आयत का क्षेत्रफल?","options":["l + b","l × b","2(l + b)","l² + b²"],"correct":1,"explanation":"l × b।"},
                    {"question":"वर्ग की भुजा 5 सेमी है तो क्षेत्रफल?","options":["10","20","25","30"],"correct":2,"explanation":"25 वर्ग सेमी।"},
                    {"question":"एक वृत्त की त्रिज्या 7 सेमी है तो क्षेत्रफल?","options":["44","77","154","308"],"correct":2,"explanation":"154 वर्ग सेमी।"},
                    {"question":"समकोण त्रिभुज में हाइपोटेनस = ?","options":["a² + b²","√(a² + b²)","2√ab","(a + b)²"],"correct":1,"explanation":"√(a² + b²)।"},
                    {"question":"एक घन की भुजा 3 सेमी है तो आयतन?","options":["9","18","27","36"],"correct":2,"explanation":"27 घन सेमी।"},
                    {"question":"दो समांतर रेखाएं आपस में मिलती हैं?","options":["कभी","हमेशा","कभी-कभी","कभी नहीं"],"correct":3,"explanation":"कभी नहीं।"},
                    {"question":"एक बेलन का आयतन सूत्र?","options":["πr²h","2πrh","πrh²","πr²h²"],"correct":0,"explanation":"πr²h।"},
                    {"question":"एक पिरामिड का आयतन = (1/3) × ?","options":["आधार × ऊंचाई","आधार² × ऊंचाई","आधार × ऊंचाई²","3 × आधार × ऊंचाई"],"correct":0,"explanation":"(1/3) × आधार × ऊंचाई।"},
                    {"question":"एक पंचभुज के कोणों का योग?","options":["360°","540°","720°","900°"],"correct":1,"explanation":"540°।"},
                    {"question":"एक गोले का आयतन?","options":["(4/3)πr³","4πr²","(2/3)πr³","(1/3)πr²"],"correct":0,"explanation":"(4/3)πr³।"},
                    {"question":"शंकु का आयतन?","options":["(1/3)πr²h","πr²h","(2/3)πr²h","(1/2)πr²h"],"correct":0,"explanation":"(1/3)πr²h।"},
                    {"question":"एक चतुर्भुज का कोण योग?","options":["180°","270°","360°","450°"],"correct":2,"explanation":"360°।"},
                    {"question":"सीधी रेखा की ढलान = ?","options":["y/x","Δy/Δx","x/y","(y₂+y₁)/(x₂+x₁)"],"correct":1,"explanation":"Δy/Δx।"},
                    {"question":"वृत्त का क्षेत्रफल?","options":["πr","πr²","2πr","πd"],"correct":1,"explanation":"πr²।"},
                    {"question":"त्रिभुज का क्षेत्रफल = ?","options":["(1/2)bh","bh","b + h","2bh"],"correct":0,"explanation":"(1/2) × base × height।"},
                    {"question":"समबाहु त्रिभुज का प्रत्येक कोण?","options":["45°","60°","90°","120°"],"correct":1,"explanation":"60°।"},
                    {"question":"पाइथागोरस प्रमेय a² + b² = ?","options":["c","c²","2c","√c"],"correct":1,"explanation":"c²।"},
                    {"question":"एक वृत्त में 360° का कौन सा कोण होता है?","options":["केंद्रीय कोण","परिधीय कोण","समकोण","ऋणात्मक कोण"],"correct":0,"explanation":"पूर्ण केंद्रीय कोण।"}
                ]
            },
            "English": {
                "Noun": [
                    {"question":"Which is a noun?","options":["Run","Beautiful","Cat","Quickly"],"correct":2,"explanation":"'Cat' is a noun."},
                    {"question":"Identify the noun: 'The sun is bright.'","options":["The","sun","is","bright"],"correct":1,"explanation":"'Sun' is a noun."},
                    {"question":"Which is a proper noun?","options":["city","Delhi","boy","river"],"correct":1,"explanation":"'Delhi' is a proper noun."},
                    {"question":"Plural of 'child'?","options":["childs","childes","children","childrens"],"correct":2,"explanation":"Children."},
                    {"question":"Collective noun for sheep?","options":["herd","flock","pack","swarm"],"correct":1,"explanation":"Flock of sheep."},
                    {"question":"Which word is an abstract noun?","options":["table","happiness","apple","car"],"correct":1,"explanation":"'Happiness' is abstract."},
                    {"question":"Find the noun: 'She bought a new dress.'","options":["She","bought","new","dress"],"correct":3,"explanation":"'Dress' is the noun."},
                    {"question":"Feminine gender of 'actor'?","options":["actress","actoress","actorine","actora"],"correct":0,"explanation":"Actress."},
                    {"question":"Identify the common noun: 'The Ganga is a holy river.'","options":["Ganga","holy","river","The"],"correct":2,"explanation":"'River' is common."},
                    {"question":"Which is an uncountable noun?","options":["book","water","pen","chair"],"correct":1,"explanation":"Water."},
                    {"question":"Material noun: 'This ring is made of gold.'","options":["ring","is","made","gold"],"correct":3,"explanation":"'Gold'."},
                    {"question":"Plural of 'mouse'?","options":["mouses","mice","mices","mouse"],"correct":1,"explanation":"Mice."},
                    {"question":"Collective noun example?","options":["team","boy","cat","table"],"correct":0,"explanation":"'Team' is collective."},
                    {"question":"Noun form of 'strong'?","options":["strongly","strength","stronger","strongest"],"correct":1,"explanation":"Strength."},
                    {"question":"Countable noun?","options":["rice","air","bottle","milk"],"correct":2,"explanation":"Bottle."},
                    {"question":"Possessive noun: 'This is Rahul's book.'","options":["Rahul","Rahul's","book","This"],"correct":1,"explanation":"'Rahul's'."},
                    {"question":"Type of noun: 'army'?","options":["Abstract","Common","Collective","Proper"],"correct":2,"explanation":"Collective."},
                    {"question":"Plural of 'tooth'?","options":["tooths","teeth","toothes","teeths"],"correct":1,"explanation":"Teeth."},
                    {"question":"Which is NOT a noun?","options":["city","run","freedom","chair"],"correct":1,"explanation":"'Run' is a verb."},
                    {"question":"Plural of 'foot'?","options":["foots","feet","feets","foot"],"correct":1,"explanation":"Feet."}
                ]
            },
            "Reasoning": {
                "Series": [
                    {"question":"2, 4, 8, 16, ?","options":["18","24","32","30"],"correct":2,"explanation":"Double each term."},
                    {"question":"1, 4, 9, 16, ?","options":["20","25","30","36"],"correct":1,"explanation":"Squares: 5²=25."},
                    {"question":"5, 10, 15, 20, ?","options":["22","24","25","30"],"correct":2,"explanation":"+5 each time."},
                    {"question":"3, 6, 12, 24, ?","options":["36","42","48","54"],"correct":2,"explanation":"Doubling."},
                    {"question":"1, 1, 2, 3, 5, ?","options":["6","7","8","9"],"correct":2,"explanation":"Fibonacci: 8."},
                    {"question":"A, C, E, G, ?","options":["H","I","J","K"],"correct":1,"explanation":"Every second letter."},
                    {"question":"Z, X, V, T, ?","options":["R","S","Q","P"],"correct":0,"explanation":"Reverse, skip one."},
                    {"question":"AB, EF, IJ, ?","options":["MN","OP","MNOP","QR"],"correct":0,"explanation":"Pairs every 4 steps."},
                    {"question":"1, 3, 6, 10, ?","options":["12","14","15","16"],"correct":2,"explanation":"Triangular numbers."},
                    {"question":"0, 1, 1, 2, 3, 5, ?","options":["6","7","8","9"],"correct":2,"explanation":"Fibonacci."},
                    {"question":"2, 5, 10, 17, ?","options":["24","26","28","30"],"correct":1,"explanation":"n²+1."},
                    {"question":"100, 81, 64, 49, ?","options":["36","25","16","9"],"correct":0,"explanation":"Squares descending."},
                    {"question":"B, D, F, H, ?","options":["I","J","K","L"],"correct":1,"explanation":"Every second letter."},
                    {"question":"1, 8, 27, 64, ?","options":["100","125","150","175"],"correct":1,"explanation":"Cubes."},
                    {"question":"12, 10, 8, 6, ?","options":["3","4","5","2"],"correct":1,"explanation":"-2."},
                    {"question":"1, 1, 2, 6, 24, ?","options":["48","60","72","120"],"correct":3,"explanation":"Factorial."},
                    {"question":"10, 20, 40, 80, ?","options":["100","120","140","160"],"correct":3,"explanation":"Double."},
                    {"question":"A, E, I, M, ?","options":["N","O","P","Q"],"correct":2,"explanation":"Every 4th."},
                    {"question":"1, 2, 6, 24, 120, ?","options":["240","360","480","720"],"correct":3,"explanation":"Factorial."},
                    {"question":"Z, Y, X, W, ?","options":["V","U","T","S"],"correct":0,"explanation":"Reverse."}
                ]
            },
            "Science": {
                "Physics": [
                    {"question":"प्रकाश की गति (m/s)?","options":["3×10⁶","3×10⁸","3×10¹⁰","3×10⁴"],"correct":1,"explanation":"≈ 3×10⁸ m/s"},
                    {"question":"गुरुत्वाकर्षण की खोज किसने की?","options":["आइंस्टीन","न्यूटन","गैलीलियो","एडिसन"],"correct":1,"explanation":"आइज़क न्यूटन।"},
                    {"question":"बल का SI मात्रक?","options":["जूल","न्यूटन","वाट","पास्कल"],"correct":1,"explanation":"Newton (N)"},
                    {"question":"पावर का मात्रक?","options":["जूल","न्यूटन","वाट","एम्पीयर"],"correct":2,"explanation":"Watt"},
                    {"question":"ध्वनि की गति (हवा में)?","options":["343 m/s","3000 m/s","30 m/s","3×10⁸ m/s"],"correct":0,"explanation":"≈ 343 m/s"},
                    {"question":"1 N बराबर है?","options":["1 kg m/s²","1 kg m/s","1 g m/s²","1 kg cm/s²"],"correct":0,"explanation":"F=ma ⇒ 1 N = 1 kg·m/s²"},
                    {"question":"प्रकाश वर्ष किसका मात्रक है?","options":["समय","दूरी","चाल","द्रव्यमान"],"correct":1,"explanation":"दूरी।"},
                    {"question":"विद्युत धारा का मात्रक?","options":["वोल्ट","एम्पीयर","ओम","वाट"],"correct":1,"explanation":"एम्पीयर (A)"},
                    {"question":"g का मान लगभग?","options":["8.9 m/s²","9.8 m/s²","10.8 m/s²","7.8 m/s²"],"correct":1,"explanation":"9.8 m/s²"},
                    {"question":"1 L = ? mL","options":["100","500","1000","1500"],"correct":2,"explanation":"1000 mL"},
                    {"question":"पारसेक किसकी इकाई है?","options":["समय","दूरी","द्रव्यमान","ऊर्जा"],"correct":1,"explanation":"खगोलीय दूरी।"},
                    {"question":"ध्वनि तरंग किस प्रकार की है?","options":["अनुप्रस्थ","अनुदैर्ध्य","विद्युत चुम्बकीय","यांत्रिक नहीं"],"correct":1,"explanation":"अनुदैर्ध्य यांत्रिक तरंग।"},
                    {"question":"प्रतिध्वनि के लिए न्यूनतम दूरी?","options":["10 m","17 m","20 m","25 m"],"correct":1,"explanation":"लगभग 17 m।"},
                    {"question":"ऊष्मा का SI मात्रक?","options":["जूल","कैलोरी","वाट","न्यूटन"],"correct":0,"explanation":"जूल (J)"},
                    {"question":"तरंग दैर्ध्य का प्रतीक?","options":["α","β","λ","γ"],"correct":2,"explanation":"λ (लैम्ब्डा)"},
                    {"question":"सूर्य का प्रकाश पृथ्वी तक आने में समय?","options":["8 मिनट","1 सेकंड","1 घंटा","24 घंटे"],"correct":0,"explanation":"≈ 8 मिनट 20 सेकंड।"},
                    {"question":"पानी का क्वथनांक किस पर निर्भर?","options":["द्रव्यमान","वायुमंडलीय दबाव","आयतन","रंग"],"correct":1,"explanation":"दबाव।"},
                    {"question":"इंद्रधनुष में कितने रंग?","options":["5","6","7","8"],"correct":2,"explanation":"7 (VIBGYOR)"},
                    {"question":"सूर्य ग्रहण कब होता है?","options":["पूर्णिमा","अमावस्या","दोनों","कभी नहीं"],"correct":1,"explanation":"अमावस्या पर।"},
                    {"question":"चंद्र ग्रहण कब होता है?","options":["पूर्णिमा","अमावस्या","दोनों","कभी नहीं"],"correct":0,"explanation":"पूर्णिमा पर।"}
                ]
            }
        }
        for cat, topics in samples.items():
            for topic, qs in topics.items():
                for q in qs:
                    db.session.add(Question(
                        category=cat, topic=topic, question=q["question"],
                        options=json.dumps(q["options"]), correct=q["correct"],
                        explanation=q.get("explanation", "")
                    ))
        db.session.commit()

# ====================== HELPERS ======================
def shuffle_options(q):
    opts = json.loads(q.options)
    correct = q.correct
    indices = list(range(4))
    random.shuffle(indices)
    new_opts = [opts[i] for i in indices]
    new_correct = indices.index(correct)
    return new_opts, new_correct

def auto_split_import(category, questions_list):
    chunk_size = 20
    objects = []
    
    # Dynamically find the next available Test number
    existing_topics = db.session.query(Question.topic).filter(
        Question.category == category, 
        Question.topic.like("Test %")
    ).all()
    max_test_num = 0
    for t in existing_topics:
        try:
            num = int(t[0].replace("Test ", ""))
            if num > max_test_num:
                max_test_num = num
        except ValueError:
            pass
            
    start_idx = max_test_num
    for i in range(0, len(questions_list), chunk_size):
        chunk = questions_list[i:i+chunk_size]
        topic_name = f"Test {start_idx + (i // chunk_size) + 1}"
        for q in chunk:
            objects.append(Question(
                category=category, topic=topic_name, question=q["question"],
                options=json.dumps(q["options"]), correct=int(q["correct"]),
                explanation=q.get("explanation", "")
            ))
    return objects

def update_user_stats(username, correct_count):
    stats = UserStats.query.filter_by(username=username).first()
    if not stats:
        stats = UserStats(username=username, xp=0, streak=1, last_active=datetime.date.utcnow())
        db.session.add(stats)
    
    today = datetime.date.utcnow()
    if stats.last_active != today:
        yesterday = today - datetime.timedelta(days=1)
        if stats.last_active == yesterday:
            stats.streak += 1
        else:
            stats.streak = 1
        stats.last_active = today
    
    stats.xp += correct_count * 10
    stats.level = min(99, (stats.xp // 100) + 1)

# ====================== API ROUTES ======================
@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/categories')
def get_categories():
    return jsonify(["GK", "Maths", "English", "Reasoning", "Science"])

@app.route('/api/topics')
def get_topics():
    category = request.args.get('category')
    if not category:
        return jsonify([])
    topics = db.session.query(Question.topic).filter(Question.category == category).distinct().all()
    topics = [t[0] for t in topics]
    result = []
    for topic in topics:
        count = Question.query.filter_by(category=category, topic=topic).count()
        result.append({"name": topic, "count": count})
    return jsonify(result)

@app.route('/api/start-test', methods=['POST'])
def start_test():
    data = request.json
    username = data.get('username', 'guest')
    category = data.get('category')
    topic = data.get('topic')
    mode = data.get('mode', 'normal')
    limit = data.get('limit', 20)
    
    if mode == 'all':
        questions = Question.query.filter_by(category=category).all()
        if not questions:
            return jsonify({'error': 'No questions in this category'}), 404
        random.shuffle(questions)
        questions = questions[:limit]  # STRICT CAP
        timer_min = max(1, len(questions) // 2)
    elif mode in ('weak', 'hard'):
        weaks = WeakQuestion.query.filter_by(username=username)
        if mode == 'hard':
            weaks = weaks.filter(WeakQuestion.wrong_count >= 2)
        else:
            weaks = weaks.filter(WeakQuestion.wrong_count >= 1)
        weaks = weaks.all()
        if not weaks:
            return jsonify({'error': f'No {mode} questions yet'}), 404
        question_ids = [w.question_id for w in weaks]
        questions = Question.query.filter(Question.id.in_(question_ids)).all()
        random.shuffle(questions)
        questions = questions[:limit]  # STRICT CAP
        timer_min = max(1, len(questions))
    else:
        questions = Question.query.filter_by(category=category, topic=topic).all()
        if len(questions) < limit:
            return jsonify({'error': f'Need at least {limit} questions for this topic'}), 404
        random.shuffle(questions)
        questions = questions[:limit]  # STRICT CAP
        timer_min = max(1, len(questions) // 2)
        
    result = []
    for q in questions:
        new_opts, new_correct = shuffle_options(q)
        result.append({
            'id': q.id, 'category': q.category, 'topic': q.topic,
            'question': q.question, 'options': new_opts,
            'correct': new_correct, 'explanation': q.explanation
        })
    return jsonify({'questions': result, 'timer_min': timer_min, 'mode': mode})

@app.route('/api/submit-test', methods=['POST'])
def submit_test():
    data = request.json
    username = data.get('username', 'guest')
    answers = data.get('answers', [])
    category = data.get('category', '')
    topic = data.get('topic', '')
    mode = data.get('mode', 'normal')
    time_sec = data.get('time_sec', 0)
    correct = wrong = skipped = 0
    for a in answers:
        q = Question.query.get(a['question_id'])
        if not q: continue
        sel = a.get('selected')
        if sel is None:
            skipped += 1
        elif sel == q.correct:
            correct += 1
            if mode == 'hard':
                weak = WeakQuestion.query.filter_by(username=username, question_id=q.id).first()
                if weak and weak.wrong_count >= 2:
                    weak.wrong_count = 1
        else:
            wrong += 1
            weak = WeakQuestion.query.filter_by(username=username, question_id=q.id).first()
            if not weak:
                db.session.add(WeakQuestion(username=username, question_id=q.id, wrong_count=1))
            else:
                weak.wrong_count += 1
                weak.last_wrong = datetime.datetime.utcnow()
    
    update_user_stats(username, correct)
    
    total = len(answers)
    pct = round(correct/total*100, 2) if total else 0
    attempt = TestAttempt(
        username=username, category=category, topic=topic,
        total=total, correct=correct, wrong=wrong, skipped=skipped,
        pct=pct, time_sec=time_sec, mode=mode
    )
    db.session.add(attempt)
    db.session.commit()
    
    stats = UserStats.query.filter_by(username=username).first()
    xp_earned = correct * 10
    new_xp = stats.xp if stats else 0
    new_level = stats.level if stats else 1
    new_streak = stats.streak if stats else 0
    
    return jsonify({
        'correct':correct,'wrong':wrong,'skipped':skipped,'total':total,'pct':pct,'time_sec':time_sec,
        'xp_earned': xp_earned, 'new_xp': new_xp, 'new_level': new_level, 'new_streak': new_streak
    })

@app.route('/api/weak-questions/<username>')
def weak_questions_paginated(username):
    page = request.args.get('page', 1, type=int)
    limit = 20
    offset = (page - 1) * limit
    weak = WeakQuestion.query.filter_by(username=username).order_by(
        WeakQuestion.wrong_count.desc(), WeakQuestion.last_wrong.desc()
    ).offset(offset).limit(limit).all()
    total = WeakQuestion.query.filter_by(username=username).count()
    total_pages = (total + limit - 1) // limit
    result = []
    for w in weak:
        q = Question.query.get(w.question_id)
        if q:
            result.append({
                'weak_id': w.id, 'question_id': q.id,
                'category': q.category, 'topic': q.topic,
                'question': q.question, 'options': json.loads(q.options),
                'correct': q.correct, 'explanation': q.explanation,
                'wrong_count': w.wrong_count,
                'last_wrong': w.last_wrong.isoformat() if w.last_wrong else None
            })
    return jsonify({'weak_questions': result, 'page': page, 'total_pages': total_pages, 'total': total})

@app.route('/api/results')
def recent_results():
    username = request.args.get('username')
    if not username:
        return jsonify([])
    attempts = TestAttempt.query.filter_by(username=username).order_by(TestAttempt.timestamp.desc()).limit(20).all()
    return jsonify([{
        'category': a.category, 'topic': a.topic, 'total': a.total,
        'correct': a.correct, 'wrong': a.wrong, 'skipped': a.skipped,
        'pct': a.pct, 'time_sec': a.time_sec, 'mode': a.mode,
        'date': a.timestamp.isoformat()
    } for a in attempts])

@app.route('/api/stats')
def user_stats():
    username = request.args.get('username')
    if not username:
        return jsonify({'total_questions':0, 'total_tests':0, 'avg_pct':0, 'weak_count':0, 'xp':0, 'level':1, 'streak':0})
    total_q = Question.query.count()
    attempts = TestAttempt.query.filter_by(username=username).all()
    total_tests = len(attempts)
    avg_pct = round(sum(a.pct for a in attempts)/total_tests, 1) if total_tests else 0
    weak_count = WeakQuestion.query.filter_by(username=username).count()
    
    stats = UserStats.query.filter_by(username=username).first()
    xp = stats.xp if stats else 0
    level = stats.level if stats else 1
    streak = stats.streak if stats else 0
    
    return jsonify({
        'total_questions': total_q, 'total_tests': total_tests, 'avg_pct': avg_pct, 
        'weak_count': weak_count, 'xp': xp, 'level': level, 'streak': streak
    })

@app.route('/api/analytics')
def user_analytics():
    username = request.args.get('username')
    if not username:
        return jsonify([])
    attempts = TestAttempt.query.filter_by(username=username).all()
    cat_stats = {}
    for a in attempts:
        if a.category not in cat_stats:
            cat_stats[a.category] = {'total': 0, 'correct': 0}
        cat_stats[a.category]['total'] += a.total
        cat_stats[a.category]['correct'] += a.correct
    result = []
    for cat, vals in cat_stats.items():
        pct = round(vals['correct']/vals['total']*100, 1) if vals['total'] > 0 else 0
        result.append({'category': cat, 'accuracy': pct, 'tests': vals['total']})
    return jsonify(result)

@app.route('/api/questions', methods=['GET','POST'])
def questions_api():
    if request.method == 'GET':
        qs = Question.query.all()
        return jsonify([{
            'id': q.id, 'category': q.category, 'topic': q.topic,
            'question': q.question, 'options': json.loads(q.options),
            'correct': q.correct, 'explanation': q.explanation
        } for q in qs])
    else:
        data = request.json
        if not isinstance(data, list):
            return jsonify({'error': 'Expected list'}), 400
        for item in data:
            q = Question(
                category=item.get('category','GK'), topic=item.get('topic','General'),
                question=item['question'], options=json.dumps(item['options']),
                correct=int(item['correct']), explanation=item.get('explanation','')
            )
            db.session.add(q)
        db.session.commit()
        return jsonify({'status':'ok','added':len(data)})

@app.route('/api/questions/<int:qid>', methods=['DELETE'])
def delete_question(qid):
    q = Question.query.get(qid)
    if not q:
        return jsonify({'error':'Not found'}), 404
    WeakQuestion.query.filter_by(question_id=qid).delete()
    db.session.delete(q)
    db.session.commit()
    return jsonify({'status':'ok'})

@app.route('/api/import-questions', methods=['POST'])
def import_questions():
    data = request.json
    category = data.get('category', 'GK')
    auto_split = data.get('auto_split', True)
    qlist = data.get('questions', [])
    if not qlist:
        return jsonify({'error': 'No questions provided'}), 400
    for q in qlist:
        if not all(k in q for k in ('question','options','correct')):
            return jsonify({'error': 'Invalid question format'}), 400
        if len(q['options']) != 4:
            return jsonify({'error': 'Each question must have exactly 4 options'}), 400
    if auto_split:
        objects = auto_split_import(category, qlist)
    else:
        objects = [Question(
            category=category, topic=q.get('topic','Imported'),
            question=q['question'], options=json.dumps(q['options']),
            correct=int(q['correct']), explanation=q.get('explanation','')
        ) for q in qlist]
    db.session.add_all(objects)
    db.session.commit()
    return jsonify({'status':'ok','added':len(objects)})

@app.route('/api/clear-all', methods=['DELETE'])
def clear_all_questions():
    WeakQuestion.query.delete()
    Question.query.delete()
    db.session.commit()
    return jsonify({'status':'ok'})

@app.route('/api/export-all', methods=['POST'])
def export_all():
    data = request.json or {}
    password = data.get('password', '')
    if hashlib.sha256(password.encode()).hexdigest() != EXPORT_PASSWORD_HASH:
        return jsonify({'error': 'Invalid password'}), 401
    qs = Question.query.all()
    export_data = []
    for q in qs:
        export_data.append({
            'category': q.category, 'topic': q.topic, 'question': q.question,
            'options': json.loads(q.options), 'correct': q.correct,
            'explanation': q.explanation
        })
    json_output = json.dumps(export_data, ensure_ascii=False, indent=2)
    bio = BytesIO(json_output.encode('utf-8'))
    bio.seek(0)
    return send_file(
        bio, mimetype='application/json', as_attachment=True,
        download_name=f'questions_export_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    )

# ====================== FRONTEND (EMBEDDED) ======================
HTML = '''<!DOCTYPE html>
<html lang="hi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
  <title>MockTest.pro - Level 99</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg:#f8faff; --card:#fff; --sunk:#edf2f9; --text:#1e2030; --text2:#5b5d6b; --muted:#9295a1;
      --line:#dce0e8; --line2:#c4c9d4; --brand:#4f46e5; --brand2:#f97316;
      --ok:#10b981; --oksoft:#d1fae5; --err:#ef4444; --errsoft:#fee2e2; --warn:#f59e0b; --warnsoft:#fef3c7;
      --shadow:0 1px 3px #0000000d,0 1px 2px #0000000a; --shadowMd:0 4px 12px #0000000f; --shadowLg:0 12px 32px #00000014;
      --radius:16px; --font:'Plus Jakarta Sans',sans-serif; --mono:'JetBrains Mono',monospace;
    }
    [data-theme="dark"] {
      --bg:#0f1123; --card:#1a1d2e; --sunk:#151828; --text:#f1f2f6; --text2:#b0b4c2; --muted:#777b8e;
      --line:#272b3a; --line2:#3a3f55; --brand:#818cf8; --brand2:#fb923c;
      --ok:#34d399; --oksoft:rgba(52,211,153,.15); --err:#f87171; --errsoft:rgba(248,113,113,.15);
      --warnsoft:rgba(245,158,11,.15);
    }
    *{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:transparent}
    body{font-family:var(--font);background:var(--bg);color:var(--text);min-height:100vh;line-height:1.5;transition:background .3s,color .3s;overflow-x:hidden}
    .container{width:100%;max-width:1200px;margin:0 auto;padding:0 16px;position:relative;z-index:2}
    button{font-family:inherit;cursor:pointer;border:0;background:none;color:inherit;transition: transform 0.1s ease, background 0.2s}
    button:active { transform: scale(0.96); }
    input,textarea,select{font-family:inherit;font-size:16px;color:var(--text);width:100%}
    a{color:var(--brand);text-decoration:none}
    
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes slideInRight { from { opacity: 0; transform: translateX(20px); } to { opacity: 1; transform: translateX(0); } }
    @keyframes popIn { 0% { opacity: 0; transform: scale(0.9); } 100% { opacity: 1; transform: scale(1); } }
    @keyframes blob { 0%, 100% { transform: translate(0, 0) scale(1); } 33% { transform: translate(30px, -50px) scale(1.1); } 66% { transform: translate(-20px, 20px) scale(0.9); } }
    @keyframes shimmer { 0% { background-position: -468px 0; } 100% { background-position: 468px 0; } }
    
    .screen { animation: fadeInUp 0.4s ease-out; }
    .stagger-item { opacity: 0; animation: fadeInUp 0.4s ease-out forwards; }

    .bg-blob { position: fixed; border-radius: 50%; filter: blur(80px); z-index: 0; opacity: 0.4; pointer-events: none; }
    .blob-1 { width: 300px; height: 300px; background: var(--brand); top: -50px; left: -50px; animation: blob 12s infinite ease-in-out; }
    .blob-2 { width: 250px; height: 250px; background: var(--brand2); bottom: -50px; right: -50px; animation: blob 15s infinite ease-in-out reverse; }

    .navbar{position:sticky;top:0;z-index:50;background:var(--card);border-bottom:1px solid var(--line);height:56px;display:flex;align-items:center;box-shadow:var(--shadow)}
    .nav-wrap{display:flex;align-items:center;justify-content:space-between;width:100%}
    .brand{display:flex;align-items:center;gap:10px;font-weight:800;font-size:1.2rem;color:var(--text)}
    .brand-dot{width:28px;height:28px;border-radius:9px;background:linear-gradient(135deg,var(--brand),#8b5cf6);position:relative}
    .brand-dot::after{content:"M";position:absolute;inset:0;display:grid;place-items:center;color:#fff;font-weight:800;font-size:14px}
    .nav-right{display:flex;align-items:center;gap:10px}
    .user-chip{display:flex;align-items:center;gap:6px;padding:5px 12px;border-radius:50px;background:var(--sunk);font-size:.85rem;cursor:pointer}
    .user-chip:hover { background: var(--line); }
    .dot-live{width:8px;height:8px;border-radius:50%;background:var(--ok);animation:pulse 2s infinite}
    @keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
    .icon-btn{width:40px;height:40px;border-radius:12px;display:flex;align-items:center;justify-content:center;background:var(--sunk);border:1px solid var(--line)}
    .icon-btn:hover{background:var(--brand);color:#fff;border-color:var(--brand)}
    .icon-btn svg{width:20px;height:20px}
    [data-theme="light"] .i-moon,[data-theme="dark"] .i-sun{display:none}
    
    .bottom-nav{display:flex;position:fixed;bottom:0;left:0;right:0;background:var(--card);border-top:1px solid var(--line);z-index:45;padding:6px 0;justify-content:space-around;align-items:center;box-shadow:0 -4px 12px rgba(0,0,0,0.05)}
    .bottom-nav button{display:flex;flex-direction:column;align-items:center;gap:2px;color:var(--muted);font-size:.65rem;padding:4px 0;font-weight:600}
    .bottom-nav button.active{color:var(--brand)}
    .bottom-nav button svg{width:22px;height:22px}
    
    .screen{display:none;padding:24px 0 80px}
    .screen.active{display:block}
    
    .hero{max-width:600px;margin:0 auto;text-align:center;padding:40px 16px}
    .hero-tag{display:inline-flex;align-items:center;gap:8px;padding:6px 16px;border-radius:100px;background:var(--sunk);font-size:.85rem;color:var(--text2);margin-bottom:20px}
    .hero-title{font-size:clamp(2rem,7vw,3.5rem);font-weight:800;line-height:1.1;margin-bottom:12px}
    .grad-word{background:linear-gradient(135deg,var(--brand),var(--brand2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
    .hero-sub{max-width:500px;margin:0 auto 24px;color:var(--text2);font-size:1rem}
    .name-card{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:24px;box-shadow:var(--shadowMd);text-align:left;margin-bottom:20px}
    .name-card label{display:block;font-weight:600;margin-bottom:8px;color:var(--text2);text-transform:uppercase;font-size:.75rem;letter-spacing:.1em}
    .name-row{display:flex;gap:10px;flex-wrap:wrap}
    input,textarea,select{padding:14px 16px;border:1px solid var(--line2);border-radius:12px;background:var(--bg);font-size:1rem;outline:none;transition:border-color .2s, box-shadow .2s}
    input:focus,textarea:focus,select:focus{border-color:var(--brand);box-shadow:0 0 0 3px rgba(79,70,229,.2)}
    .name-hint{font-size:.75rem;color:var(--muted);margin-top:8px}
    
    .btn-primary{display:inline-flex;align-items:center;gap:8px;padding:14px 24px;border-radius:12px;background:linear-gradient(135deg,var(--brand),var(--brand2));color:#fff;font-weight:700;font-size:1rem;border:none;box-shadow:0 4px 14px rgba(79,70,229,0.3)}
    .btn-primary:hover{transform:translateY(-2px);box-shadow:0 8px 20px rgba(79,70,229,.4)}
    .btn-ghost{display:inline-flex;align-items:center;gap:6px;padding:12px 20px;border-radius:12px;background:var(--card);color:var(--text);font-weight:600;font-size:.95rem;border:1px solid var(--line)}
    .btn-ghost:hover{background:var(--sunk);border-color:var(--line2)}
    .btn-danger{padding:12px 16px;border-radius:12px;background:var(--errsoft);color:var(--err);font-weight:700;border:none}
    .btn-danger:hover{background:var(--err);color:#fff}
    .hidden{display:none!important}
    
    .page-head{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;margin-bottom:24px}
    .eyebrow{text-transform:uppercase;letter-spacing:.1em;font-size:.7rem;color:var(--muted);font-weight:600}
    .page-title{font-size:2rem;font-weight:800}
    
    .profile-card { background: var(--card); border: 1px solid var(--line); border-radius: var(--radius); padding: 20px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; box-shadow: var(--shadow); }
    .pc-left h2 { font-size: 1.2rem; margin-bottom: 4px; }
    .pc-left p { font-size: 0.8rem; color: var(--muted); }
    .pc-right { text-align: center; }
    .level-badge { width: 60px; height: 60px; border-radius: 50%; background: linear-gradient(135deg, var(--brand), var(--brand2)); color: #fff; display: grid; place-items: center; font-weight: 800; font-size: 1.4rem; box-shadow: 0 4px 12px rgba(79,70,229,0.3); }
    .pc-right span { font-size: 0.65rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; }
    
    .quick-stats{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-bottom:20px}
    @media(min-width:600px){.quick-stats{grid-template-columns:repeat(4,1fr)}}
    .stat{padding:14px;background:var(--card);border:1px solid var(--line);border-radius:14px;text-align:center}
    .stat b{display:block;font-size:1.5rem;font-weight:700;background:linear-gradient(135deg,var(--brand),var(--brand2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
    .stat span{font-size:.7rem;color:var(--muted);text-transform:uppercase}
    
    .grid-2{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin:20px 0}
    @media(min-width:600px){.grid-2{grid-template-columns:repeat(3,1fr)}}
    .action-card{padding:18px;border-radius:20px;background:var(--card);border:1px solid var(--line);cursor:pointer;position:relative;overflow:hidden;text-align:left;width:100%}
    .action-card:hover{transform:translateY(-3px);box-shadow:var(--shadowLg);border-color:var(--brand)}
    .ac-icon{width:40px;height:40px;border-radius:12px;display:grid;place-items:center;margin-bottom:10px;color:#fff;font-size:1.1rem}
    .ac-icon.g1{background:linear-gradient(135deg,#6366f1,#8b5cf6)} .ac-icon.g2{background:linear-gradient(135deg,#f59e0b,#f97316)}
    .ac-icon.g3{background:linear-gradient(135deg,#10b981,#06b6d4)} .ac-icon.g4{background:linear-gradient(135deg,#ef4444,#f97316)}
    .ac-icon.g5{background:linear-gradient(135deg,#8b5cf6,#ec4899)} .ac-icon.g6{background:linear-gradient(135deg,#06b6d4,#3b82f6)}
    .action-card h3{font-size:1rem;margin-bottom:4px;font-weight:700}
    .action-card p{color:var(--text2);font-size:.8rem;margin:0}
    .ac-arrow{position:absolute;right:14px;top:14px;font-size:1.2rem;color:var(--muted);transition:.3s}
    .action-card:hover .ac-arrow{transform:translateX(6px);color:var(--brand)}
    .section-h{font-weight:700;font-size:.85rem;color:var(--text2);letter-spacing:.05em;text-transform:uppercase;margin:24px 0 10px;display:flex;align-items:center;gap:8px}
    
    .subtopic-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:10px}
    .subtopic-tile{padding:14px;border-radius:14px;background:var(--card);border:1px solid var(--line);cursor:pointer;text-align:left;width:100%}
    .subtopic-tile:hover{transform:translateY(-2px);border-color:var(--brand);box-shadow:var(--shadowMd)}
    .subtopic-tile h4{font-size:.9rem;margin-bottom:4px;font-weight:700}
    .subtopic-tile span{font-size:.7rem;color:var(--muted)}
    .empty{padding:20px;text-align:center;color:var(--muted);border:1.5px dashed var(--line);border-radius:12px;background:var(--sunk)}
    .recent-list{display:grid;gap:10px}
    .recent-item{display:flex;justify-content:space-between;align-items:center;padding:12px 14px;background:var(--card);border:1px solid var(--line);border-radius:14px}
    .ri-left{display:flex;align-items:center;gap:12px}
    .ri-badge{width:46px;height:46px;border-radius:12px;display:grid;place-items:center;font-weight:800;font-size:.95rem;color:#fff}
    .ri-badge.ok{background:linear-gradient(135deg,#10b981,#06b6d4)} .ri-badge.avg{background:linear-gradient(135deg,#f59e0b,#f97316)} .ri-badge.bad{background:linear-gradient(135deg,#ef4444,#f97316)}
    .recent-item h5{font-size:.9rem;margin:0} .recent-item small{color:var(--muted);font-size:.75rem}
    
    .skeleton-card { background: var(--sunk); border-radius: 14px; height: 80px; width: 100%; background-image: linear-gradient(90deg, var(--sunk) 0px, var(--card) 40px, var(--sunk) 80px); background-size: 600px; animation: shimmer 1.5s infinite linear; }

    .list-toolbar{display:flex;gap:8px;margin-bottom:12px;flex-wrap:wrap}
    .list-toolbar input,.list-toolbar select{flex:1;min-width:140px}
    .questions-list{display:grid;gap:8px}
    .q-row{display:flex;justify-content:space-between;align-items:flex-start;gap:10px;padding:12px;background:var(--card);border:1px solid var(--line);border-radius:14px}
    .q-row .q-cat{display:inline-block;padding:2px 8px;border-radius:20px;font-size:.65rem;font-weight:700;background:rgba(79,70,229,.1);color:var(--brand);margin-bottom:6px}
    .q-row .q-text{font-weight:600;font-size:.9rem} .q-row .q-ans{font-size:.75rem;color:var(--ok);font-weight:700}
    .q-row .del{padding:4px 8px;border-radius:6px;font-weight:700;font-size:.7rem;border:1px solid var(--line);background:transparent;color:var(--err)}
    .q-row .del:hover{background:var(--err);color:#fff}
    
    .tabs{display:flex;gap:4px;padding:4px;background:var(--sunk);border-radius:12px;margin-bottom:16px;overflow-x:auto}
    .tab{padding:10px 16px;border-radius:8px;font-weight:600;font-size:.85rem;color:var(--text2);white-space:nowrap}
    .tab.active{background:var(--card);color:var(--brand);box-shadow:var(--shadow)}
    .tab-panel{display:none} .tab-panel.active{display:block;animation: fadeInUp 0.3s ease}
    .form-card{display:grid;gap:12px;background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:20px}
    .form-card label{font-weight:600;color:var(--text2);font-size:.85rem;display:block;margin-bottom:4px}
    .form-actions{display:flex;gap:8px;justify-content:flex-end;flex-wrap:wrap} .form-actions.between{justify-content:space-between}
    
    .test-topbar{background:var(--card);border-bottom:1px solid var(--line);padding:10px 0;position:sticky;top:0;z-index:30}
    .test-topwrap{display:flex;align-items:center;gap:10px}
    .tp-progress{flex:1;display:flex;align-items:center;gap:8px;font-weight:700;font-size:.9rem}
    .tp-bar{flex:1;max-width:160px;height:5px;background:var(--sunk);border-radius:50px;overflow:hidden}
    .tp-bar span{display:block;height:100%;background:linear-gradient(90deg,var(--brand),var(--brand2));border-radius:50px;transition:width .4s}
    .tp-timer{padding:6px 10px;border-radius:8px;font-family:var(--mono);font-weight:600;background:var(--sunk);font-size:.9rem}
    .tp-timer.warn{color:var(--err);animation:pulse 1s infinite}
    .test-body{padding-top:20px}
    .question-card{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:20px;box-shadow:var(--shadowMd)}
    .q-card-animate { animation: slideInRight 0.3s ease-out; }
    .q-cat-top{display:inline-block;padding:3px 10px;border-radius:20px;font-size:.75rem;font-weight:700;background:rgba(79,70,229,.1);color:var(--brand);margin-bottom:10px}
    .q-text-lg{font-size:clamp(1rem,2.5vw,1.3rem);font-weight:700;margin:0 0 16px}
    .opt-list{display:grid;gap:8px}
    .opt{display:flex;align-items:center;gap:12px;padding:12px 14px;border:1.5px solid var(--line2);border-radius:12px;background:var(--bg);font-weight:600;font-size:.95rem;text-align:left;width:100%}
    .opt:hover:not(:disabled){border-color:var(--brand);transform:translateX(2px)}
    .opt:disabled{opacity:.95;cursor:default}
    .opt .kbd{width:30px;height:30px;border-radius:8px;display:flex;align-items:center;justify-content:center;background:var(--sunk);border:1px solid var(--line);font-weight:800;font-size:13px;color:var(--text2);flex-shrink:0}
    .opt.correct{border-color:var(--ok);background:var(--oksoft)} .opt.correct .kbd{background:var(--ok);color:#fff;border-color:var(--ok)}
    .opt.wrong{border-color:var(--err);background:var(--errsoft)} .opt.wrong .kbd{background:var(--err);color:#fff;border-color:var(--err)}
    .explanation{margin-top:14px;padding:12px;background:rgba(79,70,229,.06);border-left:3px solid var(--brand);border-radius:8px;color:var(--text2);font-size:.9rem;animation: fadeInUp 0.3s ease}
    .test-actions{display:flex;justify-content:space-between;gap:8px;margin-top:16px}
    
    .xp-popup { position: fixed; top: 20%; left: 50%; transform: translate(-50%, -50%); background: linear-gradient(135deg, var(--brand), var(--brand2)); color: #fff; padding: 20px 30px; border-radius: 16px; font-weight: 800; font-size: 1.5rem; box-shadow: 0 10px 30px rgba(0,0,0,0.2); z-index: 200; animation: popIn 0.5s ease, fadeOut 1s ease 1.5s forwards; opacity: 0; }
    @keyframes fadeOut { to { opacity: 0; visibility: hidden; } }
    
    .result-hero{max-width:560px;margin:auto;text-align:center;padding:28px 16px;background:var(--card);border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadowLg)}
    .result-emoji{font-size:3.5rem;animation:popIn .8s}
    .result-hero h2{font-size:1.8rem;font-weight:800;margin-bottom:6px}
    .ring-wrap{position:relative;width:160px;height:160px;margin:20px auto}
    .ring{width:100%;height:100%;transform:rotate(-90deg)}
    .ring-bg{fill:none;stroke:var(--sunk);stroke-width:9} .ring-fg{fill:none;stroke:url(#gradRing);stroke-width:9;stroke-linecap:round;stroke-dasharray:267;stroke-dashoffset:267;transition:stroke-dashoffset 1s}
    .ring-center{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center;align-items:center}
    .ring-center b{font-size:2rem;font-weight:800} .ring-center span{font-size:.7rem;color:var(--muted);text-transform:uppercase}
    .result-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin:20px 0}
    @media(max-width:400px){.result-grid{grid-template-columns:repeat(2,1fr)}}
    .result-grid>div{padding:12px;background:var(--card);border:1px solid var(--line);border-radius:12px;animation: fadeInUp 0.5s ease backwards}
    .result-grid>div:nth-child(1){animation-delay:0.1s} .result-grid>div:nth-child(2){animation-delay:0.2s} .result-grid>div:nth-child(3){animation-delay:0.3s} .result-grid>div:nth-child(4){animation-delay:0.4s}
    .result-grid b{display:block;font-size:1.4rem}
    .result-actions{display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin-top:20px}
    .review-list{margin-top:20px;display:grid;gap:10px}
    .review-card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px;text-align:left;animation: fadeInUp 0.4s ease}
    .rc-status{padding:2px 8px;border-radius:20px;font-size:.65rem;font-weight:800}
    .rc-status.ok{background:var(--oksoft);color:var(--ok)} .rc-status.no{background:var(--errsoft);color:var(--err)} .rc-status.sk{background:var(--sunk);color:var(--muted)}
    .review-card .rc-q{font-weight:700;margin:6px 0;font-size:.9rem}
    .rc-opts{display:grid;gap:4px}
    .rc-opt{padding:6px 8px;border-radius:8px;background:var(--sunk);font-size:.8rem;display:flex;align-items:center;gap:6px;border:1px solid var(--line)}
    .rc-opt.correct{background:var(--oksoft);border-color:transparent;color:var(--ok);font-weight:700}
    .rc-opt.wrong{background:var(--errsoft);border-color:transparent;color:var(--err);font-weight:700;text-decoration:line-through}
    .rc-explain{margin-top:6px;padding:8px;background:rgba(79,70,229,.06);border-left:3px solid var(--brand);border-radius:6px;font-size:.8rem;color:var(--text2)}
    
    .weak-q-item{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--warn);border-radius:14px;padding:14px;margin-bottom:10px;animation: fadeInUp 0.4s ease}
    .weak-q-item .wq-head{display:flex;justify-content:space-between;align-items:flex-start;gap:10px;margin-bottom:8px}
    .weak-q-item .wq-q{font-weight:700;font-size:.95rem;flex:1}
    .weak-count{background:var(--warn);color:#fff;padding:4px 10px;border-radius:20px;font-weight:700;font-size:.7rem;white-space:nowrap}
    .weak-q-item .wq-opts{display:grid;gap:4px;margin:10px 0}
    .weak-q-item .wq-opt{padding:6px 8px;border-radius:8px;background:var(--sunk);font-size:.8rem;border:1px solid var(--line)}
    .weak-q-item .wq-opt.correct{background:var(--oksoft);color:var(--ok);font-weight:700;border-color:transparent}
    .weak-q-item .wq-meta{font-size:.7rem;color:var(--muted);margin-top:8px}
    .weak-q-item .wq-explain{margin-top:8px;padding:8px;background:rgba(79,70,229,.06);border-left:3px solid var(--brand);border-radius:6px;font-size:.8rem;color:var(--text2)}
    .pagination{display:flex;gap:5px;justify-content:center;margin:20px 0;flex-wrap:wrap}
    .page-btn{padding:8px 14px;background:var(--card);border:1px solid var(--line);border-radius:8px;font-weight:600;font-size:.85rem;color:var(--text2)}
    .page-btn:hover{border-color:var(--brand);color:var(--brand)} .page-btn.active{background:var(--brand);color:#fff;border-color:var(--brand)}
    
    /* ANALYTICS */
    .analytics-chart { display: flex; flex-direction: column; gap: 16px; margin-top: 20px; }
    .bar-row { display: flex; align-items: center; gap: 12px; }
    .bar-label { width: 80px; font-weight: 700; font-size: 0.85rem; }
    .bar-track { flex: 1; height: 24px; background: var(--sunk); border-radius: 50px; overflow: hidden; }
    .bar-fill { height: 100%; background: linear-gradient(90deg, var(--brand), var(--brand2)); border-radius: 50px; display: flex; align-items: center; justify-content: flex-end; padding-right: 8px; color: #fff; font-size: 0.7rem; font-weight: 700; transition: width 0.8s ease; width: 0; }
    
    .modal{display:none;position:fixed;inset:0;background:rgba(0,0,0,.5);justify-content:center;align-items:center;z-index:5000;padding:16px;backdrop-filter:blur(4px)}
    .modal.active{display:flex}
    .modal-content{background:var(--card);padding:28px;border-radius:var(--radius);max-width:440px;width:100%;box-shadow:var(--shadowLg);animation:popIn 0.3s ease}
    .modal-header{font-size:1.25rem;font-weight:800;margin-bottom:8px;color:var(--text)} .modal-sub{color:var(--text2);font-size:.85rem;margin-bottom:16px}
    .modal-footer{display:flex;gap:8px;margin-top:20px;justify-content:flex-end}
    .loading-overlay{position:fixed;inset:0;background:rgba(0,0,0,.5);display:none;justify-content:center;align-items:center;z-index:9999;backdrop-filter:blur(4px)}
    .loading-overlay.active{display:flex}
    .loading-box{background:var(--card);padding:32px;border-radius:16px;text-align:center;animation:popIn 0.3s ease}
    .spinner{border:4px solid var(--sunk);border-top:4px solid var(--brand);border-radius:50%;width:46px;height:46px;animation:spin 1s linear infinite;margin:0 auto 14px}
    @keyframes spin{0%{transform:rotate(0)}100%{transform:rotate(360deg)}}
    
    .export-card{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:20px}
    .export-card h3{font-size:1.1rem;margin-bottom:6px} .export-card p{color:var(--text2);font-size:.85rem;margin-bottom:16px}
    .toast{position:fixed;left:50%;bottom:80px;transform:translate(-50%,150%);padding:12px 18px;border-radius:12px;background:var(--text);color:#fff;font-weight:600;font-size:.85rem;box-shadow:var(--shadowLg);z-index:100;pointer-events:none;opacity:0;transition:.3s;max-width:calc(100% - 32px)}
    .toast.show{transform:translate(-50%,0);opacity:1} .toast.success{background:var(--ok)} .toast.error{background:var(--err)}
    #confetti{position:fixed;inset:0;pointer-events:none;z-index:99}
  </style>
</head>
<body data-theme="light">
<div class="bg-blob blob-1"></div>
<div class="bg-blob blob-2"></div>

<svg width="0" height="0" style="position:absolute">
  <defs>
    <linearGradient id="gradRing" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#4f46e5"/><stop offset="60%" stop-color="#8b5cf6"/><stop offset="100%" stop-color="#ec4899"/>
    </linearGradient>
  </defs>
</svg>

<div class="loading-overlay" id="loadingOverlay">
  <div class="loading-box"><div class="spinner"></div><p style="font-weight:600;color:var(--text2)">लोड हो रहा है...</p></div>
</div>

<div class="modal" id="passwordModal">
  <div class="modal-content">
    <div class="modal-header">🔐 Export करने के लिए Password</div>
    <p class="modal-sub">सभी questions को JSON file में download करने के लिए password दर्ज करें।</p>
    <input type="password" id="exportPassword" placeholder="Password दर्ज करें" autocomplete="off">
    <div class="modal-footer">
      <button class="btn-ghost" onclick="closePasswordModal()">Cancel</button>
      <button class="btn-primary" onclick="submitExportPassword()">Export करें</button>
    </div>
  </div>
</div>

<!-- CUSTOM TEST MODAL -->
<div class="modal" id="testConfigModal">
  <div class="modal-content">
    <div class="modal-header">⚙️ Test Setup</div>
    <p class="modal-sub">अपनी test को customize करें।</p>
    <div class="form-card" style="padding:0;gap:12px">
      <div>
        <label>Number of Questions</label>
        <select id="configLimit">
          <option value="10">10 Questions (5 min)</option>
          <option value="20" selected>20 Questions (10 min)</option>
          <option value="30">30 Questions (15 min)</option>
          <option value="50">50 Questions (25 min)</option>
        </select>
      </div>
      <div>
        <label>Mode</label>
        <select id="configMode">
          <option value="normal">Normal (All Questions)</option>
          <option value="weak">Weak Practice (Wrong Questions)</option>
          <option value="hard">Hard Drill (Repeat Wrongs)</option>
        </select>
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn-ghost" onclick="closeTestConfig()">Cancel</button>
      <button class="btn-primary" onclick="startCustomTest()">Start Test</button>
    </div>
  </div>
</div>

<header class="navbar">
  <div class="container nav-wrap">
    <a class="brand" href="#" onclick="nav('welcome');return false;"><span class="brand-dot"></span>MockTest<span style="color:var(--brand2)">.pro</span></a>
    <div class="nav-right">
      <span class="user-chip" id="userChip" hidden onclick="nav('analytics')"><span class="dot-live"></span><span id="userName"></span></span>
      <button id="themeToggle" class="icon-btn" title="Theme बदलें">
        <svg class="i-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>
        <svg class="i-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
      </button>
    </div>
  </div>
</header>

<section id="welcomeScreen" class="screen active">
  <div class="container hero">
    <div class="hero-tag"><span class="dot-live"></span> Level 99 Edition • Offline First</div>
    <h1 class="hero-title">Practice करो <span class="grad-word">smart</span>,<br/>Result देखो <span class="grad-word">instant</span>.</h1>
    <p class="hero-sub">बिना login, बिना झंझट। नाम डालो, category चुनो, और tests दो। XP कमाओ और Level 99 तक पहुँचो।</p>
    <div class="name-card">
      <label for="nameInput">तुम्हारा नाम</label>
      <div class="name-row">
        <input id="nameInput" type="text" placeholder="जैसे — Rahul Sharma" autocomplete="off">
        <button id="startBtn" class="btn-primary">Enter <svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14M13 5l7 7-7 7"/></svg></button>
      </div>
      <p class="name-hint">Name सिर्फ display के लिए है — कहीं भी upload नहीं होता।</p>
    </div>
  </div>
</section>

<section id="dashboardScreen" class="screen">
  <div class="container">
    <div class="profile-card stagger-item" style="animation-delay:0s">
      <div class="pc-left">
        <h2>नमस्ते, <span id="helloName" class="grad-word">Guest</span> 👋</h2>
        <p id="streakText">🔥 Daily Streak: 0 days</p>
      </div>
      <div class="pc-right">
        <div class="level-badge" id="dashLevel">1</div>
        <span>Level</span>
      </div>
    </div>
    
    <div class="quick-stats" id="quickStats"></div>
    
    <div class="page-head" style="margin-top:24px">
      <div><p class="eyebrow">Actions</p><h2 class="page-title">क्या करना चाहोंगे?</h2></div>
    </div>
    <div class="grid-2" id="actionGrid"></div>
    
    <div class="section-h">🕒 पिछले Attempts</div>
    <div id="recentList" class="recent-list"></div>
  </div>
</section>

<section id="analyticsScreen" class="screen">
  <div class="container">
    <div class="page-head">
      <div><p class="eyebrow">Performance</p><h2 class="page-title">Analytics 📊</h2></div>
      <button class="btn-ghost" onclick="nav('dashboard')">← Home</button>
    </div>
    <div class="form-card" id="xpCard">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <div>
          <h3 style="margin-bottom:4px">Total XP</h3>
          <p style="color:var(--text2);font-size:.85rem" id="analyticsXpText">0 XP</p>
        </div>
        <div class="level-badge" id="analyticsLevel" style="width:50px;height:50px;font-size:1.2rem">1</div>
      </div>
      <div style="margin-top:12px">
        <div style="display:flex;justify-content:space-between;font-size:.75rem;color:var(--muted);margin-bottom:4px">
          <span>Progress to Level <span id="nextLevel">2</span></span>
          <span id="xpProgressText">0/100</span>
        </div>
        <div class="tp-bar" style="max-width:none;height:8px">
          <span id="xpProgressBar" style="width:0%"></span>
        </div>
      </div>
    </div>
    
    <div class="section-h">Category-wise Accuracy</div>
    <div class="analytics-chart" id="analyticsChart"></div>
  </div>
</section>

<section id="categoriesScreen" class="screen">
  <div class="container">
    <div class="page-head"><div><p class="eyebrow">Categories</p><h2 class="page-title">विषय चुनें</h2></div><button class="btn-ghost" onclick="nav('dashboard')">← Home</button></div>
    <div class="grid-2" id="categoryGrid"></div>
  </div>
</section>

<section id="topicsScreen" class="screen">
  <div class="container">
    <div class="page-head">
      <div><p class="eyebrow" id="topicCatName"></p><h2 class="page-title">Topics</h2></div>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        <button class="btn-ghost" onclick="nav('categories')">← Back</button>
        <button class="btn-primary" id="allTopicBtn">ALL Questions</button>
      </div>
    </div>
    <div id="topicList" class="subtopic-grid"></div>
  </div>
</section>

<section id="testScreen" class="screen">
  <div class="test-topbar"><div class="container test-topwrap"><div class="tp-progress"><span id="tpNow">1</span>/<span id="tpTotal">10</span><div class="tp-bar"><span id="tpBar"></span></div></div><div class="tp-timer" id="tpTimer">⏱ 10:00</div><button id="quitTestBtn" class="btn-ghost sm">Quit</button></div></div>
  <div class="container test-body"><div id="questionCard" class="question-card"></div><div class="test-actions"><button id="prevBtn" class="btn-ghost" disabled>← Previous</button><div style="display:flex;gap:8px"><button id="nextBtn" class="btn-primary">Next →</button><button id="finishBtn" class="btn-primary hidden">Finish ✓</button></div></div></div>
</section>

<section id="resultScreen" class="screen">
  <div class="container">
    <div class="result-hero">
      <div class="result-emoji" id="resultEmoji">🎉</div>
      <h2>Test Complete!</h2>
      <p id="resultSubtitle" style="color:var(--text2)">बहुत बढ़िया कोशिश!</p>
      <div class="ring-wrap"><svg class="ring" viewBox="0 0 120 120"><circle cx="60" cy="60" r="52" class="ring-bg"></circle><circle cx="60" cy="60" r="52" class="ring-fg" id="ringFg"></circle></svg><div class="ring-center"><b id="resultPct">0%</b><span>Score</span></div></div>
      <div class="result-grid">
        <div><b id="rCorrect">0</b><span>Correct</span></div>
        <div><b id="rWrong">0</b><span>Wrong</span></div>
        <div><b id="rSkip">0</b><span>Skipped</span></div>
        <div><b id="rTime">00:00</b><span>Time</span></div>
      </div>
      <div class="result-actions">
        <button id="reviewBtn" class="btn-ghost">📖 Review Answers</button>
        <button id="retakeBtn" class="btn-primary">🔄 दोबारा दें</button>
        <button class="btn-ghost" onclick="nav('dashboard')">🏠 Dashboard</button>
      </div>
    </div>
    <div id="reviewList" class="review-list hidden"></div>
  </div>
</section>

<section id="weaklistScreen" class="screen">
  <div class="container">
    <div class="page-head">
      <div><p class="eyebrow">Weak Questions</p><h2 class="page-title">कमजोर सवाल 📚</h2></div>
      <button class="btn-ghost" onclick="nav('dashboard')">← Home</button>
    </div>
    <div id="weakListContainer"></div>
    <div class="pagination" id="weakPagination"></div>
  </div>
</section>

<section id="manageScreen" class="screen">
  <div class="container">
    <div class="page-head"><div><p class="eyebrow">Question Bank</p><h2 class="page-title">Manage करें</h2></div><button class="btn-ghost" onclick="nav('dashboard')">← Home</button></div>
    <div class="tabs">
      <button class="tab active" data-tab="bulk">📋 Bulk Import</button>
      <button class="tab" data-tab="export">📥 Export</button>
      <button class="tab" data-tab="list">📜 All (<span id="qCount">0</span>)</button>
    </div>
    <div class="tab-panel active" id="tab-bulk">
      <div class="form-card">
        <div><label>Category</label>
          <select id="bulkCategory">
            <option value="GK">GK</option><option value="Maths">Maths</option><option value="English">English</option><option value="Reasoning">Reasoning</option><option value="Science">Science</option>
          </select>
        </div>
        <div style="display:flex;align-items:center;gap:10px;padding:10px;background:var(--sunk);border-radius:10px">
          <input type="checkbox" id="autoSplit" checked style="width:auto">
          <label for="autoSplit" style="margin:0;cursor:pointer;font-weight:600">Auto‑split into tests of 20 questions</label>
        </div>
        <div><label>JSON Text</label>
          <textarea id="bulkText" rows="10" placeholder='[{"question":"...","options":["A","B","C","D"],"correct":0,"explanation":"..."}]'></textarea>
        </div>
        <div class="form-actions between">
          <button id="sampleBtn" class="btn-ghost">📄 Sample Load करें</button>
          <button id="importBtn" class="btn-primary">Import Questions</button>
        </div>
      </div>
    </div>
    <div class="tab-panel" id="tab-export">
      <div class="export-card">
        <h3>📥 सभी Questions Export करें</h3>
        <p>सभी questions को JSON format में download करें। Backup या दूसरे device पर transfer करने के लिए उपयोगी।</p>
        <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px">
          <button class="btn-primary" onclick="showPasswordModal()">📥 Export All Questions</button>
          <span style="align-self:center;color:var(--muted);font-size:.8rem">🔒 Password protected</span>
        </div>
        <div style="margin-top:14px;padding:12px;background:var(--warnsoft);border-radius:8px;font-size:.8rem;color:var(--text2)">
          💡 <b>Hint:</b> Default password app में सेट है। पूछने पर मिलेगा।
        </div>
      </div>
    </div>
    <div class="tab-panel" id="tab-list">
      <div class="list-toolbar">
        <input id="searchQ" type="search" placeholder="🔎 Search...">
        <select id="filterCat"><option value="">All Categories</option><option value="GK">GK</option><option value="Maths">Maths</option><option value="English">English</option><option value="Reasoning">Reasoning</option><option value="Science">Science</option></select>
        <button id="clearAllBtn" class="btn-danger">Clear All</button>
      </div>
      <div id="questionsList" class="questions-list"></div>
    </div>
  </div>
</section>

<nav class="bottom-nav" id="bottomNav">
  <button data-nav="dashboard"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg><span>Home</span></button>
  <button data-nav="categories"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg><span>Test</span></button>
  <button data-nav="weaklist"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg><span>Weak</span></button>
  <button data-nav="analytics"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg><span>Stats</span></button>
  <button data-nav="manage"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg><span>Manage</span></button>
</nav>

<div id="toast" class="toast"></div>
<canvas id="confetti"></canvas>

<script>
let state = { username: localStorage.getItem('mtp_user') || '', currentCategory: '', currentTopic: '', currentTest: null, timerInt: null, weakPage: 1, pendingTestConfig: null };
let audioCtx = null;

// Play sound using Web Audio API
function playSound(type) {
  try {
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.connect(gain); gain.connect(audioCtx.destination);
    if (type === 'correct') {
      osc.type = 'sine'; osc.frequency.value = 880;
      gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.15);
      osc.start(); osc.stop(audioCtx.currentTime + 0.15);
    } else if (type === 'wrong') {
      osc.type = 'square'; osc.frequency.value = 220;
      gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.3);
      osc.start(); osc.stop(audioCtx.currentTime + 0.3);
    } else if (type === 'levelup') {
      osc.type = 'sine'; osc.frequency.setValueAtTime(523, audioCtx.currentTime);
      osc.frequency.setValueAtTime(659, audioCtx.currentTime + 0.1);
      osc.frequency.setValueAtTime(784, audioCtx.currentTime + 0.2);
      gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.4);
      osc.start(); osc.stop(audioCtx.currentTime + 0.4);
    }
  } catch (e) {}
}

function vibrate(ms) { if (navigator.vibrate) navigator.vibrate(ms); }

function nav(screen) {
  if (screen === 'welcome') { history.pushState({}, '', '#welcome'); renderScreen('welcome'); return; }
  history.pushState({}, '', '#' + screen);
  renderScreen(screen);
}
window.addEventListener('popstate', () => {
  const hash = window.location.hash.replace('#', '') || 'welcome';
  renderScreen(hash);
});

function renderScreen(screenId) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  const map = { welcome:'welcomeScreen', dashboard:'dashboardScreen', categories:'categoriesScreen', topics:'topicsScreen', test:'testScreen', result:'resultScreen', manage:'manageScreen', weaklist:'weaklistScreen', analytics:'analyticsScreen' };
  const el = document.getElementById(map[screenId]);
  if (el) el.classList.add('active');
  if (screenId === 'dashboard') renderDashboard();
  if (screenId === 'categories') renderCategories();
  if (screenId === 'manage') renderManage();
  if (screenId === 'weaklist') loadWeakList(1);
  if (screenId === 'analytics') renderAnalytics();
  document.querySelectorAll('.bottom-nav button').forEach(b => b.classList.remove('active'));
  const activeBtn = document.querySelector(`.bottom-nav button[data-nav="${screenId}"]`);
  if (activeBtn) activeBtn.classList.add('active');
  window.scrollTo(0,0);
}
document.querySelectorAll('.bottom-nav button').forEach(b => b.addEventListener('click', () => nav(b.dataset.nav)));

let toastTimer;
function toast(msg, type=''){ const t = document.getElementById('toast'); t.className = 'toast show '+type; t.textContent = msg; clearTimeout(toastTimer); toastTimer = setTimeout(() => t.classList.remove('show'), 2600); }

function applyTheme(t){ document.body.setAttribute('data-theme', t); localStorage.setItem('mtp_theme', t); }
document.getElementById('themeToggle').addEventListener('click', () => applyTheme(document.body.getAttribute('data-theme') === 'light' ? 'dark' : 'light'));
applyTheme(localStorage.getItem('mtp_theme') || (window.matchMedia('(prefers-color-scheme:dark)').matches ? 'dark' : 'light'));

function showLoading(show) { document.getElementById('loadingOverlay').classList.toggle('active', show); }

document.addEventListener('DOMContentLoaded', () => {
  const startBtn = document.getElementById('startBtn');
  const nameInput = document.getElementById('nameInput');
  if (startBtn && nameInput) {
    const enterApp = () => {
      const val = nameInput.value.trim();
      if (!val) { toast('कृपया अपना नाम डालें','error'); return; }
      state.username = val; localStorage.setItem('mtp_user', val);
      document.getElementById('userChip').hidden = false; document.getElementById('userName').textContent = val;
      nav('dashboard');
    };
    startBtn.addEventListener('click', enterApp);
    nameInput.addEventListener('keypress', e => { if (e.key === 'Enter') { e.preventDefault(); enterApp(); } });
  }
  if (state.username) { document.getElementById('userChip').hidden = false; document.getElementById('userName').textContent = state.username; renderScreen(window.location.hash.replace('#','') || 'dashboard'); }
});

async function renderDashboard() {
  document.getElementById('helloName').textContent = state.username || 'Guest';
  try {
    const stats = await (await fetch(`/api/stats?username=${state.username}`)).json();
    document.getElementById('dashLevel').textContent = stats.level;
    document.getElementById('streakText').textContent = `🔥 Daily Streak: ${stats.streak} days`;
    document.getElementById('quickStats').innerHTML = `
      <div class="stat stagger-item" style="animation-delay:0.05s"><b>${stats.total_questions}</b><span>Questions</span></div>
      <div class="stat stagger-item" style="animation-delay:0.1s"><b>${stats.total_tests}</b><span>Tests</span></div>
      <div class="stat stagger-item" style="animation-delay:0.15s"><b>${stats.avg_pct}%</b><span>Average</span></div>
      <div class="stat stagger-item" style="animation-delay:0.2s"><b>${stats.weak_count}</b><span>Weak</span></div>
    `;
  } catch (e) {}
  
  const grid = document.getElementById('actionGrid');
  grid.innerHTML = `
    <button class="action-card stagger-item" style="animation-delay:0.25s" onclick="nav('categories')"><div class="ac-icon g1">🎯</div><h3>Test शुरू करें</h3><p>Category और topic चुनो।</p><span class="ac-arrow">→</span></button>
    <button class="action-card stagger-item" style="animation-delay:0.3s" onclick="openTestConfig('weak')"><div class="ac-icon g4">🔥</div><h3>Weak Practice</h3><p>कभी भी गलत हुए सवाल।</p><span class="ac-arrow">→</span></button>
    <button class="action-card stagger-item" style="animation-delay:0.35s" onclick="openTestConfig('hard')"><div class="ac-icon g5">💪</div><h3>Hard Drill</h3><p>बार‑बार गलत सवाल।</p><span class="ac-arrow">→</span></button>
    <button class="action-card stagger-item" style="animation-delay:0.4s" onclick="nav('weaklist')"><div class="ac-icon g3">📚</div><h3>Weak Questions</h3><p>सभी कमजोर सवाल देखें।</p><span class="ac-arrow">→</span></button>
    <button class="action-card stagger-item" style="animation-delay:0.45s" onclick="nav('analytics')"><div class="ac-icon g6">📊</div><h3>Analytics</h3><p>Performance देखें।</p><span class="ac-arrow">→</span></button>
    <button class="action-card stagger-item" style="animation-delay:0.5s" onclick="nav('manage')"><div class="ac-icon g2">➕</div><h3>Question जोड़ें</h3><p>Bulk JSON Import।</p><span class="ac-arrow">→</span></button>
  `;
  
  const rl = document.getElementById('recentList');
  rl.innerHTML = '<div class="skeleton-card"></div><div class="skeleton-card"></div>';
  try {
    const res = await (await fetch(`/api/results?username=${state.username}`)).json();
    if (res.length === 0) { rl.innerHTML = '<div class="empty">अभी तक कोई test नहीं दिया।</div>'; } 
    else {
      rl.innerHTML = res.map((r, i) => `
        <div class="recent-item stagger-item" style="animation-delay:${0.5 + i*0.05}s">
          <div class="ri-left">
            <div class="ri-badge ${r.pct>=70?'ok':r.pct>=40?'avg':'bad'}">${Math.round(r.pct)}%</div>
            <div><h5>${escapeHtml(r.category)} · ${escapeHtml(r.topic||r.mode)}</h5><small>${new Date(r.date).toLocaleString('hi-IN')}</small></div>
          </div>
          <div><b>${r.correct}/${r.total}</b></div>
        </div>
      `).join('');
    }
  } catch (e) { rl.innerHTML = '<div class="empty">Data load error.</div>'; }
}

function renderCategories() {
  const grid = document.getElementById('categoryGrid');
  const cats = ["GK","Maths","English","Reasoning","Science"];
  const icons = ["🌍","🔢","🇬🇧","🧩","🔬"];
  grid.innerHTML = cats.map((cat,i) => `
    <button class="action-card stagger-item" style="animation-delay:${i*0.05}s" onclick="openCategory('${cat}')">
      <div class="ac-icon g${i+1}">${icons[i]}</div>
      <h3>${cat}</h3><p>Tap to view topics</p><span class="ac-arrow">→</span>
    </button>
  `).join('');
}

function openCategory(cat) {
  state.currentCategory = cat;
  nav('topics');
  document.getElementById('topicCatName').textContent = cat;
  const list = document.getElementById('topicList');
  list.innerHTML = '<div class="skeleton-card"></div><div class="skeleton-card"></div><div class="skeleton-card"></div><div class="skeleton-card"></div>';
  renderTopics(cat);
}

async function renderTopics(cat) {
  try {
    const res = await fetch(`/api/topics?category=${cat}`);
    const topics = await res.json();
    const list = document.getElementById('topicList');
    if (topics.length === 0) {
      list.innerHTML = '<div class="empty">इस category में कोई topic नहीं।</div>';
    } else {
      list.innerHTML = topics.map((t, i) => `
        <button class="subtopic-tile stagger-item" style="animation-delay:${i*0.05}s" onclick="openTestConfig('normal', '${escapeAttr(cat)}', '${escapeAttr(t.name)}')">
          <h4>${escapeHtml(t.name)}</h4><span>${t.count} questions</span>
        </button>
      `).join('');
    }
  } catch (e) {
    document.getElementById('topicList').innerHTML = '<div class="empty">Topics लोड नहीं हो सके।</div>';
  }
  document.getElementById('allTopicBtn').onclick = () => openTestConfig('all', cat, '');
}

function openTestConfig(mode, cat=null, topic=null) {
  state.pendingTestConfig = { mode, cat, topic };
  document.getElementById('testConfigModal').classList.add('active');
  const modeSelect = document.getElementById('configMode');
  
  if (mode === 'normal' || mode === 'all') {
    modeSelect.value = 'normal';
    modeSelect.disabled = true;
  } else {
    modeSelect.value = mode;
    modeSelect.disabled = false;
  }
}
function closeTestConfig() { document.getElementById('testConfigModal').classList.remove('active'); state.pendingTestConfig = null; }
function startCustomTest() {
  const config = state.pendingTestConfig;
  const limit = parseInt(document.getElementById('configLimit').value);
  const mode = document.getElementById('configMode').value;
  closeTestConfig();
  startTest(config.cat, config.topic, mode, limit);
}

async function startTest(cat, topic, mode, limit=20) {
  showLoading(true);
  const body = { username: state.username, category: cat, topic: topic, mode: mode, limit: limit };
  try {
    const res = await fetch('/api/start-test', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body) });
    const data = await res.json();
    if (!res.ok) { toast(data.error || 'Error','error'); return; }
    state.currentTest = { questions: data.questions, answers: new Array(data.questions.length).fill(null), currentIdx: 0, startTime: Date.now(), duration: data.timer_min * 60, mode: data.mode, category: cat || 'Mixed', topic: topic || '' };
    nav('test');
    renderTestQuestion();
    if (data.timer_min > 0) startTimer(data.timer_min * 60);
  } catch (e) { toast('कुछ गलत हुआ','error'); } finally { showLoading(false); }
}
function startTimer(totalSec) {
  clearInterval(state.timerInt);
  state.timerInt = setInterval(() => {
    const passed = Math.floor((Date.now() - state.currentTest.startTime)/1000);
    const left = Math.max(0, totalSec - passed);
    const m = String(Math.floor(left/60)).padStart(2,'0'), s = String(left%60).padStart(2,'0');
    document.getElementById('tpTimer').textContent = `⏱ ${m}:${s}`;
    const timerEl = document.getElementById('tpTimer');
    if (left <= 30) timerEl.classList.add('warn'); else timerEl.classList.remove('warn');
    if (left <= 0) { clearInterval(state.timerInt); submitTest(true); }
  }, 500);
}
function renderTestQuestion() {
  const t = state.currentTest;
  if (!t) return;
  const q = t.questions[t.currentIdx];
  document.getElementById('tpNow').textContent = t.currentIdx + 1;
  document.getElementById('tpTotal').textContent = t.questions.length;
  document.getElementById('tpBar').style.width = ((t.currentIdx+1)/t.questions.length*100)+'%';
  const answered = t.answers[t.currentIdx];
  const card = document.getElementById('questionCard');
  card.innerHTML = `
    <span class="q-cat-top">${escapeHtml(q.category)} · ${escapeHtml(q.topic)}</span>
    <h3 class="q-text-lg">${escapeHtml(q.question)}</h3>
    <div class="opt-list">
      ${q.options.map((op,i)=>`<button class="opt ${answered!==null ? (i===q.correct?'correct': (i===answered?'wrong':'')) : ''}" data-i="${i}" ${answered!==null?'disabled':''}><span class="kbd">${String.fromCharCode(65+i)}</span><span>${escapeHtml(op)}</span></button>`).join('')}
    </div>
    ${answered!==null && q.explanation ? `<div class="explanation"><b>💡 Explanation:</b> ${escapeHtml(q.explanation)}</div>` : ''}`;
  card.classList.remove('q-card-animate');
  void card.offsetWidth;
  card.classList.add('q-card-animate');
  
  card.querySelectorAll('.opt').forEach(b => b.addEventListener('click', () => {
    if (state.currentTest.answers[state.currentTest.currentIdx] !== null) return;
    const chosen = parseInt(b.dataset.i);
    state.currentTest.answers[state.currentTest.currentIdx] = chosen;
    
    if (chosen === q.correct) { playSound('correct'); vibrate(50); }
    else { playSound('wrong'); vibrate([50, 50, 50]); }
    
    renderTestQuestion();
  }));
  document.getElementById('prevBtn').disabled = t.currentIdx === 0;
  const last = t.currentIdx === t.questions.length-1;
  document.getElementById('nextBtn').classList.toggle('hidden', last);
  document.getElementById('finishBtn').classList.toggle('hidden', !last);
}

document.addEventListener('keydown', (e) => {
  if (!state.currentTest || !document.getElementById('testScreen').classList.contains('active')) return;
  if (state.currentTest.answers[state.currentTest.currentIdx] === null) {
    if (['1','2','3','4'].includes(e.key)) {
      e.preventDefault();
      const idx = parseInt(e.key) - 1;
      document.querySelector(`.opt[data-i="${idx}"]`)?.click();
    }
  } else {
    if (e.key.toLowerCase() === 'n' || e.key === 'Enter') {
      e.preventDefault();
      if (!document.getElementById('nextBtn').classList.contains('hidden')) document.getElementById('nextBtn').click();
      else if (!document.getElementById('finishBtn').classList.contains('hidden')) document.getElementById('finishBtn').click();
    } else if (e.key.toLowerCase() === 'p' || e.key === 'Backspace') {
      e.preventDefault();
      if (!document.getElementById('prevBtn').disabled) document.getElementById('prevBtn').click();
    }
  }
});

document.getElementById('prevBtn').addEventListener('click', ()=>{ if (state.currentTest.currentIdx > 0) { state.currentTest.currentIdx--; renderTestQuestion(); } });
document.getElementById('nextBtn').addEventListener('click', ()=>{ if (state.currentTest.currentIdx < state.currentTest.questions.length-1) { state.currentTest.currentIdx++; renderTestQuestion(); } });
document.getElementById('finishBtn').addEventListener('click', ()=> submitTest(false));
document.getElementById('quitTestBtn').addEventListener('click', ()=>{ if (confirm('Test छोड़ना है? Progress save नहीं होगा।')) { clearInterval(state.timerInt); nav('dashboard'); } });

async function submitTest(timeUp) {
  clearInterval(state.timerInt);
  const t = state.currentTest;
  const answers = t.questions.map((q,i) => ({question_id: q.id, selected: t.answers[i]}));
  const timeSec = Math.floor((Date.now() - t.startTime)/1000);
  showLoading(true);
  try {
    const res = await fetch('/api/submit-test', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ username: state.username, answers, time_sec: timeSec, category: t.category, topic: t.topic, mode: t.mode }) });
    const data = await res.json();
    document.getElementById('rCorrect').textContent = data.correct;
    document.getElementById('rWrong').textContent = data.wrong;
    document.getElementById('rSkip').textContent = data.skipped;
    document.getElementById('rTime').textContent = `${String(Math.floor(timeSec/60)).padStart(2,'0')}:${String(timeSec%60).padStart(2,'0')}`;
    document.getElementById('resultPct').textContent = data.pct+'%';
    const emoji = data.pct>=90?'🏆':data.pct>=70?'🎉':data.pct>=50?'👍':'📚';
    document.getElementById('resultEmoji').textContent = emoji;
    document.getElementById('resultSubtitle').textContent = (data.pct>=90?'शानदार!':data.pct>=70?'बहुत बढ़िया!':data.pct>=50?'अच्छा किया!':'कोशिश जारी रखो!') + (timeUp?' (समय पूरा)':'');
    const circum = 2*Math.PI*52;
    const ring = document.getElementById('ringFg');
    ring.style.strokeDasharray = circum; ring.style.strokeDashoffset = circum;
    nav('result');
    setTimeout(()=>{ ring.style.strokeDashoffset = circum - (circum*data.pct/100); }, 100);
    if (data.pct >= 70) { fireConfetti(); playSound('levelup'); vibrate(100); }
    
    if (data.xp_earned > 0) {
      const popup = document.createElement('div');
      popup.className = 'xp-popup';
      popup.innerHTML = `+${data.xp_earned} XP`;
      document.body.appendChild(popup);
      setTimeout(() => popup.remove(), 2500);
    }
    
    const rl = document.getElementById('reviewList');
    rl.classList.add('hidden');
    rl.innerHTML = t.questions.map((q,i)=>{
      const ans = t.answers[i]; const status = ans===null?'sk': ans===q.correct?'ok':'no'; const label = status==='ok'?'Correct': status==='no'?'Wrong':'Skipped';
      return `<div class="review-card"><div style="display:flex;justify-content:space-between;align-items:center"><span class="q-cat-top">${escapeHtml(q.category)} · ${escapeHtml(q.topic)} Q${i+1}</span><span class="rc-status ${status}">${label}</span></div><p class="rc-q">${escapeHtml(q.question)}</p><div class="rc-opts">${q.options.map((op,j)=>{ let cls=''; if(j===q.correct) cls='correct'; else if(j===ans && ans!==q.correct) cls='wrong'; return `<div class="rc-opt ${cls}"><span style="font-weight:800;width:22px">${String.fromCharCode(65+j)}.</span> ${escapeHtml(op)}</div>`; }).join('')}</div>${q.explanation?`<div class="rc-explain"><b>💡 Explanation:</b> ${escapeHtml(q.explanation)}</div>`:''}</div>`;
    }).join('');
  } catch (e) { toast('Submit में error','error'); } finally { showLoading(false); }
}
document.getElementById('reviewBtn').addEventListener('click', ()=>{ const rl = document.getElementById('reviewList'); rl.classList.toggle('hidden'); if (!rl.classList.contains('hidden')) rl.scrollIntoView({behavior:'smooth',block:'start'}); });
document.getElementById('retakeBtn').addEventListener('click', ()=> { const t = state.currentTest; if (t.mode === 'normal' || t.mode === 'all') nav('topics'); else openTestConfig(t.mode); });

async function loadWeakList(page) {
  state.weakPage = page;
  const container = document.getElementById('weakListContainer');
  const pagination = document.getElementById('weakPagination');
  container.innerHTML = '<div class="skeleton-card"></div><div class="skeleton-card"></div>';
  pagination.innerHTML = '';
  try {
    const res = await fetch(`/api/weak-questions/${state.username}?page=${page}`);
    const data = await res.json();
    if (data.weak_questions.length === 0) { container.innerHTML = '<div class="empty">🎉 कोई कमजोर question नहीं! बहुत बढ़िया!</div>'; return; }
    container.innerHTML = data.weak_questions.map((w, i) => `
      <div class="weak-q-item stagger-item" style="animation-delay:${i*0.05}s">
        <div class="wq-head"><div class="wq-q">${escapeHtml(w.question)}</div><span class="weak-count">❌ ${w.wrong_count}x</span></div>
        <div><span class="q-cat-top">${escapeHtml(w.category)} · ${escapeHtml(w.topic)}</span></div>
        <div class="wq-opts">${w.options.map((opt,idx)=>`<div class="wq-opt ${idx===w.correct?'correct':''}"><strong>${String.fromCharCode(65+idx)}.</strong> ${escapeHtml(opt)}</div>`).join('')}</div>
        ${w.explanation?`<div class="wq-explain"><b>💡 Explanation:</b> ${escapeHtml(w.explanation)}</div>`:''}
        <div class="wq-meta">Last attempt: ${w.last_wrong?new Date(w.last_wrong).toLocaleString('hi-IN'):'N/A'}</div>
      </div>
    `).join('');
    let phtml = '';
    for (let i=1; i<=data.total_pages; i++) phtml += `<button class="page-btn ${i===page?'active':''}" onclick="loadWeakList(${i})">${i}</button>`;
    pagination.innerHTML = phtml;
  } catch (e) { container.innerHTML = '<div class="empty">Load error.</div>'; }
}

async function renderAnalytics() {
  try {
    const stats = await (await fetch(`/api/stats?username=${state.username}`)).json();
    document.getElementById('analyticsLevel').textContent = stats.level;
    document.getElementById('analyticsXpText').textContent = `${stats.xp} XP`;
    const nextLevel = stats.level + 1;
    const xpInCurrentLevel = stats.xp % 100;
    document.getElementById('nextLevel').textContent = nextLevel;
    document.getElementById('xpProgressText').textContent = `${xpInCurrentLevel}/100`;
    document.getElementById('xpProgressBar').style.width = `${xpInCurrentLevel}%`;
  } catch (e) {}
  
  const chart = document.getElementById('analyticsChart');
  chart.innerHTML = '<div class="skeleton-card"></div>';
  try {
    const res = await (await fetch(`/api/analytics?username=${state.username}`)).json();
    if (res.length === 0) { chart.innerHTML = '<div class="empty">अभी analytics उपलब्ध नहीं हैं। पहले कुछ tests दें।</div>'; return; }
    chart.innerHTML = res.map((c, i) => `
      <div class="bar-row stagger-item" style="animation-delay:${i*0.1}s">
        <div class="bar-label">${escapeHtml(c.category)}</div>
        <div class="bar-track"><div class="bar-fill" style="width:0%" data-target="${c.accuracy}">${c.accuracy}%</div></div>
      </div>
    `).join('');
    setTimeout(() => {
      document.querySelectorAll('.bar-fill').forEach(b => {
        b.style.width = b.dataset.target + '%';
      });
    }, 100);
  } catch (e) { chart.innerHTML = '<div class="empty">Error loading analytics.</div>'; }
}

function switchTab(tabName) {
  document.querySelectorAll('.tab').forEach(x => x.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(x => x.classList.remove('active'));
  const tab = document.querySelector(`.tab[data-tab="${tabName}"]`);
  if (tab) tab.classList.add('active');
  const panel = document.getElementById('tab-'+tabName);
  if (panel) panel.classList.add('active');
}
document.querySelectorAll('.tab').forEach(t => t.addEventListener('click', ()=> switchTab(t.dataset.tab)));

document.getElementById('importBtn').addEventListener('click', async () => {
  const category = document.getElementById('bulkCategory').value;
  const autoSplit = document.getElementById('autoSplit').checked;
  const raw = document.getElementById('bulkText').value.trim();
  if (!raw) { toast('JSON खाली है','error'); return; }
  try {
    const arr = JSON.parse(raw);
    if (!Array.isArray(arr)) throw new Error();
    const res = await fetch('/api/import-questions', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ category, auto_split: autoSplit, questions: arr }) });
    const data = await res.json();
    if (!res.ok) { toast(data.error || 'Error','error'); return; }
    toast(`${data.added} questions import हो गए ✓`,'success');
    document.getElementById('bulkText').value = '';
    renderManage();
  } catch (e) { toast('Invalid JSON format','error'); }
});
document.getElementById('sampleBtn').addEventListener('click', ()=>{
  document.getElementById('bulkText').value = JSON.stringify([{"question":"Sample Q1?","options":["A","B","C","D"],"correct":0,"explanation":"Sample explanation."},{"question":"Sample Q2?","options":["A","B","C","D"],"correct":1,"explanation":"Another sample."}], null, 2);
});
document.getElementById('clearAllBtn').addEventListener('click', async ()=>{ if (!confirm('पूरा question bank delete कर दें? यह action undo नहीं हो सकता।')) return; await fetch('/api/clear-all', { method:'DELETE' }); renderManage(); toast('All questions deleted','success'); });

async function renderManage() {
  try {
    const res = await fetch('/api/questions');
    const qs = await res.json();
    document.getElementById('qCount').textContent = qs.length;
    const list = document.getElementById('questionsList');
    const q = (document.getElementById('searchQ').value||'').toLowerCase(), fc = document.getElementById('filterCat').value;
    const filtered = qs.filter(x => (!fc || x.category === fc) && (!q || x.question.toLowerCase().includes(q)));
    list.innerHTML = filtered.length ? filtered.map((x, i) => `<div class="q-row stagger-item" style="animation-delay:${i*0.02}s"><div style="flex:1"><span class="q-cat">${escapeHtml(x.category)} · ${escapeHtml(x.topic)}</span><p class="q-text">${escapeHtml(x.question)}</p><div class="q-ans">✓ ${String.fromCharCode(65+x.correct)}. ${escapeHtml(x.options[x.correct])}</div></div><button class="del" onclick="delQ(${x.id})">Delete</button></div>`).join('') : '<div class="empty">कोई question नहीं मिला।</div>';
  } catch (e) {}
}
async function delQ(id) { await fetch(`/api/questions/${id}`, { method:'DELETE' }); renderManage(); toast('Question deleted','success'); }

function showPasswordModal() { document.getElementById('passwordModal').classList.add('active'); setTimeout(()=>document.getElementById('exportPassword').focus(), 100); }
function closePasswordModal() { document.getElementById('passwordModal').classList.remove('active'); document.getElementById('exportPassword').value = ''; }
document.getElementById('exportPassword').addEventListener('keypress', e => { if (e.key === 'Enter') { e.preventDefault(); submitExportPassword(); } });
async function submitExportPassword() {
  const password = document.getElementById('exportPassword').value;
  if (!password) { toast('Password दर्ज करें','error'); return; }
  showLoading(true);
  try {
    const res = await fetch('/api/export-all', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ password }) });
    if (!res.ok) { const data = await res.json().catch(()=>({})); toast(data.error || 'गलत password!','error'); return; }
    const blob = await res.blob(); const url = window.URL.createObjectURL(blob); const a = document.createElement('a');
    a.href = url; a.download = `questions_export_${new Date().getTime()}.json`; document.body.appendChild(a); a.click();
    window.URL.revokeObjectURL(url); document.body.removeChild(a);
    toast('Export सफल! ✓','success'); closePasswordModal();
  } catch (e) { toast('Export में error','error'); } finally { showLoading(false); }
}

const canvas = document.getElementById('confetti'), ctx = canvas.getContext('2d');
function resizeC(){ canvas.width = innerWidth; canvas.height = innerHeight; }
window.addEventListener('resize', resizeC); resizeC();
function fireConfetti(){
  const colors = ['#4f46e5','#8b5cf6','#ec4899','#f59e0b','#10b981','#06b6d4']; const pieces = [];
  for (let i=0;i<140;i++) pieces.push({x:innerWidth/2+(Math.random()-0.5)*200,y:innerHeight/3,vx:(Math.random()-0.5)*10,vy:Math.random()*-14-4,g:0.35,s:Math.random()*8+4,c:colors[Math.floor(Math.random()*colors.length)],r:Math.random()*Math.PI,vr:(Math.random()-0.5)*0.3});
  let frames=0;
  function loop(){ ctx.clearRect(0,0,canvas.width,canvas.height); pieces.forEach(p=>{p.vy+=p.g;p.x+=p.vx;p.y+=p.vy;p.r+=p.vr;ctx.save();ctx.translate(p.x,p.y);ctx.rotate(p.r);ctx.fillStyle=p.c;ctx.fillRect(-p.s/2,-p.s/2,p.s,p.s*0.6);ctx.restore();}); frames++; if(frames<180) requestAnimationFrame(loop); else ctx.clearRect(0,0,canvas.width,canvas.height); }
  loop();
}

function escapeHtml(s){ return String(s??'').replace(/[&<>"']/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
function escapeAttr(s){ return String(s??'').replace(/'/g,"\\\\'"); }
document.getElementById('passwordModal').addEventListener('click', e => { if (e.target.id === 'passwordModal') closePasswordModal(); });
document.getElementById('testConfigModal').addEventListener('click', e => { if (e.target.id === 'testConfigModal') closeTestConfig(); });
</script>
</body>
</html>'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)