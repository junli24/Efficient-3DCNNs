import os
import sys
import matplotlib.pyplot as plt
import json

import nibabel as nib
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms

import pandas as pd


class adni(Dataset):
    def __init__(self, folder, csv_file):
        self.folder = folder
        self.csv_file = csv_file
        self.df = pd.read_csv(self.csv_file, header=None)
        self.filenames = self.df[0].tolist()
        self.labels = self.df[1].tolist()

    def __len__(self):
        return len(self.filenames)

    def __getitem__(self, idx):
        image_path = os.path.join(self.folder, 'mwp2' + self.filenames[idx] + '.nii')
        image_nifti = nib.load(image_path)
        image_data = image_nifti.get_fdata()
        image_tensor = torch.tensor(image_data, dtype=torch.float32)
        image_tensor = image_tensor.unsqueeze(0)
        image_tensor = image_tensor.repeat(3, 1, 1, 1)
        image_tensor = image_tensor.permute(0, 3, 1, 2)
        return image_tensor, self.labels[idx]


class adni_test(Dataset):
    def __init__(self, folder, csv_file):
        self.folder = folder
        self.csv_file = csv_file
        self.df = pd.read_csv(self.csv_file, header=None)
        self.filenames = self.df[0].tolist()
        self.labels = self.df[1].tolist()

    def __len__(self):
        return len(self.filenames)

    def __getitem__(self, idx):
        image_path = os.path.join(self.folder, 'mwp2' + self.filenames[idx] + '.nii')
        image_nifti = nib.load(image_path)
        image_data = image_nifti.get_fdata()
        image_tensor = torch.tensor(image_data, dtype=torch.float32)
        image_tensor = image_tensor.unsqueeze(0)
        image_tensor = image_tensor.repeat(3, 1, 1, 1)
        image_tensor = image_tensor.permute(0, 3, 1, 2)
        return image_tensor, self.filenames[idx]
