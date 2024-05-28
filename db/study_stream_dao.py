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
from study_stream_api.study_stream_document import StudyStreamDocument
from study_stream_api.study_stream_school_type import StudyStreamSchoolType

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

    CREATE TABLE IF NOT EXISTS study_stream_note (
        id SERIAL PRIMARY KEY,
        subject_id INT UNIQUE REFERENCES study_stream_subject(id) ON DELETE CASCADE,
        json_content JSONB NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
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
    """, ('My College', StudyStreamSchoolType.COLLEGE.value))
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
    if not table_exists(conn, 'study_stream_note'):
        logging.info("Creating Study Stream tables ...")
        create_tables(conn)
        logging.info("Creating default School with one Subject ...")
        insert_default_data(conn)
    else:
        logging.info("Study Stream tables already exist !!!")
    
    conn.close()

def get_subject(subject_id):
    print(f"DB Fetch for Subject: {subject_id}")
    try:
        with get_session() as session:
            subject = (session.query(StudyStreamSubject)
                .options(
                    joinedload(StudyStreamSubject.documents),
                    joinedload(StudyStreamSubject.note)
                )
                .filter_by(id=subject_id)
                .first())   
            process_subject(session, subject)
            return subject
    except Exception as e:
        print(f"An error occurred while fetching a subject '{subject_id}' with related data.")
        print(traceback.format_exc())
    return None   

def get_school_with_subjects(school_id):
    print(f"DB Fetch for School: {school_id}")
    try:
        with get_session() as session:
            school = (session.query(StudyStreamSchool)
                .options(
                    joinedload(StudyStreamSchool.subjects)
                    .joinedload(StudyStreamSubject.documents),
                    joinedload(StudyStreamSchool.subjects)
                    .joinedload(StudyStreamSubject.note)
                )
                .filter_by(id=school_id)
                .first())  
            process_school(session,school) 
            return school  
    except Exception as e:
        print(f"An error occurred while fetching a school '{school_id} with related data.")
        print(traceback.format_exc())
    return None  

def fetch_all_schools_with_related_data() -> List[StudyStreamSchool]:
    try:
        with get_session() as session:
            schools = session.query(StudyStreamSchool).options(
                joinedload(StudyStreamSchool.subjects).options(
                    joinedload(StudyStreamSubject.documents),
                    joinedload(StudyStreamSubject.note)
                )
            ).all()
            for school in schools:
                process_school(session, school)
        return schools
    except Exception as e:
        print("An error occurred while fetching schools with related data.")
        print(traceback.format_exc())
    return [] 

def process_school(session, school: StudyStreamSchool):
    print(f"DB Fetch for School: {school.name}, Type: {school.school_type}")
    for subject in school.subjects:
        process_subject(session, subject)
    session.expunge(school)

def process_subject(session, subject: StudyStreamSubject): 
    print(f"DB Fetch for Subject: {subject.class_name}")
    if subject.note:
        messages = subject.note.to_messages()
        #for message in messages:
        #    print(f"    Message: {message.content}, Created At: {message.created_at}")
    for document in subject.documents:
        #print(f"DB Fetch for Document: {document.name}, File Path: {document.file_path}, Status: {document.status}")
        session.expunge(document)
    session.expunge(subject)  

def fetch_messages_for_subject(session, subject_id):
    subject = session.query(StudyStreamSubject).options(joinedload(StudyStreamSubject.note)).filter_by(id=subject_id).first()
    return subject.note.to_messages() if subject and subject.note else []

def create_entity(entity):
    with get_session() as session:
        session.expire_on_commit = False
        session.add(entity)
        session.commit()     

    return entity

def update_document(updated_document: StudyStreamDocument)-> StudyStreamDocument:
    try:
        with get_session() as session:
            session.expire_on_commit = False
            # Fetch the document
            db_document = StudyStreamDocument.read(session, updated_document.id)
            if not db_document:
                print(f"Document with id {updated_document.id} not found.")
                return None
            
            # Update values
            update_values = {
                'name': updated_document.name,
                'status': updated_document.status,
                'in_progress_date':  updated_document.in_progress_date,
                'processed_date':  updated_document.processed_date
            }
            db_document.update(session, **update_values)
            session.expunge(db_document)  
            return db_document
    except Exception as e:
        print(f"An error occurred while updating Document: {updated_document.id}.")
        print(traceback.format_exc())
    return None  

def delete_entity(entity)-> bool:
    try:
        with get_session() as session:
            if isinstance(entity, StudyStreamDocument): 
                StudyStreamDocument.delete(session=session, object_id=entity.id)
            elif isinstance(entity, StudyStreamSubject):  
                StudyStreamSubject.delete(session=session, object_id=entity.id)
            elif isinstance(entity, StudyStreamSchool):    
                StudyStreamSchool.delete(session=session, object_id=entity.id)
            return True    
    except Exception as e:
        print(f"An error occurred while deleting object: {entity.id}.")
        print(traceback.format_exc())     

    return False       

def update_class(updated_class: StudyStreamSubject)-> StudyStreamSubject:
    try:
        with get_session() as session:
            session.expire_on_commit = False
            # Fetch the document
            db_class = StudyStreamSubject.read(session, updated_class.id)
            if not db_class:
                print(f"Class with id {updated_class.id} not found.")
                return None
            
            print(f"Updating Class fields: name = '{updated_class.class_name}'; start_date = '{updated_class.start_date}'; finish_date = '{updated_class.finish_date}'")
            # Update values
            update_values = {
                'class_name': updated_class.class_name,
                'start_date': updated_class.start_date,
                'finish_date':  updated_class.finish_date
            }
            db_class.update(session, **update_values)
            session.expunge(db_class)  
            return db_class
    except Exception as e:
        print(f"An error occurred while updating Class: {updated_class.id}.")
        print(traceback.format_exc())
    return None  

def update_note(updated_class: StudyStreamSubject, note: str)-> StudyStreamSubject:
    try:
        with get_session() as session:
            session.expire_on_commit = False
            # Fetch the document
            db_class = StudyStreamSubject.read(session, updated_class.id)
            if not db_class:
                print(f"Class with id {updated_class.id} not found.")
                return None
            
            print(f"Updating a note of Class fields: name = '{db_class}'")
            db_class.update_note(session, json_content=note)
            session.expunge(db_class)  
            return db_class
    except Exception as e:
        print(f"An error occurred while updating a note of Class: {updated_class.id}.")
        print(traceback.format_exc())
    return None  

def update_school(updated_school: StudyStreamSchool)-> StudyStreamSchool:
    try:
        with get_session() as session:
            session.expire_on_commit = False
            # Fetch the document
            db_school = StudyStreamSchool.read(session, updated_school.id)
            if not db_school:
                print(f"Class with id {updated_school.id} not found.")
                return None
            
            print(f"Updating Class fields: name = '{updated_school.name}'; school_type = '{updated_school.school_type}';  start_date = '{updated_school.start_date}'; finish_date = '{updated_school.finish_date}'")
            # Update values
            update_values = {
                'name': updated_school.name,
                'school_type': updated_school.school_type,
                'start_date': updated_school.start_date,
                'finish_date':  updated_school.finish_date
            }
            db_school.update(session, **update_values)
            session.expunge(db_school)  
            return db_school
    except Exception as e:
        print(f"An error occurred while updating School: {updated_school.id}.")
        print(traceback.format_exc())
    return None  