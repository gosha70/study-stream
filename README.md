# Study Stream
<img src="https://github.com/gosha70/study-stream/assets/17832712/0f225976-657e-4366-aedc-27ca012e8abf" alt="Study Stream" style="width:500px;"/>

---

# StudyStream

Welcome to StudyStream, a dynamic, fluid application designed to be your continuous, flowing source of academic support and resources. StudyStream seamlessly integrates reading, note-taking, and summarizing functionalities into a modern tool that fits into the daily routines of students from various academic backgrounds.

## About StudyStream

StudyStream brings together the essential elements of studying—reading, comprehending, and note-taking—into one intuitive platform. The name itself encapsulates our mission:

- **Study**: Rooted deeply in the academic field, StudyStream is instantly recognizable as a premier study aid.
- **Stream**: Represents the seamless and uninterrupted flow of information and support provided as you progress through your educational materials.

### Brand Identity

- **Dynamic and Fluid**: Adaptable to various subjects and learning styles, StudyStream moves with you through your educational journey.
- **Modern and Approachable**: With a design that is both contemporary and user-friendly, StudyStream is built for today’s learners.

## Features

**Integrated Reading and Note-Taking**:
- Engage with PDFs and other study materials directly within the app.
- Take and organize notes effortlessly within the reading interface.

**Content Summarization**:
- Automatically generate concise summaries to capture key concepts, aiding in quick comprehension and reinforcing learning.

**Interactive Help**:
- Receive context-specific tips, clarifications, and additional resources to enhance your understanding.

**Progress Tracking**:
- Monitor your study habits and progress with built-in analytics that provide actionable insights.

## Getting Started

To start using StudyStream, clone this repository and follow the setup instructions below.

```bash
git clone https://github.com/gosha70/study-stream.git
cd studystream
# follow specific setup instructions for your environment
```

### Install required libraries

```
pip3 install -r requirements.txt
```

### Run **Study Stream** Application

```
python3 -m app.study_stream_app
```
### Database 
All user study items are now stored in the local  `PostgreSQL` database. 
The database is automatically created and populated on the firth application run. The database settings can be found in the local `.env` file.

<img width="730" alt="image" src="https://github.com/gosha70/study-stream/assets/17832712/fff027bb-0f19-47d9-9961-4a5e661deca8">


### Application Configuration
The `Study Stream Settings` dialog allows a user to customize the application presenation and configure optional feature.
<img width="601" alt="image" src="https://github.com/gosha70/study-stream/assets/17832712/2ed0fc8b-c987-4f6e-963f-e9a6319a18ec">

- Set the location for local Large Language Model
- Enable Open AI to be used as an additional assistor for the local RAG
- Switch the color scheme:
  - Light mode:
    <img width="1728" alt="image" src="https://github.com/gosha70/study-stream/assets/17832712/d602ca83-d217-4225-9d8f-facc55cffbe7">

  - Dark mode:
    <img width="1728" alt="image" src="https://github.com/gosha70/study-stream/assets/17832712/791f14df-733d-4b09-b203-323740821101">

  - Turquoise
    <img width="1724" alt="image" src="https://github.com/gosha70/study-stream/assets/17832712/36c275b2-2e12-4e56-a189-d5be1757cbda">
- Change the connection to the local database 


#### `05`/`28`/`2024`
- Enhnaced PDF view allows a user send a question with the selected document content to AI:
<img width="1725" alt="image" src="https://github.com/gosha70/study-stream/assets/17832712/a107bf11-1b2a-44b3-8408-3c69c88d7f46">

- Allow to add and processed all supported document types, sush: `Java`, `Python`, `Json`, `CSV`, etc.

- Allow to save and load the chat history to/from the database

  




