import os
from urllib.parse import urlparse
import uuid
import requests
from schemas.exam_schemas import ExamSubmission, InputCreateExam, Question
from third_parties.question_pipeline import QuestionPipeline
from third_parties.document_pipeline import DocumentPipeline


class ExamService():
    def __init__(self):
        self.document_pipeline=DocumentPipeline()
        self.question_pipeline=QuestionPipeline()

    def create_exam_handler(self, exam: InputCreateExam):
        exam_id=str(uuid.uuid4())
        self.download_file(exam_id,exam.file_upload)
        list_file=[]
        if len(exam.file_upload)>0: 
            for file in os.listdir(exam_id):
                list_file.append(f"{exam_id}/{file}")
        self.document_pipeline.run({"converter":{"sources":list_file}})
        single,multiple,essay=self.question_pipeline.create_question(exam)
        result=[]
        print("/////////////////////////////////")
        print(single)
        for question in single:
            result.append(Question(question_type="single_choice",question=question["question"],options=question["choices"],ai_answer=question["correct_answer"]))
        for question in multiple:
            result.append(Question(question_type="multiple_choice",question=question["question"],options=question["choices"],ai_answer=question["correct_answer"]))
        for question in essay: 
            result.append(Question(question_type="essay",question=question["question"],ai_answer=question["correct_answer"]))
        return result
        
    def download_file(self,exam_id,urls):
        if len(urls)>0: os.makedirs(exam_id, exist_ok=True)
        for url in urls:
            # Get the filename from the URL
            parsed_url = urlparse(url)

            # Extract the filename from the path
            filename = os.path.basename(parsed_url.path)
            # Send a GET request to the URL
            response = requests.get(url)
            # Check if the request was successful
            if response.status_code == 200:
                # Open a local file in write-binary mode and save the content
                with open(f"{exam_id}/{filename}", 'wb') as file:
                    file.write(response.content)
                print(f"File downloaded successfully as {filename}")
            else:
                print(f"Failed to download the file {filename}. Status code:", response.status_code)
    
    def evaluate_exam_handler(self, submission:ExamSubmission):
        result=self.question_pipeline.evaluate_question(submission)
        return result