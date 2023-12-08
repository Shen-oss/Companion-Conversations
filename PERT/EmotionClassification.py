from transformers import BertTokenizer, BertForSequenceClassification
import torch
import numpy as np

class EmotionClassification():
    
    def __init__(self, model_path):
        self.model_path = model_path
        self.model = BertForSequenceClassification.from_pretrained(
                        'hfl/chinese-pert-base',
                        num_labels=8,
                        output_attentions=False,
                        output_hidden_states=False,
                    )
        
        self.model.load_state_dict(torch.load(self.model_path))
        self.tokenizer = BertTokenizer.from_pretrained('hfl/chinese-pert-base', do_lower_case=True)

    def preprocessing(self, input_text, tokenizer):
        return tokenizer.encode_plus(
            input_text,
            add_special_tokens=True,
            max_length=128,
            pad_to_max_length=True,
            return_attention_mask=True,
            return_tensors='pt'
        )
    
    def infer(self, input_text):

        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        self.model.to(device)
        self.model.eval()  # 設置為評估模式

        test_ids = []
        test_attention_mask = []

        # 使用 tokenizer 進行處理
        encoding = self.preprocessing(input_text, self.tokenizer)

        # 提取 IDs 和 Attention Mask
        test_ids.append(encoding['input_ids'])
        test_attention_mask.append(encoding['attention_mask'])
        test_ids = torch.cat(test_ids, dim=0).to(device)
        test_attention_mask = torch.cat(test_attention_mask, dim=0).to(device)

        # 正向傳播，計算 logit 預測值
        with torch.no_grad():
            output = self.model(test_ids, token_type_ids=None, attention_mask=test_attention_mask)

        prediction = np.argmax(output.logits.cpu().numpy()).item()
        return prediction

if __name__ == "__main__":

    ec = EmotionClassification('PERT/EmotionClassification_42.pt')
    new_sentence = '但是，哥吉拉是個巨大的怪獸，醬油並不是我的弱點'

    print('Input Sentence: ', new_sentence)
    print('Predicted Class: ', ec.infer(new_sentence))