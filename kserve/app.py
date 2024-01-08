import json

import kserve
import numpy as np
import torch
from transformers import BertForTokenClassification, BertTokenizerFast

unique_tags = {'B-LOC', 'B-ORG', 'B-PER', 'I-LOC', 'I-ORG', 'I-PER', 'O'}
ids_to_labels = {0: 'I-PER',
  1: 'I-LOC',
  2: 'B-LOC',
  3: 'B-PER',
  4: 'B-ORG',
  5: 'O',
  6: 'I-ORG'}
labels_to_ids = {'I-PER': 0,
  'I-LOC': 1,
  'B-LOC': 2,
  'B-PER': 3,
  'B-ORG': 4,
  'O': 5,
  'I-ORG': 6}

class MyModel(kserve.Model):
    def __init__(self, name: str):
        super().__init__(name)
        self.name = name
        self.ready = False
        self.bert = BertForTokenClassification.from_pretrained('./model/NERtagger')
        self.tokenizer = BertTokenizerFast.from_pretrained('ai-forever/ruBert-base')

    def get_prediction(self, tokens_preds, offset_mapping):
        entities = []
        ent_text=''
        ent_type=''
        cur_start = 0
        cur_end = 0
        for (token, pred), (start, stop) in zip(tokens_preds, offset_mapping.squeeze().tolist()):
            if token.startswith("##"):
                ent_text += token[2:]
                cur_end = stop
                continue
            if pred.startswith("B"):
                entities += [{'text': ent_text, 'type': ent_type, 'start': cur_start, 'end':cur_end}]
                ent_text, ent_type, cur_start, cur_end = token, pred[2:], start, stop
            if pred.startswith("O"):
                entities += [{'text': ent_text, 'type': ent_type, 'start': cur_start, 'end':cur_end}]
                ent_text, ent_type, cur_start, cur_end = token, pred, start, stop
            if pred.startswith("I"):
                ent_text += ' ' + token
                cur_end = stop
        return entities[1:]                       

    def predict(self, request_data, request_headers=None):
        text = request_data["text"]
        inputs = self.tokenizer(text,
                    return_offsets_mapping=True,
                    padding='max_length',
                    truncation=True,
                    max_length=512,
                    return_tensors="pt")
        ids = inputs["input_ids"]
        mask = inputs["attention_mask"]

        outputs = self.bert(ids, attention_mask=mask)
        logits = outputs[0]
        logits = logits.view(-1, len(unique_tags))
        preds = torch.argmax(logits, axis=1)
        preds = preds[1:mask[mask==1].shape[0]]

        tokens = self.tokenizer.convert_ids_to_tokens(ids.view(-1))
        tokens = tokens[1:mask[mask==1].shape[0]]
        preds = [ids_to_labels[i] for i in preds.cpu().numpy()]
        tokens_preds = list(zip(tokens, preds))
        entities = self.get_prediction(tokens_preds, inputs["offset_mapping"])
        result = {'text': text, 'entities': entities}

        return result


if __name__ == "__main__":
    model = MyModel("NERtagger")
    model.load()
    kserve.ModelServer().start([model])