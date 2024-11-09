import os
import streamlit as st
from spellchecker import SpellChecker
from groq import Groq
import re
from gtts import gTTS
import tempfile
from audio_recorder_streamlit import audio_recorder

# Initialize the Groq client
api_key=st.secrets['API_KEY']
print(api_key)
client = Groq(api_key=api_key)

def transcribe_audio(audio_file):
    # Transcribe audio using Groq's Whisper model
    with open(audio_file, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(audio_file, file.read()),
            model="whisper-large-v3-turbo",
            prompt="Transcribe spoken English",
            response_format="json",
            language="en",
            temperature=0.0
        )
    return transcription.text

def get_feedback(transcription):
    # Generate feedback using Groq
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a highly experienced Spoken English expert. Your task is to provide detailed feedback on the following transcription from an English learner. Focus on pronunciation, grammar, fluency, vocabulary usage, sentence structure, coherence, cohesion, and intonation. Provide feedback in these sections: Summary of Feedback, Detailed Mistake Identification, Suggestions for Improvement, and Encouragement."
            },
            {
                "role": "user",
                "content": f"Please provide feedback on the following spoken English: {transcription}"
            }
        ],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content

def text_to_speech(text):
    # Convert feedback text to speech
    tts = gTTS(text=text, lang='en')
    tts.save("feedback_audio.mp3")
    return "feedback_audio.mp3"

class GrammarCorrector:
    def __init__(self):
        self.spell = SpellChecker()

    def identify_mistakes(self, text):
        words = re.findall(r'\b\w+\b', text.lower())
        misspelled = self.spell.unknown(words)
        mistakes = []

        for word in misspelled:
            for match in re.finditer(r'\b' + re.escape(word) + r'\b', text.lower()):
                start = match.start()
                end = match.end()
                original_word = text[start:end]
                mistakes.append((original_word, start, end))

        return mistakes

def report_mistakes(self, text):
        mistakes = self.identify_mistakes(text)
        st.write("\n--- Spelling Mistakes Found ---")
        for i, (mistake, start, end) in enumerate(mistakes, start=1):
            correction = self.spell.correction(mistake.lower())
            st.write(f"{i}. Misspelled: '{mistake}' at position {start}-{end}.")

        return mistakes
# App Configuration
st.set_page_config(page_title="EnglishCoach 2.0", layout="wide")
st.title("EnglishCoach 2.0: Improve Your Communication Skills")
st.write("Unlock Your English Potential with Personalized Feedback!")

# Sidebar for Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Choose a module", ["Home", "Writing Module", "Speaking Module"])

# Function to display writing plan
def display_writing_plan(plan_days, topics):
    # Allow the user to select their current day
    day = st.number_input(f"Select your current day (1-{plan_days})", 1, plan_days)
    
    # Display today's topic
    topic = topics[day - 1]  # Get the topic for the selected day
    st.write(f"### Today's Topic (Day {day}): {topic}")
    
    # Show upcoming topics in a dropdown (next 5 days)
    upcoming_days = list(range(day + 1, min(day + 6, plan_days + 1)))  # Next 5 days
    upcoming_topics = [f"Day {d}: {topics[d - 1]}" for d in upcoming_days]
    
    if upcoming_topics:
        st.selectbox("Upcoming Topics", upcoming_topics)
    else:
        st.write("No upcoming topics available.")

    # Write area for user to submit their essay
    st.write("#### Write your essay below:")
    user_input = st.text_area(f"Write your essay on: {topic}", height=200)

    # Submit button for essay
    if st.button("Submit for Feedback"):
        if len(user_input.strip()) == 0:
            st.warning("Please enter some text before submitting.")
        else:
            input_text = user_input

            corrector = GrammarCorrector()
           
            # Initialize the client with your API key
            retrieved_content = "Please analyze my writing for grammar, cohesion, sentence structure, vocabulary, and the use of simple, complex, and compound sentences, as well as the effectiveness of abstraction, then provide detailed feedback on any mistakes and present an improved version of my writing."

            # Use the retrieved content as context for the chat completion
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an expert academic writer with 40 years of experience in providing conscise but effective feedback. Instead of asking the student to do this and that you just say replace this with this to improve in a concise manner. You provide concise grammer mistake saying replace this with this alongwith mistake type. you also provide specific replacement sentences for cohesion and abstraction and you point out all the vocab saying that replace this word with this. You have to Analyze the writing for grammar, cohesion, sentence structure, vocabulary, and the use of simple, complex, and compound sentences, as well as the effectiveness of abstraction. Provide detailed feedback on any mistakes and present an improved version of writing. don't use words such as Dive, discover, uncover, delve , , tailor, equipped, navigate, landscape,delve, magic, comprehensive embrace, well equipped,unleash, cutting edge harness that are giving AI generated look... strictly follow academic style in writing. You have the change the sentence according to the english standards if needed but add any sentence by yourself just change the input provided to you.If user is of A1 level then retur the output for the begineers A2 for average and A3 for advance and you can go till C1 level"},
                    {"role": "user", "content": retrieved_content},
                    {"role": "user", "content": input_text},
                ],
                model="llama3-70b-8192",
                temperature=0.5,
                max_tokens=1024,
                top_p=1,
                stop=None,
                stream=False,
            )

            model_output = chat_completion.choices[0].message.content
            feedback=model_output

            if feedback:
                st.success("Your writing has been submitted! Here’s the feedback:")
                st.write(f"**Feedback**: {feedback}")


