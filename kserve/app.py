import json

import kserve
import numpy as np
import torch
from transformers import BertForTokenClassification, BertTokenizerFast

unique_tags = {'B-LOC', 'B-ORG', 'B-PER', 'I-LOC', 'I-ORG', 'I-PER', 'O'}
labels_to_ids = {k: v for v, k in enumerate(unique_tags)}
ids_to_labels = {v: k for v, k in enumerate(unique_tags)}

def beauty_visual(preds, offset_mapping):
    prediction = ''
    for token_pred, mapping in zip(preds, offset_mapping.squeeze().tolist()):
        if token_pred[0][0] =='[':
            continue
        pred = ''
        if token_pred[1][0] == 'B':
            prediction += ' '
            pred = token_pred[1][2:]
        elif token_pred[1][0] == 'I' and token_pred[0][:2] != '##':
            pred = '-' * len(token_pred[0]) + '-'
        elif token_pred[0][:2] == '##' or token_pred[1][0] == 'I':
            pred = '-' * len(token_pred[0][3:])
        else:
            prediction += ' '
            pred = token_pred[1]
        pred += (mapping[1]-mapping[0] - len(pred)) * '-'
        prediction += pred
    return prediction[1:]

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
            if token.startswith("["):
                continue
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
                ent_text += token
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

        tokens = self.tokenizer.convert_ids_to_tokens(ids.view(-1))
        preds = [ids_to_labels[i] for i in preds.cpu().numpy()]
        tokens_preds = list(zip(tokens, preds))
        entities = self.get_prediction(tokens_preds, inputs["offset_mapping"])
        result = {'text': text, 'entities': entities}

        return result


if __name__ == "__main__":
    model = MyModel("NERtagger")
    model.load()
    kserve.ModelServer().start([model])