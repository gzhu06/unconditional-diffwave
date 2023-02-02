# Copyright 2020 LMNT, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

import numpy as np
import os
import torch
import torchaudio

from argparse import ArgumentParser

from params import AttrDict, params as base_params
from model import AudioDiffusionModel
        
def predict(model_dir=None, params=None, 
            num_wavs=16, device=torch.device('cuda')):
    checkpoint = torch.load(os.path.join(model_dir, 'weights-300000.pt'))
    model = AudioDiffusionModel(AttrDict(base_params)).to(device)
    model.load_state_dict(checkpoint['model'])
    model.eval()
    
    with torch.no_grad():
        
        audio = torch.randn(num_wavs, 1, params.audio_len).to(device)
        sampled = model.sample(noise=audio, num_steps=50)
    
    return sampled.squeeze(1), params.sample_rate

def main(args):
    batch_size = 128
    batch_num = args.num_wavs // batch_size
    os.makedirs(args.output, exist_ok=True)
    for i in range(batch_num):
        audios, sr = predict(model_dir=args.model_dir, 
                            num_wavs=batch_size,
                            params=base_params)
        for j, audio in enumerate(audios):
            
            audio_idx = str(i * batch_size + j)
            torchaudio.save(os.path.join(args.output, audio_idx + '.wav'), 
                            audio.unsqueeze(0).cpu(), sample_rate=sr)

if __name__ == '__main__':
    parser = ArgumentParser(description='runs inference on a spectrogram file generated by diffwave.preprocess')
    parser.add_argument('--model_dir', help='directory containing a trained model (or full path to weights.pt file)')
    parser.add_argument('--output', '-o', default='output',
                        type=str, help='output folder name')
    parser.add_argument('--num_wavs', '-n', default=16, type=int,
                        help='number of generated wav files')
    main(parser.parse_args())
