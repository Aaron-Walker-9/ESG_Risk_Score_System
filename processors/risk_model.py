import pandas as pd
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline

def clean_text_to_scored_ESG_df(clean_text):
    """_
    Applies ESG model to text, returns df of sentence labels and scores 
    
    """
    ### Load the models (takes ca. 1 min)
    # Environmental model.
        # In simple words, the tokenizer prepares the text for the model and the model classifies the text
    name = "ESGBERT/EnvironmentalBERT-environmental" # path to download from HuggingFace
    tokenizer = AutoTokenizer.from_pretrained(name)
    model = AutoModelForSequenceClassification.from_pretrained(name, safe_serialization=True)
    # The pipeline combines tokenizer and model to one process.
    pipe_env = pipeline("text-classification", model=model, tokenizer=tokenizer)

    # Also load the social and governance model.
    # Social model.
    name = "ESGBERT/SocialBERT-social"
    tokenizer = AutoTokenizer.from_pretrained(name)
    model = AutoModelForSequenceClassification.from_pretrained(name, safe_serialization=True)
    pipe_soc = pipeline("text-classification", model=model, tokenizer=tokenizer)

    #load Governance model.
    name = "ESGBERT/GovernanceBERT-governance"
    tokenizer = AutoTokenizer.from_pretrained(name)
    model = AutoModelForSequenceClassification.from_pretrained(name, safe_serialization=True)
    pipe_gov = pipeline("text-classification", model=model, tokenizer=tokenizer)
    
    #load sentiment model
    pipe_senti = pipeline("sentiment-analysis", model="distilbert/distilbert-base-uncased-finetuned-sst-2-english", framework="pt")
    
    ESG_features = [pipe_env, pipe_soc, pipe_gov, pipe_senti]
    
    report_df = pd.DataFrame({"sentence":clean_text})
     
    for pipe in ESG_features:

        results = pipe(clean_text, padding=True, truncation=True)

        labels = [x["label"] for x in results]
        scores = [x["score"] for x in results]


        if pipe == pipe_env:
            report_df["Environment"] = labels 
            report_df["Env_score"] = scores
            
        elif pipe == pipe_soc:
            report_df["Social"] = labels 
            report_df["Social_score"] = scores
            
        elif pipe == pipe_gov:
            report_df["Government"] = labels 
            report_df["Gov_score"] = scores
            
        else:
            report_df["Sentiment"] = labels 
            report_df["Senti_score"] = scores
            
            
    return report_df