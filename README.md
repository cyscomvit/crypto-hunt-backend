## Cyber Odyssey

A web-app made by CYSCOM VIT, for their event Cyber Odyssey, a treasure hunt with a focus on cyber-security. Similar to a cryptic hunt.

## Features

1. Question can be text or image.
    - Questions are stored in a `questions.json` file. Every question is of type `i` (image) or `t` (text).
    - If image, the question text is the URL to the image. Store in [images](static/images/questions) folder.
    - Logs all attempts to a log file.
2. "Location Keys"
    - All questions are tied to a location, and all locations have a key that must be entered to go to the next question. So a participant can see the question and the location they can get the key from. They can go to the location, solving the question on the way, and get the key from a CYSCOM member standing at the location.
3. Hints
    - Supports hints for every question, which can be shown by clicking the show hint button.
4. Leaderboard
     - A leaderboard that shows the rank of all registered teams when the competition is happening.
4. Sequence generation.
    - Each question must have a `difficulty` attribute in the and this is used for generating a sequence. For example, if a user has to solve 15 questions in total. They can be of `easy`, `medium`, `hard`, `ctf-e` (ctf-easy), `ctf-m`(ctf-medium) type.
    - If every user must also start with one question from a list of specific "start" questions with the location as the event starting location, the question difficulty can also be set as `start` and the user will have his first question as one of the any questions with difficulty as `start`.
5. Can pass HTML to question field.
    - Can pass raw HTML to question and hint field, and it is rendered. This can be used for building complex questions like sudoku and crosswords.
6. Spreadsheet writer
    - Writes all registrations to a spreadsheet using Google Cloud.
    - Store credentials in a `credentials-spreadsheet.json` file.

## Config

1. `questions.json` - All questions, hints and answers.
    - JSONList.
    ```JSON
    [
       {
       "no": 1, // Irrevelant. Just to understand which question you are editing if the file has many questions.
       "type": "i", // 'i' or 't' for image or text.
       "text": "1-79d25484-0e5e-4d04-a580-087358f26919.png", // Question text or file name. Images must be stored in /static/images folder.
       "ans": "ransomware", // Answer. Case insensitive.
       "hint": "form of malware designed to encrypt files", // Hint, shown when user clicks show hint button on the play site
       "difficulty": "easy", // Difficulty, used for generating a sequence of questions for every user, i.e solve easy questions first and then medium and then hard, etc.
       "key": "links-sclera", // Location key, to be put along with the actual answer.
       "location": "Outside Gymkhana" // Location where they have to get the key from.
       },
       {
           // 2nd question.
       }
    ]
    ```

2. `cyber-odyssey.env`
```
SPREADSHEET_ID=
REGISTRATIONS_SPREADSHEET=
DEBUG=FALSE
EVENT_END_TIME=1677054600
PORT=80
EVENT_ENDED=FALSE
```

## Techstack

1. Server - Flask (Python)
    - to process the requests and handle the registration, login and play logic.
2. Database - Firebase.
    - It stores the data in [Firebase's realtime database](https://firebase.google.com/products/realtime-database)
    - NoSQL database structure is
    ```
        cyber-odyssey
            - users
                - regno1
                    - name
                    - email
                    - pw_hash
                    - etc
                - regno2
                    - name
                    - email
                    - pw_hash
                    - etc
    ```
    - Store the keys in a `credentials-cyber-odyssey.json` file in the root directory.
3. Frontend - Plain HTML, CSS and JS.
    - present in[ /templates](/templates/) and [/static](/static/) folder
4. Docker - For deployment
    - Both [`Dockerfile`](Dockerfile) and [`docker-compose.yml`](docker-compose.yml) are included for ease of use.
