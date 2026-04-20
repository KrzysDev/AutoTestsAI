from backend.app.services.html_test_converter_service import HtmlConvertingService

service = HtmlConvertingService()

pdf = service.convert_html_to_pdf("""<!DOCTYPE html>

<html lang="en">
<head>
<meta charset="UTF-8">
<title>English Language Assessment - Past Simple</title>
<style>
@page {
size: A4;
margin: 1.5cm 2cm;
@bottom-center {
content: "— " counter(page) " —";
font-size: 9pt;
color: #999;
}
}

    * { box-sizing: border-box; }
    body { 
        margin: 0; 
        padding: 0; 
        background: #ffffff; 
        font-family: Georgia, 'Times New Roman', serif;
        font-size: 11pt;
        color: #333;
    }

    .test-container { width: 100%; }

    /* Header Styles */
    .header-bar {
        background: #1a2744;
        color: #ffffff;
        padding: 20px;
        text-align: center;
        border-bottom: 4px solid #c0392b;
    }
    .header-bar h1 {
        margin: 0;
        font-size: 18pt;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 3px;
        font-family: 'Segoe UI', Tahoma, sans-serif;
    }
    .header-info {
        margin-top: 10px;
        font-size: 10pt;
        font-family: 'Segoe UI', Tahoma, sans-serif;
    }

    /* Student Info Bar */
    .student-info {
        display: table;
        width: 100%;
        background: #f5f5f5;
        padding: 10px;
        margin-bottom: 20px;
        border-collapse: separate;
    }
    .info-cell {
        display: table-cell;
        width: 33.33%;
        padding: 5px 10px;
    }
    .info-label {
        font-family: 'Segoe UI', Tahoma, sans-serif;
        font-weight: bold;
        font-size: 9pt;
        margin-right: 5px;
    }
    .info-dotted {
        border-bottom: 1.5px dotted #333;
        display: inline-block;
        width: 70%;
        height: 14px;
    }

    /* Section Dividers */
    .section-divider {
        background: #1a2744;
        color: white;
        text-align: center;
        padding: 8px;
        margin: 20px 0;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-size: 10pt;
        font-family: 'Segoe UI', Tahoma, sans-serif;
        page-break-before: auto;
        page-break-after: avoid;
        page-break-inside: avoid;
    }

    /* Exercise Blocks */
    .exercise {
        background: #ffffff;
        border: 1.5px solid #ddd;
        padding: 16px;
        margin-bottom: 20px;
        page-break-inside: avoid;
        position: relative;
    }
    .ex-tag {
        background: #c0392b;
        color: white;
        font-size: 9pt;
        font-family: 'Segoe UI', Tahoma, sans-serif;
        padding: 3px 8px;
        float: right;
        margin-left: 10px;
    }
    .score-tag {
        font-style: italic;
        font-size: 9pt;
        color: #666666;
        float: right;
    }
    .exercise-title {
        font-family: 'Segoe UI', Tahoma, sans-serif;
        font-size: 12pt;
        font-weight: bold;
        text-transform: uppercase;
        color: #1a2744;
        border-left: 4px solid #c0392b;
        padding-left: 8px;
        margin-bottom: 10px;
        page-break-after: avoid;
    }
    .instructions {
        font-style: italic;
        color: #666;
        font-size: 10pt;
        margin-bottom: 15px;
        display: block;
    }

    /* Question Styles */
    .question-list {
        list-style-type: decimal;
        padding-left: 25px;
        margin: 0;
    }
    .question-item {
        font-size: 10.5pt;
        line-height: 1.7;
        margin-bottom: 8px;
    }
    .gap-fill {
        border-bottom: 1px solid #aaa;
        display: inline-block;
        min-width: 120px;
        text-align: center;
    }
    
    /* Multiple Choice */
    .mc-option {
        display: inline-block;
        margin-right: 15px;
    }
    .circle {
        display: inline-block;
        width: 12px;
        height: 12px;
        border: 1px solid #333;
        border-radius: 50%;
        vertical-align: middle;
        margin-right: 4px;
    }

    /* Writing Box */
    .writing-box {
        border: 1.5px solid #aaa;
        width: 100%;
        min-height: 400px;
        background: white;
        background-image: repeating-linear-gradient(white, white 24px, #e5e5e5 25px);
        padding: 5px 10px;
        line-height: 25px;
    }

    /* Answer Key */
    .answer-key-section {
        page-break-before: always;
        border-top: 4px solid #c0392b;
    }
    .ak-header {
        background: #1a2744;
        color: white;
        padding: 10px;
        font-family: 'Segoe UI', Tahoma, sans-serif;
        font-weight: bold;
        text-align: center;
    }
    .ak-table {
        display: table;
        width: 100%;
        border-collapse: separate;
        border-spacing: 5px;
    }
    .ak-row { display: table-row; }
    .ak-cell {
        display: table-cell;
        width: 33%;
        border: 1px solid #444;
        padding: 10px;
        background: #1e3055;
        color: white;
        font-size: 9pt;
        vertical-align: top;
    }
    .ak-title {
        font-weight: bold;
        color: #c0392b;
        margin-bottom: 5px;
        display: block;
    }
</style>
</head>
<body>

<div class="test-container">
<div class="header-bar">
<h1>Past Simple Mastery Test</h1>
<div class="header-info">
LEVEL: B1 | AGE GROUP: TEENS | TOTAL SCORE: 75 PTS
</div>
</div>

<div class="student-info">
    <div class="info-cell">
        <span class="info-label">NAME:</span>
        <span class="info-dotted"></span>
    </div>
    <div class="info-cell">
        <span class="info-label">DATE:</span>
        <span class="info-dotted"></span>
    </div>
    <div class="info-cell">
        <span class="info-label">CLASS:</span>
        <span class="info-dotted"></span>
    </div>
</div>

<div class="section-divider">SECTION A — GRAMMAR & VOCABULARY</div>

<div class="exercise">
    <span class="ex-tag">Ex. 1</span>
    <span class="score-tag">( 6 pts )</span>
    <div class="exercise-title">Multiple Choice: Social Media & Tech</div>
    <span class="instructions">Choose the correct past form of the verb to complete the sentence.</span>
    <ol class="question-list">
        <li class="question-item">Tom __________ a photo of his lunch on Instagram an hour ago.
            <br>
            <span class="mc-option"><span class="circle"></span> A) postted</span>
            <span class="mc-option"><span class="circle"></span> B) posted</span>
            <span class="mc-option"><span class="circle"></span> C) posts</span>
        </li>
        <li class="question-item">I __________ my laptop yesterday because it was broken.
            <br>
            <span class="mc-option"><span class="circle"></span> A) don't use</span>
            <span class="mc-option"><span class="circle"></span> B) didn't used</span>
            <span class="mc-option"><span class="circle"></span> C) didn't use</span>
        </li>
        <li class="question-item">They __________ to the new podcast during their break.
            <br>
            <span class="mc-option"><span class="circle"></span> A) listened</span>
            <span class="mc-option"><span class="circle"></span> B) listen</span>
            <span class="mc-option"><span class="circle"></span> C) listening</span>
        </li>
        <li class="question-item">__________ you see that viral video last night?
            <br>
            <span class="mc-option"><span class="circle"></span> A) Do</span>
            <span class="mc-option"><span class="circle"></span> B) Were</span>
            <span class="mc-option"><span class="circle"></span> C) Did</span>
        </li>
        <li class="question-item">Sarah __________ her password after the security alert.
            <br>
            <span class="mc-option"><span class="circle"></span> A) changed</span>
            <span class="mc-option"><span class="circle"></span> B) changeed</span>
            <span class="mc-option"><span class="circle"></span> C) change</span>
        </li>
        <li class="question-item">We __________ the online game together on Friday.
            <br>
            <span class="mc-option"><span class="circle"></span> A) winned</span>
            <span class="mc-option"><span class="circle"></span> B) won</span>
            <span class="mc-option"><span class="circle"></span> C) win</span>
        </li>
    </ol>
</div>

<div class="exercise">
    <span class="ex-tag">Ex. 2</span>
    <span class="score-tag">( 6 pts )</span>
    <div class="exercise-title">Irregular Verbs: School Life</div>
    <span class="instructions">Complete the sentences with the Past Simple form of the verbs in brackets.</span>
    <ol class="question-list">
        <li class="question-item">I (see) <span class="gap-fill"></span> my teacher at the cinema last Saturday.</li>
        <li class="question-item">The students (buy) <span class="gap-fill"></span> some snacks for the class party.</li>
        <li class="question-item">He (write) <span class="gap-fill"></span> a long essay for his English project.</li>
        <li class="question-item">We (go) <span class="gap-fill"></span> to the library to study for the test.</li>
        <li class="question-item">My best friend (give) <span class="gap-fill"></span> me a cool birthday present.</li>
        <li class="question-item">The school bell (ring) <span class="gap-fill"></span> exactly at 8:00 AM.</li>
    </ol>
</div>

<div class="exercise">
    <span class="ex-tag">Ex. 3</span>
    <span class="score-tag">( 6 pts )</span>
    <div class="exercise-title">Negative Transformations: Hobbies</div>
    <span class="instructions">Rewrite the positive sentences in the negative form.</span>
    <ol class="question-list">
        <li class="question-item">Mark played football after school. <br> ________________________________________________________</li>
        <li class="question-item">I understood the instructions for the guitar lesson. <br> ________________________________________________________</li>
        <li class="question-item">They went to the rock concert last month. <br> ________________________________________________________</li>
        <li class="question-item">The girls took many photos at the art gallery. <br> ________________________________________________________</li>
        <li class="question-item">We visited the new skatepark on Sunday. <br> ________________________________________________________</li>
        <li class="question-item">She spoke to the coach about the team. <br> ________________________________________________________</li>
    </ol>
</div>

<div class="exercise">
    <span class="ex-tag">Ex. 4</span>
    <span class="score-tag">( 6 pts )</span>
    <div class="exercise-title">Interrogative Form: Travel</div>
    <span class="instructions">Put the words in the correct order to make questions.</span>
    <ol class="question-list">
        <li class="question-item">you / did / where / go / summer / last / ? <br> ________________________________________________________</li>
        <li class="question-item">stay / they / in / hotel / a / did / ? <br> ________________________________________________________</li>
        <li class="question-item">time / did / arrive / what / the / train / ? <br> ________________________________________________________</li>
        <li class="question-item">buy / souvenirs / any / you / did / ? <br> ________________________________________________________</li>
        <li class="question-item">she / like / did / the / local / food / ? <br> ________________________________________________________</li>
        <li class="question-item">many / photos / how / take / did / he / ? <br> ________________________________________________________</li>
    </ol>
</div>

<div class="exercise">
    <span class="ex-tag">Ex. 5</span>
    <span class="score-tag">( 6 pts )</span>
    <div class="exercise-title">Error Correction: Daily Routine</div>
    <span class="instructions">Each sentence contains ONE mistake. Rewrite the sentence correctly.</span>
    <ol class="question-list">
        <li class="question-item">I didn't went to the park yesterday. <br> ________________________________________________________</li>
        <li class="question-item">She eated a huge pizza for dinner. <br> ________________________________________________________</li>
        <li class="question-item">Did you saw the news this morning? <br> ________________________________________________________</li>
        <li class="question-item">They was very happy about the results. <br> ________________________________________________________</li>
        <li class="question-item">We builded a treehouse last summer. <br> ________________________________________________________</li>
        <li class="question-item">He don't like the film we watched. <br> ________________________________________________________</li>
    </ol>
</div>

<div class="exercise">
    <span class="ex-tag">Ex. 6</span>
    <span class="score-tag">( 6 pts )</span>
    <div class="exercise-title">Sentence Completion: My Weekend</div>
    <span class="instructions">Complete the sentences about YOURSELF using Past Simple.</span>
    <ol class="question-list">
        <li class="question-item">Last Saturday morning, I <span class="gap-fill"></span>.</li>
        <li class="question-item">For breakfast yesterday, I <span class="gap-fill"></span>.</li>
        <li class="question-item">The last movie I watched <span class="gap-fill"></span>.</li>
        <li class="question-item">Two days ago, I didn't <span class="gap-fill"></span>.</li>
        <li class="question-item">Last night, my friends and I <span class="gap-fill"></span>.</li>
        <li class="question-item">I (learn) <span class="gap-fill"></span> something new in class on Monday.</li>
    </ol>
</div>

<div class="exercise">
    <span class="ex-tag">Ex. 7</span>
    <span class="score-tag">( 6 pts )</span>
    <div class="exercise-title">Matching: Action & Reaction</div>
    <span class="instructions">Match the verb (1-6) with the correct object (A-F) to create a past simple sentence.</span>
    <div style="display: table; width: 100%;">
        <div style="display: table-cell; width: 50%;">
            1. I lost ___ <br>
            2. We drank ___ <br>
            3. She found ___ <br>
            4. They met ___ <br>
            5. He broke ___ <br>
            6. You told ___
        </div>
        <div style="display: table-cell; width: 50%;">
            A. a new friend at the mall. <br>
            B. my keys on the bus. <br>
            C. some cold lemonade. <br>
            D. a funny secret. <br>
            E. a ten-euro note in the street. <br>
            F. his phone screen.
        </div>
    </div>
</div>

<div class="exercise">
    <span class="ex-tag">Ex. 8</span>
    <span class="score-tag">( 6 pts )</span>
    <div class="exercise-title">Vocabulary: Past Time Expressions</div>
    <span class="instructions">Choose the correct time expression to complete the sentence.</span>
    <ol class="question-list">
        <li class="question-item">I finished my homework two hours (ago / last).</li>
        <li class="question-item">We went to Paris (yesterday / last) year.</li>
        <li class="question-item">Did you talk to him (yesterday / ago) afternoon?</li>
        <li class="question-item">She started her blog (in / on) 2022.</li>
        <li class="question-item">They left the party (at / last) midnight.</li>
        <li class="question-item">I bought these shoes (last / yesterday) week.</li>
    </ol>
</div>

<div class="exercise">
    <span class="ex-tag">Ex. 9</span>
    <span class="score-tag">( 6 pts )</span>
    <div class="exercise-title">Verb Transformation: Technology</div>
    <span class="instructions">Fill the gaps with the correct Past Simple form of the verb in brackets.</span>
    <ol class="question-list">
        <li class="question-item">The battery (die) <span class="gap-fill"></span> while I was playing.</li>
        <li class="question-item">I (forget) <span class="gap-fill"></span> to charge my phone last night.</li>
        <li class="question-item">We (download) <span class="gap-fill"></span> a new app for our trip.</li>
        <li class="question-item">He (send) <span class="gap-fill"></span> me a text message five minutes ago.</li>
        <li class="question-item">They (not / find) <span class="gap-fill"></span> the charger in the drawer.</li>
        <li class="question-item">My brother (take) <span class="gap-fill"></span> my headphones without asking!</li>
    </ol>
</div>

<div class="exercise">
    <span class="ex-tag">Ex. 10</span>
    <span class="score-tag">( 6 pts )</span>
    <div class="exercise-title">Revision: A Busy Day</div>
    <span class="instructions">Choose the correct form to complete the story.</span>
    <p style="font-size: 10.5pt; line-height: 1.8;">
        Yesterday (1) (was / were) a very busy day. I (2) (woke / waked) up early and (3) (have / had) a quick breakfast. 
        Then, I (4) (run / ran) to catch the bus. At school, we (5) (did / doed) a science experiment. 
        After school, I (6) (meet / met) my friends at the park.
    </p>
</div>

<div class="section-divider">SECTION B — WRITING</div>

<div class="exercise">
    <span class="ex-tag">Ex. 11</span>
    <span class="score-tag">( 15 pts )</span>
    <div class="exercise-title">Email Writing: An Amazing Weekend</div>
    <span class="instructions">Write an email (80-100 words) to a friend about a weekend trip you took recently. 
    Use the Past Simple and include: where you went, what you did, and how you felt.</span>
    <div class="writing-box">
        To: <br>
        Subject: My weekend trip! <br><br>
        Hi!
    </div>
</div>

<div class="answer-key-section">
    <div class="ak-header">ANSWER KEY — FOR TEACHER USE ONLY</div>
    <div class="ak-table">
        <div class="ak-row">
            <div class="ak-cell">
                <span class="ak-title">Ex 1: Multiple Choice</span>
                1. B (posted)<br>2. C (didn't use)<br>3. A (listened)<br>4. C (Did)<br>5. A (changed)<br>6. B (won)
            </div>
            <div class="ak-cell">
                <span class="ak-title">Ex 2: Irregular Verbs</span>
                1. saw<br>2. bought<br>3. wrote<br>4. went<br>5. gave<br>6. rang
            </div>
            <div class="ak-cell">
                <span class="ak-title">Ex 3: Negative</span>
                1. Mark didn't play...<br>2. I didn't understand...<br>3. They didn't go...<br>4. The girls didn't take...<br>5. We didn't visit...<br>6. She didn't speak...
            </div>
        </div>
        <div class="ak-row">
            <div class="ak-cell">
                <span class="ak-title">Ex 4: Questions</span>
                1. Where did you go last summer?<br>2. Did they stay in a hotel?<br>3. What time did the train arrive?<br>4. Did you buy any souvenirs?<br>5. Did she like the local food?<br>6. How many photos did he take?
            </div>
            <div class="ak-cell">
                <span class="ak-title">Ex 5: Error Correction</span>
                1. ...didn't go...<br>2. ...ate...<br>3. Did you see...<br>4. They were...<br>5. ...built...<br>6. He didn't like...
            </div>
            <div class="ak-cell">
                <span class="ak-title">Ex 6: Personal</span>
                (Student's own answers - check for correct V2 form)
            </div>
        </div>
        <div class="ak-row">
            <div class="ak-cell">
                <span class="ak-title">Ex 7: Matching</span>
                1-B, 2-C, 3-E, 4-A, 5-F, 6-D
            </div>
            <div class="ak-cell">
                <span class="ak-title">Ex 8: Signal Words</span>
                1. ago, 2. last, 3. yesterday, 4. in, 5. at, 6. last
            </div>
            <div class="ak-cell">
                <span class="ak-title">Ex 9 & 10</span>
                Ex 9: 1. died, 2. forgot, 3. downloaded, 4. sent, 5. didn't find, 6. took.<br>
                Ex 10: 1. was, 2. woke, 3. had, 4. ran, 5. did, 6. met.
            </div>
        </div>
    </div>
    <div style="padding: 10px; color: white; background: #c0392b; margin-top: 5px; font-size: 9pt;">
        <strong>WRITING (Ex 11):</strong> Mark for: Content (5), Grammar/Past Simple (5), Vocabulary (3), Length (2).
    </div>
</div>
</div>

</body>
</html>""")
with open("output.pdf", "wb") as f:
    f.write(pdf)