import json
import sys

import numpy as np
import pandas as pd
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix
from sklearn.metrics import accuracy_score, precision_score, f1_score, recall_score, classification_report
from matplotlib import pyplot as plt


class ADNIclassification(object):
    GROUND_TRUTH_FIELDS = ['database', 'labels']
    PREDICTION_FIELDS = ['results', 'version', 'external_data']

    def __init__(self, ground_truth_filename=None, prediction_filename=None,
                 ground_truth_fields=GROUND_TRUTH_FIELDS,
                 prediction_fields=PREDICTION_FIELDS,
                 subset='validation', verbose=False, top_k=1,
                 check_status=True):
        if not ground_truth_filename:
            raise IOError('Please input a valid ground truth file.')
        if not prediction_filename:
            raise IOError('Please input a valid prediction file.')
        self.subset = subset
        self.verbose = verbose
        self.gt_fields = ground_truth_fields
        self.pred_fields = prediction_fields
        self.top_k = top_k
        self.ap = None
        self.hit_at_k = None
        self.check_status = check_status
        # Retrieve blocked videos from server.
        if self.check_status:
            self.blocked_videos = get_blocked_videos()
        else:
            self.blocked_videos = list()
        # Import ground truth and predictions.
        self.ground_truth = self._import_ground_truth(ground_truth_filename)
        self.prediction = self._import_prediction(prediction_filename)

        if self.verbose:
            print('[INIT] Loaded annotations from {} subset.'.format(subset))
            nr_gt = len(self.ground_truth)
            print('\tNumber of ground truth instances: {}'.format(nr_gt))
            nr_pred = len(self.prediction)
            print('\tNumber of predictions: {}'.format(nr_pred))

    def _import_ground_truth(self, ground_truth_filename):
        """Reads ground truth file, checks if it is well formatted, and returns
           the ground truth instances and the activity classes.

        Parameters
        ----------
        ground_truth_filename : str
            Full path to the ground truth json file.

        Outputs
        -------
        ground_truth : df
            Data frame containing the ground truth instances.
        activity_index : dict
            Dictionary containing class index.
        """
        data = pd.read_csv(ground_truth_filename, header=None)
        # Checking format
        # if not all([field in data.keys() for field in self.gt_fields]):
            # raise IOError('Please input a valid ground truth file.')

        # Initialize data frame
        video_lst = data[0].tolist()
        label_lst = data[1].tolist()

        for i, label in enumerate(label_lst):
            if label == 0:
                label_lst[i] = 'CN'
            elif label == 1:
                label_lst[i] = 'MCI'
            elif label == 2:
                label_lst[i] = 'AD'

        ground_truth = pd.DataFrame({'video-id': video_lst,
                                     'label': label_lst})
        ground_truth = ground_truth.drop_duplicates().reset_index(drop=True)
        return ground_truth

    def _import_prediction(self, prediction_filename):
        """Reads prediction file, checks if it is well formatted, and returns
           the prediction instances.

        Parameters
        ----------
        prediction_filename : str
            Full path to the prediction json file.

        Outputs
        -------
        prediction : df
            Data frame containing the prediction instances.
        """
        with open(prediction_filename, 'r') as fobj:
            data = json.load(fobj)
        # Checking format...
        # if not all([field in data.keys() for field in self.pred_fields]):
            # raise IOError('Please input a valid prediction file.')

        # Initialize data frame
        video_lst, label_lst, score_lst = [], [], []
        for videoid, v in data['results'].items():
            if videoid in self.blocked_videos:
                continue
            for result in v:
                video_lst.append(videoid)
                label_lst.append(result['label'])
                score_lst.append(result['score'])
        prediction = pd.DataFrame({'video-id': video_lst,
                                   'label': label_lst,
                                   'score': score_lst})
        return prediction

    def evaluate(self):
        """Evaluates a prediction file. For the detection task we measure the
        interpolated mean average precision to measure the performance of a
        method.
        """
        hit_at_k = compute_video_hit_at_k(self.ground_truth,
                                          self.prediction, top_k=self.top_k)
        # avg_hit_at_k = compute_video_hit_at_k(
            # self.ground_truth, self.prediction, top_k=self.top_k, avg=True)
        if self.verbose:
            print('[RESULTS] Performance on ActivityNet untrimmed video '
                   'classification task.')
            # print '\tMean Average Precision: {}'.format(ap.mean())
            print('\tError@{}: {}'.format(self.top_k, 1.0 - hit_at_k))
            #print '\tAvg Hit@{}: {}'.format(self.top_k, avg_hit_at_k)
        # self.ap = ap
        self.hit_at_k = hit_at_k
        # self.avg_hit_at_k = avg_hit_at_k

################################################################################
# Metrics
################################################################################

def compute_video_hit_at_k(ground_truth, prediction, top_k=3, avg=False):
    """Compute accuracy at k prediction between ground truth and
    predictions data frames. This code is greatly inspired by evaluation
    performed in Karpathy et al. CVPR14.

    Parameters
    ----------
    ground_truth : df
        Data frame containing the ground truth instances.
        Required fields: ['video-id', 'label']
    prediction : df
        Data frame containing the prediction instances.
        Required fields: ['video-id, 'label', 'score']

    Outputs
    -------
    acc : float
        Top k accuracy score.
    """
    video_ids = np.unique(ground_truth['video-id'].values)
    avg_hits_per_vid = np.zeros(video_ids.size)
    gt_labels = []
    pred_labels = []
    for i, vid in enumerate(video_ids):
        pred_idx = prediction['video-id'] == vid
        if not pred_idx.any():
            continue
        this_pred = prediction.loc[pred_idx].reset_index(drop=True)
        # Get top K predictions sorted by decreasing score.
        sort_idx = this_pred['score'].values.argsort()[::-1][:top_k]
        this_pred = this_pred.loc[sort_idx].reset_index(drop=True)
        # Get labels and compare against ground truth.
        pred_label = this_pred['label'].tolist()
        gt_idx = ground_truth['video-id'] == vid
        gt_label = ground_truth.loc[gt_idx]['label'].tolist()
        avg_hits_per_vid[i] = np.mean([1 if this_label in pred_label else 0
                                       for this_label in gt_label])
        if not avg:
            avg_hits_per_vid[i] = np.ceil(avg_hits_per_vid[i])

        gt_labels.append(gt_label)
        pred_labels.append(pred_label)

    confusion_mat = confusion_matrix(gt_labels, pred_labels, labels=['CN', 'MCI', 'AD'])
    disp = ConfusionMatrixDisplay(confusion_matrix=confusion_mat, display_labels=['CN', 'MCI', 'AD'])
    disp.plot()
    plt.savefig('../results/confusion_matrix.pdf', format='pdf')

    print('accuracy_score', accuracy_score(gt_labels, pred_labels))

    print('Micro precision', precision_score(gt_labels, pred_labels, labels=['CN', 'MCI', 'AD'], average='micro'))
    print('Micro recall', recall_score(gt_labels, pred_labels, labels=['CN', 'MCI', 'AD'], average='micro'))
    print('Micro f1-score', f1_score(gt_labels, pred_labels, labels=['CN', 'MCI', 'AD'], average='micro'))

    print('classification_report\n', classification_report(gt_labels, pred_labels, labels=['CN', 'MCI', 'AD'], digits=8))

    return float(avg_hits_per_vid.mean())
