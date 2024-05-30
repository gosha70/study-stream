
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

:triangular_flag_on_post: _We apologize for the inconvenience; our team is actively working on completing the binary installation of our product._

However, you can start using the **StudyStream** application right now by following these steps:

```bash
git clone https://github.com/gosha70/study-stream.git
cd studystream
```

### Install Required Libraries

```bash
pip3 install -r requirements.txt
```

### Run the **StudyStream** Application

Currently, we only provide the script for running the application on Mac or Unix systems through:
```bash
./study_stream.sh
```
* You might need to run `chmod +x study_stream.sh` before running it.

Alternatively, you can run the Python application directly through:
```bash
python3 -m app.study_stream_app
```
When the application runs for the first time, it will create the **PostgreSQL** database with the following configuration:
- `DB_NAME`=study_stream_db
- `DB_USER`=study_stream_db_admin
- `DB_PASSWORD`=study_stream_db_psw
- `DB_HOST`=localhost
- `DB_PORT`=5432

If you have **PostgreSQL** installed on your machine, you can create `/profiles/.env` with the following customized parameters before running the application:
```plaintext
LLM_FOLDER=llm_models
DOCUMENT_FOLDER=study_document
COLOR_SCHEME=dark
OPEN_AI_ENABLED=false
OPEN_AI_KEY=
DB_NAME=study_stream_db
DB_USER=study_stream_db_admin
DB_PASSWORD=study_stream_db_psw
DB_HOST=localhost
DB_PORT=5432
```

### Database

All user study items are now stored in the local `PostgreSQL` database. The database is automatically created and populated on the first application run. The database settings can be found in the local `.env` file.

<img width="300" alt="image" src="https://github.com/gosha70/study-stream/assets/17832712/fff027bb-0f19-47d9-9961-4a5e661deca8">

### Application Configuration

The `StudyStream Settings` dialog allows a user to customize the application presentation and configure optional features.
<img width="300" alt="image" src="https://github.com/gosha70/study-stream/assets/17832712/2ed0fc8b-c987-4f6e-963f-e9a6319a18ec">

- Set the location for the local Large Language Model.
- Enable OpenAI to be used as an additional assistant for the local RAG.
- Switch the color scheme:
  - Light mode:
    <img width="500" alt="image" src="https://github.com/gosha70/study-stream/assets/17832712/d602ca83-d217-4225-9d8f-facc55cffbe7">

  - Dark mode:
    <img width="500" alt="image" src="https://github.com/gosha70/study-stream/assets/17832712/791f14df-733d-4b09-b203-323740821101">

  - Turquoise:
    <img width="500" alt="image" src="https://github.com/gosha70/study-stream/assets/17832712/36c275b2-2e12-4e56-a189-d5be1757cbda">
- Change the connection to the local database.

#### `05/28/2024`

- Enhanced PDF view allows a user to send a question with the selected document content to AI:
<img width="500" alt="image" src="https://github.com/gosha70/study-stream/assets/17832712/a107bf11-1b2a-44b3-8408-3c69c88d7f46">

- Support for adding and processing all supported document types, such as `Java`, `Python`, `JSON`, `CSV`, etc.

- Save and load chat history to/from the database.
