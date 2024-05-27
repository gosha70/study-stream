# Copyright (c) EGOGE - All Rights Reserved.
# This software may be used and distributed according to the terms of the Apache-2.0 license.
import os
from typing import List
import psycopg2
import traceback
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import joinedload, subqueryload
from study_stream_api.study_stream_school import StudyStreamSchool
from study_stream_api.study_stream_subject import StudyStreamSubject
from study_stream_api.study_stream_message import StudyStreamMessage
from study_stream_api.study_stream_message_link import StudyStreamMessageLink
from study_stream_api.study_stream_message_link_type import StudyStreamMessageLinkType

# Context manager for session handling
from contextlib import contextmanager

# Database connection parameters from environment variables
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# Connect to the database
def get_db_connection(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT):
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    return conn

def get_engine():
    engine = create_engine(
        f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}',        
        poolclass=NullPool
    )
    return engine

engine = get_engine()
Session = sessionmaker(bind=engine)

@contextmanager
def get_session():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()

# Check if a table exists
def table_exists(conn, table_name):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1 
            FROM information_schema.tables 
            WHERE table_name = %s
        );
    """, (table_name,))
    exists = cursor.fetchone()[0]
    cursor.close()
    return exists

# Create tables
def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS study_stream_school (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        school_type SMALLINT NOT NULL,           
        start_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        finish_date TIMESTAMP                      
    );

    CREATE TABLE IF NOT EXISTS study_stream_subject (
        id SERIAL PRIMARY KEY,
        school_id INT REFERENCES study_stream_school(id) ON DELETE CASCADE,
        class_name VARCHAR(255) NOT NULL,
        start_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        finish_date TIMESTAMP     
    );

    CREATE TABLE IF NOT EXISTS study_stream_document (
        id SERIAL PRIMARY KEY,        
        subject_id INT REFERENCES study_stream_subject(id) ON DELETE CASCADE,
        name VARCHAR(255) NOT NULL,
        file_path VARCHAR(255) NOT NULL,
        file_type SMALLINT NOT NULL,
        status SMALLINT NOT NULL,
        creation_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        in_progress_date TIMESTAMP,
        processed_date TIMESTAMP
    );                   
                   
    CREATE TABLE IF NOT EXISTS study_stream_message (
        id SERIAL PRIMARY KEY,   
        type SMALLINT NOT NULL,
        public_content BYTEA NOT NULL,
        secret_content BYTEA,
        created_at TIMESTAMP NOT NULL          
    );                   
    
    CREATE TABLE IF NOT EXISTS study_stream_message_link (
        message_id INT REFERENCES study_stream_message(id) ON DELETE CASCADE,
        entity_type SMALLINT NOT NULL,
        entity_id INT NOT NULL,
        PRIMARY KEY (message_id, entity_type)
    );                              
    """)
    conn.commit()
    cursor.close()

# Insert default/template data
def insert_default_data(conn):
    cursor = conn.cursor()
    
    # Insert dummy StudyStreamSchool
    cursor.execute("""
        INSERT INTO study_stream_school (name, school_type) 
        VALUES (%s, %s) RETURNING id
    """, ('My School', StudyStreamMessageLinkType.SCHOOL.value))
    school_id = cursor.fetchone()[0]

    # Insert dummy StudyStreamSubject
    cursor.execute("""
        INSERT INTO study_stream_subject (class_name, school_id) 
        VALUES (%s, %s)
    """, ('My First Class', school_id))

    conn.commit()
    cursor.close()

def check_study_stream_database(logging):
    conn = get_db_connection()
    
    # Check and create tables if they don't exist
    if not table_exists(conn, 'study_stream_message'):
        logging.info("Creating Study Stream tables ...")
        create_tables(conn)
        logging.info("Creating default School with one Subject ...")
        insert_default_data(conn)
    else:
        logging.info("Study Stream tables already exist !!!")
    
    conn.close()

def get_school_with_subjects(school_id):
    print(f"DB Fetch for School: {school_id}")
    try:
        with get_session() as session:
            school = session.query(StudyStreamSchool).options(joinedload(StudyStreamSchool.subjects)).filter_by(id=school_id).first()  
            process_school(session,school) 
            return school  
    except Exception as e:
        print("An error occurred while fetching schools with related data.")
        print(traceback.format_exc())
    return []          

def fetch_all_schools_with_related_data()-> List[StudyStreamSchool]:
    try:
        with get_session() as session:
            schools = session.query(StudyStreamSchool).options(
                joinedload(StudyStreamSchool.subjects).options(
                    subqueryload(StudyStreamSubject.documents)
                )
            ).all()
            for school in schools:
                process_school(session,school)     
        return schools                    
    except Exception as e:
        print("An error occurred while fetching schools with related data.")
        print(traceback.format_exc())
    return []     

def process_school(session, school: StudyStreamSchool):
    print(f"DB Fetch for School: {school.name}, Type: {school.school_type}")
    messages = fetch_messages(session, StudyStreamMessageLinkType.SCHOOL.value, school.id)
    if len(messages) > 0:
        school.messages = messages
    for subject in school.subjects:
        print(f"DB Fetch for Subject: {subject.class_name}")
        messages = fetch_messages(session, StudyStreamMessageLinkType.SUBJECT.value, subject.id)
        if len(messages) > 0:
            subject.messages = messages
        for document in subject.documents:
            print(f"DB Fetch for Document: {document.name}, File Path: {document.file_path}, Status: {document.status}")
            messages = fetch_messages(session, StudyStreamMessageLinkType.DOCUMENT.value, document.id)
            if len(messages) > 0:
                document.messages = messages
            session.expunge(document)                      
        session.expunge(subject)                       
    session.expunge(school) 

def fetch_messages(session, entity_type, entity_id)-> List[StudyStreamMessage]:
    try:
        links = session.query(StudyStreamMessageLink).filter_by(entity_type=entity_type, entity_id=entity_id).all()
        messages = []
        for link in links:
            message = session.query(StudyStreamMessage).filter_by(id=link.message_id).first()
            if message:
                print(f"    Message Type: {message.type}")
                messages.append(message)
            session.expunge(message)       
        return messages      
    except Exception as e:
        print("An error occurred while fetching schools with related data.")
        print(traceback.format_exc())
    return []   


def create_entity(entity):
    with get_session() as session:
        session.expire_on_commit = False
        session.add(entity)
        session.commit()     

    return entity
