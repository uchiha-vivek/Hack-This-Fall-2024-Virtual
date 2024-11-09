import os
import streamlit as st
from spellchecker import SpellChecker
from groq import Groq
import re
from gtts import gTTS
import tempfile
from audio_recorder_streamlit import audio_recorder

# Initialize the Groq client
client = Groq(api_key= st.secrets["GROQ_API_KEY"])

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
st.set_page_config(page_title="SmartScore", layout="wide")
st.title("SmartScore: Improve Your Grammar and Communication Skills")
st.write("Get Instant Feedback!")

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
            st.warning("Kindly Enter some text before submitting.")
        else:
            input_text = user_input

            corrector = GrammarCorrector()
           
            # Initialize the client with your API key
            retrieved_content = "Please analyze my writing for grammar, cohesion, sentence structure, vocabulary, and the use of simple, complex, and compound sentences, as well as the effectiveness of abstraction, then provide detailed feedback on any mistakes and present an improved version of my writing."

            # Use the retrieved content as context for the chat completion
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an expert academic writer with 30 years of experience in providing conscise but effective feedback. Instead of asking the student to do this and that you just say replace this with this to improve in a concise manner. You provide concise grammer mistake saying replace this with this alongwith mistake type. you also provide specific replacement sentences for cohesion and abstraction and you point out all the vocab saying that replace this word with this. You have to Analyze the writing for grammar, cohesion, sentence structure, vocabulary, and the use of simple, complex, and compound sentences, as well as the effectiveness of abstraction. Provide detailed feedback on any mistakes and present an improved version of writing. don't use words such as Dive, discover, uncover, delve , , tailor, equipped, navigate, landscape,delve, magic, comprehensive embrace, well equipped,unleash, cutting edge harness that are giving AI generated look... strictly follow academic style in writing. You have the change the sentence according to the english standards if needed but add any sentence by yourself just change the input provided to you.If user is of A1 level then retur the output for the begineers A2 for average and A3 for advance and you can go till C1 level"},
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
    st.write("SmartScore is a sophisticated application designed to elevate your English communication and grammar skills through personalized feedback and structured learning plans. Whether you are preparing for proficiency exams such as IELTS, PTE, or DET, or aiming to enhance your overall fluency, SmartScore offers tailored guidance to improve both your writing and speaking abilities. With a focus on providing actionable insights and targeted strategies, the app empowers users to boost their confidence and achieve their language goals with precision and efficiency.")

