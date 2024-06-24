The code will work for input provided to it using example_text which in this case has been provided the article from test dataframe. However this project was 
created on google collab which doesn't allow you to open a Local host I tried to use ngork for it but still it didn't work. For furthur executing and launching
the webpage you need to create a  app.py file which will have the code for the flask application and save the preprocessed csv of the dataframe on you're local 
storage. besides that the summerization part for both BART and openai API is same you only need to create an API key from openai which is easily created 
through https://platform.openai.com/settings/profile?tab=api-keys once you create the api key simply replace it for the OPENAI_API_KEY = 'Your Own API key'.

