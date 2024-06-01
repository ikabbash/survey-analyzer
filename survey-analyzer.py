from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.ai.textanalytics import TextAnalyticsClient
from dotenv import load_dotenv
import json, os

# Set endpoint, key and model from .env
load_dotenv()
COGNITIVE_SERVICES_ENDPOINT = os.environ.get("COGNITIVE_SERVICES_ENDPOINT")
COGNITIVE_SERVICES_KEY = os.environ.get("COGNITIVE_SERVICES_KEY")
FORM_RECOGNIZER_ENDPOINT = os.environ.get("FORM_RECOGNIZER_ENDPOINT")
FORM_RECOGNIZER_KEY = os.environ.get("FORM_RECOGNIZER_KEY")
MODEL_ID = os.environ.get("MODEL_ID")

def extract_document_feedback():
    # Connect to the document intelligence service
    document_analysis_client = DocumentAnalysisClient(endpoint=FORM_RECOGNIZER_ENDPOINT, credential=AzureKeyCredential(FORM_RECOGNIZER_KEY))
    # Path to your local document
    document_path = "surveys/response-1.pdf"
    # Open and read the document
    with open(document_path, "rb") as document:
        # Document analysis
        poller = document_analysis_client.begin_analyze_document(MODEL_ID, document)
        result = poller.result()
        # Initialize an empty dictionary to store the key-value pairs then add field information
        fields_dict = {}
        for name, field in result.documents[0].fields.items():
            field_value = field.value if field.value else field.content
            fields_dict[name] = {
                "ValueType": field.value_type,
                "Value": field_value,
                "Confidence": field.confidence
            }
        # Convert the output dictionary to JSON format then print for logging
        print("Formatted JSON output:\n" + json.dumps(fields_dict, indent=2))
    return fields_dict['Feedback']['Value']

def get_feedback_sentiment():
    # Authenticate to Text Analytics client
    text_analytics_client = TextAnalyticsClient(endpoint=COGNITIVE_SERVICES_ENDPOINT, credential=AzureKeyCredential(COGNITIVE_SERVICES_KEY))
    # Input for sentiment analysis must be in an array
    feedback = [extract_document_feedback()]
    # The list contains exactly only one element, hence using "," extracts it rather than having to use result[0] in the code every time
    result, = text_analytics_client.analyze_sentiment(feedback)
    if not result.is_error:
        print(f"Document Sentiment: {result.sentiment}")
        print(f"Document Confidence Scores: Positive={result.confidence_scores.positive}; Neutral={result.confidence_scores.neutral}; Negative={result.confidence_scores.negative}")
        return result.sentiment

get_feedback_sentiment()