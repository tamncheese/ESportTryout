# E-Sport Tryout
#### Video Demo:  <https://youtu.be/UozUHyh28Sg>
#### Description:
Author: tamncheese on Github

This is a webapp written in flask framework in Python for Harvard's CS50x Final Project
The user will compete in three games (sequence, tag, and motivation) to be a part of an e-sports team and will be ranked by how fast they are.
Uses Python, HTML, CSS, Javascript and SQL. Uses bootstrap toolkit
The webapp aims to use all the tools presented in the course to show Computational Thinking, Abstraction and Precision

In the parent directory you will find the backend files including app.py and database. Includes subdirectories, static and templates
The static directory include images and css files
The templates directory includes all client facing html files.

Detailed Description:
app.py contains the backend code for each template.
login.html and register.html: The user is first directed to the login page and click a button to go to the register page.Uses Werkzeug to hash the password.
The user inputs there username and password. Gives an error is no the user is not complying. Initilizes the duration SQL table. The SQL databse contains three tables. 1. users account info 2. users game times 3. users durations in each game.
index.html; homepage displaying the rankings and a button to start the tryout. Uses Sqlite3 Select Join to diplay the username and times in a bootstrap class table.
sequence.html: A 5x5 grid of buttons with randomly positioned buttons numbered 1-5. User needs to click on the butons sequentially to proceed. Buttons start out as deactivated and changed to active as they click.
tag.html: Canvas tag allows to use of the drawImage to move the cat around. "Bounces" the cat when it hits the boundary. Makes sure the cat doesn't spawn out of bounds. Uses event.offSetX and Y to check if the user pointer coordinates are in the cat's hitbox
motivation.html: randomly pulls a image from the static folder. Uses bootstrap textarea so the user can type the message in. Compares the inputs when checked is clicked.
The decision was made to split the instructions into a different page for easier implenmentation without using hidden elements and allows a timestamp to be recorded when the game loads. Each game was desgiend to use showvase Python, Javasctipt and HTML. WIth new objects, new tags and hwo to use timestamps.
After each game the SQL datetime is SELECTED (string), then coverted into a datetime object to calculate the time difference using datetime time delta. e
The nav bar contains a favicon and disabled nav buttons that changes color on different games. The tag html uses a picture of my cat.