# Home Navigation
if page == "Home":
    st.write("This platform is designed to help you enhance your English communication skills through personalized feedback and structured learning plans. Whether you're preparing for exams like IELTS, PTE, or DET, or simply looking to improve your English fluency, this app provides targeted guidance to boost your confidence in both writing and speaking.")

# Writing Module
elif page == "Writing Module":
    st.header("Writing Module")
    st.write(""" 
    **EnglishCoach 2.0** is designed to assist you in improving your English communication skills.
    Choose a **Writing Plan** (30, 45, or 60 days) and practice writing on various topics. You’ll get real-time feedback.
    The key to mastering writing is consistency. Select a plan that fits your goals and start practicing today!
    """)
    
    # Key Feature Rectangles
    st.subheader("Key Features of Writing Plans")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("### 30-Day Plan")
        st.write("Focused on basics: introduction, conclusion, argumentative, descriptive writing.")
      
            
    with col2:
        st.write("### 45-Day Plan")
        st.write("Expanded topics: deep-dive into opinion-based and analytical essays.")
        
            
    with col3:
        st.write("### 60-Day Plan")
        st.write("Comprehensive plan covering reports, summaries, and essay writing.")
        

    # Sub-navigation for Writing Plans
    writing_page = st.radio("Select Writing Plan", ["Home", "30-Day Plan", "45-Day Plan", "60-Day Plan"])

    if writing_page == "Home":
        st.write("""Writing is an essential skill. Choose a plan to begin practicing.""")

    elif writing_page == "30-Day Plan":
        st.write("### 30-Day Writing Plan")
        topics_30_day = [
            "The Role of Media in Shaping Public Opinion",
            "Sustainable Practices for Environmental Conservation",
            "The Future of Education: Online vs. Traditional Classrooms",
            "Cultural Impacts of Rapid Technological Advancement",
            "Challenges and Solutions for Global Healthcare Accessibility",
            "Social Justice Movements: Impact and Future Prospects",
            "Globalization: Its Influence on Local Cultures and Economies",
            "The Rise of Youth Activism: Drivers and Effects",
            "The Importance of Mental Health in Modern Society",
            "Climate Change Policies: Are Governments Doing Enough?",
            "Artificial Intelligence: Balancing Innovation with Ethical Responsibility",
            "The Future of Work: Remote vs. Office Environments",
            "Civic Responsibility: The Role of Citizens in a Democracy",
            "Digital Privacy and Security: Protecting Personal Information Online",
            "Achieving the Sustainable Development Goals: A Global Effort",
            "Promoting Gender Equality in the Workplace",
            "Ensuring Food Security in a Globalized World",
            "How Technology is Transforming Education: Opportunities and Risks",
            "Building Stronger Communities: The Role of Local Initiatives",
            "Art as a Tool for Social Change: Historical and Modern Perspectives",
            "Crisis Management in the Face of Global Disasters",
            "Data Privacy in the Age of Information: How Safe Are We?",
            "The Influence of Social Media on Public Discourse",
            "Renewable Energy: The Key to a Sustainable Future?",
            "Public Health Policies: Lessons Learned from Global Pandemics",
            "The Impact of Consumerism on the Environment and Society",
            "Urban Development: Solutions for Overcrowded Cities",
            "The Role of Sports in Building a Healthier Society",
            "Diversity and Inclusion in the Workplace: Benefits and Challenges",
            "The Future of Transportation: Innovations and Challenges"
      ]
        display_writing_plan(30, topics_30_day)

    elif writing_page == "45-Day Plan":
        st.write("### 45-Day Writing Plan")
        topics_45_day = topics =  [
          "The Role of Media in Shaping Public Opinion",
          "Sustainable Practices for Environmental Conservation",
          "The Future of Education: Online vs. Traditional Classrooms",
          "Cultural Impacts of Rapid Technological Advancement",
          "Challenges and Solutions for Global Healthcare Accessibility",
          "Social Justice Movements: Impact and Future Prospects",
          "Globalization: Its Influence on Local Cultures and Economies",
          "The Rise of Youth Activism: Drivers and Effects",
          "The Importance of Mental Health in Modern Society",
          "Climate Change Policies: Are Governments Doing Enough?",
          "Artificial Intelligence: Balancing Innovation with Ethical Responsibility",
          "The Future of Work: Remote vs. Office Environments",
          "Civic Responsibility: The Role of Citizens in a Democracy",
          "Digital Privacy and Security: Protecting Personal Information Online",
          "Achieving the Sustainable Development Goals: A Global Effort",
          "Promoting Gender Equality in the Workplace",
          "Ensuring Food Security in a Globalized World",
          "How Technology is Transforming Education: Opportunities and Risks",
          "Building Stronger Communities: The Role of Local Initiatives",
          "Art as a Tool for Social Change: Historical and Modern Perspectives",
          "Crisis Management in the Face of Global Disasters",
          "Data Privacy in the Age of Information: How Safe Are We?",
          "The Influence of Social Media on Public Discourse",
          "Renewable Energy: The Key to a Sustainable Future?",
          "Public Health Policies: Lessons Learned from Global Pandemics",
          "The Impact of Consumerism on the Environment and Society",
          "Urban Development: Solutions for Overcrowded Cities",
          "The Role of Sports in Building a Healthier Society",
          "Diversity and Inclusion in the Workplace: Benefits and Challenges",
          "The Future of Transportation: Innovations and Challenges",
          "The Digital Divide: Addressing Inequality in Access to Technology",
          "Ethical Considerations in Gene Editing Technologies",
          "The Impact of Automation on Job Markets",
          "Water Scarcity: A Global Challenge",
          "Green Architecture: Designing for a Sustainable Future",
          "Impact of Online Learning on Education Systems",
          "The Role of Governments in Tackling Income Inequality",
          "Balancing Economic Growth with Environmental Protection",
          "Mental Health Support Systems in the Workplace",
          "The Rise of Freelancing: Impacts on Traditional Employment",
          "The Role of Public Spaces in Community Well-being",
          "Addressing Misinformation in the Digital Age",
          "The Influence of Pop Culture on Social Values",
          "Cybersecurity Threats in a Globalized World",
          "The Future of Energy: Exploring Nuclear and Hydrogen Power"
      ]


        display_writing_plan(45, topics_45_day)

    elif writing_page == "60-Day Plan":
        st.write("### 60-Day Writing Plan")
        topics_60_day = topics= topics = [
        "The Role of Media in Shaping Public Opinion",
        "Sustainable Practices for Environmental Conservation",
        "The Future of Education: Online vs. Traditional Classrooms",
        "Cultural Impacts of Rapid Technological Advancement",
        "Challenges and Solutions for Global Healthcare Accessibility",
        "Social Justice Movements: Impact and Future Prospects",
        "Globalization: Its Influence on Local Cultures and Economies",
        "The Rise of Youth Activism: Drivers and Effects",
        "The Importance of Mental Health in Modern Society",
        "Climate Change Policies: Are Governments Doing Enough?",
        "Artificial Intelligence: Balancing Innovation with Ethical Responsibility",
        "The Future of Work: Remote vs. Office Environments",
        "Civic Responsibility: The Role of Citizens in a Democracy",
        "Digital Privacy and Security: Protecting Personal Information Online",
        "Achieving the Sustainable Development Goals: A Global Effort",
        "Promoting Gender Equality in the Workplace",
        "Ensuring Food Security in a Globalized World",
        "How Technology is Transforming Education: Opportunities and Risks",
        "Building Stronger Communities: The Role of Local Initiatives",
        "Art as a Tool for Social Change: Historical and Modern Perspectives",
        "Crisis Management in the Face of Global Disasters",
        "Data Privacy in the Age of Information: How Safe Are We?",
        "The Influence of Social Media on Public Discourse",
        "Renewable Energy: The Key to a Sustainable Future?",
        "Public Health Policies: Lessons Learned from Global Pandemics",
        "The Impact of Consumerism on the Environment and Society",
        "Urban Development: Solutions for Overcrowded Cities",
        "The Role of Sports in Building a Healthier Society",
        "Diversity and Inclusion in the Workplace: Benefits and Challenges",
        "The Future of Transportation: Innovations and Challenges",
        "The Digital Divide: Addressing Inequality in Access to Technology",
        "Ethical Considerations in Gene Editing Technologies",
        "The Impact of Automation on Job Markets",
        "Water Scarcity: A Global Challenge",
        "Green Architecture: Designing for a Sustainable Future",
        "Impact of Online Learning on Education Systems",
        "The Role of Governments in Tackling Income Inequality",
        "Balancing Economic Growth with Environmental Protection",
        "Mental Health Support Systems in the Workplace",
        "The Rise of Freelancing: Impacts on Traditional Employment",
        "The Role of Public Spaces in Community Well-being",
        "Addressing Misinformation in the Digital Age",
        "The Influence of Pop Culture on Social Values",
        "Cybersecurity Threats in a Globalized World",
        "The Future of Energy: Exploring Nuclear and Hydrogen Power",
        "Ethical Dilemmas in Business: Profit vs. Social Responsibility",
        "The Importance of Multilingualism in a Globalized World",
        "Space Exploration: Benefits and Challenges for Humanity",
        "The Role of NGOs in Solving Global Crises",
        "Improving Urban Mobility Through Smart Cities",
        "Human Rights in the Age of Global Politics",
        "The Impact of Digital Currencies on Traditional Banking",
        "The Role of Education in Fostering Innovation",
        "Mental Health in the Digital Age: Addressing New Challenges",
        "Women in Leadership: Progress and Remaining Barriers",
        "Addressing Climate Refugees: Legal and Moral Obligations",
        "Artificial Intelligence in Healthcare: Opportunities and Risks",
        "The Impact of Global Tourism on Local Economies"
    ]  
        display_writing_plan(60, topics_60_day)

