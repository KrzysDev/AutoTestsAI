import requests
import os

def test_convert_endpoint():
    # URL Twojego endpointu
    url = "http://localhost:8000/v1/rag/test/convert"
    
    # Dane testowe (Twoje wejście JSON)
    payload = {
      "groups": [
        {
          "questions": [
            {
              "instruction": "Select the correct word for each picture.",
              "text": "a) ![image1](<alt: school-object-1>)\n b) ![image2](<alt: school-object-2>)\n c) ![image3](<alt: school-object-3>)\n d) ![image4](<alt: school-object-4>)\n e) ![image5](<alt: school-object-5>)\nChoose from: teacher, blackboard, pencil, book, bag, chair, eraser, computer.",
              "type": "multiple_choice",
              "correct_answer": "teacher, blackboard, pencil, book, bag"
            },
            {
              "instruction": "Select the correct word for each picture.",
              "text": "a) ![image6](<alt: school-object-6>)\n b) ![image7](<alt: school-object-7>)\n c) ![image8](<alt: school-object-8>)\n d) ![image9](<alt: school-object-9>)\n e) ![image10](<alt: school-object-10>)\nChoose from: chair, eraser, computer, notebook, ruler, uniform, lunch, playground.",
              "type": "multiple_choice",
              "correct_answer": "chair, eraser, computer, notebook, ruler"
            },
            {
              "instruction": "Select the correct word for each picture.",
              "text": "a) ![image11](<alt: school-object-11>)\n b) ![image12](<alt: school-object-12>)\n c) ![image13](<alt: school-object-13>)\n d) ![image14](<alt: school-object-14>)\n e) ![image15](<alt: school-object-15>)\nChoose from: library, playground, desk‑mate, principal, hallway, bag, pencil case, marker.",
              "type": "multiple_choice",
              "correct_answer": "library, playground, desk‑mate, principal, hallway"
            },
            {
              "instruction": "Select the correct word for each picture.",
              "text": "a) ![image16](<alt: school-object-16>)\n b) ![image17](<alt: school-object-17>)\n c) ![image18](<alt: school-object-18>)\n d) ![image19](<alt: school-object-19>)\n e) ![image20](<alt: school-object-20>)\nChoose from: scissors, glue, paint, bell, homework, lesson, school bus, uniform.",
              "type": "multiple_choice",
              "correct_answer": "scissors, glue, paint, bell, homework"
            },
            {
              "instruction": "Select the correct word for each picture.",
              "text": "a) ![image21](<alt: school-object-21>)\n b) ![image22](<alt: school-object-22>)\n c) ![image23](<alt: school-object-23>)\n d) ![image24](<alt: school-object-24>)\n e) ![image25](<alt: school-object-25>)\nChoose from: lesson, recess, lunch, computer, notebook, marker, ruler, bag.",
              "type": "multiple_choice",
              "correct_answer": "lesson, recess, lunch, computer, notebook"
            },
            {
              "instruction": "Fill in the missing word in each sentence.",
              "text": "1) The ___ sits at the front of the class.\n2) I write with a ___ in my notebook.\n3) We keep our books in a ___.\nWord bank: teacher, pencil, bag, desk, chair, eraser, computer, ruler.",
              "type": "open_ended",
              "correct_answer": "teacher, pencil, bag"
            },
            {
              "instruction": "Fill in the missing word in each sentence.",
              "text": "1) The ___ tells us the lesson plan.\n2) You can find a ___ in the library.\n3) My ___ is red and heavy.\nWord bank: principal, book, bag, teacher, marker, notebook, computer, uniform.",
              "type": "open_ended",
              "correct_answer": "principal, book, bag"
            },
            {
              "instruction": "Fill in the missing word in each sentence.",
              "text": "1) During ___ we play outside.\n2) I need a ___ to cut paper.\n3) The ___ hangs on the wall.\nWord bank: recess, scissors, bell, teacher, ruler, glue, paint, computer.",
              "type": "open_ended",
              "correct_answer": "recess, scissors, bell"
            },
            {
              "instruction": "Fill in the missing word in each sentence.",
              "text": "1) Please put your ___ on the desk.\n2) We use a ___ to erase mistakes.\n3) The ___ shows us the time for each lesson.\nWord bank: notebook, eraser, clock, bell, ruler, bag, book, computer.",
              "type": "open_ended",
              "correct_answer": "notebook, eraser, bell"
            },
            {
              "instruction": "Choose the correct option for each statement.",
              "text": "a) We have ___ at the end of the lesson.\n   A) a bell   B) a lunch   C) a book   D) a ruler\nb) The ___ tells us what to do.\n   A) teacher   B) notebook   C) computer   D) playground\nc) You can find a ___ in the library.\n   A) pencil   B) book   C) glue   D) lunch",
              "type": "multiple_choice",
              "correct_answer": "A, A, B"
            },
            {
              "instruction": "Choose the correct option for each statement.",
              "text": "a) The ___ sits on the blackboard.\n   A) marker   B) ruler   C) bag   D) scissors\nb) Our ___ is blue and has our name on it.\n   A) uniform   B) notebook   C) computer   D) desk‑mate\nc) The ___ comes to pick us up in the morning.\n   A) school bus   B) principal   C) hallway   D) lesson",
              "type": "multiple_choice",
              "correct_answer": "A, A, A"
            },
            {
              "instruction": "Choose the correct option for each statement.",
              "text": "a) You need a ___ to draw a straight line.\n   A) ruler   B) eraser   C) glue   D) marker\nb) The ___ is where we keep our coats.\n   A) hallway   B) playground   C) computer   D) lunch\nc) ___ is a time to eat food.\n   A) Recess   B) Lunch   C) Homework   D) Lesson",
              "type": "multiple_choice",
              "correct_answer": "A, A, B"
            },
            {
              "instruction": "Choose the correct option for each statement.",
              "text": "a) The ___ helps us find information.\n   A) computer   B) bag   C) pencil   D) bell\nb) The ___ is where we read books.\n   A) library   B) desk   C) playground   D) uniform\nc) The ___ is used to stick paper together.\n   A) glue   B) ruler   C) marker   D) notebook",
              "type": "multiple_choice",
              "correct_answer": "A, A, A"
            },
            {
              "instruction": "Choose the correct option for each statement.",
              "text": "a) The ___ tells us the day’s schedule.\n   A) bell   B) book   C) pencil   D) computer\nb) The ___ is where we sit during class.\n   A) chair   B) playground   C) hallway   D) scissors\nc) ___ are used for coloring pictures.\n   A) Paint   B) Glue   C) Ruler   D) Marker",
              "type": "multiple_choice",
              "correct_answer": "A, A, A"
            },
            {
              "instruction": "Choose the correct option for each statement.",
              "text": "a) The ___ watches over the school.\n   A) principal   B) teacher   C) desk‑mate   D) bag\nb) The ___ is used to fix torn pages.\n   A) glue   B) pencil   C) book   D) marker\nc) ___ helps us write neatly.\n   A) pencil   B) eraser   C) ruler   D) computer",
              "type": "multiple_choice",
              "correct_answer": "A, A, A"
            },
            {
              "instruction": "Choose the correct option for each statement.",
              "text": "a) The ___ is where we store our books.\n   A) bag   B) desk   C) chair   D) hallway\nb) ___ is a place to play during break.\n   A) Playground   B) Library   C) Classroom   D) Uniform\nc) The ___ hangs on the wall with the date.\n   A) calendar   B) bell   C) ruler   D) marker",
              "type": "multiple_choice",
              "correct_answer": "A, A, B"
            },
            {
              "instruction": "Choose the correct option for each statement.",
              "text": "a) You can borrow a ___ from the library.\n   A) book   B) pencil   C) bag   D) ruler\nb) The ___ is used to clean the board.\n   A) eraser   B) marker   C) glue   D) scissors\nc) ___ is the time when lessons start.\n   A) Bell   B) Lunch   C) Recess   D) Homework",
              "type": "multiple_choice",
              "correct_answer": "A, A, A"
            },
            {
              "instruction": "Choose the correct option for each statement.",
              "text": "a) The ___ helps us count numbers.\n   A) ruler   B) computer   C) bag   D) marker\nb) The ___ is where we keep our coats.\n   A) hallway   B) library   C) classroom   D) playground\nc) ___ is a task we do at home.\n   A) Homework   B) Lunch   C) Recess   D) Bell",
              "type": "multiple_choice",
              "correct_answer": "A, A, A"
            }
          ],
          "answers": [
            "teacher, blackboard, pencil, book, bag",
            "chair, eraser, computer, notebook, ruler",
            "library, playground, desk‑mate, principal, hallway",
            "scissors, glue, paint, bell, homework",
            "lesson, recess, lunch, computer, notebook",
            "teacher, pencil, bag",
            "principal, book, bag",
            "recess, scissors, bell",
            "notebook, eraser, bell",
            "A, A, B",
            "A, A, A",
            "A, A, B",
            "A, A, A",
            "A, A, A",
            "A, A, A",
            "A, A, A",
            "A, A, B",
            "A, A, A",
            "A, A, A"
          ]
        },
        {
          "questions": [
            {
              "instruction": "Select the correct word for each picture.",
              "text": "a) ![image31](<alt: school-object-31>)\nChoose from: uniform, school bus, marker, classroom, pencil case, book, desk, bell",
              "type": "multiple_choice",
              "correct_answer": "uniform"
            },
            {
              "instruction": "Select the correct word for each picture.",
              "text": "a) ![image32](<alt: school-object-32>)\nChoose from: school bus, uniform, marker, classroom, pencil case, chair, eraser, ruler",
              "type": "multiple_choice",
              "correct_answer": "school bus"
            },
            {
              "instruction": "Select the correct word for each picture.",
              "text": "a) ![image33](<alt: school-object-33>)\nChoose from: pencil case, marker, uniform, classroom, school bus, notebook, scissors, glue",
              "type": "multiple_choice",
              "correct_answer": "pencil case"
            },
            {
              "instruction": "Select the correct word for each picture.",
              "text": "a) ![image34](<alt: school-object-34>)\nChoose from: marker, uniform, school bus, classroom, pencil case, ruler, bell, bag",
              "type": "multiple_choice",
              "correct_answer": "marker"
            },
            {
              "instruction": "Select the correct word for each picture.",
              "text": "a) ![image35](<alt: school-object-35>)\nChoose from: classroom, uniform, school bus, marker, pencil case, desk, eraser, lunch",
              "type": "multiple_choice",
              "correct_answer": "classroom"
            },
            {
              "instruction": "Fill in the missing word in each sentence.",
              "text": "1) My ___ is blue and has my name on it.\nWord bank: uniform, school bus, pencil case, marker, classroom, desk, ruler, book.",
              "type": "open_ended",
              "correct_answer": "uniform"
            },
            {
              "instruction": "Fill in the missing word in each sentence.",
              "text": "2) We travel to school on the ___.\nWord bank: uniform, school bus, pencil case, marker, classroom, desk, ruler, book.",
              "type": "open_ended",
              "correct_answer": "school bus"
            },
            {
              "instruction": "Fill in the missing word in each sentence.",
              "text": "3) The ___ holds my pens and pencils.\nWord bank: uniform, school bus, pencil case, marker, classroom, desk, ruler, book.",
              "type": "open_ended",
              "correct_answer": "pencil case"
            },
            {
              "instruction": "Fill in the missing word in each sentence.",
              "text": "4) The teacher uses a ___ to write on the board.\nWord bank: uniform, school bus, pencil case, marker, classroom, desk, ruler, book.",
              "type": "open_ended",
              "correct_answer": "marker"
            },
            {
              "instruction": "Fill in the missing word in each sentence.",
              "text": "5) The ___ is where we learn together.\nWord bank: uniform, school bus, pencil case, marker, classroom, desk, ruler, book.",
              "type": "open_ended",
              "correct_answer": "classroom"
            },
            {
              "instruction": "Circle T for True or F for False.",
              "text": "1) The principal sits at the front of the class.",
              "type": "open_ended",
              "correct_answer": "F"
            },
            {
              "instruction": "Circle T for True or F for False.",
              "text": "2) The bell rings at the end of the lesson.",
              "type": "open_ended",
              "correct_answer": "T"
            },
            {
              "instruction": "Circle T for True or F for False.",
              "text": "3) We store our books in a bag.",
              "type": "open_ended",
              "correct_answer": "T"
            },
            {
              "instruction": "Circle T for True or F for False.",
              "text": "4) The playground is inside the classroom.",
              "type": "open_ended",
              "correct_answer": "F"
            },
            {
              "instruction": "Circle T for True or F for False.",
              "text": "5) The school bus arrives at 8 o’clock.",
              "type": "open_ended",
              "correct_answer": "T"
            }
          ],
          "answers": [
            "uniform",
            "school bus",
            "pencil case",
            "marker",
            "classroom",
            "uniform",
            "school bus",
            "pencil case",
            "marker",
            "classroom",
            "F",
            "T",
            "T",
            "F",
            "T"
          ]
        }
      ]
    }

    print("Wysyłanie żądania do konwertera...")
    try:
        # Wysyłamy payload jako JSON body
        response = requests.post(url, json=payload)
        
        # Sprawdzamy status
        if response.status_code == 200:
            output_file = "test_generated.pdf"
            with open(output_file, "wb") as f:
                f.write(response.content)
            print(f"Sukces! PDF został zapisany jako: {os.path.abspath(output_file)}")
        else:
            print(f"Błąd! Serwer zwrócił status {response.status_code}:")
            print(response.text)
            
    except Exception as e:
        print(f"Wystąpił błąd podczas testu: {e}")

if __name__ == "__main__":
    test_convert_endpoint()
