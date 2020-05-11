# COMP30910
Creates recommendations to tourists of the Wild Atlantic Way, taking temporal constraints into account.

FYP Title- Spatially and Temporally Constrained Decisions   
Name: Karen Jones  
Student Number: 16462826  
Supervisor: Gavin McArdle

This repository contains 1 python file; 'app.py' and 2 folders; 'static' and 'templates'   
The 'static' folder contains the javascript and CSS files.   
The 'templates' folder contains all of the HTML files.  
The python, 'app.py' file is written with Flask.

The purpose of this code is to create and display recommendations to visitors of the Wild Atlantic Way.  
The code renders a register and login page ('register.html', 'login.html') which allows users to create a profile for themselves. The 'home.html' allows users to enter in their travel details such as start location, end location, number of days and activites. A Mapquest API is called to return the coordinates of these 2 locations. A Fáilte Ireland API is called to retrieve the attractions along the Wild Atlantic Way route. This API will be fetched on a bi-annual basis in order to keep the data up to date.
The flask code is connected to the Postgis database. Data is passed to and from flask and Postgis. A user, attraction, accommodation and activity table are created in flask and stored in Postgis. Spatial queries are executed from flask on the Postgis database which return information about the users and attractions.  
A web-page is rendered with a map-based interface displaying the recommendations for the user (recommendations.html)


Installation:
In order to run the above code, the following installations must be completed:  
1) Python environment
2) Flask   
3) SQLAlchemy  
4) WT-Forms   

The code is run by going to it's directory and typing the command: 'python app.py'
