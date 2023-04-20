# pokemon-data-extractor
Project to show python skills with async and modular design with chain of responsibility pattern.

The Project is very simple, provide as input a list of Pokemon names <br> 
- It will use the Pokemon api (https://pokeapi.co/) to extract the pokemon information. <br>
- Save the pokemon data in a specified place, at this version is being saved
on json file but that can easy be configured due to the chain of responsability
pattern that allows removing and adding code like lego bricks. <br>
- If any errors occurred during any previous steps log them. <br>

![Model](https://github.com/robertointerface/pokemon-data-extractor/blob/develop-data-extractor/pokemon-extractor-explanation.png)

# How to run it.
- You can run it locally, package management is poetry. if you don't have it,
install it according to documentation https://python-poetry.org/docs/#installation.
Navigate to directory where poetry file poetry.lock is located and run "poetry install". 
 Once is installed, set the interpreter created by poetry,
 this is normally under ~/.cache/pypoetry/virtualenvs, once is done you can simple
 run file as a script src/main.py "pokemon_name1" "pokemon_name2" ...
- You can also build the dockerfile and run it in isolation.


# So what is so special about this design? <br>
- All steps are happening concurrently thanks to Asyncio library. <br>
- Each step has more than one processor, so i.e if you provide a list of 
10 pokemon names, the first step will be getting data concurrently by async of 
those 10 pokemons. <br>
- Steps communicate with each other with async queues, this allows that
while we are waiting for responses from the Pokemon Rest API, step number 2 
(saving pokemon data) can take already receive responses from the rest api
and start saving it. <br>
- Project has unit testing with pytest, which means we are doing async unit
testing. <br>
- Project is very modular, this is important for the code to grow organically,
classes have a defined protocol by 'abc' module and as long they are followed
modules can be removed or added. <br>
- Error handling happens in the last step, error handling is crucial when 
doing async, one needs to determine if an error happens we stop all the async
workers? or we continue and handle the error at the end?...

  
# THINGS THAT NEED TO BE IMPROVED:
- Some code is repeated specially the methods 'process_work' on classes  
"DataSaverManager" & 'LogErrors' for sure this can be improved. <br>
- the class "DataExtractorOrganizer" (located at src/job_organizer.py) the method
'supervisor' is too long, this could be made into a builder pattern as there is a lot
of initialization of classes in this method. <br>
- Probably a better and more reliable way to synchronize async queues pulling
could be done better. By implementing this project I found that synchronization 
of async queues is not so simple, :) <br>
- Monitoring overall pipeline should be done outside of workers, at the moment
is inside, that is not good practice. <br>

