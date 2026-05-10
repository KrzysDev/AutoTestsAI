from backend.app.services.html_test_converter_service import HtmlConvertingService

service = HtmlConvertingService()

data = service.convert_html_to_pdf("""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<title>Test – Präteritum (Gruppe B)</title>
<style>
  @page { size: A4; margin: 1cm 1.5cm; @bottom-center { content: "— " counter(page) " —"; font-size: 9pt; color: #666; } }
  * { box-sizing: border-box; }
  body { margin:0; padding:0; font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; font-size: 10.5pt; line-height: 1.25; color: #1e2a3a; background:#fff; }
  .test-container { width:100%; }

  /* header */
  .header-bar { background: #1e3c5c; color: #fff; padding: 10px 14px 6px 14px; border-radius: 0 0 8px 8px; }
  .header-title { font-size: 16pt; font-weight: 700; text-align: center; letter-spacing: 1px; margin:0 0 2px 0; }
  .header-meta { text-align: center; font-size: 10pt; color: #d4e0ed; margin:2px 0 0 0; }
  .header-meta span { margin: 0 14px; }

  /* student info */
  .student-info { display:table; width:100%; margin:6px 0 12px 0; border-bottom: 2px solid #1e3c5c; }
  .info-row { display:table-row; }
  .info-cell { display:table-cell; padding: 3px 6px; font-size: 10pt; }
  .info-label { font-weight:600; color:#1e3c5c; }
  .info-underline { border-bottom:1px solid #1e3c5c; min-width:120px; display:inline-block; margin-left:4px; padding:0 4px; }

  /* exercises layout */
  .exercise { margin-bottom: 10px; padding: 3px 0; page-break-inside: auto; }
  .exercise-header { page-break-after: avoid; margin-bottom: 3px; padding:0; }
  .exercise-header .ex-n { font-weight:700; color:#1e3c5c; font-size:11pt; }
  .exercise-header .ex-instr { font-weight:600; color:#2a4a6a; font-size:10.5pt; }
  .ex-score { float:right; font-weight:600; color:#1e3c5c; font-size:10pt; margin-top:2px; }

  .question-item { margin: 3px 0 3px 14px; page-break-inside: avoid; }
  .question-item .q-n { font-weight:600; }
  .gap { display:inline-block; min-width:80px; border-bottom: 2px solid #1e3c5c; margin:0 2px; height:1.1em; }
  .sentence { margin:2px 0; }

  /* verb table */
  .verb-table { border-collapse: collapse; margin:4px 0 6px 18px; width:auto; }
  .verb-table td { border:1px solid #7f9eb5; padding:1px 6px; font-size:10pt; }
  .verb-table .pron { background:#eaf0f6; font-weight:600; }
  .verb-table .blank { min-width:100px; border-bottom:2px solid #1e3c5c; height:1.2em; display:block; }

  /* mcq */
  .mcq-option { display:inline-block; margin-right:14px; font-size:10.5pt; }

  /* reading passage */
  .reading-box { background:#f4f7fa; border-left:4px solid #1e3c5c; padding:6px 10px; margin:4px 0; }

  /* writing box */
  .writing-box { width:100%; min-height:120px; border:2px solid #7f9eb5; border-radius:4px; margin:4px 0; padding:6px; background:#fafcfe; }

  /* answer key */
  .answer-key-section { page-break-before: always; }
  .answer-key-section h2 { color:#1e3c5c; font-size:13pt; border-bottom:2px solid #1e3c5c; padding-bottom:2px; margin:0 0 6px 0; }
  .ak-table { display:table; width:100%; border-collapse: collapse; }
  .ak-row { display:table-row; }
  .ak-cell { display:table-cell; padding:2px 6px; border:1px solid #b0c7d8; font-size:9.5pt; vertical-align:top; }
  .ak-cell b { color:#1e3c5c; }

  /* utilities */
  .clearfix::after { content:""; display:table; clear:both; }
  .mt-2 { margin-top:2px; }
  .mb-2 { margin-bottom:2px; }
</style>
</head>
<body>
<div class="test-container">

<!-- HEADER -->
<div class="header-bar">
  <div class="header-title">Test – Präteritum (Gruppe B)</div>
  <div class="header-meta">
    <span>Niveau: A2</span>
    <span>Altersgruppe: Erwachsene</span>
    <span>Gesamtpunktzahl: 60</span>
  </div>
</div>

<!-- STUDENT INFO -->
<div class="student-info">
  <div class="info-row">
    <div class="info-cell"><span class="info-label">Name:</span><span class="info-underline">&nbsp;</span></div>
    <div class="info-cell"><span class="info-label">Datum:</span><span class="info-underline">&nbsp;</span></div>
    <div class="info-cell"><span class="info-label">Klasse:</span><span class="info-underline">&nbsp;</span></div>
  </div>
</div>

<!-- ============ EXERCISE 1 ============ -->
<div class="exercise">
  <div class="exercise-header clearfix">
    <span class="ex-n">1.</span> <span class="ex-instr">Konjugieren Sie die Verben im Präteritum. Tragen Sie alle 6 Formen in die Tabelle ein.</span>
    <span class="ex-score">(6 Pkt)</span>
  </div>
  <div class="question-item"><span class="q-n">a) </span><strong>lernen</strong>
    <table class="verb-table"><tr><td class="pron">ich</td><td><span class="blank">&nbsp;</span></td><td class="pron">wir</td><td><span class="blank">&nbsp;</span></td></tr><tr><td class="pron">du</td><td><span class="blank">&nbsp;</span></td><td class="pron">ihr</td><td><span class="blank">&nbsp;</span></td></tr><tr><td class="pron">er/sie/es</td><td><span class="blank">&nbsp;</span></td><td class="pron">sie/Sie</td><td><span class="blank">&nbsp;</span></td></tr></table>
  </div>
  <div class="question-item"><span class="q-n">b) </span><strong>fahren</strong>
    <table class="verb-table"><tr><td class="pron">ich</td><td><span class="blank">&nbsp;</span></td><td class="pron">wir</td><td><span class="blank">&nbsp;</span></td></tr><tr><td class="pron">du</td><td><span class="blank">&nbsp;</span></td><td class="pron">ihr</td><td><span class="blank">&nbsp;</span></td></tr><tr><td class="pron">er/sie/es</td><td><span class="blank">&nbsp;</span></td><td class="pron">sie/Sie</td><td><span class="blank">&nbsp;</span></td></tr></table>
  </div>
</div>

<!-- ============ EXERCISE 2 ============ -->
<div class="exercise">
  <div class="exercise-header clearfix">
    <span class="ex-n">2.</span> <span class="ex-instr">Konjugieren Sie die Verben im Präteritum.</span>
    <span class="ex-score">(6 Pkt)</span>
  </div>
  <div class="question-item"><span class="q-n">a) </span><strong>werden</strong>
    <table class="verb-table"><tr><td class="pron">ich</td><td><span class="blank">&nbsp;</span></td><td class="pron">wir</td><td><span class="blank">&nbsp;</span></td></tr><tr><td class="pron">du</td><td><span class="blank">&nbsp;</span></td><td class="pron">ihr</td><td><span class="blank">&nbsp;</span></td></tr><tr><td class="pron">er/sie/es</td><td><span class="blank">&nbsp;</span></td><td class="pron">sie/Sie</td><td><span class="blank">&nbsp;</span></td></tr></table>
  </div>
  <div class="question-item"><span class="q-n">b) </span><strong>wohnen</strong>
    <table class="verb-table"><tr><td class="pron">ich</td><td><span class="blank">&nbsp;</span></td><td class="pron">wir</td><td><span class="blank">&nbsp;</span></td></tr><tr><td class="pron">du</td><td><span class="blank">&nbsp;</span></td><td class="pron">ihr</td><td><span class="blank">&nbsp;</span></td></tr><tr><td class="pron">er/sie/es</td><td><span class="blank">&nbsp;</span></td><td class="pron">sie/Sie</td><td><span class="blank">&nbsp;</span></td></tr></table>
  </div>
</div>

<!-- ============ EXERCISE 3 ============ -->
<div class="exercise">
  <div class="exercise-header clearfix">
    <span class="ex-n">3.</span> <span class="ex-instr">Konjugieren Sie die Verben im Präteritum.</span>
    <span class="ex-score">(6 Pkt)</span>
  </div>
  <div class="question-item"><span class="q-n">a) </span><strong>schlafen</strong>
    <table class="verb-table"><tr><td class="pron">ich</td><td><span class="blank">&nbsp;</span></td><td class="pron">wir</td><td><span class="blank">&nbsp;</span></td></tr><tr><td class="pron">du</td><td><span class="blank">&nbsp;</span></td><td class="pron">ihr</td><td><span class="blank">&nbsp;</span></td></tr><tr><td class="pron">er/sie/es</td><td><span class="blank">&nbsp;</span></td><td class="pron">sie/Sie</td><td><span class="blank">&nbsp;</span></td></tr></table>
  </div>
  <div class="question-item"><span class="q-n">b) </span><strong>spielen</strong>
    <table class="verb-table"><tr><td class="pron">ich</td><td><span class="blank">&nbsp;</span></td><td class="pron">wir</td><td><span class="blank">&nbsp;</span></td></tr><tr><td class="pron">du</td><td><span class="blank">&nbsp;</span></td><td class="pron">ihr</td><td><span class="blank">&nbsp;</span></td></tr><tr><td class="pron">er/sie/es</td><td><span class="blank">&nbsp;</span></td><td class="pron">sie/Sie</td><td><span class="blank">&nbsp;</span></td></tr></table>
  </div>
</div>

<!-- ============ EXERCISE 4 ============ -->
<div class="exercise">
  <div class="exercise-header clearfix">
    <span class="ex-n">4.</span> <span class="ex-instr">Konjugieren Sie die Verben im Präteritum.</span>
    <span class="ex-score">(6 Pkt)</span>
  </div>
  <div class="question-item"><span class="q-n">a) </span><strong>bleiben</strong>
    <table class="verb-table"><tr><td class="pron">ich</td><td><span class="blank">&nbsp;</span></td><td class="pron">wir</td><td><span class="blank">&nbsp;</span></td></tr><tr><td class="pron">du</td><td><span class="blank">&nbsp;</span></td><td class="pron">ihr</td><td><span class="blank">&nbsp;</span></td></tr><tr><td class="pron">er/sie/es</td><td><span class="blank">&nbsp;</span></td><td class="pron">sie/Sie</td><td><span class="blank">&nbsp;</span></td></tr></table>
  </div>
  <div class="question-item"><span class="q-n">b) </span><strong>aufstehen</strong>
    <table class="verb-table"><tr><td class="pron">ich</td><td><span class="blank">&nbsp;</span></td><td class="pron">wir</td><td><span class="blank">&nbsp;</span></td></tr><tr><td class="pron">du</td><td><span class="blank">&nbsp;</span></td><td class="pron">ihr</td><td><span class="blank">&nbsp;</span></td></tr><tr><td class="pron">er/sie/es</td><td><span class="blank">&nbsp;</span></td><td class="pron">sie/Sie</td><td><span class="blank">&nbsp;</span></td></tr></table>
  </div>
</div>

<!-- ============ EXERCISE 5 ============ -->
<div class="exercise">
  <div class="exercise-header clearfix">
    <span class="ex-n">5.</span> <span class="ex-instr">Konjugieren Sie die Verben im Präteritum.</span>
    <span class="ex-score">(6 Pkt)</span>
  </div>
  <div class="question-item"><span class="q-n">a) </span><strong>sich waschen</strong>
    <table class="verb-table"><tr><td class="pron">ich</td><td><span class="blank">&nbsp;</span></td><td class="pron">wir</td><td><span class="blank">&nbsp;</span></td></tr><tr><td class="pron">du</td><td><span class="blank">&nbsp;</span></td><td class="pron">ihr</td><td><span class="blank">&nbsp;</span></td></tr><tr><td class="pron">er/sie/es</td><td><span class="blank">&nbsp;</span></td><td class="pron">sie/Sie</td><td><span class="blank">&nbsp;</span></td></tr></table>
  </div>
  <div class="question-item"><span class="q-n">b) </span><strong>laufen</strong>
    <table class="verb-table"><tr><td class="pron">ich</td><td><span class="blank">&nbsp;</span></td><td class="pron">wir</td><td><span class="blank">&nbsp;</span></td></tr><tr><td class="pron">du</td><td><span class="blank">&nbsp;</span></td><td class="pron">ihr</td><td><span class="blank">&nbsp;</span></td></tr><tr><td class="pron">er/sie/es</td><td><span class="blank">&nbsp;</span></td><td class="pron">sie/Sie</td><td><span class="blank">&nbsp;</span></td></tr></table>
  </div>
</div>

<!-- ============ EXERCISE 6 ============ -->
<div class="exercise">
  <div class="exercise-header clearfix">
    <span class="ex-n">6.</span> <span class="ex-instr">Setzen Sie das Verb in Klammern im Präteritum ein.</span>
    <span class="ex-score">(10 Pkt)</span>
  </div>
  <div class="question-item"><span class="q-n">a) </span>Gestern <span class="gap">&nbsp;</span> (sein) ich im Kino.</div>
  <div class="question-item"><span class="q-n">b) </span>Mein Bruder <span class="gap">&nbsp;</span> (haben) keine Zeit.</div>
  <div class="question-item"><span class="q-n">c) </span>Wir <span class="gap">&nbsp;</span> (gehen) gestern spazieren.</div>
  <div class="question-item"><span class="q-n">d) </span>Ihr <span class="gap">&nbsp;</span> (essen) im Restaurant.</div>
  <div class="question-item"><span class="q-n">e) </span>Die Kinder <span class="gap">&nbsp;</span> (schlafen) früh.</div>
  <div class="question-item"><span class="q-n">f) </span>Meine Mutter <span class="gap">&nbsp;</span> (kochen) das Abendessen.</div>
  <div class="question-item"><span class="q-n">g) </span>Der Zug <span class="gap">&nbsp;</span> (kommen) um 8 Uhr.</div>
  <div class="question-item"><span class="q-n">h) </span>Ich <span class="gap">&nbsp;</span> (lesen) ein spannendes Buch.</div>
  <div class="question-item"><span class="q-n">i) </span>Sie <span class="gap">&nbsp;</span> (trinken) Tee.</div>
  <div class="question-item"><span class="q-n">j) </span>Wir <span class="gap">&nbsp;</span> (finden) den Schlüssel nicht.</div>
</div>

<!-- ============ EXERCISE 7 ============ -->
<div class="exercise">
  <div class="exercise-header clearfix">
    <span class="ex-n">7.</span> <span class="ex-instr">Setzen Sie das Verb in Klammern im Präteritum ein.</span>
    <span class="ex-score">(10 Pkt)</span>
  </div>
  <div class="question-item"><span class="q-n">a) </span>Damals <span class="gap">&nbsp;</span> (wohnen) sie in Berlin.</div>
  <div class="question-item"><span class="q-n">b) </span>Ich <span class="gap">&nbsp;</span> (werden) sehr müde.</div>
  <div class="question-item"><span class="q-n">c) </span>Du <span class="gap">&nbsp;</span> (fahren) mit dem Fahrrad.</div>
  <div class="question-item"><span class="q-n">d) </span>Es <span class="gap">&nbsp;</span> (regnen) den ganzen Tag.</div>
  <div class="question-item"><span class="q-n">e) </span>Die Schüler <span class="gap">&nbsp;</span> (lernen) fleißig.</div>
  <div class="question-item"><span class="q-n">f) </span>Mein Freund <span class="gap">&nbsp;</span> (geben) mir ein Geschenk.</div>
  <div class="question-item"><span class="q-n">g) </span>Wir <span class="gap">&nbsp;</span> (sehen) einen schönen Film.</div>
  <div class="question-item"><span class="q-n">h) </span>Ihr <span class="gap">&nbsp;</span> (bleiben) zu Hause.</div>
  <div class="question-item"><span class="q-n">i) </span>Er <span class="gap">&nbsp;</span> (aufstehen) um 7 Uhr.</div>
  <div class="question-item"><span class="q-n">j) </span>Sie <span class="gap">&nbsp;</span> (waschen) sich die Hände.</div>
</div>

<!-- ============ EXERCISE 8 ============ -->
<div class="exercise">
  <div class="exercise-header clearfix">
    <span class="ex-n">8.</span> <span class="ex-instr">Bilden Sie Sätze im Präteritum aus den gegebenen Wörtern.</span>
    <span class="ex-score">(10 Pkt)</span>
  </div>
  <div class="question-item"><span class="q-n">a) </span>ich / gestern / ein Buch / lesen<br>___________________________________________________________</div>
  <div class="question-item"><span class="q-n">b) </span>wir / im Park / spazieren gehen<br>___________________________________________________________</div>
  <div class="question-item"><span class="q-n">c) </span>meine Schwester / Musik / hören<br>___________________________________________________________</div>
  <div class="question-item"><span class="q-n">d) </span>ihr / im Urlaub / sein<br>___________________________________________________________</div>
  <div class="question-item"><span class="q-n">e) </span>der Hund / im Garten / schlafen<br>___________________________________________________________</div>
  <div class="question-item"><span class="q-n">f) </span>du / deinen Freund / anrufen<br>___________________________________________________________</div>
  <div class="question-item"><span class="q-n">g) </span>der Zug / eine Stunde / später / kommen<br>___________________________________________________________</div>
  <div class="question-item"><span class="q-n">h) </span>ich / kaltes Wasser / trinken<br>___________________________________________________________</div>
  <div class="question-item"><span class="q-n">i) </span>die Kinder / Fußball / spielen<br>___________________________________________________________</div>
  <div class="question-item"><span class="q-n">j) </span>wir / das Fenster / öffnen<br>___________________________________________________________</div>
</div>

<!-- ============ EXERCISE 9 ============ -->
<div class="exercise">
  <div class="exercise-header clearfix">
    <span class="ex-n">9.</span> <span class="ex-instr">Bilden Sie Sätze im Präteritum aus den gegebenen Wörtern.</span>
    <span class="ex-score">(10 Pkt)</span>
  </div>
  <div class="question-item"><span class="q-n">a) </span>er / gestern / früh / aufstehen<br>___________________________________________________________</div>
  <div class="question-item"><span class="q-n">b) </span>ich / Tee / mit Honig / trinken<br>___________________________________________________________</div>
  <div class="question-item"><span class="q-n">c) </span>sie (Pl.) / ihre Hausaufgaben / machen<br>___________________________________________________________</div>
  <div class="question-item"><span class="q-n">d) </span>mein Vater / ein Auto / kaufen<br>___________________________________________________________</div>
  <div class="question-item"><span class="q-n">e) </span>ihr / im See / schwimmen<br>___________________________________________________________</div>
  <div class="question-item"><span class="q-n">f) </span>es / gestern / sehr kalt / sein<br>___________________________________________________________</div>
  <div class="question-item"><span class="q-n">g) </span>du / ein Bild / malen<br>___________________________________________________________</div>
  <div class="question-item"><span class="q-n">h) </span>wir / den Bus / nehmen<br>___________________________________________________________</div>
  <div class="question-item"><span class="q-n">i) </span>die Lehrerin / die Fragen / beantworten<br>___________________________________________________________</div>
  <div class="question-item"><span class="q-n">j) </span>ich / meinen Schlüssel / verlieren<br>___________________________________________________________</div>
</div>

<!-- ============ EXERCISE 10 ============ -->
<div class="exercise">
  <div class="exercise-header clearfix">
    <span class="ex-n">10.</span> <span class="ex-instr">Bilden Sie Sätze im Präteritum aus den gegebenen Wörtern.</span>
    <span class="ex-score">(10 Pkt)</span>
  </div>
  <div class="question-item"><span class="q-n">a) </span>letztes Jahr / ich / in Hamburg / wohnen<br>___________________________________________________________</div>
  <div class="question-item"><span class="q-n">b) </span>wir / den ganzen Abend / tanzen<br>___________________________________________________________</div>
  <div class="question-item"><span class="q-n">c) </span>der Film / um 20 Uhr / beginnen<br>___________________________________________________________</div>
  <div class="question-item"><span class="q-n">d) </span>ihr / Süßigkeiten / kaufen<br>___________________________________________________________</div>
  <div class="question-item"><span class="q-n">e) </span>mein Bruder / und / ich / Schach / spielen<br>___________________________________________________________</div>
  <div class="question-item"><span class="q-n">f) </span>die Katze / auf dem Sofa / sich waschen<br>___________________________________________________________</div>
  <div class="question-item"><span class="q-n">g) </span>du / deine Eltern / besuchen<br>___________________________________________________________</div>
  <div class="question-item"><span class="q-n">h) </span>der Chef / die Dokumente / unterschreiben<br>___________________________________________________________</div>
  <div class="question-item"><span class="q-n">i) </span>ich / den Kaffee / schwarz / trinken<br>___________________________________________________________</div>
  <div class="question-item"><span class="q-n">j) </span>die Touristen / das Museum / sehen<br>___________________________________________________________</div>
</div>

<!-- ============================================================ -->
<!-- ANSWER KEY -->
<!-- ============================================================ -->
<div class="answer-key-section">
  <h2>Antwortschlüssel – Präteritum (Gruppe B)</h2>

  <!-- 1 -->
  <div class="ak-table">
    <div class="ak-row"><div class="ak-cell" style="width:33%"><b>1a) lernen</b><br>ich lernte, du lerntest, er/sie/es lernte, wir lernten, ihr lerntet, sie/Sie lernten</div>
    <div class="ak-cell" style="width:33%"><b>1b) fahren</b><br>ich fuhr, du fuhrst, er/sie/es fuhr, wir fuhren, ihr fuhrt, sie/Sie fuhren</div>
    <div class="ak-cell" style="width:33%"><b>2a) werden</b><br>ich wurde, du wurdest, er/sie/es wurde, wir wurden, ihr wurdet, sie/Sie wurden</div></div>
    <div class="ak-row"><div class="ak-cell"><b>2b) wohnen</b><br>ich wohnte, du wohntest, er/sie/es wohnte, wir wohnten, ihr wohntet, sie/Sie wohnten</div>
    <div class="ak-cell"><b>3a) schlafen</b><br>ich schlief, du schliefst, er/sie/es schlief, wir schliefen, ihr schlieft, sie/Sie schliefen</div>
    <div class="ak-cell"><b>3b) spielen</b><br>ich spielte, du spieltest, er/sie/es spielte, wir spielten, ihr spieltet, sie/Sie spielten</div></div>
    <div class="ak-row"><div class="ak-cell"><b>4a) bleiben</b><br>ich blieb, du bliebst, er/sie/es blieb, wir blieben, ihr bliebt, sie/Sie blieben</div>
    <div class="ak-cell"><b>4b) aufstehen</b><br>ich stand auf, du standst auf, er/sie/es stand auf, wir standen auf, ihr standet auf, sie/Sie standen auf</div>
    <div class="ak-cell"><b>5a) sich waschen</b><br>ich wusch mich, du wuschst dich, er/sie/es wusch sich, wir wuschen uns, ihr wuscht euch, sie/Sie wuschen sich</div></div>
    <div class="ak-row"><div class="ak-cell"><b>5b) laufen</b><br>ich lief, du liefst, er/sie/es lief, wir liefen, ihr lieft, sie/Sie liefen</div>
    <div class="ak-cell"><b>6a–j)</b><br>a) war b) hatte c) gingen d) aßt(e) e) schliefen f) kochte g) kam h) las i) trank j) fanden</div>
    <div class="ak-cell"><b>7a–j)</b><br>a) wohnte b) wurde c) fuhrst d) regnete e) lernten f) gab g) sahen h) bliebt i) stand auf j) wusch sich</div></div>
    <div class="ak-row"><div class="ak-cell"><b>8a–j)</b><br>a) Ich las gestern ein Buch.<br>b) Wir gingen im Park spazieren.<br>c) Meine Schwester hörte Musik.<br>d) Ihr wart im Urlaub.<br>e) Der Hund schlief im Garten.<br>f) Du riefst deinen Freund an.<br>g) Der Zug kam eine Stunde später.<br>h) Ich trank kaltes Wasser.<br>i) Die Kinder spielten Fußball.<br>j) Wir öffneten das Fenster.</div>
    <div class="ak-cell"><b>9a–j)</b><br>a) Er stand gestern früh auf.<br>b) Ich trank Tee mit Honig.<br>c) Sie machten ihre Hausaufgaben.<br>d) Mein Vater kaufte ein Auto.<br>e) Ihr schwammt im See.<br>f) Es war gestern sehr kalt.<br>g) Du maltest ein Bild.<br>h) Wir nahmen den Bus.<br>i) Die Lehrerin beantwortete die Fragen.<br>j) Ich verlor meinen Schlüssel.</div>
    <div class="ak-cell"><b>10a–j)</b><br>a) Letztes Jahr wohnte ich in Hamburg.<br>b) Wir tanzten den ganzen Abend.<br>c) Der Film begann um 20 Uhr.<br>d) Ihr kauftet Süßigkeiten.<br>e) Mein Bruder und ich spielten Schach.<br>f) Die Katze wusch sich auf dem Sofa.<br>g) Du besuchtest deine Eltern.<br>h) Der Chef unterschrieb die Dokumente.<br>i) Ich trank den Kaffee schwarz.<br>j) Die Touristen sahen das Museum.</div></div>
  </div>
</div>

</div>
</body>
</html>""")

with open("test_praeteritum_gruppe_b.pdf", "wb") as f:
    f.write(data)
