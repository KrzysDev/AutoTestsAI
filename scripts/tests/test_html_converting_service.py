from backend.app.services.html_test_converter_service import HtmlConvertingService

service = HtmlConvertingService()

pdf = service.convert_html_to_pdf("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>English Grammar Test: Present Simple & Present Continuous</title>

    <style>
        :root {
            --primary-color: #4a90e2;
            --secondary-color: #f5f7fa;
            --accent-color: #ff6b6b;
            --text-color: #333;
            --border-color: #ddd;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #eef2f3;
            color: var(--text-color);
            margin: 0;
            padding: 20px;
            line-height: 1.6;
        }

        .test-container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            border-top: 10px solid var(--primary-color);
        }

        .header {
            text-align: center;
            border-bottom: 2px solid var(--primary-color);
            margin-bottom: 30px;
            padding-bottom: 20px;
        }

        .header h1 {
            color: var(--primary-color);
            margin: 0;
            font-size: 28px;
            text-transform: uppercase;
        }

        .student-info {
            display: flex;
            justify-content: space-between;
            margin-bottom: 30px;
            font-weight: bold;
        }

        .student-info input {
            border: none;
            border-bottom: 1px solid #000;
            width: 200px;
            outline: none;
        }

        .exercise {
            margin-bottom: 30px;
            padding: 20px;
            border: 1px solid var(--border-color);
            border-radius: 10px;
            background-color: var(--secondary-color);
        }

        .exercise-title {
            font-weight: bold;
            color: var(--primary-color);
            margin-bottom: 15px;
            font-size: 18px;
            display: block;
            border-left: 5px solid var(--primary-color);
            padding-left: 10px;
        }

        .question {
            margin-bottom: 15px;
            display: block;
        }

        .options {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 5px;
        }

        .option {
            background: white;
            padding: 5px 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }

        .gap {
            display: inline-block;
            width: 120px;
            border-bottom: 1px solid #000;
            text-align: center;
        }

        .answer-key-section {
            margin-top: 50px;
            padding: 30px;
            background-color: #fffbe6;
            border: 3px dashed var(--accent-color);
            border-radius: 15px;
        }

        .answer-key-section h2 {
            color: var(--accent-color);
            text-align: center;
            text-transform: uppercase;
        }

        .key-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
        }

        .key-item {
            font-size: 14px;
            border-bottom: 1px solid #eee;
            padding: 5px 0;
        }

        .key-item strong {
            color: var(--primary-color);
        }
    </style>
</head>

<body>

