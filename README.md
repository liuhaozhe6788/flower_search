# A Flower Search System🌷
A flower search application using VGG19 and KNN

## Prerequistes
1. install chrome and chromedriver

2. install MySQL. User: `root`, Password: `12345678`. Create a table named `flower_data`.

## Run

1. run image scrapper:
```
python flower_scraper.py
```

2. run feature extraction:
```
python offline_extract.py
```

3. run validation(OPTIONAL):
```
python validate.py
```
3. run the server:
```
python server.py
```

