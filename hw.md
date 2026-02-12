Hello!

Welcome to LMT Defence junior developer homework! 
Best of luck and may the force be with you!

Some notes before you start:

1. AI use is ok, but be aware we will ask what specific lines of code mean and do. 
    So DO understand what AI writes.
    I highly suggest writing code on your own!
2. If something is not clear ask Dace and she will forward the questions
3. Please add a comment where AI was used
4. Add a comment with source if you use code samples from internet 

Expected outcome is a containerized Python application

Recommended tech to use:
1. Docker
2. Python 3.12 or newer 
3. FastAPI 
6. PyTest
4. SQL (Any SQL database acceptable)
5. VSCODE


So brief description.

You have to build a threat classification and interception application. You know that Latvia has three imaginary counter unmanned air system bases.
1. One in Riga (56.97475845607155, 24.1670070219384)
2. One in Liepāja (56.516083346891044, 21.0182217849017)
3. One in Daugavpils (55.87409588616014, 26.51864225209475)

You also know that Latvia has 4 types of air defense solutions

1. Interceptor drone, Speed 80 m/s, range of operations: 30 000 m,  max altitude 2000 m, price: 10 000 EUR
2. Fighter jet, Speed 700 m/s, range of operations  3500 m, max altitude 15 000 m, price per minute 1 000 EUR
3. Rocket, Speed 1500 m/s, range of operations 100 000 m, max altitude 30 000 m, price 300 000 EUR
4. 50Cal, Speed 900 m/s, range of operations 2000 m, max altitude 2000 m, price 1 eur per shot


You know that:
* Riga has all types of counter defense
* Daugavpils lacks Fighter jet
* Liepaja has only Interceptor drone and 50Cal.

Your mission, should you choose to accept it:

Is to write a software that runs in a containerized environment (Docker) and responds to threats. 
Your system should be able to accept data from radar systems and choose the best (most cost effective, or the only feasible) way to intercept the threat. 
(let's not shoot a Rocket from Daugavpils to strike down a cheap drone near Liepaja)
(let's not bring a fighter jet from Riga to strike down a cheap drone near Daugavpils)

System should classify threat based on flying altitude and speed. 
If the speed is below 15 m/s or flying altitude is below 200 m we can assume it is not a threat
If the speed is above 15 m/s it is caution
If the speed is above 50 m/s it is a threat
All other cases should be classified as potential threat

The system outcome should be a chosen type of interception, chosen base and coordinate where the target will be intercepted. (Optionally you can show it on a map)

Sample of radar system data. Radar system will send a new data every 1 second.
```JSON
{
    "speed_ms": 0,
    "altitude_m": 0,
    "heading_deg": 0,
    "latitude": 0,
    "longitude": 0,
    "report_time": 0,
}
```



So what do I expect:
1. A decent documentation on how to run it, don't forget we use lots of Linux and Macs. Windows rarely.
2. The locations and interceptors should be read from an SQL database
3. A working debugger in .vscode so we can walk trough the code together
4. Unit tests that validate your functions / methods, so I can quickly check if they make sense.
5. System has fully functional API (fastAPI)
6. A test scenario that you demonstrate and explain how your system works and why
7. A Public GIT repository with commit history of work

Thanks!
See you soon!