# Writing Module
elif page == "Writing Module":
    st.header("Writing Module")
    st.write(""" 
     SmartScore is expertly crafted to help you enhance your English communication and grammar skills. Select from a range of Writing Plans (30, 45, or 60 days) and engage in writing exercises across a variety of diverse topics. Receive real-time, personalized feedback to guide your progress. Consistency is key to mastering writing, and with SmartScore, you can choose a plan tailored to your needs and pace, ensuring steady improvement in both proficiency and confidence.
    """)
    
    # Key Feature Rectangles
    st.subheader("Key Features of Writing Plans")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("### 15-Day Plan")
        st.write("Focused on basics: introduction, conclusion, argumentative, descriptive writing.")
      
            
    with col2:
        st.write("### 60-Day Plan")
        st.write("Expanded topics: Deep-dive into opinion-based and analytical essays .")
        
            
    with col3:
        st.write("### 90-Day Plan")
        st.write("Comprehensive plan covering reports, summaries, and essay writing.")
        

    # Sub-navigation for Writing Plans
    writing_page = st.radio("Select Writing Plan", ["Home", "15-Day Plan", "60-Day Plan", "90-Day Plan"])

    if writing_page == "Home":
        st.write("""Writing is an essential skill. Choose a plan to begin practicing.""")

    elif writing_page == "15-Day Plan":
        st.write("### 15-Day Writing Plan")
        topics_15_day = [
    "The Power of Media in Shaping Political Narratives",
    "Innovative Approaches to Sustainable Agriculture",
    "Virtual Learning vs. In-Person Education: What's the Best Approach?",
    "How Technology Is Altering Cultural Norms Across the Globe",
    "Overcoming Healthcare Inequalities in Low-Income Countries",
    "The Evolution of Global Social Justice Movements",
    "The Impact of Globalization on National Identity",
    "The Role of Gen Z in Shaping Modern Activism",
    "Mental Health in the Digital Age: The Connection Between Social Media and Wellbeing",
    "Exploring Government Accountability in Combatting Climate Change",
    "Artificial Intelligence: Enhancing Innovation While Ensuring Ethical Boundaries",
    "The Future of the Workplace: Hybrid Models and Employee Wellbeing",
    "Democracy and Civic Engagement: How Can We Empower Citizens?",
    "Protecting Personal Data in an Era of Surveillance",
    "Strategies for Achieving Global Sustainability Goals",
    "Tackling Gender Bias in Corporate Leadership Roles",
    "Ensuring Global Food Security in the Age of Climate Change",
    "The Disruption of Education: How Technology Is Changing Learning",
    "The Role of Local Communities in Promoting Global Sustainability",
    "Art in Activism: How Creative Expression Influences Social Change",
    "Effective Crisis Management: Lessons from Natural Disasters and Pandemics",
    "Data Privacy: Is Digital Security Adequate in Protecting Personal Information?",
    "Social Media's Role in Shaping Public Opinion in the Digital Age",
    "The Transition to Renewable Energy: Opportunities and Barriers",
    "Health Systems After COVID-19: How to Build Resilience for Future Pandemics",
    "The Influence of Consumerism on Global Environmental Policy",
    "Addressing the Challenges of Urbanization in Growing Metropolises",
    "Promoting Public Health through Sports and Physical Activity",
    "The Business Case for Diversity and Inclusion in Modern Workplaces",
    "The Future of Mobility: Autonomous Vehicles and Their Impact on Cities"
]

        display_writing_plan(15, topics_15_day)

    elif writing_page == "60-Day Plan":
        st.write("### 60-Day Writing Plan")
        topics_60_day = [
    "The Power of Media in Shaping Political Narratives",
    "Innovative Approaches to Sustainable Agriculture",
    "Virtual Learning vs. In-Person Education: What's the Best Approach?",
    "How Technology Is Altering Cultural Norms Across the Globe",
    "Overcoming Healthcare Inequalities in Low-Income Countries",
    "The Evolution of Global Social Justice Movements",
    "The Impact of Globalization on National Identity",
    "The Role of Gen Z in Shaping Modern Activism",
    "Mental Health in the Digital Age: The Connection Between Social Media and Wellbeing",
    "Exploring Government Accountability in Combatting Climate Change",
    "Artificial Intelligence: Enhancing Innovation While Ensuring Ethical Boundaries",
    "The Future of the Workplace: Hybrid Models and Employee Wellbeing",
    "Democracy and Civic Engagement: How Can We Empower Citizens?",
    "Protecting Personal Data in an Era of Surveillance",
    "Strategies for Achieving Global Sustainability Goals",
    "Tackling Gender Bias in Corporate Leadership Roles",
    "Ensuring Global Food Security in the Age of Climate Change",
    "The Disruption of Education: How Technology Is Changing Learning",
    "The Role of Local Communities in Promoting Global Sustainability",
    "Art in Activism: How Creative Expression Influences Social Change",
    "Effective Crisis Management: Lessons from Natural Disasters and Pandemics",
    "Data Privacy: Is Digital Security Adequate in Protecting Personal Information?",
    "Social Media's Role in Shaping Public Opinion in the Digital Age",
    "The Transition to Renewable Energy: Opportunities and Barriers",
    "Health Systems After COVID-19: How to Build Resilience for Future Pandemics",
    "The Influence of Consumerism on Global Environmental Policy",
    "Addressing the Challenges of Urbanization in Growing Metropolises",
    "Promoting Public Health through Sports and Physical Activity",
    "The Business Case for Diversity and Inclusion in Modern Workplaces",
    "The Future of Mobility: Autonomous Vehicles and Their Impact on Cities",
    "The Digital Divide: Bridging the Gap in Access to Technology",
    "Ethical Considerations in Gene Editing and Biotechnology",
    "The Future of Work: How Automation Will Reshape Job Markets",
    "Water Scarcity: Innovative Solutions for a Thirsty World",
    "Sustainable Architecture: Balancing Design with Environmental Responsibility",
    "The Impact of Remote Learning on Education and Student Wellbeing",
    "The Role of Government Policy in Addressing Income Inequality",
    "Balancing Economic Growth and Environmental Sustainability",
    "Mental Health Initiatives in the Corporate Sector",
    "The Impact of the Gig Economy on Traditional Employment Structures",
    "The Importance of Public Spaces for Community Mental Health",
    "Combating Misinformation in the Age of Social Media",
    "Pop Culture's Influence on Shaping Social Values and Norms",
    "Cybersecurity in a Globalized World: Risks and Solutions",
    "Exploring the Future of Energy: Nuclear and Hydrogen Power Innovations"
]



        display_writing_plan(60, topics_60_day)

    elif writing_page == "90-Day Plan":
        st.write("### 90-Day Writing Plan")
        topics_90_day = [
    "The Power of Media in Shaping Political Narratives",
    "Innovative Approaches to Sustainable Agriculture",
    "Virtual Learning vs. In-Person Education: What's the Best Approach?",
    "How Technology Is Altering Cultural Norms Across the Globe",
    "Overcoming Healthcare Inequalities in Low-Income Countries",
    "The Evolution of Global Social Justice Movements",
    "The Impact of Globalization on National Identity",
    "The Role of Gen Z in Shaping Modern Activism",
    "Mental Health in the Digital Age: The Connection Between Social Media and Wellbeing",
    "Exploring Government Accountability in Combatting Climate Change",
    "Artificial Intelligence: Enhancing Innovation While Ensuring Ethical Boundaries",
    "The Future of the Workplace: Hybrid Models and Employee Wellbeing",
    "Democracy and Civic Engagement: How Can We Empower Citizens?",
    "Protecting Personal Data in an Era of Surveillance",
    "Strategies for Achieving Global Sustainability Goals",
    "Tackling Gender Bias in Corporate Leadership Roles",
    "Ensuring Global Food Security in the Age of Climate Change",
    "The Disruption of Education: How Technology Is Changing Learning",
    "The Role of Local Communities in Promoting Global Sustainability",
    "Art in Activism: How Creative Expression Influences Social Change",
    "Effective Crisis Management: Lessons from Natural Disasters and Pandemics",
    "Data Privacy: Is Digital Security Adequate in Protecting Personal Information?",
    "Social Media's Role in Shaping Public Opinion in the Digital Age",
    "The Transition to Renewable Energy: Opportunities and Barriers",
    "Health Systems After COVID-19: How to Build Resilience for Future Pandemics",
    "The Influence of Consumerism on Global Environmental Policy",
    "Addressing the Challenges of Urbanization in Growing Metropolises",
    "Promoting Public Health through Sports and Physical Activity",
    "The Business Case for Diversity and Inclusion in Modern Workplaces",
    "The Future of Mobility: Autonomous Vehicles and Their Impact on Cities",
    "The Digital Divide: Bridging the Gap in Access to Technology",
    "Ethical Considerations in Gene Editing and Biotechnology",
    "The Future of Work: How Automation Will Reshape Job Markets",
    "Water Scarcity: Innovative Solutions for a Thirsty World",
    "Sustainable Architecture: Balancing Design with Environmental Responsibility",
    "The Impact of Remote Learning on Education and Student Wellbeing",
    "The Role of Government Policy in Addressing Income Inequality",
    "Balancing Economic Growth and Environmental Sustainability",
    "Mental Health Initiatives in the Corporate Sector",
    "The Impact of the Gig Economy on Traditional Employment Structures",
    "The Importance of Public Spaces for Community Mental Health",
    "Combating Misinformation in the Age of Social Media",
    "Pop Culture's Influence on Shaping Social Values and Norms",
    "Cybersecurity in a Globalized World: Risks and Solutions",
    "Exploring the Future of Energy: Nuclear and Hydrogen Power Innovations"
]

        display_writing_plan(90, topics_90_day)

# Speaking Module
elif page == "Speaking Module":
    st.header("Speaking Module")

    # Speaking options
    option = st.radio("Choose an option:", ("Speak in Real Time", "Submit your Audio for feedback"))

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
st.sidebar.write("Developed by NitKeLaunde.")