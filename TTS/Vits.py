from TTS.models import SynthesizerTrn
from TTS.text.symbols import symbols
from TTS.text import  _clean_text
from TTS import commons
from TTS import utils
from torch import no_grad, LongTensor

import torch
import pygame
import soundfile as sf


class TextToSpeak():

    def __init__(self, language = '简体中文', filename = 'result') -> None:
        self.language = language
        self.filename = filename
        # self.modles = os.listdir("modles")
        # self.config = os.listdir("configs")
        self.language_marks = {
                                "Japanese": "",
                                "日本語": "[JA]",
                                "简体中文": "[ZH]",
                                "English": "[EN]",
                                "Mix": "",
                            }
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"

    def text_to_sequence(self, text, symbols, cleaner_names):

        '''Converts a string of text to a sequence of IDs corresponding to the symbols in the text.
            Args:
            text: string to convert to a sequence
            cleaner_names: names of the cleaner functions to run the text through
            Returns:
            List of integers corresponding to the symbols in the text
        '''
        sequence = []
        symbol_to_id = {s: i for i, s in enumerate(symbols)}
        clean_text = _clean_text(text, cleaner_names)
        print(clean_text)
        print(f" length:{len(clean_text)}")
        for symbol in clean_text:
            if symbol not in symbol_to_id.keys():
                continue
            symbol_id = symbol_to_id[symbol]
            sequence += [symbol_id]
        print(f" length:{len(sequence)}")
        return sequence

    def get_text(self, text, hps, is_symbol):

        text_norm = self.text_to_sequence(text, hps.symbols, [] if is_symbol else hps.data.text_cleaners)
        if hps.data.add_blank:
            text_norm = commons.intersperse(text_norm, 0)
        text_norm = LongTensor(text_norm)
        return text_norm

    def TTS(self, speaker, prompt, speed = 1):

        config = f"TTS/configs/{speaker}.json"
        model = f"TTS/models/{speaker}.pth"

        audio_path = f'{self.filename}.wav'

        # 创建模型，加载参数
        hps = utils.get_hparams_from_file(config)
        net_g = SynthesizerTrn(
            len(symbols),
            hps.data.filter_length // 2 + 1,
            hps.train.segment_size // hps.data.hop_length,
            **hps.model).cuda()
        net_g.eval()
        utils.load_checkpoint(model, net_g)

        stn_tst = utils.get_text(prompt, hps)
        with torch.no_grad():
            x_tst = stn_tst.cuda().unsqueeze(0)
            x_tst_lengths = torch.LongTensor([stn_tst.size(0)]).cuda()
            audio = net_g.infer(x_tst, x_tst_lengths, noise_scale=.667, noise_scale_w=0.8, length_scale= 1.0 / speed)[0][
                0, 0].data.cpu().float().numpy()
        sf.write(audio_path, audio, samplerate=hps.data.sampling_rate)

    def fastTTS(self, speaker, prompt, speed = 1):
        
        config = f"TTS/configs/{speaker}.json"
        model = f"TTS/models/{speaker}.pth"
        
        audio_path = f'{self.filename}.wav'
        hps = utils.get_hparams_from_file(config)

        speaker_ids = hps.speakers

        net_g = SynthesizerTrn(
            len(hps.symbols),
            hps.data.filter_length // 2 + 1,
            hps.train.segment_size // hps.data.hop_length,
            n_speakers=hps.data.n_speakers,
            **hps.model).to(self.device)
        _ = net_g.eval()

        _ = utils.load_checkpoint(model, net_g, None)

        if self.language is not None:
            prompt = self.language_marks[self.language] + prompt + self.language_marks[self.language]
        speaker_id = speaker_ids[speaker]
        stn_tst = self.get_text(prompt, hps, False)
        with no_grad():
            x_tst = stn_tst.unsqueeze(0).to(self.device)
            x_tst_lengths = LongTensor([stn_tst.size(0)]).to(self.device)
            sid = LongTensor([speaker_id]).to(self.device)
            
            audio = net_g.infer(x_tst, x_tst_lengths, sid=sid, noise_scale=.667, noise_scale_w=0.8,
                                length_scale=1.0 / speed)[0][0, 0].data.cpu().float().numpy()
        sf.write(audio_path, audio, samplerate=hps.data.sampling_rate)

        def play(self):

            pygame.mixer.init()
            pygame.mixer.music.load(f'{self.filename}.wav')

            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            pygame.quit()

if __name__ == '__main__':
    tts = TextToSpeak()
    tts.fastTTS("Hutao", "有一天有一個小女孩,他走在一條大路上,看到樹上掉了一顆蘋果,從此他把這整個世界剷除了")
    # tts.TTS('Paimon', "有一天有一個小女孩，他走在一條大路上，看到樹上掉了一顆蘋果，從此他把這整個世界剷除了！")
    




