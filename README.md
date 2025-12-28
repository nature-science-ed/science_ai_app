# Science AI Assistant

A Streamlit-based AI assistant that provides formative feedback on students’ written answers in junior high school science.

## Overview
This application supports science education by analyzing students’ written responses and returning constructive feedback that helps them improve their understanding, rather than simply giving correct answers.

The app is designed for **junior high school students** and focuses on **encouraging scientific thinking and explanation skills**.

## Features
- Input a science question and a student’s written answer
- Classify the answer into three levels:
  - **A**: Scientifically correct and sufficient for junior high school level
  - **B**: Mostly correct but explanation is insufficient or partially missing
  - **C**: Contains important misunderstandings or incorrect reasoning
- Generate feedback in **Japanese**, written in language understandable to students
- Avoid directly presenting the correct answer
- Suggest concrete next steps for improving the response

## Educational Design
This app was designed based on real classroom needs:
- Reduces teachers’ workload in grading descriptive answers
- Provides consistent and structured feedback
- Encourages students to reflect and revise their own thinking
- Emphasizes *learning process* rather than correctness alone

Prompt rules were carefully designed to ensure:
- Clear evaluation criteria
- Positive and supportive feedback tone
- Age-appropriate explanations

## Technologies Used
- Python
- Streamlit
- OpenAI API
- python-dotenv
- Prompt Engineering (rule-based output control)

## Use Cases
- Science classes using descriptive questions
- Practice for written explanations in exams
- Teacher support tool for formative assessment
- Educational research and experimentation with AI-assisted feedback

## Notes
- The OpenAI API key is managed via environment variables (`.env`)
- This project is intended for educational and experimental use

## Author
Developed by a science teacher and researcher with experience in junior high school education.