# Speaking Module
elif page == "Speaking Module":
    st.header("Speaking Module")

    # Speaking options
    option = st.radio("Choose an option:", ("Speak in Real Time", "Submit Audio for feedback"))

    audio_file = None
    audio_bytes = None

    if option == "Submit Audio for feedback":
        audio_file = st.file_uploader("Upload your audio file", type=['wav', 'mp3', 'ogg'])
        if audio_file is not None:
            st.audio(audio_file, format=f"audio/{audio_file.type.split('/')[-1]}")
    else:
        st.write("Click the button below to start recording your voice:")
        audio_bytes = audio_recorder()
        if audio_bytes:
            st.audio(audio_bytes, format="audio/wav")

    if st.button("Get Feedback"):
        if (option == "Submit Audio for feedback" and audio_file is not None) or (option == "Speak in Real Time" and audio_bytes is not None):
            # Save audio to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                if option == "Submit Audio for feedback":
                    tmp_file.write(audio_file.getvalue())
                else:
                    tmp_file.write(audio_bytes)
                tmp_file_path = tmp_file.name

            try:
                # Transcribe audio
                transcription = transcribe_audio(tmp_file_path)
                st.subheader("Transcription:")
                st.write(transcription)

                # Get feedback
                feedback = get_feedback(transcription)
                st.subheader("Feedback:")
                st.write(feedback)

                # Convert feedback to audio
                audio_feedback = text_to_speech(feedback)
                st.audio(audio_feedback)

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

            finally:
                # Clean up temporary file
                os.unlink(tmp_file_path)
        else:
            st.warning("Please upload or record an audio file before requesting feedback.")

# Footer
st.sidebar.markdown("---")
st.sidebar.write("Developed by BotBuilders.")