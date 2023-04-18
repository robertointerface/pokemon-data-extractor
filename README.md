# pokemon-data-extractor
Project to show python skills with async and modular design with chain of responsibility pattern.

The Project is very simple, provide as input a list of Pokemon names <br> 
1 - It will use the Pokemon api (https://pokeapi.co/) to extract the pokemon information. <br>
2 - Save the pokemon data in a specified place, at this version is being saved
on json file. <br>
3 - If any errors occurred during any previous steps log them. <br>


So what is so special about this design? <br>
1 - All steps are happening concurrently. <br>
2 - Each step has more than one processor, so i.e if you provide a list of 
10 pokemon names, the first step will be getting data at the same time from
multiple pokemons at the same time. <br>
3 - Steps communicate with each other with async queues, this allows that
while we are waiting for responses from the Pokemon Rest API, step number 2 
(saving pokemon data) can take already receive responses from the rest api
and start saving it. <br>
4 - Project has unit testing with pytest, which means we are doing async unit
testing. <br>

THINGS THAT NEED TO BE IMPROVED:
1 - Some code is repeated specially the methods 'process_work' on classes  
"DataSaverManager" & 'LogErrors' for sure this can be improved. <br>
2 - the class "DataExtractorOrganizer" (located at src/job_organizer.py) the method
'supervisor' is too long, this could be made into a builder pattern as there is a lot
of initialization of classes. <br>
3 - Probably a better and more reliable way to synchronize async queues pulling
could be done better but by implementing this project I found that synchronization 
of async queues is not so simple, :) <br>
