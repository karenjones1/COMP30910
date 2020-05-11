# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 16:08:22 2020

@author: karjo
"""

from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, url_for, abort
from wtforms import Form, PasswordField, StringField, validators
from flask_sqlalchemy import SQLAlchemy
import os, time
from werkzeug.security import generate_password_hash, check_password_hash
import requests, json


app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:B@nj0@localhost/Recommender'
db = SQLAlchemy(app)

#Returns 'Home' HTML page and creates user session variable
@app.route('/home', methods=['GET', 'POST'])
def main():
    if 'username' in session:
      username = session['username']
      return render_template('home.html', username = username + ',')
    else:
        return render_template('home.html')
    

#Returns 'Login' HTML page and checks if login details are correct
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    
    if request.method == 'POST':
        
        name = request.form['username']
        password = request.form['password']

        Username = User.query.filter_by(username=name).first()
        print("password: " + Username.password)
        
        session['username'] = request.form['username']
        
    
        if not Username or not check_password_hash(Username.password, password):
            error = 'Invalid credentials'
            return render_template('login.html', error=error)
        else:
            return redirect(url_for('main'))

    else:
        return render_template('login.html')


@app.route('/postjson', methods=['GET', 'POST'])
def getLocation():
    if 'username' in session:
    
        startLocation = requests.get('http://open.mapquestapi.com/geocoding/v1/address?key=bgfRX1pCkKZgL7Tx03A0Hvh4AGRO4Jsk&location={loc1},Ireland'.format(loc1 = request.form['traveldestination']))
        endLocation = requests.get('http://open.mapquestapi.com/geocoding/v1/address?key=bgfRX1pCkKZgL7Tx03A0Hvh4AGRO4Jsk&location={loc2},Ireland'.format(loc2 = request.form['traveldestinationend']))
        data = json.loads(startLocation.text) # change json into python dict
        data2 = json.loads(endLocation.text)
        place_coord = data['results'][0]['locations'][0]['latLng']
        place_coord2 = data2['results'][0]['locations'][0]['latLng']
        print(place_coord)
        print(place_coord2)
        form_days = request.form['durationofstay']
        
        #Return error if all details not entered       
        if not request.form['traveldestination'] or not request.form['traveldestinationend'] or not request.form['durationofstay']:
            username = session['username']
            details_error = 'You must enter in all travel destination details'
            return render_template('home.html', details_error = details_error, username = username + ',')
        num_days = int(form_days)
        session['num_days'] = num_days
        
       #call function to do calculations if latitude of start destination is greater than latitude of end destination.
       #i.e. if start destiantion = Donegal, end destination = Cork
        if(place_coord['lat'] > place_coord2['lat']):
            direction = 'route'
            line = 'geom_type'
            displayRoute = calculateRecommendations(place_coord,place_coord2,direction,line,num_days)
            return displayRoute
        #call function to do calculations if latitude of start destination is less than latitude of end destination.
        #i.e. if start destiantion = Cork, end destination = Donegal
        else:
            direction = 'route_reverse'
            line = 'reverseline'
            displayRouteReverse = calculateRecommendations(place_coord,place_coord2,direction,line,num_days)
            return displayRouteReverse
    else:
        error = 'You must log in first'
        return render_template('home.html', error = error)
  
    
def calculateRecommendations(place_coord,place_coord2,direction,line, num_days):            
            #Finds closest point on line from entered coord 
            result = db.engine.execute("SELECT * FROM (SELECT ST_GeomFromText(ST_AsText(ST_ClosestPoint({line},'POINT({long} {lat})')))\
                                        FROM {direction}) as line".format(lat =place_coord['lat'], long = place_coord['lng'], line =line, direction = direction))
            
            
            result2 = db.engine.execute("SELECT * FROM (SELECT ST_GeomFromText(ST_AsText(ST_ClosestPoint({line},('POINT({lngend} {latend})'))))\
                                        FROM {direction})as line1".format(latend = place_coord2['lat'], lngend =place_coord2['lng'], line =line, direction = direction ))
            
            session['currentCount'] = 0
            location1= None
            for item in result:
                location1 = item
            location1 = location1[0]
           
            location2= None
            for item2 in result2:
                location2 = item2
            location2 = location2[0]
                
            print(location1)
            print(location2)
             
            #Finds line segment from entered start and end destination
            segment  = db.engine.execute("WITH road AS (SELECT \
                                                St_GeomFromText(ST_AsText(Geometry((select {line} from public.\"{direction}\")))) AS geom,\
                                                least(St_GeomFromText(ST_AsText(Geometry('{loc1}')))) AS point1,\
                                                greatest(St_GeomFromText(ST_AsText(Geometry('{loc2}')))) AS point2)\
                            SELECT ST_LineSubstring(geom,  ST_LineLocatePoint(geom, point2),  ST_LineLocatePoint(geom, point1)) FROM road;".format(loc1 = location1, loc2 = location2, direction = direction, line=line))
           
            
            line_seg= None
            for item_seg in segment:
               line_seg = item_seg
            line_seg = line_seg[0]
                
        #If the user has not checked any checkboxes(activities), see if they have any previously rated items in their profile
            if not check:
                profileValues = []
                profileValues = UserProfileSelection()
                array = profileValues 
                        
            else:
                    array = check
            
            var = "select * from attractions,{direction} where ST_DWITHIN(Geography('{seg}'), ST_MakePoint(attractions.longitude, attractions.latitude),10000)"
            print(len(array))
            if not array:
                km_attr = db.engine.execute(var.format(seg=line_seg, direction = direction))
            else:
                for i in range (len(array)):
                 if i == 0:
                     var = (var + " AND (\"typeAttr\" = '" + array[i] + "'")
                 else:
                     var = (var + " OR \"typeAttr\" = '" + array[i] + "'")
                 if i == len(array):
                     var = var + ")"
                print(var)
                var = var + ")"
                print(var)
                km_attr = db.engine.execute(var.format(seg=line_seg, direction = direction))
            
            
            #activities
            var = "select * from activities,{direction} where ST_DWITHIN(Geography('{seg}'), ST_MakePoint(activities.longitude, activities.latitude),10000)"
            print(len(array))
            if not array:
                km_activ = db.engine.execute(var.format(seg=line_seg, direction = direction))
            else:
                for i in range (len(array)):
                 if i == 0:
                     var = (var + " AND (\"typeAttr\" = '" + array[i] + "'")
                 else:
                     var = (var + " OR \"typeAttr\" = '" + array[i] + "'")
                 if i == len(array):
                     var = var + ")"
                print(var)
                var = var + ")"
                print(var)
                km_activ = db.engine.execute(var.format(seg=line_seg,direction = direction))
                
            
            #accomodation
            accom = ['Hotel', 'BedAndBreakfast', 'Campground', 'LodgingBusiness']
            matches = []
            for i in array:
                if i in accom and i in array:
                    matches.append(i)
            print("matches: ")
            print(matches)
            var = "select * from accomodation,{direction} where ST_DWITHIN(Geography('{seg}'), ST_MakePoint(accomodation.longitude, accomodation.latitude),10000)"
            print(len(matches))
            if not matches:
                km_accom = db.engine.execute(var.format(seg=line_seg, direction = direction))
            else:
                for i in range (len(matches)):
                 if i == 0:
                     var = (var + " AND (\"typeAttr\" = '" + matches[i] + "'")
                 else:
                     var = (var + " OR \"typeAttr\" = '" + matches[i] + "'")
                 if i == len(array):
                     var = var + ")"
                print(var)
                var = var + ")"
                print(var)
                km_accom = db.engine.execute(var.format(seg=line_seg, direction = direction))
                accomItems = [r for r in km_accom]
                import random
                if (len(accomItems) > num_days):
                    sample_accom = random.sample(accomItems , k=num_days)
                    # sort attractions based on closest point to start and end point
                    sort_accom = sorted(sample_accom, key=lambda desc: desc[3], reverse=True)
                    print(sort_accom)
                    len_sample = len(sort_accom)
                    loc_list_accom = []
                    for i in range (len_sample):
                        loc_list_accom.append({"lat": sort_accom[i][4],
                                         "lng": sort_accom[i][3],
                                         "name":sort_accom[i][0]
                                })
                else:
                    # sort attractions based on closest point to start and end point
                    sort_accom = sorted(accomItems, key=lambda desc: desc[3], reverse=True)
                    print(sort_accom)
                    len_sample = len(sort_accom)
                    loc_list_accom = []
                    for i in range (len_sample):
                        loc_list_accom.append({"lat": sort_accom[i][4],
                                         "lng": sort_accom[i][3],
                                         "name":sort_accom[i][0]
                                })
      
            # puts the results into an array
            answer = [r for r in km_activ] + [r for r in km_attr] #+ [r for r in km_accom]
            print(answer)
            print(len(answer))
            
            if (len(answer) >= num_days*2):
                #get random sample of attractions based on user inputted value
                import random
                rdm_sample = random.sample(answer , k=num_days*2)
                print(rdm_sample)
            
                # sort attractions based on closest point to start and end point
                sort_desc = sorted(rdm_sample, key=lambda desc: desc[3], reverse=True) 
                
                #Create key,value for markers on map
                loc_list = loclist(sort_desc, answer)
                
                #creates an array of arrays to make tables(2 rows for each table)
                test = []
                i =0
                for j in range(num_days):
                    day = []
                    for k in range(2):
                        day.append(sort_desc[i])
                        i = i + 1
                    test.append(day)
                if not matches:          
                    return render_template('recommendations.html', Location = test, len_days = num_days, loc_list = loc_list)
                else:
                    return render_template('recommendations.html', Location = test, len_days = num_days, loc_list = loc_list, km_accom = sort_accom, loc_list_accom = loc_list_accom)
            else:
                sort_desc = sorted(answer, key=lambda desc: desc[3], reverse=True) #Sorts attractions by latitude in descending order
    
                #Create key,value for markers on map
                loc_list = loclist(sort_desc, answer)
                
                test = []
                i = 0
                for j in range(num_days):
                    day = []
                    for k in range(2):
                        try:
                            sort_desc[i]
                            day.append(sort_desc[i])
                            i = i + 1
                        except:
                            print("fall out of loop")
                    test.append(day)
                if not matches: 
                    return render_template('recommendations.html', Location = test, len_days = num_days,  loc_list = loc_list)
                else:
                    return render_template('recommendations.html', Location = test, len_days = num_days,  loc_list = loc_list, km_accom = sort_accom, loc_list_accom = loc_list_accom)
    
#Returns an array of objects 
def loclist(sort_desc, answer):
    len_sample = len(sort_desc)
    loc_list = []
    for i in range (len_sample):
        loc_list.append({"lat": sort_desc[i][4],
                         "lng": sort_desc[i][3],
                         "name":sort_desc[i][0]
                })
    return loc_list
 

#Returns attractions that a user has previously rated       
def UserProfileSelection():
  
    usr = session['username']
    userProfile = []
    userPreferences = []
    userProfile = db.engine.execute("select cafeorcoffeeshop, Restaurant, PlaceOfWorship,Museum,ArtGallery,\
                      LandmarksOrHistoricalBuildings,Beach,Landform,Hotel, BedAndBreakfast,Campground,LodgingBusiness,\
                      GolfCourse, Park,SportsActivityLocation,\
                      Stores, BikeStore, ShoppingCentre, LocalBusiness from users where username = '{usr}'".format(usr = usr))

    userProfileArray = []
    for i in userProfile:
        userProfileArray.append(i)
   
    if userProfileArray[0][0] > 0:
        userPreferences.append('cafeorcoffeeshop')
    if userProfileArray[0][1] > 0:
        userPreferences.append('Restaurant')
    if userProfileArray[0][2] > 0:
        userPreferences.append('PlaceOfWorship')
    if userProfileArray[0][3] > 0:
        userPreferences.append('Museum')
    if userProfileArray[0][4] > 0:
        userPreferences.append('ArtGallery')
    if userProfileArray[0][5] > 0:
        userPreferences.append('LandmarksOrHistoricalBuildings')
    if userProfileArray[0][6] > 0:
        userPreferences.append('Beach')
    if userProfileArray[0][7] > 0:
        userPreferences.append('Landform')
    if userProfileArray[0][8] > 0:
        userPreferences.append('Hotel')
    if userProfileArray[0][9] > 0:
        userPreferences.append('BedAndBreakfast')
    if userProfileArray[0][10] > 0:
        userPreferences.append('Campground')
    if userProfileArray[0][11] > 0:
        userPreferences.append('LodgingBusiness')
    if userProfileArray[0][12] > 0:
        userPreferences.append('GolfCourse')
    if userProfileArray[0][13] > 0:
        userPreferences.append('Park')
    if userProfileArray[0][14] > 0:
        userPreferences.append('SportsActivityLocation')
    if userProfileArray[0][15] > 0:
        userPreferences.append('Stores')
    if userProfileArray[0][16] > 0:
        userPreferences.append('BikeStore')
    if userProfileArray[0][17] > 0:
        userPreferences.append('ShoppingCentre')
    if userProfileArray[0][18] > 0:
        userPreferences.append('LocalBusiness') 
        
    return userPreferences


#Create class for accomodation, activities and attractions 
class Locations(db.Model):
    __abstract__ = True
    name = db.Column(db.String(80), primary_key=True, unique=True)
    url = db.Column(db.String(120))
    typeAttr = db.Column(db.String(120))
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)
    telephone = db.Column(db.String(120))
    addressLocality = db.Column(db.String(120))
    addressRegion = db.Column(db.String(120))
    addressCountry = db.Column(db.String(120))
    
    def __init__(self, name, url, typeAttr, longitude, latitude, telephone, addressLocality, addressRegion, addressCountry):
        self.name = name
        self.url = url
        self.typeAttr = typeAttr
        self.longitude = longitude
        self.latitude = latitude
        self.telephone = telephone
        self.addressLocality = addressLocality
        self.addressRegion = addressRegion
        self.addressCountry = addressCountry
      
    def __repr__(self):
        return '<Location %r>' % self.name
  
class Activities(Locations):
    __tablename__ = "activities"
    
class Accomodation(Locations):
    __tablename__ = "accomodation"

class Attractions(Locations):
    __tablename__ = "attractions"  


#Create table 'users' with columns:username,email,password      
class User(db.Model):
    __tablename__ = "users"
    username = db.Column(db.String(80), primary_key=True, unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120), unique=True)
    
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
        
    def __repr__(self):
        return '<User %r>' % self.username


# Register Form Class
class RegisterForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')
       

# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'GET': 
        return render_template('register.html',form=form)
    else:
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username = username).first()
        if user:
            flash('User already exists')
            return redirect(url_for('register'))
        new_user = User(username=username,email=email, password=generate_password_hash(password, method='sha256'))
        db.session.add(new_user)
        db.session.commit()
        flash('Thank you for registering')
        return render_template('login.html')
 

#User session
@app.route('/profile')
def index():
   if 'username' in session:
      username = session['username']
      user_likes = []
      user_likes = UserProfileSelection()
      print(user_likes)
      return render_template('profile.html' ,username=username, user_likes=user_likes)
         
   return "You are not logged in"
    
   
#Send static files to html
@app.route('/checkbox.js')
def myjsfile():
    print("CALLED")
    return app.send_static_file('checkbox.js')


@app.route('/testurl',methods=['POST'] )
def testingcheckfetch():
 print("CALLED here")
 global check
 check = json.loads(request.data)
 if not check:
     print("Check is none")
 else:
     print("check is...")
     print(check)

 return {"details":"success"}


@app.route('/mapmarkers.js')
def myjsmapfile():
    print("CALLEDmap")
    return app.send_static_file('mapmarkers.js')

@app.route('/style.css')
def mystylefile():
    print("CALLEDCSS")
    return app.send_static_file('style.css')

@app.route('/style-post.css')
def mystylepostfile():
    print("CALLEDCSS-post")
    return app.send_static_file('style-post.css')

@app.route('/ratetest.js')
def myjsratefile():
    print("CALLEDrate")
    return app.send_static_file('ratetest.js')

@app.route('/ratings',methods=['POST'] )
def testingratefetch():
    rate = json.loads(request.data)
    usr = session['username']
    
    typ = rate["type"]
    counter = db.engine.execute("select {typ} from users where username = '{usr}'".format(typ=typ, usr=usr))
    
    count = None
    for i in counter:
       count = i
    count = int(count[0])
    
    if (rate["rating"] >= "3"):
        count = count + 1
        session['currentCount'] = session['currentCount'] + 1
    db.engine.execute("update users set {typ} = {count} where username = '{usr}'".format(typ=typ, count=count, usr=usr))
    if session['username'] is not None and session['num_days'] is not None :
        getPrecision()
    return {"details":"success"}

def getPrecision():
    usr = session['username']
    relevant = session['num_days']*2
    relevant_rec = session['currentCount']
    precision = relevant_rec/relevant
    if session['currentCount'] == 1:
        db.engine.execute("INSERT INTO evaluation (username, precision_val) VALUES ('{usr}', {precision})".format(precision = precision, usr=usr))
    else:
        db.engine.execute("update evaluation set precision_val={precision} where key_column IN(SELECT max(key_column) FROM evaluation)".format(precision = precision))


#Logout
@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('username', None)
   return render_template('home.html')
   
    
@app.route('/questionnaire', methods=['GET', 'POST'])
def questionnaire():
    return render_template('questionnaire.html')

@app.route('/PrivacyPolicy', methods=['GET', 'POST'])
def privacyPolicy():
    return render_template('PrivacyPolicy.html')

#Function to add the headings of each of the tables   
def AddLocation(info,type):
    
    if type == "atract":
        table_type = Attractions
    elif type == "activ":
        table_type = Activities
    elif type == "accom":
        table_type= Accomodation
                      
    num_attractions = len(info['results'])
    print(num_attractions)
    for i in range (0, num_attractions):
        if info['results'][i]['address']['addressRegion'] in ["Kerry", "Mayo","Cork","Clare","Galway","Sligo", "Donegal", "Leitrim", "Limerick"]:
            name = info['results'][i]['name']
            url = info['results'][i]['url']
            longitude = info['results'][i]['geo']['longitude']
            latitude = info['results'][i]['geo']['latitude']
            telephone = info['results'][i]['telephone']
            addressLocality = info['results'][i]['address']['addressLocality']
            addressRegion = info['results'][i]['address']['addressRegion']
            addressCountry = info['results'][i]['address']['addressCountry']
            
            try: 
                typeAttr = info['results'][i]['@type'][1]
            except:
                typeAttr = info['results'][i]['@type'][0]
            
            
            new_attraction = table_type(name, url, typeAttr, longitude, latitude, telephone,addressLocality, addressRegion,addressCountry)
            try:
                db.session.add(new_attraction)
                db.session.commit()
                print('attractions added')
            except:
                db.session.rollback()
                print('An exception occured')

            
    return  

 #Function to get items from all pages of API   
def next_page(url, type):
    attract = requests.get(url)
    info = json.loads(attract.text)
    if 'statusCode' in info:
        print("waiting for api")
        time.sleep(30)
    if 'results' not in info:
        print("exit")
        return

    AddLocation(info,type)
    if info.get('nextPage'):
        next_page(info['nextPage'],type)
    else:
        return

        
def load():
    next_page("https://failteireland.azure-api.net/opendata-api/v1/attractions","atract")
    next_page("https://failteireland.azure-api.net/opendata-api/v1/activities","activ")
    next_page("https://failteireland.azure-api.net/opendata-api/v1/accommodation","accom")

    return

def checkbox():

        return render_template('home.html')


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True,host='127.0.0.1', port=4000)
    
    
    

    
        