<div class="test-container">

    <div class="header">
        <h1>English Grammar Mastery: A1 Level</h1>
        <p>Topic: Present Simple vs. Present Continuous</p>
    </div>

    <div class="student-info">
        <div>Name: <input type="text"></div>
        <div>Date: <input type="text"></div>
        <div>Score: <input type="text"> / 120</div>
    </div>

    <!-- EXERCISE 1 -->
    <div class="exercise">
        <span class="exercise-title">Exercise 1: Multiple Choice (Habits)</span>

        <div class="question">1. I ___ my teeth every morning.
            <div class="options">
                <div class="option">a) brush</div>
                <div class="option">b) brushes</div>
            </div>
        </div>

        <div class="question">2. Sarah ___ to school by bus.
            <div class="options">
                <div class="option">a) go</div>
                <div class="option">b) goes</div>
            </div>
        </div>

        <div class="question">3. We ___ in a big house.
            <div class="options">
                <div class="option">a) live</div>
                <div class="option">b) lives</div>
            </div>
        </div>

        <div class="question">4. My cat ___ a lot of fish.
            <div class="options">
                <div class="option">a) eat</div>
                <div class="option">b) eats</div>
            </div>
        </div>

        <div class="question">5. They ___ football on Saturdays.
            <div class="options">
                <div class="option">a) play</div>
                <div class="option">b) plays</div>
            </div>
        </div>

        <div class="question">6. You ___ English very well.
            <div class="options">
                <div class="option">a) speak</div>
                <div class="option">b) speaks</div>
            </div>
        </div>
    </div>

    <!-- EXERCISE 2 -->
    <div class="exercise">
        <span class="exercise-title">Exercise 2: Gap Fill (Daily Routines)</span>

        <div class="question">1. He <span class="gap"></span> (wake up) at 7 AM.</div>
        <div class="question">2. She <span class="gap"></span> (drink) milk for breakfast.</div>
        <div class="question">3. I <span class="gap"></span> (read) a book before bed.</div>
        <div class="question">4. The dog <span class="gap"></span> (sleep) on the sofa.</div>
        <div class="question">5. We <span class="gap"></span> (walk) to the park.</div>
        <div class="question">6. My parents <span class="gap"></span> (work) in an office.</div>
    </div>

    <!-- EXERCISE 3 -->
    <div class="exercise">
        <span class="exercise-title">Exercise 3: Negative Transformation</span>

        <div class="question">1. I like apples → I <span class="gap"></span> like apples.</div>
        <div class="question">2. He plays tennis → He <span class="gap"></span> play tennis.</div>
        <div class="question">3. She speaks French → She <span class="gap"></span> speak French.</div>
        <div class="question">4. We have a car → We <span class="gap"></span> have a car.</div>
        <div class="question">5. They live here → They <span class="gap"></span> live here.</div>
        <div class="question">6. It rains in July → It <span class="gap"></span> rain in July.</div>
    </div>

    <!-- EXERCISE 4 -->
    <div class="exercise">
        <span class="exercise-title">Exercise 4: Subject-Verb Matching</span>

        <div class="question">1. I / We / You / They → <span class="gap"></span> (work / works)</div>
        <div class="question">2. He / She / It → <span class="gap"></span> (work / works)</div>
        <div class="question">3. My brother → <span class="gap"></span> (study / studies)</div>
        <div class="question">4. My friends → <span class="gap"></span> (study / studies)</div>
        <div class="question">5. The teacher → <span class="gap"></span> (teach / teaches)</div>
        <div class="question">6. The students → <span class="gap"></span> (teach / teaches)</div>
    </div>

    <!-- EXERCISE 5 -->
    <div class="exercise">
        <span class="exercise-title">Exercise 5: Error Correction</span>

        <div class="question">1. She go to the cinema → <span class="gap"></span></div>
        <div class="question">2. I does not like milk → <span class="gap"></span></div>
        <div class="question">3. Do he play guitar? → <span class="gap"></span></div>
        <div class="question">4. We plays games → <span class="gap"></span></div>
        <div class="question">5. It don't snow here → <span class="gap"></span></div>
        <div class="question">6. They likes pizza → <span class="gap"></span></div>
    </div>

    <!-- EXERCISE 11 -->
    <div class="exercise">
        <span class="exercise-title">Exercise 11: Present Continuous (Now)</span>

        <div class="question">1. I ___ a book right now.
            <div class="options">
                <div class="option">a) am reading</div>
                <div class="option">b) is reading</div>
            </div>
        </div>

        <div class="question">2. She ___ TV at the moment.
            <div class="options">
                <div class="option">a) am watching</div>
                <div class="option">b) is watching</div>
            </div>
        </div>

        <div class="question">3. We ___ for the bus.
            <div class="options">
                <div class="option">a) are waiting</div>
                <div class="option">b) is waiting</div>
            </div>
        </div>
    </div>

    <!-- ANSWER KEY -->
    <div class="answer-key-section">
        <h2>Answer Key</h2>

        <div class="key-grid">
            <div class="key-item"><strong>Ex1:</strong> 1a 2b 3a 4b 5a 6a</div>
            <div class="key-item"><strong>Ex2:</strong> wakes drinks reads sleeps walk work</div>
            <div class="key-item"><strong>Ex3:</strong> don’t / doesn’t forms</div>
            <div class="key-item"><strong>Ex4:</strong> work / works / studies</div>
            <div class="key-item"><strong>Ex5:</strong> goes / don’t / Does / play / doesn’t / like</div>
        </div>
    </div>

</div>

</body>
</html>
""")

with open("output.pdf", "wb") as f:
    f.write(pdf)