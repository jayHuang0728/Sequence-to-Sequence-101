import torch
import torch.nn as nn

from torch.autograd import Variable


class Seq2Seq(nn.Module):

    def __init__(self, encoder, decoder, sos_index, use_cuda):
        self.encoder = encoder
        self.decoder = decoder
        self.sos_index = sos_index
        self.use_cuda = use_cuda

    def forward(self, inputs, targets):

        # data unzip (torch.Variables, list of length)
        input_vars, input_lengths = inputs
        target_vars, target_lengths = targets
        batch_size = input_vars.size(1)

        encoder_outputs, encoder_hidden = self.encoder(input_vars, input_lengths)

        # Prepare variable for decoder on time_step_0
        decoder_input = Variable(torch.LongTensor([[self.sos_index] * batch_size]))

        # Pass the context vector
        decoder_hidden = encoder_hidden

        max_target_length = max(target_lengths)
        decoder_outputs = Variable(torch.zeros(
            max_target_length,
            batch_size,
            self.decoder.output_size
        ))  # (time_steps, batch_size, output_dim)

        if self.use_cuda:
            decoder_input = decoder_input.cuda()
            decoder_outputs = decoder_outputs.cuda()

        # Unfold the decoder RNN on the time dimension
        for t in range(max_target_length):
            decoder_outputs_on_t, decoder_hidden = self.decoder(decoder_input, decoder_hidden)
            decoder_outputs[t] = decoder_outputs_on_t
            decoder_input = decoder_outputs_on_t  # select the former output as input

        return decoder_outputs, decoder_hidden